from __future__ import print_function

import difflib

import vfp2py


def Test0():
    input_str = '''
*comment;
  continued on another line;
  and another
LOCAL STRING_VAL, FLOAT_VAL, MONEY_VAL, INT_VAL, BLOB_VAL, BOOL_VAL, NULL_VAL, NULLDATE_VAL, DATE_VAL, DATETIME_VAL, OBJ_VAL
LOCAL Y, Z, W
STRING_VAL = \'str\'
ü1 = "Hellü"
float_val = 3.0
float_val = .5e-5
float_val = 8e+18
float_val = 1.3e12
float_val = .1e
money_val = $3.512345
int_val = 3
int_val = 0x3
int_val = 0X3F
int_val = 0x
blob_val = 0h123456789abcde
blob_val = 0h0123456789abcde
blob_val = 0h
BOOL_VAL = .F.
NULL_VAL = NULL
NULLDATE_VAL = { / / }
NULLDATE_VAL = {:}
DATE_VAL = {^2017-5-6}
DATETIME_VAL = {^2017-5-6 5P}
?(float_val + INT_VAL + INT_VAL + - - FLOAT_VAL + int_VAL - FLOAT_val) / ++3 / --4 * -5 - INT_VAL * 3
?CHR(3)
?CHR(INT_VAL)
?SPACE(3)
?space(20)
?SPACE(INT_VAL)
?DAY(DATE_VAL)
?DOW(DATE_VAL)
?\'chr(65)\' + space(1) + chr(61) + \' \' + chr(65) + \', just letting you know.\' + chr(13) + chr(10)
?TRIM(\'test   \')
?2 ** 3 ** 4
?2 ** (3 ** 4)
?(((2)))
?10 >= 5
?10 => 5
?10 <= 5
?10 =< 5
?.t. or .f. AND .f. or .f.
?x .or. y AND w .or. z
?CAST(string_val as blob)
?cast(float_val as currency)
?substr(string_val, int_val, 13)
?subs(string_val, 1, 13)
?at(\'.\', string_val)
?repli(string_val, FLOAT_VAL)
OBJ_VAL = CREATEOBJECT(\'TEST\')
OBJ_VAL = CREATE(\'FORM\')
RELEASE STRING_VAL, INT_VAL, BOOL_VAL, NULL_VAL
LOCAL ARRAY ITEMS[3, 5]
LOCAL ITEM
FOR EACH ITEM IN ITEMS
    IF NOT ITEM
       LOOP
*!*    IF
*!*       TEST()
*!*    ENDIF
    ENDIF
    EXIT
ENDFOR
RELEASE ITEMS, item
FOR X = 4 TO 7
ENDFOR
FOR X = 1 TO 7 STEP 2
ENDFOR
DO CASE
   *line comment1
   * line comment2
   CASE X == 1
   CASE X == 2
   CASE (X == 2)
   OTHERWISE
      ?Test
ENDCASE
TEXT TO SOMESTRING NOSHOW
       1234567890
       0123456789
       ABCDEFGHIJ
       KLMNOPQRST
       UVWXYZ
ENDTEXT
QUIT
CANCEL
RESUME
COMPILE test.prg
READ
READ EVENTS
DOEVENTS
DOEVENTS FORCE
UNLOCK ALL
LIST NEXT 5
RESTORE FROM test ADDITIVE
SHOW GETS
HIDE WINDOW test
SORT TO sortedTable ON (sortField)
COPY TO ARRAY FOR X = 3
SAVE TO test ALL LIKE something
ZOOM WINDOW SCREEN MAX
SOMEFUNC(,A,)
MODIFY WINDOW SCREEN FONT "FONT", 12 STYLE "B" TITLE "TITLE" NOFLOAT NOCLOSE NOZOOM
MODIFY COMMAND c:\\test.prg
DEFINE MENU test BAR AT LINE 2 IN SCREEN
DEFINE PAD test OF thing PROMPT "text" MESSAGE "menu" KEY ALT+F, "ALT+F" COLOR SCHEME 3
DEFINE POPUP test
DEFINE BAR 1 OF test PROMPT \'text\'
ON PAD test OF thing ACTIVATE POPUP test
ON BAR 1 of test ACTIVATE POPUP test
ACTIVATE WINDOW window
ACTIVATE SCREEN
ACTIVATE MENU test NOWAIT
ACTIVATE POPUP test
'''.strip()
    output_str = '''
# comment
# continued on another line
# and another
M.add_local(\'string_val\', \'float_val\', \'money_val\', \'int_val\', \'blob_val\', \'bool_val\', \'null_val\', \'nulldate_val\', \'date_val\', \'datetime_val\', \'obj_val\')
M.add_local(\'y\', \'z\', \'w\')
S.string_val = \'str\'
S.ü1 = \'Hellü\'
S.float_val = 3.0
S.float_val = .5e-5
S.float_val = 8e+18
S.float_val = 1.3e12
S.float_val = .1e0
S.money_val = 3.5123
S.int_val = 3
S.int_val = 0x3
S.int_val = 0x3f
S.int_val = 0x0
S.blob_val = bytearray(b\'\\x124Vx\\x9a\\xbc\\xde\')
S.blob_val = bytearray(b\'\\x00\\x124Vx\\x9a\\xbc\\xde\')
S.blob_val = bytearray(b\'\')
S.bool_val = False
S.null_val = None
S.nulldate_val = None
S.nulldate_val = None
S.date_val = dt.date(2017, 5, 6)
S.datetime_val = dt.datetime(2017, 5, 6, 17)
print((S.float_val + S.int_val + S.int_val + S.float_val + S.int_val - S.float_val) / 3 / 4 * -5 - S.int_val * 3)
print(\'\\x03\')
print(chr(int(S.int_val)))
print(\'   \')
print(20 * \' \')
print(int(S.int_val) * \' \')
print(S.date_val.day)
print(vfpfunc.dow_fix(S.date_val.weekday()))
print(\'chr(65) = A, just letting you know.\\r\\n\')
print(\'test   \'.rstrip())
print((2 ** 3) ** 4)
print(2 ** 3 ** 4)
print(2)
print(10 >= 5)
print(10 >= 5)
print(10 <= 5)
print(10 <= 5)
print(True or False and False or False)
print(S.x or S.y and S.w or S.z)
print(bytearray(S.string_val))
print(float(S.float_val))
print(S.string_val[int(S.int_val) - 1:13 + int(S.int_val) - 1])
print(S.string_val[:13])
print(S.string_val.find(\'.\') + 1)
print(S.string_val * int(S.float_val))
S.obj_val = vfpfunc.create_object(\'Test\')
S.obj_val = vfpfunc.Form()
del M.string_val, M.int_val, M.bool_val, M.null_val
M.add_local(items=Array(3, 5))
M.add_local(\'item\')
for S.item in S.items:
    if not S.item:
        continue
        # IF
        # TEST()
        # ENDIF
    break
del M.items, M.item
for S.x in range(4, 8):
    pass
for S.x in range(1, 8, 2):
    pass
    # line comment1
    # line comment2
if S.x == 1:
    pass
elif S.x == 2:
    pass
elif S.x == 2:
    pass
else:
    print(S.test)
S.somestring = vfpfunc.text([\'       1234567890\',
                             \'       0123456789\',
                             \'       ABCDEFGHIJ\',
                             \'       KLMNOPQRST\',
                             \'       UVWXYZ\'], show=False)
vfpfunc.quit()
# FIX ME: CANCEL
# FIX ME: RESUME
# FIX ME: COMPILE test.prg
# FIX ME: READ
vfpfunc.read_events()
# FIX ME: DOEVENTS
# FIX ME: DOEVENTS FORCE
# FIX ME: UNLOCK ALL
# FIX ME: LIST NEXT 5
# FIX ME: RESTORE FROM test ADDITIVE
# FIX ME: SHOW GETS
# FIX ME: HIDE WINDOW test
# FIX ME: SORT TO sortedTable ON (sortField)
# FIX ME: COPY TO ARRAY FOR X = 3
# FIX ME: SAVE TO test ALL LIKE something
# FIX ME: ZOOM WINDOW SCREEN MAX
F.somefunc(False, S.a, False)
# FIX ME: MODIFY WINDOW SCREEN FONT "FONT", 12 STYLE "B" TITLE "TITLE" NOFLOAT NOCLOSE NOZOOM
# FIX ME: MODIFY COMMAND c:\\test.prg
vfpfunc.define_menu(\'test\', window=vfpfunc.SCREEN, bar=True, line=2)
vfpfunc.define_pad(\'test\', \'thing\', \'text\', color_scheme=3, message=\'menu\', key=(\'alt+f\', \'ALT+F\'))
vfpfunc.define_popup(\'test\')
vfpfunc.define_bar(1, \'test\', \'text\')
vfpfunc.on_pad_bar(\'pad\', \'test\', \'thing\', (\'popup\', \'test\'))
vfpfunc.on_pad_bar(\'bar\', 1, \'test\', (\'popup\', \'test\'))
# FIX ME: ACTIVATE WINDOW window
# FIX ME: ACTIVATE SCREEN
vfpfunc.activate_menu(\'test\', nowait=True)
# FIX ME: ACTIVATE POPUP test
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
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
#DEFINE THREE 3 &&the number 3
#IFDEF cantbewrong
#IF FILE ( \'test.h\' )
   ***************
   *** comment ***
   ***************
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

WAIT WIND space(3) + \'please wait\' + CHR(32) NOWAIT TIMEOUT 1.3
#ENDIF
#IF NOT FILE(\'test.h\')
   ?"This shouldn\'t be here"
#ENDIF
DO TEST.PRG
#IF THREE > 1
   ?STR(THREE)
   ??STR(THREE)
   DEBUGOUT STR(THREE)
   @ 10, 10 SAY THREE
#ENDIF
RETURN X
'''.strip()
    output_str = '''
from __future__ import division, print_function

import sys
import test

from vfp2py import vfpfunc
from vfp2py.vfpfunc import DB, Array, C, F, M, S, lparameters, parameters, vfpclass


@lparameters()
def MAIN():
    # comment with spaces
    ###############
    ### comment ###
    ###############
    S.x = \'\\n\'
    S.x = \'\\n\'
    S.x = \'\\n\'
    # set x to 5
    S.x = 5
    S.x = \'test\\r\\n\'
    S.x = \'\\x05\'
    S.x = \'\\r\\n\'
    test.MAIN()
    print(vfpfunc.str(3))
    print(vfpfunc.str(3), end=\'\')
    print(vfpfunc.str(3), file=sys.stderr)
    print(3)  # @ 10, 10 SAY 3
    return S.x
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test2():
    input_str = '''
