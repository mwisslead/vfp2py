# coding=utf-8
from __future__ import absolute_import, division, print_function

import io

import sys
import os
import struct
from math import floor, log10
from datetime import datetime, timedelta
from collections import OrderedDict
import re
import errno

import dbf

HEADER_SIZE = 0x29
FOOTER_ENTRY_SIZE = 0x19
ENCRYPTED_IDENTIFIER = b'\xfe\xf2\xee'
IDENTIFIER = b'\xfe\xf2\xff'

def checksum_calc(string):
    chunk = string[0]
    chunka = (chunk & 0xF0) >> 4
    chunkb = (chunk & 0x0F) >> 0
    chunk = string[1]
    chunkc = (chunk & 0xF0) >> 4
    chunkd = (chunk & 0x0F) >> 0

    for chunk in string:
        chunka ^= (chunk & 0xF0) >> 4
        chunkb ^= (chunk & 0x0F) >> 0

        chunk = (chunka << 9) + ((chunka ^ chunkb) << 5)

        chunka, chunkb, chunkc, chunkd = (
            chunka ^ chunkb ^ chunkc ^ ((chunk & 0xF000) >> 12),
            chunkd ^ ((chunk & 0x0F00) >> 8),
            chunka ^ ((chunk & 0x00F0) >> 4),
            chunka ^ chunkb ^ ((chunk & 0x000F) >> 0),
        )

    return (chunka << 12) + (chunkb << 8) + (chunkc << 4) + (chunkd << 0)

class BinaryFix(object):
    def __init__(self, name, open_params):
        self.fid = io.open(name, open_params)

    def read(self, length=None):
        return bytearray(self.fid.read(length))

    def write(self, string):
        self.fid.write(string)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.fid.close()

    def seek(self, pos, start_pos=0):
        self.fid.seek(pos, start_pos)

    def tell(self):
        return self.fid.tell()

def open(name, open_params):
    return BinaryFix(name, open_params)

class FXPName(object):
    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return self.name

class FXPAlias(FXPName):
    def __repr__(self):
        return self.name + '.'

class FXPNumber(object):
    def __init__(self, number, digits, dec_digits=0):
        self.number = number
        digits -= dec_digits
        digits = max(digits, 0)
        self.format_string = '{{:0{}.{}f}}'.format(digits, dec_digits)

    def __repr__(self):
        return self.format_string.format(self.number)

