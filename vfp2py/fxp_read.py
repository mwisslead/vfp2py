import sys
import struct
from math import floor, log10
from datetime import datetime

HEADER_SIZE = 0x29

def round_sig(x, sig):
    if x == 0:
        return 0.
    return round(x, sig-int(floor(log10(abs(x))))-1)

def read_string(fid):
    return fid.read(read_ushort(fid))

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
    digits = fid.read(1)[0]
    return round_sig(struct.unpack('@d', fid.read(8)), digits)

def read_name(fid):
    return 'name {}'.format(read_ushort(fid))

def read_alias(fid):
    return 'alias {}'.format(read_ushort(fid))

def read_field(fid):
    return 'field {}'.format(read_ushort(fid))

COMMANDS = {
    #Commands are identified by a single byte as shown in the following list:
    0x01: lambda fid, length: fid.read(length),
    0x02: '?',
    0x03: '??',
    0x0C: 'CASE',
    0x0F: 'CLOSE',
    0x18: 'DO',
    0x1B: 'ELSE',
    0x1C: 'ENDCASE',
    0x1D: 'ENDDO',
    0x1E: 'ENDIF',
    0x23: 'GO',
    0x25: 'IF',
    0x2D: 'LOCATE',
    0x32: 'OTHERWISE',
    0x34: 'PARAMETERS',
    0x35: 'PRIVATE',
    0x37: 'PUBLIC',
    0x38: 'QUIT',
    0x3c: 'RELEASE',
    0x42: 'RETURN',
    0x45: 'SEEK',
    0x46: 'SELECT',
    0x47: 'SET',
    0x48: 'SKIP',
    0x4A: 'STORE',
    0x51: 'USE',
    0x54: 'variable assignment',
    0x55: 'ENDPROC',
    0x84: 'FOR',
    0x85: 'ENDFOR',
    0x86: 'expression',
    0x99: 'function call',
    0xA2: 'add method',
    0xA3: 'add protected method',
    0xA6: 'WITH',
    0xA7: 'ENDWITH',
    0xAC: 'NODEFAULT',
    0xAE: 'LOCAL',
    0xAF: 'LPARAMETERS',
    0xB0: 'CD'
}

CODES = {
    #Functions are also identified by a single byte code. To deal with more than 255 functions, Microsoft added an escape code (0xEA) that provides another 255 function. This is enough to handle all functions available in FoxPro. Function codes are only used in expressions. The following list contains all regular functions
    0x30: 'FILE', 
    0x3E: 'LEN',
    0x5A: 'STR',
    0x62: 'TYPE',
    0x9B: 'ALLTRIM',
    0xAA: 'USED',
    0xB2: 'PADR',
    0xEA: lambda fid: read_func(fid, EXTENDED),

    #Clauses share the same value range as expressions and functions:
    0x14: 'FORM',
    0x16: 'IN',
    0x28: 'TO',
    0x2B: 'WHILE',
    0x51: 'AS',
    0xD1: 'WITH',
    #Expressions are stored in inverse polish notation. A calculation like lnSum + 5 is stored as:
    #Expressions must be treated as a stream. The first byte identifies an expression element. However, depending on the type, multiple bytes follow. The following list contains expression elements. Expression codes share the same range of values as functions because both can be mxed:
    0x06: '+',
    0x07: ',',
    0x0A: 'Not',
    0x0B: 'OR',
    0x0D: '<',
    0x0E: '<=',
    0x0F: '!=',
    0x10: '=',
    0x11: '>=',
    0x12: '>',
    0x14: '==',
    0x43: 'Parameter Mark',
    0x61: '.T.',
    0xD9: read_string,
    0xE9: read_int32,
    0xF4: read_alias,
    0xF6: read_field,
    0xF7: read_name,
    0xF8: read_int8,
    0xF9: read_int16,
    0xFA: read_double,
    0xFB: read_string,
    0xFC: 'Start Name',
    0xFD: 'End Name',
    0xFE: 'End of Expr'
}

EXTENDED = {
    #This list contains all those functions that are available through the 0xEA (extended function) code:
    0x4E: 'CREATEOBJECT',
    0x5A: 'ISBLANK',
    0x78: 'MESSAGEBOX',
    0xF0: 'STREXTRACT'
}
def read_short(fid):
    return struct.unpack('<h', fid.read(2))[0]

def read_ushort(fid):
    return struct.unpack('<H', fid.read(2))[0]

def read_uint(fid):
    return struct.unpack('<i', fid.read(4))[0]

def read_uint(fid):
    return struct.unpack('<I', fid.read(4))[0]

def read_func(fid, codes=CODES):
    code = fid.read(1)[0]
    try:
        code = codes[code]
        if callable(code):
            return code(fid)
    except:
        pass
    return code

def parse_line(fid, length):
    final = fid.tell() + length
    line = []
    command = fid.read(1)[0]
    try:
        command = COMMANDS[command]
    except:
        command = hex(command)
    if callable(command):
        line.append('RAW CODE')
        line.append(command(fid, length-1))
    else:
        line.append(command)
    while fid.tell() < final:
        line.append(read_func(fid))
    fid.seek(final)
    import pdb
    pdb.set_trace()
    return line

def read_code_line_area(fid):
    tot_length = read_ushort(fid)
    d = []
    while tot_length > 0:
        length = read_ushort(fid)
        d.append(parse_line(fid, length-2))
        tot_length -= length
    return d

def read_code_name_list(fid):
    num_entries = read_ushort(fid)
    return [read_string(fid) for i in range(num_entries)]

def read_code_block(fid):
    d = []
    d.append(read_code_line_area(fid))
    d.append(read_code_name_list(fid))
    return d

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
    return {'name': name, 'pos': code_pos, 'class': class_num}

def read_class_header(fid):
    name = read_string(fid)
    parent_name = read_string(fid)
    code_pos = read_uint(fid) + HEADER_SIZE
    unknown1 = read_short(fid)
    return {'name': name, 'parent': parent_name, 'procedures': []}

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

        num_procedures, num_classes, unknown2, procedure_pos, class_pos, unknown_pos, num_code_lines, code_lines_pos = struct.unpack('<hh4siiiii', fid.read(0x1c))

        procedure_pos += HEADER_SIZE
        class_pos += HEADER_SIZE
    
        print(num_procedures)
        print(num_classes)
        print(unknown2)
        print(procedure_pos)
        print(class_pos)
        print(unknown_pos)
        print(num_code_lines)
        print(code_lines_pos)

        date = get_date(fid)
        print(date)

        fid.seek(procedure_pos, 0)
        procedures = [{'name': '', 'pos': 0x4e, 'class': -1}] + [read_procedure_header(fid) for i in range(num_procedures)]
        
        for proc in procedures:
            fid.seek(proc['pos'], 0)
            proc['code'] = read_code_block(fid)
            proc.pop('pos')

        print(procedures[1])
        exit()

        fid.seek(class_pos, 0)
        classes = [read_class_header(fid) for i in range(num_classes)]

        for i, cls in enumerate(classes):
            for proc in procedures:
                if proc['class'] == i:
                    proc.pop('class')
                    cls['procedures'].append(proc)
            for proc in cls['procedures']:
                procedures.pop(procedures.index(proc))

        for proc in procedures:
            proc.pop('class')

        print(procedures)
        print(classes)

if __name__ == '__main__':
    main()