DEFINE CLASS SUBOBJ AS CUSTOM
   X = 3

   FUNCTION INIT(X)
      DODEFAULT()
      THIS.X = X
      THIS.ARGTEST(THIS.X, 2)
   ENDFUNC

   PROCEDURE ARGTEST(X, Y)
   ENDPROC

   *comment
ENDDEFINE

*comment about subobj2
DEFINE CLASS SUBOBJ2 AS SUBOBJ
   X = 4
ENDDE

DEFINE CLASS TESTCLASS AS COMMANDBUTTON
   PROTECTED SOMEVAR
   ADD OBJECT TEST1 as custom
   ADD OBJECT TEST2 as subobj WITH X = 4
   ADD OBJECT TEST3 as unknownobj WITH X = \'4\'
   FUNCTION INIT(X)
      NODEFAULT
   ENDFUNC
ENDDEFINE

DEFINE CLASS ABUTTON AS testclass
  PROCEDURE Click
     TestClass::Click

ENDDEFINE

FUNCTION RANDOM_FUNCTION

   * something
   LPARAMETERS X
   ?x
ENDFUNC

*comment about testclass2
DEFINE CLASS TESTCLASS2 AS UNKNOWNCLASS
ENDDEFINE

FUNCTION ANOTHER_RANDOM_FUNCTION

   * something
   PARAMETERS X, Y
   ?x
