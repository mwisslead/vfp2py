from __future__ import print_function

import difflib

import vfp2py


def Test0():
    input_str = '''
LOCAL STRING_VAL, FLOAT_VAL, INT_VAL, BOOL_VAL, NULL_VAL, NULLDATE_VAL, DATE_VAL, DATETIME_VAL
STRING_VAL = \'str\'
float_val = 3.0
int_val = 3
BOOL_VAL = .F.
NULL_VAL = NULL
NULLDATE_VAL = { / / }
DATE_VAL = {^2017-5-6}
DATETIME_VAL = {^2017-5-6 5P}
?(float_val + INT_VAL + INT_VAL + - - FLOAT_VAL + int_VAL - FLOAT_val) / ++3 / --4 * -5 - INT_VAL * 3
?CHR(3)
?CHR(INT_VAL)
?SPACE(3)
?SPACE(INT_VAL)
?\'chr(65)\' + space(1) + chr(61) + \' \' + chr(65) + \', just letting you know.\' + chr(13) + chr(10)
?2 ** 3 ** 4
?2 ** (3 ** 4)
?(((2)))
RELEASE STRING_VAL, INT_VAL, BOOL_VAL, NULL_VAL
'''.strip()
    output_str = '''
string_val = float_val = int_val = bool_val = null_val = nulldate_val = date_val = datetime_val = False #LOCAL Declaration
string_val = \'str\'
float_val = 3.0
int_val = 3
bool_val = False
null_val = None
nulldate_val = None
date_val = dt.date(2017, 5, 6)
datetime_val = dt.datetime(2017, 5, 6, 17)
print((float_val + int_val + int_val + float_val + int_val - float_val) / 3 / 4 * -5 - int_val * 3)
print(\'\\x03\')
print(chr(int(int_val)))
print(\'   \')
print(int(int_val) * \' \')
print(\'chr(65) = A, just letting you know.\\r\\n\')
print((2 ** 3) ** 4)
print(2 ** 3 ** 4)
print(2)
del string_val, int_val, bool_val, null_val
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
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
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test2():
    input_str = '''
DEFINE CLASS TESTCLASS AS COMMANDBUTTON
   FUNCTION INIT(X)
   ENDFUNC
ENDDEFINE
'''.strip()
    output_str = '''
class Testclass(vfpfunc.Commandbutton):
    def init(self, x=False):
        pass
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='classDef', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test3():
    input_str = '''
DO A
DO A+B
DO A + B
DO ALLTRIM(A)
'''.strip()
    output_str = '''
a._program_main()
__import__(\'a+b\')._program_main() #NOTE: function call here may not work
__import__(a + b)._program_main() #NOTE: function call here may not work
__import__(a.strip())._program_main() #NOTE: function call here may not work
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test4():
    input_str = '''
LOCAL test
mkdir test - test
MD test+test
rmdir (test+test)
rd alltrim(test)
'''.strip()
    output_str = '''
test = False #LOCAL Declaration
os.mkdir(test - test)
os.mkdir(\'test+test\')
os.rmdir(test + test)
os.rmdir(test.strip())
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test5():
    input_str = '''
continue
LOCAL SEARCH_FOR
SEARCH_FOR = \'PAUL\'
SEEK ALLTRIM(SEARCH_FOR)
RELEASE SEARCH_FOR
'''.strip()
    output_str = '''
vfpfunc.db.continue_locate()
search_for = False #LOCAL Declaration
search_for = \'PAUL\'
vfpfunc.db.seek(None, search_for.strip())
del search_for
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise

