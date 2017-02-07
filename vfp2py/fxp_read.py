import sys
import struct
from math import floor, log10
from datetime import datetime
from collections import OrderedDict

HEADER_SIZE = 0x29

def round_sig(x, sig):
    if x == 0:
        return 0.
    return round(x, sig-int(floor(log10(abs(x))))-1)

def read_string(fid):
    return fid.read(read_ushort(fid)).decode('utf-8')

def read_int8(fid):
    digits = fid.read(1)[0]
    return round_sig(fid.read(1)[0], digits)

def read_int16(fid):
    digits = fid.read(1)[0]
    return round_sig(read_short(fid), digits)

def read_int32(fid):
    digits = fid.read(1)[0]
    return round_sig(read_int(fid), digits)

def read_double(fid):
    digits = fid.read(1)[0] - 1
    digits += fid.read(1)[0]
    return round_sig(struct.unpack('<d', fid.read(8))[0], digits)

def read_alias(fid):
    return 'NAME {}.'.format(read_ushort(fid))

def read_special_alias(fid):
    return 'SPECIAL_NAME {}.'.format(fid.read(1)[0])

def read_name(fid):
    return 'NAME {}'.format(read_ushort(fid))

def read_field(fid):
    return 'NAME {}'.format(read_ushort(fid))

def read_raw(fid, length):
    return ' '.join('{:02x}'.format(d) for d in fid.read(length))

def read_expr(fid):
    codeval = fid.read(1)[0]
    expr = []
    while codeval != 0xFD:
        try:
            code = FUNCTIONS[codeval]
            if callable(code):
                code = code(fid)
        except:
            code = 'FUNCTION {:02x}'.format(codeval)
        expr.append(code)
        codeval = fid.read(1)[0]
    return expr

def read_setcode(fid, length):
    try:
        return [SETCODES[fid.read(1)[0]]]
    except:
        fid.seek(fid.tell() - 1)
        return ['{:02x}'.format(fid.read(1)[0])]

class Token(object):
    def __init__(self, tokenstr, tokenval):
        self.str = tokenstr
        self.val = tokenval

    def __repr__(self):
        return repr('{}({})'.format(self.str, self.val))

SPECIAL_NAMES = {
    0x39: '_SCREEN',
    0x43: '_VFP',
}

COMMANDS = {
    #Commands are identified by a single byte as shown in the following list:
    0x01: lambda fid, length: ['RAW CODE', read_raw(fid, length)],
    0x02: '?',
    0x03: '??',
    0x0C: 'CASE',
    0x0E: 'CLEAR',
    0x0F: 'CLOSE',
    0x14: 'DELETE',
    0x18: 'DO',
    #0x18: lambda fid, length: ['DO', CLAUSES[fid.read(1)[0]]],
    0x1B: 'ELSE',
    0x1C: 'ENDCASE',
    0x1D: 'ENDDO',
    0x1E: 'ENDIF',
    0x20: 'ERASE',
    0x23: 'GO',
    0x25: 'IF',
    0x2D: 'LOCATE',
    0x31: 'ON',
    0x32: 'OTHERWISE',
    0x34: 'PARAMETERS',
    0x35: 'PRIVATE',
    0x37: 'PUBLIC',
    0x38: 'QUIT',
    0x3C: 'RELEASE',
    0x3E: 'REPLACE',
    0x42: 'RETURN',
    0x45: 'SEEK',
    0x46: 'SELECT',
    0x47: read_setcode,
    0x48: 'SKIP',
    0x4A: 'STORE',
    0x51: 'USE',
    0x54: 'variable assignment',
    0x55: 'ENDPROC',
    0x7C: 'DECLARE',
    0x7E: 'SCAN',
    0x7F: 'SCAN',
    0x83: 'COMPILE',
    0x84: 'FOR',
    0x85: 'ENDFOR',
    0x86: 'expression',
    0x8A: 'PUSH',
    0x8B: 'POP',
    0x99: 'function call',
    0xA2: 'add method',
    0xA3: 'add protected method',
    0xA6: 'WITH',
    0xA7: 'ENDWITH',
    0xA8: 'ERROR',
    0xAC: 'NODEFAULT',
    0xAE: 'LOCAL',
    0xAF: 'LPARAMETERS',
    0xB0: 'CD',
    0xB5: 'FOR EACH',
    0xB6: 'ENDFOREACH',
}

SETCODES = {
    0x62: 'SET LIBRARY',
    0x28: 'SET ORDER',
    0x2B: 'SET PROCEDURE'
}

TYPECODES = {
    0x57: 'SHORT',
    0xD1: 'INTEGER',
    0xD6: 'STRING'
}

CLAUSES = {
    0x01: 'ADDITIVE',
    0x02: 'ALIAS',
    0x03: 'ALL',
    0x07: ',',
    0x0C: 'CLEAR',
    0x10: '=',
    0x12: 'FILE',
    0x13: 'FOR',
    0x14: 'FORM',
    0x16: 'IN',
    0x17: 'KEY',
    0x28: 'TO',
    0x29: 'TOP',
    0x2B: 'WHILE',
    0x31: 'TABLE',
    0x32: 'LABEL',
    0x36: 'BOTTOM',
    0x48: 'CASE',
    0x4B: 'PROGRAM',
    0x51: 'AS',
    0x52: 'CLASSLIB',
    0x56: 'DLLS',
    0xBE: 'PROCEDURE',
    0xC2: 'SHARED',
    0xD1: 'WITH',
    0xD5: 'EVENTS',
    0xFC: read_expr,
    0xFD: 'END EXPR',
    0xFE: 'END COMMAND'
}

VALUES = {
    0xD9: read_string,
    0xE1: read_special_alias,
    0xE2: '.',
    0xE9: read_int32,
    0xF0: lambda fid: ' '.join('{:02x}'.format(d) for d in (b'\xf1' + fid.read(2))),
    0xF1: lambda fid: ' '.join('{:02x}'.format(d) for d in (b'\xf1' + fid.read(2))),
    0xFF: lambda fid: ' '.join('{:02x}'.format(d) for d in (b'\xf1' + fid.read(2))),
    0xF4: read_alias,
    0xF6: read_field,
    0xF7: read_name,
    0xF8: read_int8,
    0xF9: read_int16,
    0xFA: read_double,
    0xFB: read_string,
}

FUNCTIONS = {
    0x00: 'NOP',
    0x03: 'END PAREN',
    0x04: '*',
    0x06: '+',
    0x07: ',',
    0x08: '-',
    0x09: 'AND',
    0x0A: 'NOT',
    0x0B: 'OR',
    0x0C: '/',
    0x0D: '<',
    0x0E: '<=',
    0x0F: '!=',
    0x10: '=',
    0x11: '>=',
    0x12: '>',
    0x14: '==',
    0x18: '@',
    0x1A: lambda fid: EXTENDED1[fid.read(1)[0]],
    0x1C: 'ASC',
    0x1E: 'BOF',
    0x1F: 'CDOW',
    0x20: 'CHR',
    0x23: 'CTOD',
    0x24: 'DATE',
    0x25: 'DAY',
    0x2A: 'DTOC',
    0x2B: 'EOF',
    0x2D: '.F.',
    0x30: 'FILE', 
    0x34: 'FOUND',
    0x37: 'INKEY',
    0x3D: 'LEFT',
    0x3E: 'LEN',
    0x43: 'MARK PARAMETERS',
    0x46: 'MIN',
    0x48: 'MONTH',
    0x4E: 'RECCOUNT',
    0x4F: 'RECNO',
    0x51: 'REPLICATE',
    0x52: 'RIGHT',
    0x54: 'ROUND',
    0x57: 'SELECT',
    0x58: 'SPACE',
    0x5A: 'STR',
    0x5C: 'SUBSTR',
    0x5D: 'SYS',
    0x5E: 'TIME',
    0x61: '.T.',
    0x62: 'TYPE',
    0x66: 'UPPER',
    0x67: 'VAL',
    0x69: 'YEAR',
    0x77: 'CEILING',
    0x91: 'FCLOSE',
    0x95: 'FCREATE',
    0x9B: 'ALLTRIM',
    0xAA: 'USED',
    0xAB: 'BETWEEN',
    0xB2: 'PADR',
    0xBA: 'CURDIR',
    0xC4: 'PARAMETERS',
    0xCE: 'EVALUATE',
    0xE4: '.NULL.',
    0xEA: lambda fid: EXTENDED2[fid.read(1)[0]],
}

EXTENDED1 = {
    0x04: 'BINDEVENT',
    0x0F: 'CAST',
}

EXTENDED2 = {
    #This list contains all those functions that are available through the 0xEA (extended function) code:
    0x2C: 'DDEINITIATE',
    0x2F: 'DDESETSERVICE',
    0x30: 'DDESETTOPIC',
    0x31: 'DDETERMINATE',
    0x35: 'DDESETOPTION',
    0x3E: 'CAPSLOCK',
    0x4E: 'CREATEOBJECT',
    0x5A: 'ISBLANK',
    0x5E: 'RGB',
    0x68: 'PEMSTATUS',
    0x74: 'PCOUNT',
    0x78: 'MESSAGEBOX',
    0x83: 'HOUR',
    0x84: 'MINUTE',
    0x85: 'SEC',
    0x86: 'DATETIME',
    0xA1: 'DODEFAULT',
    0xA7: 'BITLSHIFT',
    0xA8: 'BITRSHIFT',
    0xAA: 'BITOR',
    0xAB: 'BITNOT',
    0xAC: 'BITXOR',
    0xAD: 'BITSET',
    0xAE: 'BITTEST',
    0xAF: 'BITCLEAR',
    0xBF: 'BINTOC',
    0xCC: 'FILETOSTR',
    0xC6: 'DIRECTORY',
    0xD9: 'VARTYPE',
    0xF0: 'STREXTRACT'
}

CLAUSES.update(VALUES)
FUNCTIONS.update(VALUES)

def read_short(fid):
    return struct.unpack('<h', fid.read(2))[0]

def read_ushort(fid):
    return struct.unpack('<H', fid.read(2))[0]

def read_int(fid):
    return struct.unpack('<i', fid.read(4))[0]

def read_uint(fid):
    return struct.unpack('<I', fid.read(4))[0]

def parse_line(fid, length):
    final = fid.tell() + length
    line = []
    command = fid.read(1)[0]
    try:
        command = COMMANDS[command]
    except:
        command = hex(command)
    if callable(command):
        line += command(fid, length-1)
    else:
        line.append(command)
    while fid.tell() < final:
        clause = fid.read(1)[0]
        try:
            clause = CLAUSES[clause]
        except:
            clause = hex(clause)
        if callable(clause):
            clause = clause(fid)
        line.append(clause)
    fid.seek(final - length)
    return line + [read_raw(fid, length)] + [fid.tell() - length]

def read_code_line_area(fid):
    tot_length = read_ushort(fid)
    d = []
    while tot_length > 0:
        length = read_ushort(fid)
        try:
            file_pos = fid.tell()
            d.append(parse_line(fid, length-2))
        except Exception as err:
            import traceback
            traceback.print_exc()
            fid.seek(file_pos)
            #import pdb
            #pdb.set_trace()
            #d.append(parse_line(fid, length-2))
            d.append(read_raw(fid, length-2))
        tot_length -= length
    return d

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
    lines = read_code_line_area(fid)
    names = read_code_name_list(fid)
    for line_num, line in enumerate(lines):
        for i, code in enumerate(line):
            if isinstance(code, list):
                line[i] = concatenate_aliases(code, names)
        lines[line_num] = concatenate_aliases(line, names)
    return lines

def get_date(fid):
    date_bits = read_uint(fid)
    year = ((date_bits & 0xfe000000) >> 25) + 1980
    month = (date_bits & 0x1e00000) >> 21
    day = (date_bits & 0x1f0000) >> 16
    hour = (date_bits & 0xf800) >> 11
    minute = (date_bits & 0x7e0) >> 5
    second = (date_bits & 0x1f) << 1
    return datetime(year, month, day, hour, minute, second)

def read_procedure_header(fid):
    name = read_string(fid)
    code_pos = read_uint(fid) + HEADER_SIZE
    unknown = read_short(fid)
    class_num = read_short(fid)
    return OrderedDict((key, val) for key, val in zip(('name', 'pos', 'class'), (name, code_pos, class_num)))

def read_class_header(fid):
    name = read_string(fid)
    parent_name = read_string(fid)
    code_pos = read_uint(fid) + HEADER_SIZE
    unknown1 = read_short(fid)
    return {'name': name, 'parent': parent_name, 'procedures': []}

def read_line_info(fid):
    return ' '.join('{:02x}'.format(d) for d in fid.read(2))

def read_source_info(fid):
    unknown1, unknown2, unknown3, line_num_start = struct.unpack('IIII', fid.read(16))
    return line_num_start, unknown1, unknown2, unknown3

def read_until_newline(fid):
    string = fid.read(1)
    while string[-1] != 0:
        string += fid.read(1)
    return string

def fxp_read():
    with open(sys.argv[1], 'rb') as fid:
        identifier, head, footer_pos, name_pos, unknown1, unknown2, unknown3 = struct.unpack('<3s6sllB21sH', fid.read(HEADER_SIZE))

        print(identifier)

        if identifier != b'\xfe\xf2\xff':
            print('bad header')
            return

        print(footer_pos)
        print(name_pos)
        print(bin(unknown1))
        print(unknown2)
        print(bin(unknown3))

        num_procedures, num_classes, unknown2, procedure_pos, class_pos, source_info_pos, num_code_lines, code_lines_pos = struct.unpack('<hh4siiiii', fid.read(0x1c))

        procedure_pos += HEADER_SIZE
        class_pos += HEADER_SIZE
        code_lines_pos += HEADER_SIZE
        source_info_pos += HEADER_SIZE
    
        print(num_procedures)
        print(num_classes)
        print(unknown2)
        print(procedure_pos)
        print(class_pos)
        print(source_info_pos)
        print(num_code_lines)
        print(code_lines_pos)

        date = get_date(fid)
        print(date)

        fid.seek(procedure_pos)
        procedures = [OrderedDict((key, val) for key, val in zip(('name', 'pos', 'class'), ('', 0x4e, -1)))] + [read_procedure_header(fid) for i in range(num_procedures)]
        
        fid.seek(class_pos, 0)
        classes = [read_class_header(fid) for i in range(num_classes)]

        fid.seek(code_lines_pos)
        line_info = [read_line_info(fid) for i in range(num_code_lines)]

        fid.seek(name_pos)
        file_names = [read_until_newline(fid) for i in range(3)]

        fid.seek(footer_pos)
        unknown1, name_pos2, unknown2, first_name_len, unknown3, unknown4 = struct.unpack('<5sIIIII', fid.read(25))
        print(unknown1, name_pos2, unknown2, first_name_len, unknown3, unknown4)

        fid.seek(source_info_pos)
        source_info = [read_source_info(fid) for i in range(num_procedures + num_classes + 1)]

        for proc in procedures:
            fid.seek(proc['pos'])
            proc['code'] = read_code_block(fid)
            proc.pop('pos')

    if len(sys.argv) > 2:
        with open(sys.argv[2], 'rb') as fid:
            for item in source_info:
                fid.seek(item[2])
                print(item[1])
                print(fid.read(item[3] - item[2]).decode('utf-8'))

    for i, cls in enumerate(classes):
        for proc in procedures:
            if proc['class'] == i:
                proc.pop('class')
                cls['procedures'].append(proc)
        for proc in cls['procedures']:
            procedures.pop(procedures.index(proc))

    for proc in procedures:
        proc.pop('class')

    import pprint
    printer = pprint.PrettyPrinter(depth=10, indent=4)
    printer.pprint(line_info)
    printer.pprint(procedures)
    printer.pprint(classes)

if __name__ == '__main__':
    fxp_read()