ENDFUNC
'''.strip()
    output_str = '''
from __future__ import division, print_function

from vfp2py import vfpfunc
from vfp2py.vfpfunc import DB, Array, C, F, M, S, lparameters, parameters, vfpclass


@lparameters()
def MAIN():
    pass


@vfpclass
def Subobj():
    BaseClass = vfpfunc.Custom

    class Subobj(BaseClass):

        @lparameters()
        def _assign(self):
            BaseClass._assign(self)
            self.x = 3

            # comment
        @lparameters(\'x\')
        def init(self):
            super(type(self), self).init()
            self.x = S.x
            self.argtest(self.x, 2)

        @lparameters(\'x\', \'y\')
        def argtest(self):
            pass
    return Subobj

# comment about subobj2


@vfpclass
def Subobj2():
    BaseClass = SubobjType()

    class Subobj2(BaseClass):

        @lparameters()
        def _assign(self):
            BaseClass._assign(self)
            self.x = 4
    return Subobj2


@vfpclass
def Testclass():
    BaseClass = vfpfunc.Commandbutton

    class Testclass(BaseClass):

        @lparameters()
        def _assign(self):
            BaseClass._assign(self)
            self.test1 = vfpfunc.Custom(name=\'test1\', parent=self)
            self.test2 = Subobj(x=4, name=\'test2\', parent=self)
            self.test3 = vfpfunc.create_object(\'Unknownobj\', x=\'4\', name=\'test3\', parent=self)

        @lparameters(\'x\')
        def init(self):
            # FIX ME: NODEFAULT
            pass
    return Testclass


@vfpclass
def Abutton():
    BaseClass = TestclassType()

    class Abutton(BaseClass):

        @lparameters()
        def _assign(self):
            BaseClass._assign(self)

        @lparameters()
        def click(self):
            Testclass.click()

    return Abutton


@lparameters(\'x\')
def random_function():

    # something
    print(S.x)

# comment about testclass2


@vfpclass
def Testclass2():
    BaseClass = C[\'Unknownclass\']

    class Testclass2(BaseClass):

        @lparameters()
        def _assign(self):
            BaseClass._assign(self)
    return Testclass2


@parameters(\'x\', \'y\')
def another_random_function():

    # something
    print(S.x)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test3():
    input_str = '''
LOCAL A
DO A
DO A+B
DO A + B
DO ALLTRIM(A)
DO TEST in A
DO TEST in (A)
DO TEST IN A+\'.PRG\'
DO TEST IN A+(B)
DO TEST.PRG
DO TEST IN TEST.PRG
DO FORM SPLASH.SCX
DO FORM SPLASH.SCX NAME splashy
DO FORM SPLASH.SCX NAME splashy LINKED
CD ..
delete file test.txt
erase test.txt
delete file ?
delete file test.txt recycle
'''.strip()
    output_str = '''
M.add_local(\'a\')
F.a()
F[\'a+b\']()
F[S.a + S.b]()
F[S.a.strip()]()
a.test()
vfpfunc.module(S.a).test()
vfpfunc.module(S.a + \'.PRG\').test()
vfpfunc.module(S.a + (S.b)).test()
test.MAIN()
test.test()
vfpfunc.do_form(\'splash.scx\')
vfpfunc.do_form(\'splash.scx\', name=\'splashy\')
vfpfunc.do_form(\'splash.scx\', name=\'splashy\', linked=True)
os.chdir(\'..\')
os.remove(\'test.txt\')
os.remove(\'test.txt\')
os.remove(vfpfunc.getfile(\'\', \'Select file to\', \'Delete\', 0, \'Delete\'))
send2trash(\'test.txt\')
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test4():
    input_str = '''
LOCAL test
copy file (test) to tset
rename (test) to tset
mkdir test - test
MD test+test
rmdir (test+test)
rd alltrim(test)
!ls -al &pathname
'''.strip()
    output_str = '''
M.add_local(\'test\')
shutil.copyfile(S.test, \'tset\')
shutil.move(S.test, \'tset\')
os.mkdir(S.test - S.test)
os.mkdir(\'test+test\')
os.rmdir(S.test + S.test)
os.rmdir(S.test.strip())
vfpfunc.macro_eval(\'!ls -al &pathname\')
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test5():
    input_str = '''
CREAT CURSO TEST_CURSOR (SOMEFIELD N(3))
continue
LOCAL SEARCH_FOR, COUNTVAL, SUMVAL
SEARCH_FOR = \'PAUL\'
SEEK ALLTRIM(SEARCH_FOR)
COUNT FOR TEST = 3 TO COUNTVAL
SUM T * T FOR T > 0 TO SUMVAL
LOCATE WHILE X > 5 NOOPTIMIZE
RELEASE SEARCH_FOR, COUNTVAL, SUMVAL
update test set a=b, c=d, e=f where x=3
'''.strip()
    output_str = '''
DB.create_cursor(\'test_cursor\', \'somefield n(3)\', \'\')
DB.continue_locate()
M.add_local(\'search_for\', \'countval\', \'sumval\')
S.search_for = \'PAUL\'
DB.seek(None, S.search_for.strip())
S.countval = DB.count(None, (\'all\',), for_cond=lambda: S.test == 3)
S.sumval = DB.sum(None, (\'all\',), lambda: S.t * S.t, for_cond=lambda: S.t > 0)
DB.locate(nooptimize=True, while_cond=lambda: S.x > 5)
del M.search_for, M.countval, M.sumval
DB.update(\'test\', [(\'a\', S.b), (\'c\', S.d), (\'e\', S.f)], where=lambda: S.x == 3)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test6():
    input_str = '''
MKDIR TEST
?DATE()
?PI()
'''.strip()
    output_str = '''
from __future__ import division, print_function

import datetime as dt
import math
import os

from vfp2py import vfpfunc
from vfp2py.vfpfunc import DB, Array, C, F, M, S, lparameters, parameters, vfpclass


@lparameters()
def MAIN():
    os.mkdir(\'test\')
    print(dt.datetime.now().date())
    print(math.pi)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test7():
    input_str = '''
PUSH KEY CLEAR
PUSH KEY
PUSH MENU test
PUSH POPUP test
POP KEY ALL
POP KEY
POP MENU TO MASTER test
POP POPUP test
declare integer printf in c as c_printf string
CLEAR DLLS "TEST1", "TEST2"
CLEAR MACROS
CLEAR EVENTS
CLEAR ALL
CLEAR READ
CLEAR READ ALL
CLEAR
'''.strip()
    output_str = '''
 # FIX ME: PUSH KEY CLEAR
# FIX ME: PUSH KEY
# FIX ME: PUSH MENU test
# FIX ME: PUSH POPUP test
# FIX ME: POP KEY ALL
# FIX ME: POP KEY
# FIX ME: POP MENU TO MASTER test
# FIX ME: POP POPUP test
F.dll_declare(\'c\', \'printf\', \'c_printf\')
F.dll_clear(\'test1\', \'test2\')
vfpfunc.clear(\'macros\')
vfpfunc.clear(\'events\')
vfpfunc.clear(None, \'all\')
vfpfunc.clear(\'read\')
vfpfunc.clear(\'read\', \'all\')
vfpfunc.clear(None)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test8():
    input_str = '''
LOCAL X, Y
X = .F.
Y = \'failed\'
ASSERT NOT X
ASSERT X = .T. MESSAGE Y + \' ASSERT\'
'''.strip()
    output_str = '''
M.add_local(\'x\', \'y\')
S.x = False
S.y = \'failed\'
assert not S.x
assert S.x == True, S.y + \' ASSERT\'
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test9():
    input_str = '''
SET COMPATIBLE OFF
SET COMPATIBLE DB4
SET COMPATIBLE FOXPLUS
SET COMPATIBLE ON
SET COMPATIBLE FOXPLUS PROMPT
SET COMPATIBLE DB4 NOPROMPT
SET CLASSLIB TO TEST
SET CLASSLIB TO TEST IN TEST
SET CLASSLIB TO TEST ALIAS NOTTEST
SET CLASSLIB TO TEST IN TEST ALIAS NOTTEST ADDITIVE
SET TABLEPROMPT ON
SET EXCLUSIVE ON
SET DEFAULT TO SOMETHING
SET HELP OFF
SET HELP TO TEST
SET HELP COLLECTION test
SET HELP SYSTEM
SET RELATION TO a=b INTO test
SET TALK OFF
SET UDFPARMS TO REFERENCE
SET UDFPARMS TO VALUE
'''.strip()
    output_str = '''
vfpfunc.set(\'compatible\', \'OFF\', set_value=True)
vfpfunc.set(\'compatible\', \'ON\', set_value=True)
vfpfunc.set(\'compatible\', \'OFF\', set_value=True)
vfpfunc.set(\'compatible\', \'ON\', set_value=True)
vfpfunc.set(\'compatible\', \'OFF\', \'PROMPT\', set_value=True)
vfpfunc.set(\'compatible\', \'ON\', \'NOPROMPT\', set_value=True)
vfpfunc.set(\'classlib\', \'test\', set_value=True)
vfpfunc.set(\'classlib\', \'test\', class_file=\'test\', set_value=True)
vfpfunc.set(\'classlib\', \'test\', alias=\'nottest\', set_value=True)
vfpfunc.set(\'classlib\', \'test\', alias=\'nottest\', class_file=\'test\', additive=True, set_value=True)
vfpfunc.set(\'tableprompt\', \'ON\', set_value=True)
vfpfunc.set(\'exclusive\', \'ON\', set_value=True)
# FIX ME: SET DEFAULT TO SOMETHING
# FIX ME: SET HELP OFF
# FIX ME: SET HELP TO TEST
# FIX ME: SET HELP COLLECTION test
# FIX ME: SET HELP SYSTEM
# FIX ME: SET RELATION TO a=b INTO test
vfpfunc.set(\'talk\', \'OFF\', set_value=True)
vfpfunc.set(\'udfparms\', \'reference\', set_value=True)
vfpfunc.set(\'udfparms\', \'value\', set_value=True)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test10():
    input_str = '''
APPEND FROM TABLE_NAME
APPEND FROM TABLE_NAME TYPE DELIMITED
APPEND FROM \'table\' + \'_\' + \'name\' TYPE \'Delimited\'
APPEND FROM ARRAY TEST
'''.strip()
    output_str = '''
DB.append_from(None, \'table_name\')
DB.append_from(None, \'table_name\', filetype=\'delimited\')
DB.append_from(None, \'table_name\', filetype=\'delimited\')
DB.insert(None, S.test)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test11():
    input_str = '''
LOCAL MYFILE, mydir
MYFILE = \'c:\\test\\test.prg\'
MYDIR = \'c:\\test\\test\\dir\'
?file(myfile)
?justdrive(MYFILE)
?justpath(MYFILE)
?justfname(MYFILE)
?juststem(myfile)
?JUSTEXT(myfile)
?FORCEEXT(myfile, \'py\')
?directory(mydir)
?justdrive(MYDIR)
?justpath(MYDIR)
?justfname(MYDIR)
?juststem(mydir)
?JUSTEXT(mydir)
?FORCEEXT(mydir, \'PY\')
?ADDBS(MYDIR) + \'dir1\'
?ADDBS(ADDBS(MYDIR) + \'dir1\') + \'dir2\'
?ADDBS(ADDBS(ADDBS(MYDIR) + \'dir1\') + \'dir2\') + \'dir3\'
?CURDIR()
RELEASE MYFILE, MYDIR
'''.strip()
    output_str = '''
M.add_local(\'myfile\', \'mydir\')
S.myfile = \'c:\\\\test\\\\test.prg\'
S.mydir = \'c:\\\\test\\\\test\\\\dir\'
print(os.path.isfile(S.myfile))
print(os.path.splitdrive(S.myfile)[0])
print(os.path.dirname(S.myfile))
print(os.path.basename(S.myfile))
print(os.path.splitext(os.path.basename(S.myfile))[0])
print(os.path.splitext(S.myfile)[1][1:])
print(os.path.splitext(S.myfile)[0] + \'.\' + \'py\')
print(os.path.isdir(S.mydir))
print(os.path.splitdrive(S.mydir)[0])
print(os.path.dirname(S.mydir))
print(os.path.basename(S.mydir))
print(os.path.splitext(os.path.basename(S.mydir))[0])
print(os.path.splitext(S.mydir)[1][1:])
print(os.path.splitext(S.mydir)[0] + \'.\' + \'py\')
print(os.path.join(S.mydir, \'dir1\'))
print(os.path.join(S.mydir, \'dir1\', \'dir2\'))
print(os.path.join(S.mydir, \'dir1\', \'dir2\', \'dir3\'))
print(os.getcwd())
del M.myfile, M.mydir
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test12():
    input_str = '''
LOCAL ARRAY somearray[2, 5]
LOCAL pytuple, pylist, pydict
pytuple = createobject(\'pythontuple\', \'a\', 3, .T.)
pylist = createobject(\'pythonlist\', @somearray)
pylist.callmethod(\'append\', createobject(\'pythontuple\', \'appended value\'))
pydict = createobject(\'pythondictionary\')
pydict.setitem(\'one\', 1)
?pydict.getitem(\'one\')
pythonfunctioncall(\'test\', \'test\', pytuple)
'''.strip()
    output_str = '''
M.add_local(somearray=Array(2, 5))
M.add_local(\'pytuple\', \'pylist\', \'pydict\')
S.pytuple = (\'a\', 3, True)
S.pylist = S.somearray.data[:]
S.pylist.append(\'appended value\')
S.pydict = {}
S.pydict[\'one\'] = 1
print(S.pydict[\'one\'])
test.test(*S.pytuple)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test13():
    input_str = '''
PUBLIC ARRAY somearray[2, 5]
public array def[10]
SOMEARRAY(1, 4) = 3
PRIVATE TEST, somearray[2, 5]
EXTERNAL ARRAY someotherarray[3]
EXTERNAL PROCEDURE test
'''.strip()
    output_str = '''
M.add_public(somearray=Array(2, 5))
M.add_public(**{\'def\': Array(10)})
S.somearray[1, 4] = 3
M.add_private(\'test\', somearray=Array(2, 5))
# FIX ME: EXTERNAL ARRAY someotherarray[3]
# FIX ME: EXTERNAL PROCEDURE test
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test14():
    input_str = '''
Try
   assert .f.
catch to oerr
   throw
endtry
throw \'Error\' + \' Message\'
RETRY
'''.strip()
    output_str = '''
try:
    assert False
except Exception as err:
    S.oerr = vfpfunc.Exception.from_pyexception(err)
    raise
raise Exception(\'Error Message\')
# FIX ME: RETRY
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test15():
    input_str = '''
LOCAL CNT_FIELDS
LOCAL ARRAY MAIN_ARRAY(1)
CNT_FIELDS = AFIELDS(MAIN_ARRAY) + 32
CNT_FIELDS = AFIELDS(MAIN_ARRAY2, \'report\') + 47
T = aINS(main_array, 3)
T = aINS(main_array, 3, 2)
vals_copied = acopy(main_array, new_array)
vals_copied = acopy(main_array, new_array, 5)
vals_copied = acopy(main_array, new_array, 5, num_elements)
vals_copied = acopy(main_array, new_array, 5, num_elements, 0)
'''.strip()
    output_str = '''
M.add_local(\'cnt_fields\')
M.add_local(main_array=Array(1))
S.cnt_fields = DB.afields(None, \'main_array\', (locals(), S)) + 32
S.cnt_fields = DB.afields(\'report\', \'main_array2\', (locals(), S)) + 47
S.t = S.main_array.insert(None, 3)
S.t = S.main_array.insert(None, 3, 2)
S.vals_copied = S.main_array.copy(\'new_array\')
S.vals_copied = S.main_array.copy(\'new_array\', 5)
S.vals_copied = S.main_array.copy(\'new_array\', 5, S.num_elements)
S.vals_copied = S.main_array.copy(\'new_array\', 5, S.num_elements, 0)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test16():
    input_str = '''
SKIP
SKIP 10
SKIP IN TEST
SKIP someval IN TEST
'''.strip()
    output_str = '''
DB.skip(None, 1)
DB.skip(None, 10)
DB.skip(\'test\', 1)
DB.skip(\'test\', S.someval)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test17():
    input_str = '''
ON ERROR
ON ERROR DO test
ON SHUTDOWN
ON SHUTDOWN DO SHUTDOWN IN SHUTDOWN
ON SHUTDOWN QUIT
ON ESCAPE QUIT
ON KEY LABEL F12 ?\'KEY PRESSED\'
'''.strip()
    output_str = '''
vfpfunc.error_func = None
vfpfunc.error_func = lambda: F.test()
vfpfunc.shutdown_func = None
vfpfunc.shutdown_func = lambda: shutdown.shutdown()
vfpfunc.shutdown_func = lambda: vfpfunc.quit()
vfpfunc.escape_func = lambda: vfpfunc.quit()
vfpfunc.on_key[\'f12\'] = lambda: print(\'KEY PRESSED\')
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test18():
    input_str = '''
@x, y 
@x, y CLEAR
@x, y CLEAR TO a, b
@x, y say \'hello \' + username
@x, y say \'hello \' + username STYLE thestyle
'''.strip()
    output_str = '''
print()  # @x, y
print()  # @x, y CLEAR
print()  # @x, y CLEAR TO a, b
print(\'hello \' + S.username)  # @x, y say \'hello \' + username
print(\'hello \' + S.username)  # @x, y say \'hello \' + username STYLE thestyle
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test19():
    input_str = '''
scatter name test
scatter blank memvar
scatter to somearray
gather name test
gather memvar
gather from somearray
'''.strip()
    output_str = '''
S.test = vfpfunc.scatter(totype=\'name\')
vfpfunc.scatter(blank=True)
S.somearray = vfpfunc.scatter(totype=\'array\')
vfpfunc.gather(val=S.test)
vfpfunc.gather()
vfpfunc.gather(val=S.somearray)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise


def Test20():
    input_str = '''
REPORT FORM TEST.FRX TO PRINTER NOCONSOLE
REPORT FORM ?
'''.strip()
    output_str = '''
vfpfunc.report_form(\'test.frx\')
vfpfunc.report_form(None)
'''.strip()
    test_output_str = vfp2py.vfp2py.prg2py(input_str, 'cp1252', parser_start='lines', prepend_data='').strip()
    try:
        assert test_output_str == output_str
    except AssertionError:
        diff = difflib.unified_diff((test_output_str + '\n').splitlines(1), (output_str + '\n').splitlines(1))
        print(''.join(diff))
        raise

