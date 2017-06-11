from __future__ import print_function

import difflib

import vfp2py


def Test0():
    input_str = '''
LOCAL STRING_VAL, INT_VAL, BOOL_VAL, NULL_VAL
STRING_VAL = \'str\'
int_val = 3
BOOL_VAL = .F.
NULL_VAL = NULL
?CHR(3)
?CHR(INT_VAL)
?SPACE(3)
?SPACE(INT_VAL)
RELEASE STRING_VAL, INT_VAL, BOOL_VAL, NULL_VAL
'''.strip()
    output_str = '''
string_val = int_val = bool_val = null_val = False #LOCAL Declaration
string_val = \'str\'
int_val = 3
bool_val = False
null_val = None
print(\'\\x03\')
print(chr(int(int_val)))
print(\'   \')
print(int(int_val) * \' \')
del string_val, int_val, bool_val, null_val
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff(test_output_str.splitlines(1), output_str.splitlines(1))
        print(''.join(diff))
        raise


def Test1():
    input_str = '''
   *comment with spaces
#DEFINE cantbewrong
#DEFINE SPACE CHR
#IFDEF cantbewrong
#IF FILE ( \'test.h\' )
   ***comment***
   # include  test.h
   # include  \'test.h\'
   # include  \'test\' + \'.h\'
   STORE 5 to  x && set x to 5
#ELSE
#ENDIF
   x = \'test\' + CHR(13) + CHR(10)
   x = space(5)
   x = \'\' + CHR(13) + CHR(10)
#ELSE
_SCREEN.LOGO.TOP = (_SCREEN.HEIGHT-_SCREEN.LOGO.HEIGHT)/2-3

WAIT WINDOW space(3) + \'please wait\' + CHR(32) NOWAIT TIMEOUT 1.3
#ENDIF
'''.strip()
    output_str = '''
from __future__ import division, print_function

from vfp2py import vfpfunc
def _program_main():
    vfpfunc.variable.pushscope()
    #comment with spaces
    ###comment###
    vfpfunc.variable[\'x\'] = \'\\n\'
    vfpfunc.variable[\'x\'] = \'\\n\'
    vfpfunc.variable[\'x\'] = \'\\n\'
    # set x to 5
    vfpfunc.variable[\'x\'] = 5
    vfpfunc.variable[\'x\'] = \'test\\r\\n\'
    vfpfunc.variable[\'x\'] = \'\\x05\'
    vfpfunc.variable[\'x\'] = \'\\r\\n\'
    vfpfunc.variable.popscope()
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str).strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff(test_output_str.splitlines(1), output_str.splitlines(1))
        print(''.join(diff))
        raise