class FXPCurrency(object):
    def __init__(self, number, digits, dec_digits=0):
        self.number = number
        self.dec_digits = dec_digits
        digits -= dec_digits
        digits = max(digits, 0)
        self.digits = digits

    def __repr__(self):
        base = 10**self.dec_digits
        return '${}.{}'.format(self.number // base, self.number % base)

def round_sig(x, sig):
    if x == 0:
        return 0.
    return round(x, sig-int(floor(log10(abs(x))))-1)

def read_string(fid, *args):
    return fid.read(read_ushort(fid)).decode('ISO-8859-1')

def read_single_quoted_string(fid, *args):
    return FXPName("'{}'".format(read_string(fid)))

def read_double_quoted_string(fid, *args):
    return FXPName('"{}"'.format(read_string(fid)))

def read_int8(fid, *args):
    digits = fid.read(1)[0]
    return FXPNumber(fid.read(1)[0], digits)

def read_int16(fid, *args):
    digits = fid.read(1)[0]
    return FXPNumber(read_short(fid), digits)

def read_int32(fid, *args):
    digits = fid.read(1)[0]
    return FXPNumber(read_int(fid), digits)

def read_double(fid, *args):
    digits = fid.read(1)[0] - 1
    dec_digits = fid.read(1)[0]
    return FXPNumber(struct.unpack('<d', fid.read(8))[0], digits, dec_digits)

def read_float(fid, *args):
    return FXPNumber(struct.unpack('<i', fid.read(4))[0] / 65536., 10, 4)

def read_currency(fid, *args):
    digits = fid.read(1)[0] - 1
    dec_digits = fid.read(1)[0]
    return FXPCurrency(struct.unpack('<q', fid.read(8))[0], digits, dec_digits)

def read_datetimeexpr(fid):
    days = struct.unpack('<d', fid.read(8))[0]
    if not days:
        return None
    days = timedelta(days - 2440588)
    days=timedelta(seconds=round(days.total_seconds()))
    return datetime.utcfromtimestamp(0) + days

def read_datetime(fid, *args):
    dt = read_datetimeexpr(fid)
    if not dt:
        return '{ / / }'
    return '{{^{}}}'.format(dt)

def read_date(fid, *args):
    dt = read_datetimeexpr(fid)
    if not dt:
        return '{ / / }'
    return '{{^{}}}'.format(dt.date())

def read_alias(fid, names, *args):
    return FXPAlias(names[read_ushort(fid)])

def read_special_alias(fid, *args):
    return FXPAlias(SPECIAL_NAMES[fid.read(1)[0]])

def read_system_alias(fid, *args):
    return FXPAlias(SYSTEM_NAMES[fid.read(1)[0]])

def read_system_name(fid, *args):
    return FXPName(SYSTEM_NAMES[fid.read(1)[0]])

def read_menu_system_name(fid, *args):
    return FXPName(MENU_SYSTEM_NAMES[fid.read(1)[0]])

def read_name(fid, names):
    return FXPName(names[read_ushort(fid)])

def read_raw(fid, length):
    return ' '.join('{:02x}'.format(d) for d in fid.read(length))

def read_next_code(fid, names, expr=None):
    if expr is None:
        expr = []
    codeval = fid.read(1)[0]
    if codeval == END_EXPR:
        return codeval
    if codeval == PARAMETER_MARK:
        code = codeval
    elif codeval == SQL_SUBQUERY:
        length = read_ushort(fid)
        final = fid.tell() + length
        fid.read(1)
        code = FXPName('(SELECT {})'.format(parse_subline(fid, length, final, names, [])))
    elif codeval in FUNCTIONS:
        code = FUNCTIONS[codeval]
        if codeval in (0xE5, 0xF6):
            code = code(fid, names)
            while expr and type(expr[-1]) is FXPAlias:
                code = FXPName(repr(expr.pop()) + repr(code))
            code = repr(code)
        elif callable(code):
            code = code(fid)
        parameters = []
        while expr:
            parameter = expr.pop()
            if parameter == PARAMETER_MARK:
                break
            parameters.insert(0, parameter)
        code += '({})'.format(', '.join(repr(p) for p in parameters))
        if codeval == 0xE5:
            code = FXPAlias(code)
        else:
            code = FXPName(code)
    elif codeval in OPERATORS:
        code = OPERATORS[codeval]
        if code[1] == 0:
            return read_next_code(fid, names, expr)
        elif code[1] > 0:
            parameters = [p for p in reversed([expr.pop() for i in range(code[1])])]
            if len(parameters) == 1:
                code = FXPName('({} {})'.format(code[0], repr(parameters[0])))
            else:
                code = FXPName('({})'.format((' ' + code[0] + ' ').join(repr(p) for p in parameters)))
        else:
            code = code[0]
    elif codeval in VALUES:
        code = VALUES[codeval]
        if callable(code):
            code = code(fid, names)
        if codeval in (0xF0, 0xF1):
            return read_next_code(fid, names, expr)
        if type(code) is FXPName:
            while expr and type(expr[-1]) is FXPAlias:
                code = FXPName(repr(expr.pop()) + repr(code))
        elif type(code) is FXPAlias:
            pass
        elif type(code) in (float, int):
            code = FXPName(repr(code))
        else:
            code = FXPName(code)
    else:
        raise KeyError(hex(codeval))
    return code

def read_expr(fid, names, *args):
    expr = []
    while True:
        code = read_next_code(fid, names, expr)
        if code == END_EXPR:
            break
        if code:
            expr.append(code)
    if len(expr) == 1:
        return expr[0]
    return expr

def read_setcode(fid, length):
    return ['SET ' + SETCODES[fid.read(1)[0]]]

def read_text(fid, length):
    length = read_ushort(fid)
    return [''.join(chr(x) for x in fid.read(length))]

class Token(object):
    def __init__(self, tokenstr, tokenval):
        self.str = tokenstr
        self.val = tokenval

    def __repr__(self):
        return repr('{}({})'.format(self.str, self.val))

END_EXPR = 0xFD;
PARAMETER_MARK = 0x43;
SQL_SUBQUERY = 0xE8

SPECIAL_NAMES = {
    0x0D: 'M',
}

SYSTEM_NAMES = {
    0x00: '_ALIGNMENT',
    0x05: '_PAGENO',
    0x19: '_DBLCLICK',
    0x1A: '_CALCVALUE',
    0x1B: '_CALCMEM',
    0x1C: '_DIARYDATE',
    0x1D: '_CLIPTEXT',
    0x1E: '_TEXT',
    0x1F: '_PRETEXT',
    0x20: '_TALLY',
    0x21: '_CUROBJ',
    0x22: '_MLINE',
    0x23: '_THROTTLE',
    0x24: '_GENMENU',
    0x2F: '_STARTUP',
    0x30: '_TRANSPORT',
    0x31: '_BEAUTIFY',
    0x32: '_DOS',
    0x33: '_MAC',
    0x34: '_UNIX',
    0x35: '_WINDOWS',
    0x36: '_SPELLCHK',
    0x37: '_SHELL',
    0x39: '_SCREEN',
    0x3A: '_BUILDER',
    0x3B: '_CONVERTER',
    0x3C: '_WIZARD',
    0x3D: '_TRIGGERLEVEL',
    0x3E: '_ASCIICOLS',
    0x3F: '_ASCIIROWS',
    0x40: '_BROWSER',
    0x41: '_SCCTEXT',
    0x42: '_COVERAGE',
    0x43: '_VFP',
    0x44: '_GALLERY',
    0x45: '_GETEXPR',
    0x46: '_INCLUDE',
    0x47: '_GENHTML',
    0x49: '_SAMPLES',
    0x4A: '_TASKLIST',
    0x4B: '_ObjectBrowser',
    0x4D: '_FOXCODE',
    0x4E: '_FoxTask',
    0x4F: '_CODESENSE',
    0x50: '_INCSEEK',
    0x51: '_PAGETOTAL',
    0x52: '_FOXREF',
    0x53: '_TOOLBOX',
    0x54: '_TASKPANE',
    0x55: '_REPORTBUILDER',
    0x56: '_REPORTPREVIEW',
    0x57: '_REPORTOUTPUT',
}

MENU_SYSTEM_NAMES = {
    0x02: '_MSYSMENU',
    0x03: '_MSM_SYSTM',
    0x04: '_MSM_FILE',
    0x05: '_MSM_EDIT',
    0x08: '_MSM_PROG',
    0x09: '_MSM_WINDO',
    0x0A: '_MSM_VIEW',
    0x0B: '_MSM_TOOLS',
    0x0D: '_MSYSTEM',
    0x10: '_MST_HPSCH',
    0x12: '_MST_MACRO',
    0x13: '_MST_SP100',
    0x1B: '_MST_SP200',
    0x1E: '_MST_TECHS',
    0x1F: '_MST_ABOUT',
    0x22: '_MST_VFPWEB',
    0x23: '_MFILE',
    0x24: '_MFI_NEW',
    0x25: '_MFI_OPEN',
    0x26: '_MFI_CLOSE',
    0x27: '_MFI_CLALL',
    0x28: '_MFI_SP100',
    0x29: '_MFI_SAVE',
    0x2A: '_MFI_SAVAS',
    0x2B: '_MFI_REVRT',
    0x2C: '_MFI_SP200',
    0x2F: '_MFI_SYSPRINT',
    0x31: '_MFI_SP300',
    0x32: '_MFI_QUIT',
    0x33: '_MFI_PREVU',
    0x34: '_MFI_PGSET',
    0x35: '_MFI_IMPORT',
    0x36: '_MFI_EXPORT',
    0x37: '_MFI_SP400',
    0x38: '_MFI_SEND',
    0x39: '_MEDIT',
    0x3A: '_MED_UNDO',
    0x3B: '_MED_REDO',
    0x3C: '_MED_SP100',
    0x3D: '_MED_CUT',
    0x3E: '_MED_COPY',
    0x3F: '_MED_PASTE',
    0x40: '_MED_PSTLK',
    0x41: '_MED_CLEAR',
    0x42: '_MED_SP200',
    0x43: '_MED_INSOB',
    0x44: '_MED_OBJ',
    0x45: '_MED_LINK',
    0x47: '_MED_SP300',
    0x48: '_MED_SLCTA',
    0x49: '_MED_SP400',
    0x4A: '_MED_GOTO',
    0x4B: '_MED_FIND',
    0x4D: '_MED_REPL',
    0x4F: '_MED_SP500',
    0x50: '_MED_BEAUT',
    0x51: '_MED_PREF',
    0x70: '_MPROG',
    0x71: '_MPR_DO',
    0x72: '_MPR_SP100',
    0x73: '_MPR_CANCL',
    0x74: '_MPR_RESUM',
    0x76: '_MPR_COMPL',
    0x7C: '_MPR_SUSPEND',
    0x7D: '_MWINDOW',
    0x7E: '_MWI_ARRAN',
    0x7F: '_MWI_HIDE',
    0x82: '_MWI_CLEAR',
    0x83: '_MWI_SP100',
    0x88: '_MWI_ROTAT',
    0x8A: '_MWI_SP200',
    0x8B: '_MWI_CMD',
    0x8C: '_MWI_VIEW',
    0x8D: '_MVI_TOOLB',
    0x8E: '_MVIEW',
    0x90: '_MTOOLS',
    0x91: '_MTL_WZRDS',
    0x92: '_MTL_SP100',
    0x93: '_MTL_SP200',
    0x94: '_MTL_SP300',
    0x95: '_MTL_SP400',
    0x96: '_MTL_OPTNS',
    0x97: '_MTL_BROWSER',
    0x98: '_MTI_FOXCODE',
    0x99: '_MTL_DEBUGGER',
    0x9A: '_MTI_TRACE',
    0x9E: '_MTI_LOCALS',
    0x9F: '_MTI_DBGOUT',
    0xA0: '_MTI_CALLSTACK',
    0xC4: '_MSM_TEXT',
    0xE6: '_MST_MSDNS',
    0xED: '_MTL_GALLERY',
    0xEE: '_MTL_COVERAGE',
    0xEF: '_MTI_TASKLIST',
    0xF1: '_MTI_DOCVIEW',
    0xF2: '_MTI_BREAKPOINT',
    0xF4: '_MED_LISTMEMBERS',
    0xF5: '_MED_QUICKINFO',
    0xF6: '_MED_BKMKS',
    0xFD: '_MWI_CASCADE',
    0xFE: '_MWI_DOCKABLE',
}

COMMANDS = {
    #Commands are identified by a single byte as shown in the following list:
    0x00: 'SELECT',
    0x01: lambda fid, length: ['RAW CODE: ' + fid.read(length).decode('ISO-8859-1')],
    0x02: '?',
    0x03: '??',
    0x04: '@',
    0x05: 'ACCEPT',
    0x06: 'APPEND',
    0x07: 'ASSIST',
    0x08: 'AVERAGE',
    0x09: 'BROWSE',
    0x0A: 'CALL',
    0x0B: 'CANCEL',
    0x0C: 'CASE',
    0x0D: 'CHANGE',
    0x0E: 'CLEAR',
    0x0F: 'CLOSE',
    0x10: 'CONTINUE',
    0x11: 'COPY',
    0x12: 'COUNT',
    0x13: 'CREATE',
    0x14: 'DELETE',
    0x15: 'DIMENSION',
    0x16: 'DIR',
    0x17: 'DISPLAY',
    0x18: 'DO',
    0x19: 'EDIT',
    0x1A: 'EJECT',
    0x1B: 'ELSE',
    0x1C: 'ENDCASE',
    0x1D: 'ENDDO',
    0x1E: 'ENDIF',
    0x1F: 'ENDTEXT',
    0x20: 'ERASE',
    0x21: 'EXIT',
    0x22: 'FIND',
    0x23: 'GO',
    0x24: 'HELP',
    0x25: 'IF',
    0x26: 'INDEX',
    0x27: 'INPUT',
    0x28: 'INSERT',
    0x29: 'JOIN',
    0x2A: 'LABEL',
    0x2B: 'LIST',
    0x2C: 'LOAD',
    0x2D: 'LOCATE',
    0x2E: 'LOOP',
    0x2F: 'MODIFY',
    0x30: lambda fid, length: ['NOTE'] + [fid.read(length).decode('ISO-8859-1')],#'NOTE',
    0x31: 'ON',
    0x32: 'OTHERWISE',
    0x33: 'PACK',
    0x34: 'PARAMETERS',
    0x35: 'PRIVATE',
    0x36: 'PROCEDURE',
    0x37: 'PUBLIC',
    0x38: 'QUIT',
    0x39: 'READ',
    0x3A: 'RECALL',
    0x3B: 'REINDEX',
    0x3C: 'RELEASE',
    0x3D: 'RENAME',
    0x3E: 'REPLACE',
    0x3F: 'REPORT',
    0x40: 'RESTORE',
    0x41: 'RESUME',
    0x42: 'RETURN',
    0x43: 'RUN',
    0x44: 'SAVE',
    0x45: 'SEEK',
    0x46: 'SELECT',
    0x47: read_setcode,
    0x48: 'SKIP',
    0x49: 'SORT',
    0x4A: 'STORE',
    0x4B: 'SUM',
    0x4C: 'SUSPEND',
    0x4D: 'TEXT',
    0x4E: 'TOTAL',
    0x4F: 'TYPE',
    0x50: 'UPDATE',
    0x51: 'USE',
    0x52: 'WAIT',
    0x53: 'ZAP',
    0x54: lambda fid, length: [], #variable assignment
    0x55: 'ENDPROC\n',
    0x56: 'EXPORT',
    0x57: 'IMPORT',
    0x58: 'RETRY',
    0x5A: 'UNLOCK',
    0x5B: 'FLUSH',
    0x5C: 'KEYBOARD',
    0x5D: 'MENU',
    0x5E: 'SCATTER',
    0x5F: 'GATHER',
    0x60: 'SCROLL',
    0x68: 'CREATE',
    0x69: 'ALTER',
    0x6A: 'DROP',
    0x6F: 'SELECT',
    0x70: 'UPDATE',
    0x71: 'DELETE',
    0x72: 'INSERT',
    0x73: 'DEFINE',
    0x74: 'ACTIVATE',
    0x75: 'DEACTIVATE',
    0x76: 'PRINTJOB',
    0x77: 'ENDPRINTJOB',
    0x79: '???',
    0x7A: 'MOVE',
    0x7B: 'ON', #CLEAR ON event
    0x7C: 'DECLARE',
    0x7D: 'CALCULATE',
    0x7E: 'SCAN',
    0x7F: 'ENDSCAN',
    0x80: 'SHOW',
    0x81: 'PLAY',
    0x82: 'GETEXPR',
    0x83: 'COMPILE',
    0x84: 'FOR',
    0x85: 'ENDFOR',
    0x86: '=', #expression,
    0x87: 'HIDE',
    0x89: 'SIZE',
    0x8A: 'PUSH',
    0x8B: 'POP',
    0x8C: 'ZOOM',
    0x8D: '\\',
    0x8E: '\\\\',
    0x8F: 'BUILD',
    0x90: 'EXTERNAL',
    0x93: 'BLANK',
    0x95: 'OPEN',
    0x96: 'ADD',
    0x97: 'REMOVE',
    0x99: lambda fid, length: [], #function call
    0x9B: 'BEGIN',
    0x9C: 'ROLLBACK',
    0x9D: 'END',
    0x9E: 'add hidden method',
    0x9F: 'HIDDEN',
    0xA0: 'VALIDATE',
    0xA1: 'PROTECTED',
    0xA2: 'add method',
    0xA3: 'add protected method',
    0xA6: 'WITH',
    0xA7: 'ENDWITH',
    0xA8: 'ERROR',
    0xA9: 'ASSERT',
    0xAA: 'DEBUGOUT',
    0xAB: 'FREE',
    0xAC: 'NODEFAULT',
    0xAD: 'MOUSE',
    0xAE: 'LOCAL',
    0xAF: 'LPARAMETERS',
    0xB0: 'CD',
    0xB1: 'MKDIR',
    0xB2: 'RMDIR',
    0xB3: 'DEBUG',
    0xB4: lambda fid, length: ['BAD CODE: ' + fid.read(length).decode('ISO-8859-1')],
    0xB5: 'FOR EACH',
    0xB6: 'ENDFOREACH',
    0xB7: 'DOEVENTS',
    0xB9: 'IMPLEMENTS',
    0xBA: 'TRY',
    0xBB: 'CATCH',
    0xBC: 'FINALLY',
    0xBD: 'THROW',
    0xBE: 'ENDTRY',
    0xFB: read_text,
}

SETCODES = {
    0x01: 'ALTERNATE',
    0x02: 'BELL',
    0x03: 'CARRY',
    0x05: 'CENTURY',
    0x07: 'COLOR',
    0x09: 'CONFIRM',
    0x0A: 'CONSOLE',
    0x0B: 'DATE',
    0x0C: 'DEBUG',
    0x0E: 'DEFAULT',
    0x0D: 'DECIMALS',
    0x0F: 'DELETED',
    0x15: 'ESCAPE',
    0x16: 'EXACT',
    0x17: 'EXCLUSIVE',
    0x18: 'FIELDS',
    0x1A: 'FILTER',
    0x1B: 'FIXED',
    0x1C: 'FORMAT',
    0x1D: 'FUNCTION',
    0x1E: 'HEADINGS',
    0x1F: 'HELP',
    0x21: 'INDEX',
    0x23: 'MARGIN',
    0x24: 'MEMOWIDTH',
    0x26: 'MESSAGE',
    0x27: 'ODOMETER',
    0x28: 'ORDER',
    0x29: 'PATH',
    0x2A: 'PRINTER',
    0x2B: 'PROCEDURE',
    0x2D: 'RELATION',
    0x2E: 'SAFETY',
    0x30: 'STATUS',
    0x31: 'STEP',
    0x32: 'TALK',
    0x35: 'TYPEAHEAD',
    0x36: 'UNIQUE',
    0x37: 'VIEW',
    0x39: 'HOURS',
    0x3A: 'MARK',
    0x3B: 'POINT',
    0x3C: 'SEPERATOR',
    0x3D: 'BORDER',
    0x3E: 'CLOCK',
    0x40: 'SPACE',
    0x41: 'COMPATIBLE',
    0x42: 'AUTOSAVE',
    0x43: 'BLOCKSIZE',
    0x45: 'DEVELOPMENT',
    0x46: 'NEAR',
    0x48: 'REFRESH',
    0x49: 'LOCK',
    0x4C: 'WINDOW',
    0x4D: 'REPROCESS',
    0x4E: 'SKIP',
    0x51: 'FULLPATH',
    0x54: 'RESOURCE',
    0x55: 'TOPIC',
    0x57: 'LOGERRORS',
    0x59: 'SYSMENU',
    0x5A: 'NOTIFY',
    0x5C: 'MACKEY',
    0x5D: 'CURSOR',
    0x5E: 'UDFPARMS',
    0x5F: 'MULTILOCKS',
    0x60: 'TEXTMERGE',
    0x61: 'OPTIMIZE',
    0x62: 'LIBRARY',
    0x64: 'ANSI',
    0x65: 'TRBETWEEN',
    0x66: 'PDSETUP',
    0x68: 'KEYCOMP',
    0x69: 'PALETTE',
    0x6A: 'READBORDER',
    0x6B: 'COLLATE',
    0x6D: 'NOCPTRANS',
    0x77: 'NULL',
    0x79: 'TAG',
    0x7B: 'CPDIALOG',
    0x7C: 'CPCOMPILE',
    0x7D: 'SECONDS',
    0x7E: 'CLASSLIB',
    0x7F: 'DATABASE',
    0x80: 'DATASESSION',
    0x81: 'FDOW',
    0x82: 'FWEEK',
    0x83: 'SYSFORMATS',
    0x84: 'OLEOBJECT',
    0x85: 'ASSERTS',
    0x86: 'COVERAGE',
    0x87: 'EVENTTRACKING',
    0x88: 'NULLDISPLAY',
    0x89: 'EVENTLIST',
    0x8D: 'BROWSEIME',
    0x8E: 'STRICTDATE',
    0x8F: 'AUTOINCERROR',
    0x90: 'ENGINEBEHAVIOR',
    0x91: 'TABLEVALIDATE',
    0x92: 'SQLBUFFERING',
    0x94: 'TABLEPROMPT',
    0xFE: '\n',
}

CLAUSES = {
    0x01: 'ADDITIVE',
    0x02: 'ALIAS',
    0x03: 'ALL',
    0x04: 'ARRAY',
    0x05: 'AT',
    0x06: 'BAR',
    0x07: ',',
    0x08: 'BLANK',
    0x0C: 'CLEAR',
    0x0D: 'COLOR',
    0x0E: 'DEFAULT',
    0x0F: 'DOUBLE',
    0x11: 'FIELDS',
    0x12: 'FILE',
    0x13: 'FOR',
    0x14: 'FORM',
    0x15: 'FROM',
    0x16: 'IN',
    0x17: 'KEY',
    0x18: '(@ or LIKE)',
    0x1A: 'MACROS',
    0x1B: 'MEMO',
    0x1C: 'MENU',
    0x1D: 'MESSAGE',
    0x1E: 'NEXT',
    0x1F: 'OFF',
    0x20: 'ON',
    0x21: 'PRINTER',
    0x22: 'PROMPT',
    0x23: 'RECORD',
    0x24: 'REST',
    0x25: 'SAVE',
    0x26: 'SCREEN',
    0x27: 'TITLE',
    0x28: 'TO',
    0x29: 'TOP',
    0x30: 'NOOPTIMIZE',
    0x2B: 'WHILE',
    0x2C: 'WINDOW',
    0x2E: 'OBJECT',
    0x31: 'TABLE',
    0x32: 'LABEL',
    0x33: 'REPORT',
    0x36: 'BOTTOM',
    0x38: 'BY',
    0x39: 'NOCONSOLE',
    0x3A: 'NOWAIT',
    0x3B: 'PLAIN',
    0x3C: 'DESCENDING',
    0x3D: 'NOWINDOW',
    0x40: 'FONT',
    0x41: 'STYLE',
    0x42: 'RGB',
    0x48: 'CASE',
    0x49: 'ID',
    0x4A: 'NAME',
    0x4B: 'PROGRAM',
    0x4C: 'QUERY',
    0x4E: 'SCHEME',
    0x4F: 'CLASS',
    0x51: 'AS',
    0x52: 'CLASSLIB',
    0x56: 'DLLS',
    0x57: 'SHORT',
    0x58: 'LEFT',
    0x59: 'RIGHT',
    0x5B: 'RTLJUSTIFY',
    0x5C: 'LTRJUSTIFY',
    0x5F: 'PICTRES',

    0xE5: read_name, #user defined function alias
    0xF6: read_name, #user defined function
    0xFC: read_expr,
    END_EXPR: 'END EXPR', #0xFD
    0xFE: '\n'
}

MULTICLAUSES = {
    0x10: ('=', 'ERROR'),
    0xBB: ('XL5', 'WITH BUFFERING='),
    0xBC: ('INTO', 'ACTIVATE', 'COMMAND', 'PAD'),
    0xBD: ('CENTER', 'CURSOR', 'TRANSACTION', 'APP', 'MINIMIZE', 'ESCAPE'),
    0xBE: ('PROCEDURE', 'DELIMITED', 'EXE', 'DISTINCT', 'DOS', 'PAGE'),
    0xBF: ('UNKNOWN', 'MIN', 'FLOAT'),
    0xC0: ('HAVING', 'FREE', 'LOCAL', 'FOOTER'),
    0xC1: ('LINE', 'TRIGGER', 'GLOBAL', 'GET'),
    0xC2: ('SHARED', 'DATABASE', 'DROP', 'GETS', 'NOINIT'),
    0xC3: ('ORDER BY', 'OF', 'REPLACE', 'NOCLOSE'),
    0xC4: ('SAY', 'VIEWS'),
    0xC5: ('VALUES', 'DBLCLICK'),
    0xC6: ('POPUP', 'WHERE', 'DLL', 'DRAG', 'EXCLUDE'),
    0xC7: ('*', 'STEP', 'XLS', 'MARK'),
    0xC8: ('READ', 'MARGIN', 'RPD', 'READERROR'),
    0xCA: ('TAG', 'SET', 'FORCE', 'NOMINIMIZE', 'EXIT'),
    0xCB: ('STATUS', 'RECOMPILE', 'PRIMARY', 'WRK'),
    0xCC: ('STRUCTURE', 'RELATIVE', 'FOREIGN', 'PROTECTED'),
    0xCD: ('SHUTDOWN', 'NOFILTER'),
    0xCE: ('TIMEOUT', 'UPDATE'),
    0xCF: ('SHADOW',),
    0xD0: ('NOCLEAR', 'SELECTION'),
    0xD1: ('WITH', 'INTEGER', 'CONNECTION'),
    0xD2: ('NOMARGIN',),
    0xD3: ('UNIQUE', 'SIZE'),
    0xD4: ('TYPE', 'LONG', 'SYSTEM'),
    0xD5: ('EVENTS', 'CSV', 'COLUMN'),
    0xD6: ('STRING', 'SHEET', 'NORM'),
    0xD7: ('READWRITE',),
}

VALUES = {
    0x2D: '.F.',
    0x61: '.T.',
    0xE4: '.NULL.',
    0xD9: read_double_quoted_string,
    0xDB: '',
    0xDE: read_currency,
    0xDF: '::',
    0xE0: read_name,
    0xE1: read_system_alias,
    0xE2: '.',
    0xE3: read_alias,
    0xE6: read_datetime,
    0xE7: read_float,
    SQL_SUBQUERY: 'SQL SUBQUERY', #0xE8
    0xE9: read_int32,
    0xEB: read_next_code,
    0xEC: read_menu_system_name,
    0xED: read_system_name,
    0xEE: read_date,
    0xF0: lambda fid, *args: '(SHORT CIRCUIT AND IN {})'.format(read_ushort(fid)),
    0xF1: lambda fid, *args: '(SHORT CIRCUIT OR IN {})'.format(read_ushort(fid)),
    0xF2: lambda fid, *args: '(SHORT CIRCUIT IIF IN {})'.format(read_ushort(fid)),
    0xF3: lambda fid, *args: '(SHORT CIRCUIT IIF IN {})'.format(read_ushort(fid)),
    0xF4: read_alias,
    0xF5: read_special_alias,
    0xF7: read_name,
    0xF8: read_int8,
    0xF9: read_int16,
    0xFA: read_double,
    0xFB: read_single_quoted_string,
    0xFC: read_expr,
    0xFF: lambda fid, *args: 'ff ' + read_raw(fid, 2),
}

OPERATORS = {
    0x00: ('NOP', 0),
    0x01: ('$', 2),
    0x03: ('END PAREN', 0),
    0x04: ('*', 2),
    0x05: ('^', 2),
    0x06: ('+', 2),
    0x07: (',', 2),
    0x08: ('-', 2),
    0x09: ('AND', 2),
    0x0A: ('NOT', 1),
    0x0B: ('OR', 2),
    0x0C: ('/', 2),
    0x0D: ('<', 2),
    0x0E: ('<=', 2),
    0x0F: ('!=', 2),
    0x10: ('=', 2),
    0x11: ('>', 2),
    0x12: ('>=', 2),
    0x14: ('==', 2),
    0x18: ('@', -1),
    0xCC: ('', 1),
}

FUNCTIONS = {
    0x19: 'ABS',
    0x1A: lambda fid: EXTENDED1[fid.read(1)[0]],
    0x1B: 'ALIAS',
    0x1C: 'ASC',
    0x1D: 'AT',
    0x1E: 'BOF',
    0x1F: 'CDOW',
    0x20: 'CHR',
    0x21: 'CMONTH',
    0x22: 'COL',
    0x23: 'CTOD',
    0x24: 'DATE',
    0x25: 'DAY',
    0x26: 'DBF',
    0x27: 'DELETED',
    0x28: 'DISKSPACE',
    0x29: 'DOW',
    0x2A: 'DTOC',
    0x2B: 'EOF',
    0x2C: 'ERROR',
    0x2E: 'FCOUNT',
    0x2F: 'FIELD',
    0x30: 'FILE', 
    0x31: 'FKLABEL',
    0x32: 'FKMAX',
    0x33: 'FLOCK',
    0x34: 'FOUND',
    0x35: 'GETENV',
    0x36: 'IIF',
    0x37: 'INKEY',
    0x38: 'INT',
    0x39: 'ISALPHA',
    0x3A: 'ISCOLOR',
    0x3B: 'ISLOWER',
    0x3C: 'ISUPPER',
    0x3D: 'LEFT',
    0x3E: 'LEN',
    0x3F: 'LOCK',
    0x40: 'LOWER',
    0x41: 'LTRIM',
    0x42: 'LUPDATE',
    PARAMETER_MARK: 'MARK PARAMETERS', #0x43
    0x44: 'MAX',
    0x45: 'MESSAGE',
    0x46: 'MIN',
    0x47: 'MOD',
    0x48: 'MONTH',
    0x49: 'NDX',
    0x4A: 'OS',
    0x4B: 'PCOL',
    0x4C: 'PROW',
    0x4D: 'READKEY',
    0x4E: 'RECCOUNT',
    0x4F: 'RECNO',
    0x50: 'RECSIZE',
    0x51: 'REPLICATE',
    0x52: 'RIGHT',
    0x53: 'RLOCK',
    0x54: 'ROUND',
    0x55: 'ROWS',
    0x56: 'RTRIM',
    0x57: 'SELECT',
    0x58: 'SPACE',
    0x59: 'SQRT',
    0x5A: 'STR',
    0x5B: 'STUFF',
    0x5C: 'SUBSTR',
    0x5D: 'SYS',
    0x5E: 'TIME',
    0x5F: 'TRANSFORM',
    0x60: 'TRIM',
    0x62: 'TYPE',
    0x64: 'UPDATED',
    0x66: 'UPPER',
    0x67: 'VAL',
    0x68: 'VERSION',
    0x69: 'YEAR',
    0x6A: 'DMY',
    0x6B: 'MDY',
    0x6C: 'BAR',
    0x6D: 'KEY',
    0x6F: 'MEMORY',
    0x70: 'MENU',
    0x72: 'PAD',
    0x73: 'POPUP',
    0x74: 'PROGRAM',
    0x75: 'PV',
    0x76: 'SET',
    0x77: 'CEILING',
    0x7A: 'FLOOR',
    0x7B: 'FV',
    0x7C: 'LASTKEY',
    0x7D: 'LIKE',
    0x7E: 'LOOKUP',
    0x7F: 'CDX',
    0x80: 'MEMLINES',
    0x81: 'MLINE',
    0x82: 'ORDER',
    0x83: 'PAYMENT',
    0x84: 'PRINTSTATUS',
    0x85: 'PROMPT',
    0x86: 'RAND',
    0x87: 'VARREAD',
    0x89: 'RTOD',
    0x8A: 'SEEK',
    0x8B: 'SIGN',
    0x8C: 'TAG',
    0x8D: 'DTOR',
    0x8E: 'DTOS',
    0x8F: 'SCHEME',
    0x90: 'FOPEN',
    0x91: 'FCLOSE',
    0x92: 'FREAD',
    0x93: 'FWRITE',
    0x94: 'FERROR',
    0x95: 'FCREATE',
    0x96: 'FSEEK',
    0x97: 'FGETS',
    0x98: 'FFLUSH',
    0x99: 'FPUTS',
    0x9B: 'ALLTRIM',
    0x9C: 'ATLINE',
    0x9D: 'CHRTRAN',
    0x9E: 'FILTER',
    0x9F: 'RELATION',
    0xA0: 'TARGET',
    0xA1: 'EMPTY',
    0xA2: 'FEOF',
    0xA3: 'HEADER',
    0xA5: 'RAT',
    0xA6: 'RATC',
    0xA7: 'SECONDS',
    0xA8: 'STRTRAN',
    0xAA: 'USED',
    0xAB: 'BETWEEN',
    0xAC: 'CHRSAW',
    0xAD: 'INLIST',
    0xAE: 'ISDIGIT',
    0xAF: 'OCCURS',
    0xB0: 'PADC',
    0xB1: 'PADL',
    0xB2: 'PADR',
    0xB3: 'FSIZE',
    0xB4: 'SROWS',
    0xB5: 'SCOLS',
    0xB6: 'WCOLS',
    0xB7: 'WROWS',
    0xB8: 'ATC',
    0xB9: 'ATCLINE',
    0xBA: 'CURDIR',
    0xBC: 'PROPER',
    0xBB: 'FULLPATH',
    0xBD: 'WEXISTS',
    0xBE: 'WONTOP',
    0xBF: 'WOUTPUT',
    0xC0: 'WVISIBLE',
    0xC1: 'GETFILE',
    0xC2: 'PUTFILE',
    0xC3: 'GOMONTH',
    0xC4: 'PARAMETERS',
    0xC5: 'MCOL',
    0xC6: 'MDOWN',
    0xC7: 'MROW',
    0xC8: 'WLCOL',
    0xC9: 'WLROW',
    0xCB: 'FCHSIZE',
    0xCD: 'ALEN',
    0xCE: 'EVALUATE',
    0xD1: 'ISNULL',
    0xD2: 'NVL',
    0xE5: read_name, #user defined function alias
    0xEA: lambda fid: EXTENDED2[fid.read(1)[0]],
    0xF6: read_name, #user defined function
}

EXTENDED1 = {
    0x00: 'DISPLAYPATH',
    0x01: 'CURSORTOXML',
    0x02: 'XMLTOCURSOR',
    0x03: 'GETINTERFACE',
    0x04: 'BINDEVENT',
    0x05: 'RAISEEVENT',
    0x06: 'ADOCKSTATE',
    0x07: 'GETCURSORADAPTER',
    0x08: 'UNBINDEVENTS',
    0x09: 'AEVENTS',
    0x0A: 'ADDPROPERTY',
    0x0E: 'ICASE',
    0x0C: 'EVL',
    0x0F: 'CAST',
    0x10: 'ASQLHANDLES',
    0x11: 'SETRESULTSET',
    0x12: 'GETRESULTSET',
    0x13: 'CLEARRESULTSET',
    0x14: 'SQLIDLEDISCONNECT',
    0x15: 'ISMEMOFETCHED',
    0x16: 'GETAUTOINCVALUE',
    0x17: 'MAKETRANSACTABLE',
    0x18: 'ISTRANSACTABLE',
    0x19: 'ISPEN',
}

EXTENDED2 = {
    #This list contains all those functions that are available through the 0xEA (extended function) code:
    0x00: 'PRMPAD',
    0x01: 'PRMBAR',
    0x02: 'MRKPAD',
    0x03: 'MRKBAR',
    0x04: 'CNTPAD',
    0x05: 'CNTBAR',
    0x06: 'GETPAD',
    0x07: 'GETBAR',
    0x08: 'MWINDOW',
    0x09: 'OBJNUM',
    0x0A: 'WPARENT',
    0x0B: 'WCHILD',
    0x0C: 'RDLEVEL',
    0x0D: 'ACOPY',
    0x0E: 'AINS',
    0x0F: 'ADEL',
    0x10: 'ASORT',
    0x11: 'ASCAN',
    0x12: 'AELEMENT',
    0x13: 'ASUBSCRIPT',
    0x14: 'AFIELDS',
    0x15: 'ADIR',
    0x16: 'LOCFILE',
    0x17: 'WBORDER',
    0x18: 'ON',
    0x19: '', #Some sort of array indicator?
    0x1A: 'WLAST',
    0x1B: 'SKPBAR',
    0x1C: 'SKPPAD',
    0x1D: 'WMAXIMUM',
    0x1E: 'WMINIMUM',
    0x1F: 'WREAD',
    0x20: 'WTITLE',
    0x21: 'GETPEM',
    0x23: 'TXTWIDTH',
    0x24: 'FONTMETRIC',
    0x25: 'SYSMETRIC',
    0x26: 'WFONT',
    0x27: 'GETFONT',
    0x28: 'AFONT',
    0x29: 'DDEADVISE',
    0x2A: 'DDEENABLED',
    0x2B: 'DDEEXECUTE',
    0x2C: 'DDEINITIATE',
    0x2D: 'DDEPOKE',
    0x2E: 'DDEREQUEST',
    0x2F: 'DDESETSERVICE',
    0x30: 'DDESETTOPIC',
    0x31: 'DDETERMINATE',
    0x32: 'DDELASTERROR',
    0x33: 'GETDIR',
    0x34: 'DDEABORTTRANS',
    0x35: 'DDESETOPTION',
    0x36: 'OEMTOANSI',
    0x38: 'RGBSCHEME',
    0x39: 'CPCONVERT',
    0x3A: 'CPCURRENT',
    0x3B: 'CPDBF',
    0x3C: 'IDXCOLLATE',
    0x3E: 'CAPSLOCK',
    0x3F: 'NUMLOCK',
    0x40: 'INSMODE',
    0x41: 'SOUNDEX',
    0x42: 'DIFFERENCE',
    0x43: 'COS',
    0x44: 'SIN',
    0x45: 'TAN',
    0x46: 'ACOS',
    0x47: 'ASIN',
    0x48: 'ATAN',
    0x49: 'ATN2',
    0x4A: 'LOG',
    0x4B: 'LOG10',
    0x4C: 'EXP',
    0x4D: 'PI',
    0x4E: 'CREATEOBJECT',
    0x4F: 'BARPROMPT',
    0x51: 'HOME',
    0x53: 'FOR',
    0x54: 'UNIQUE',
    0x55: 'DESCENDING',
    0x56: 'TAGCOUNT',
    0x57: 'TAGNO',
    0x58: 'FDATE',
    0x59: 'FTIME',
    0x5A: 'ISBLANK',
    0x5B: 'ISMOUSE',
    0x5C: 'GETOBJECT',
    0x5D: 'OBJTOCLIENT',
    0x5E: 'RGB',
    0x5F: 'OLDVAL',
    0x60: 'ASELOBJ',
    0x61: 'ACLASS',
    0x62: 'AMEMBERS',
    0x63: 'COMPOBJ',
    0x64: 'SQLCANCEL',
    0x65: 'SQLCOLUMNS',
    0x66: 'SQLCONNECT',
    0x67: 'SQLDISCONNECT',
    0x68: 'PEMSTATUS',
    0x69: 'SQLEXEC',
    0x6A: 'SQLGETPROP',
    0x6B: 'SQLMORERESULTS',
    0x6C: 'SQLSETPROP',
    0x6D: 'SQLTABLES',
    0x6E: 'FLDLIST',
    0x6F: 'PRTINFO',
    0x70: 'KEYMATCH',
    0x71: 'OBJVAR',
    0x72: 'NORMALIZE',
    0x73: 'ISREADONLY',
    0x74: 'PCOUNT',
    0x78: 'MESSAGEBOX',
    0x79: 'AUSED',
    0x7A: 'AERROR',
    0x7B: 'SQLCOMMIT',
    0x7C: 'SQLROLLBACK',
    0x7D: 'MTON',
    0x7E: 'NTOM',
    0x7F: 'DTOT',
    0x80: 'TTOD',
    0x81: 'TTOC',
    0x82: 'CTOT',
    0x83: 'HOUR',
    0x84: 'MINUTE',
    0x85: 'SEC',
    0x86: 'DATETIME',
    0x87: 'REQUERY',
    0x88: 'CURSORSETPROP',
    0x89: 'CURSORGETPROP',
    0x8A: 'DBSETPROP',
    0x8B: 'DBGETPROP',
    0x8C: 'GETCOLOR',
    0x8D: 'PRIMARY',
    0x8E: 'CANDIDATE',
    0x8F: 'CURVAL',
    0x90: 'GETFLDSTATE',
    0x91: 'SETFLDSTATE',
    0x92: 'GETNEXTMODIFIED',
    0x93: 'TABLEUPDATE',
    0x94: 'TABLEREVERT',
    0x95: 'ADATABASES',
    0x96: 'DBC',
    0x98: 'ADBOBJECTS',
    0x99: 'APRINTERS',
    0x9A: 'GETPRINTER',
    0x9B: 'GETPICT',
    0x9C: 'WEEK',
    0x9D: 'REFRESH',
    0x9E: 'GETCP',
    0x9F: 'SQLSTRINGCONNECT',
    0xA0: 'CREATEBINARY',
    0xA1: 'DODEFAULT',
    0xA2: 'ISEXCLUSIVE',
    0xA3: 'TXNLEVEL',
    0xA4: 'DBUSED',
    0xA5: 'AINSTANCE',
    0xA6: 'INDBC',
    0xA7: 'BITLSHIFT',
    0xA8: 'BITRSHIFT',
    0xA9: 'BITAND',
    0xAA: 'BITOR',
    0xAB: 'BITNOT',
    0xAC: 'BITXOR',
    0xAD: 'BITSET',
    0xAE: 'BITTEST',
    0xAF: 'BITCLEAR',
    0xB0: 'AT_C',
    0xB1: 'ATCC',
    0xB2: 'RATLINE',
    0xB3: 'LEFTC',
    0xB4: 'RIGHTC',
    0xB5: 'SUBSTRC',
    0xB6: 'STUFFC',
    0xB7: 'LENC',
    0xB8: 'CHRTRANC',
    0xBA: 'LIKEC',
    0xBC: 'IMESTATUS',
    0xBD: 'ISLEADBYTE',
    0xBE: 'STRCONV',
    0xBF: 'BINTOC',
    0xC0: 'CTOBIN',
    0xC1: 'ISFLOCKED',
    0xC2: 'ISRLOCKED',
    0xC3: 'LOADPICTURE',
    0xC4: 'SAVEPICTURE',
    0xC5: 'SQLPREPARE',
    0xC6: 'DIRECTORY',
    0xC7: 'CREATEOFFLINE',
    0xC8: 'DROPOFFLINE',
    0xC9: 'AGETCLASS',
    0xCA: 'AVCXCLASSES',
    0xCB: 'STRTOFILE',
    0xCC: 'FILETOSTR',
    0xCD: 'ADDBS',
    0xCE: 'DEFAULTEXT',
    0xCF: 'DRIVETYPE',
    0xD0: 'FORCEEXT',
    0xD1: 'FORCEPATH',
    0xD2: 'JUSTDRIVE',
    0xD3: 'JUSTEXT',
    0xD4: 'JUSTFNAME',
    0xD5: 'JUSTPATH',
    0xD6: 'JUSTSTEM',
    0xD7: 'INDEXSEEK',
    0xD8: 'COMRETURNERROR',
    0xD9: 'VARTYPE',
    0xDA: 'ALINES',
    0xDB: 'NEWOBJECT',
    0xDC: 'AMOUSEOBJ',
    0xDD: 'COMCLASSINFO',
    0xE0: 'ANETRESOURCES',
    0xE1: 'AGETFILEVERSION',
    0xE2: 'CREATEOBJECTEX',
    0xE3: 'COMARRAY',
    0xE4: 'EXECSCRIPT',
    0xE5: 'XMLUPDATEGRAM',
    0xE6: 'COMPROP',
    0xE7: 'ATAGINFO',
    0xE8: 'ASTACKINFO',
    0xE9: 'EVENTHANDLER',
    0xEA: 'EDITSOURCE',
    0xEB: 'ADLLS',
    0xEC: 'QUARTER',
    0xED: 'GETWORDCOUNT',
    0xEE: 'GETWORDNUM',
    0xEF: 'ALANGUAGE',
    0xF0: 'STREXTRACT',
    0xF1: 'INPUTBOX',
    0xF2: 'APROCINFO',
    0xF3: 'WDOCKABLE',
    0xF4: 'ASESSIONS',
    0xF5: 'TEXTMERGE',
    0xFD: 'MIN',
}

CLAUSES.update(VALUES)

def read_short(fid):
    return struct.unpack('<h', fid.read(2))[0]

def read_ushort(fid):
    return struct.unpack('<H', fid.read(2))[0]

def read_int(fid):
    return struct.unpack('<i', fid.read(4))[0]

def read_uint(fid):
    return struct.unpack('<I', fid.read(4))[0]

def parse_subline(fid, length, final, names, line):
    while fid.tell() < final:
        clauseval = fid.read(1)[0]
        if clauseval in CLAUSES:
            clause = CLAUSES[clauseval]
        if clauseval in MULTICLAUSES:
            clause = ' or '.join(MULTICLAUSES[clauseval])
        if clauseval == 0xF6 or clauseval == 0xF7:
            clause = clause(fid, names)
            while line and type(line[-1]) is FXPAlias:
                clause = FXPName(repr(line.pop()) + repr(clause))
        elif callable(clause):
            clause = clause(fid, names)
        else:
            clause = FXPName(clause)
        line.append(clause)
    if len(line) > 1 and isinstance(line[-2], int):
        line.pop(-2)
    fid.seek(final - length)
    try:
        line = [' '.join(repr(l) for l in line)]
    except:
        pass
    line + [read_raw(fid, length)] + [fid.tell() - length]
    return line[0]

def parse_line(fid, length, names):
    final = fid.tell() + length
    line = []
    command = COMMANDS[fid.read(1)[0]]
    if callable(command):
        line += [FXPName(c) for c in command(fid, length-1)]
    else:
        line.append(FXPName(command))
    return parse_subline(fid, length, final, names, line)

def read_code_line_area(fid, names, final_fpos):
    d = []
    while fid.tell() < final_fpos:
        try:
            start_pos = fid.tell()
            length = read_ushort(fid)
            d.append(parse_line(fid, length-2, names))
        except:
            import traceback
            traceback.print_exc()
            fid.seek(start_pos)
            length = read_ushort(fid)
            line = read_raw(fid, length-2)
            print(line, file=sys.stderr)
            d.append(line)
    return ''.join(d)

def read_code_name_list(fid):
    num_entries = read_ushort(fid)
    return [read_string(fid) for i in range(num_entries)]

def change_named_value(expr, names):
    expr = expr.split()[1]
    if expr.endswith('.'):
        return names[int(expr[:-1])] + '.'
    else:
        return names[int(expr)]
    return expr

def concatenate_aliases(codes, names):
    codes = codes[:]
    new_codes = []
    while codes:
        code = codes.pop(0)
        if isinstance(code, str) and code.startswith('NAME '):
            code = change_named_value(code, names)
            while code.endswith('.'):
                code += change_named_value(codes.pop(0), names)
        if isinstance(code, str) and code.startswith('SPECIAL_NAME '):
            code = change_named_value(code, SPECIAL_NAMES)
            while code.endswith('.'):
                code += change_named_value(codes.pop(0), names)
        new_codes.append(code)
    return new_codes

def read_code_block(fid):
    tot_length = read_ushort(fid)
    if tot_length == 0:
        tot_length = read_uint(fid)
    start_pos = fid.tell()
    fid.seek(fid.tell() + tot_length)
    names = read_code_name_list(fid)

    fid.seek(start_pos)
    return read_code_line_area(fid, names, start_pos+tot_length)

def convert_date(date_bits):
    year = ((date_bits & 0xfe000000) >> 25) + 1980
    month = (date_bits & 0x1e00000) >> 21
    day = (date_bits & 0x1f0000) >> 16
    hour = (date_bits & 0xf800) >> 11
    minute = (date_bits & 0x7e0) >> 5
    second = (date_bits & 0x1f) << 1
    return datetime(year, month, day, hour, minute, second)

def read_procedure_header(fid):
    return OrderedDict((
        ('name', read_string(fid)),
        ('pos', read_uint(fid)),
        ('class_flag', read_short(fid)),
        ('class', read_short(fid)),
    ))

def read_class_header(fid):
    return {
        'name': read_string(fid),
        'parent': read_string(fid),
        'pos': read_uint(fid),
        'reserved': fid.read(2),
    }

def read_line_info(fid):
    return read_raw(fid, 2)

def read_source_info(fid):
    unknown1, unknown2, unknown3, line_num_start = struct.unpack('IIII', fid.read(16))
    return line_num_start, unknown1, unknown2, unknown3

def read_until_null(fid):
    string = fid.read(1)
    while string[-1] != 0:
        string += fid.read(1)
    if string:
        string = string[:-1]
    return string.decode('ISO-8859-1')

def read_fxp_file_block(fid, start_pos, name_pos):
    fid.seek(start_pos)
    fmt = '<hhiiiiiiIIB'
    num_procedures, num_classes, main_codepos, procedure_pos, class_pos, source_info_pos, num_code_lines, code_lines_pos, date, original_name_pos, codepage = struct.unpack(fmt, fid.read(struct.calcsize(fmt)))

    procedure_pos += start_pos
    class_pos += start_pos
    code_lines_pos += start_pos
    source_info_pos += start_pos

    date = convert_date(date)

    codepage = dbf.code_pages[255 - codepage]

    fid.seek(name_pos + original_name_pos)
    original_name = read_until_null(fid)

    for item in ('num_procedures', 'num_classes', 'main_codepos', 'procedure_pos', 'class_pos', 'source_info_pos', 'num_code_lines', 'code_lines_pos', 'date', 'original_name', 'codepage'):
        print('{} = {!r}'.format(item, eval(item)))

    fid.seek(procedure_pos)
    procedures = [OrderedDict((key, val) for key, val in zip(('name', 'pos', 'class_flag', 'class'), ('', main_codepos, 0, -1)))]
    procedures += [read_procedure_header(fid) for i in range(num_procedures)]
    
    fid.seek(class_pos, 0)
    classes = [read_class_header(fid) for i in range(num_classes)]

    fid.seek(code_lines_pos)
    line_info = [read_line_info(fid) for i in range(num_code_lines)]

    fid.seek(source_info_pos)
    source_info = [read_source_info(fid) for i in range(num_procedures + num_classes + 1)]

    for proc_or_cls in procedures + classes:
        fid.seek(proc_or_cls['pos'] + start_pos)
        proc_or_cls['code'] = read_code_block(fid)
        proc_or_cls.pop('pos')

    return procedures, classes

def fxp_read(fxp_file, output_dir=None):
    with open(fxp_file, 'rb') as fid:
        header_bytes = fid.read(HEADER_SIZE)

        if len(header_bytes) < HEADER_SIZE:
            raise Exception('File header too short')

        identifier, head, num_files, main_file, footer_pos, name_pos, name_len, reserved, checksum = struct.unpack('<3s2sHHIII18sH', header_bytes)

        if identifier == ENCRYPTED_IDENTIFIER:
            print(repr(header_bytes))
            raise Exception('Encrypted file')

        if identifier != IDENTIFIER:
            print('bad header')
            raise Exception('bad header: {!r}'.format(identifier))

        if checksum != checksum_calc(header_bytes[:-4]):
            raise Exception('bad checksum')

        for item in ('head', 'num_files', 'main_file', 'footer_pos', 'name_pos', 'name_len', 'reserved', 'checksum'):
            print('{} = {!r}'.format(item, eval(item)))
        print()

        if output_dir:
            try:
                os.makedirs(output_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        fid.seek(footer_pos)
        footer_entries = [struct.unpack('<BIIII8s', fid.read(FOOTER_ENTRY_SIZE)) for i in range(num_files)]

        output = OrderedDict()
        for i, (file_type, file_start, file_stop, dirname_start, filename_start, reserved) in enumerate(footer_entries):
            if i == main_file:
                print('MAIN')
            fid.seek(name_pos + dirname_start)
            dirname = read_until_null(fid)
            fid.seek(name_pos + filename_start)
            filename = read_until_null(fid)
            for item in ('file_type', 'file_start', 'file_stop', 'dirname_start', 'filename_start', 'reserved', 'dirname', 'filename'):
                print('{} = {!r}'.format(item, eval(item)))
            if file_type == 0:
                try:
                    output[filename] = read_fxp_file_block(fid, file_start, name_pos)
                except:
                    pass
                if output_dir:
                    with open(os.path.join(output_dir, filename), 'wb') as outfid:
                        fid.seek(file_start)
                        blocklen = file_stop - file_start
                        filename_blocklen = len(dirname) + len(filename) + 3
                        new_footer_pos = HEADER_SIZE + blocklen + filename_blocklen
                        new_name_pos = HEADER_SIZE + blocklen
                        header_data = bytearray(struct.pack('<5sHHIII', IDENTIFIER, 1, 0, new_footer_pos, new_name_pos, filename_blocklen))
                        header_data += b'\x00' * 16
                        outfid.write(header_data)
                        outfid.write(b'\x00' * 2)
                        outfid.write(struct.pack('<H', checksum_calc(header_data)))
                        file_start = outfid.tell()
                        outfid.write(fid.read(blocklen))
                        file_stop = outfid.tell()
                        outfid.write(b'\x00')
                        outfid.write((dirname + '\x00').encode('ISO-8859-1'))
                        outfid.write((filename + '\x00').encode('ISO-8859-1'))
                        outfid.write(struct.pack('<BIIII', file_type, file_start, file_stop, 1, 1 + len(dirname) + 1))
                        outfid.write(b'\x00' * 8)
            else:
                if output_dir:
                    with open(os.path.join(output_dir, filename), 'wb') as outfid:
                        fid.seek(file_start)
                        outfid.write(fid.read(file_stop - file_start))
            print()

        if output_dir:
            for filename in output:
                with open(os.path.join(output_dir, os.path.splitext(filename)[0]) + '.prg', 'wb') as outfid:
                    procedures, classes = output[filename]
                    for proc in procedures:
                        if not proc['class_flag']:
                            if proc['name']:
                                outfid.write('PROCEDURE {}\n'.format(proc['name']).encode('ISO-8859-1'))
                            outfid.write(proc['code'].encode('ISO-8859-1'))
                    for cls in classes:
                        outfid.write('DEFINE CLASS {} AS {}\n'.format(cls['name'], cls['parent']).encode('ISO-8859-1'))
                        for line in cls['code'].splitlines(True):
                            match = re.match(r'add (hidden |protected |)?method ([0-9]*)', line)
                            if match:
                                qualifier = match.groups()[0]
                                proc = procedures[int(match.groups()[1])]
                                outfid.write('{}PROCEDURE {}\n'.format(qualifier, proc['name']).encode('ISO-8859-1'))
                                outfid.write(proc['code'].encode('ISO-8859-1'))
                            else:
                                outfid.write(line)

        for filename in output:
            import pprint
            printer = pprint.PrettyPrinter(depth=10, indent=4)
            procedures, classes = output[filename]
            printer.pprint(filename)
            printer.pprint(procedures)
            printer.pprint(classes)

if __name__ == '__main__':
    fxp_read(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
