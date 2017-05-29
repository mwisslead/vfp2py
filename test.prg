   *comment with spaces
#DEFINE cantbewrong
#DEFINE SPACE CHR
#IFDEF cantbewrong
#IF FILE ( 'test.h' )
   ***comment***
   # include  test.h
   # include  'test.h'
   # include  'test' + '.h'
   STORE 5 to  x && set x to 5
#ELSE
#ENDIF
   x = 'test' + CHR(13) + CHR(10)
   x = space(5)
   x = '' + CHR(13) + CHR(10)
#ELSE
_SCREEN.LOGO.TOP = (_SCREEN.HEIGHT-_SCREEN.LOGO.HEIGHT)/2-3

WAIT WINDOW space(3) + 'please wait' + CHR(32) NOWAIT TIMEOUT 1.3
#ENDIF

ON ERROR
ON ERROR DO test
SET TYPEAHEAD TO 0
?LEFT('Hello, World', 5)
WAIT WINDOW space(3) + 'please wait' + CHR(32) NOWAIT TIMEOUT 1.3
md test - test
MD test+test
md (test+test)
*com;
ment
NOTE note;
comment
x = 5*2**3**4
x = (1+2)*3
None = .nUlL.
Bool = .Y.
somedate = { / / }

if x > 5
else
   ?'hello'
   ?'goodbye'
ENDif

if x > 5
**do nothing
else
endif

delete file test . txt
delete file test.txt
delete file x
delete file (x)
delete file '' + x

_screen.refresh
test.prg()
test.prg(1)

if .f.
else
DO CASE
   CASE X == 1 && case 1
      do case
         case x == 1

      endcase
      X = 2
   CASE X == 2 && case 2
      X = 3
   CASE X == 2 && case 2 again
      X = 3
   CASE X == 2
      X = 3
   CASE X == 2
      X = 3
   CASE X == 2
      X = 3
ENDCASE
endif

do case
endcase

do case
endcase &&empty case end with comment

t=u(v(w(x(y(z)))))

*** CREATE REPORT TABLE
CREATE TABLE REPORT FREE (NAME C(50), ST C(2), QUANTITY N(5, 0), RECEIVED L(1))
USE REPORT IN 0 SHARED
SELECT REPORT
APPEND BLANK

REPLACE REPORT.NAME WITH 'Michael'
REPLACE REPORT.ST WITH 'IA'
REPLACE REPORT.QUANTITY WITH 4
REPLACE REPORT.RECEIVED WITH .F.

GO TOP

FOR X = 1 TO REPORT.QUANITY
    SET PRINTER TO ALLTRIM('printer')
    REPORT FORM TEST.FRX TO PRINTER NOCONSOLE
    SET PRINTER TO
    EXIT
ENDFOR

FOR X = 1 TO REPORT.QUANITY
ENDFOR

LOCAL ARRAY ITEMS[3, 5]
FOR EACH ITEM IN ITEMS
    EXIT
ENDFOR
RELEASE ITEMS

&&Demo using local to generate cleaner code since no way to know if variable is local otherwise.
LOCAL ITEM
WITH item
   DO WHILE .value <= 3
      .value = .value + 1
      .test
   ENDDO
ENDWITH
RELEASE ITEM, X
***ITEM no long a local***
ITEM.VALUE = 3

tablename = 'REPORT'

USE (tablename) IN 0 SHARED

IF USED('REPORT')
   SELECT REPORT
   USE IN REPORT
ENDIF

DO test
DO test in test
DO prg\test.prg
DO test.mpr

IF FILE('DBFTABLE.DBF')
   USE DBFTABLE IN 0 SHARED
   SELECT DBFTABLE
   COPY STRUCTURE TO 'DBFTEMP.DBF'
   IF USED('DBFTABLE')
      SELECT DBFTABLE
      USE IN DBFTABLE
   ENDIF
   IF USED('DBFTEMP')
      SELECT DBFTEMP
      USE IN DBFTEMP
   ENDIF
ENDIF

DEACTIVATE MENU test
DEACTIVATE POPUP ALL
RELEASE ALL
RELEASE test1
RELEASE test1, test2, test3
RELEASE POPUPS popup1
RELEASE POPUPS popup1 EXTENDED

RUN /N2 ls -al

local x
?SIGN(x)
?NVL(x, 0)
?EVL(x, 0)
release x
local empty_test, x
?1 + + 3 - - 3
?empty_test # 'string'
empty_test = .NULL.
?exp(tan(PI()/4))
?EMPTY(0)
?EMPTY(.NULL.)
?EMPTY('test')
?EMPTY('')
?EMPTY(empty_test)
?SUBSTR('string', 2)
?SUBSTR('string', 2, 3)
QUIT

CREATE TABLE REPORT FREE (NAME C(50), ST C(2), QUANTITY N(5, 0), RECEIVED L(1))
CREATE TABLE REPORT2 FREE (NAME C(50), ST C(2), QUANTITY N(5, 0), RECEIVED L(1))
USE REPORT IN 0 SHARED
USE REPORT2 IN 0 SHARED
SELECT REPORT2
APPEND BLANK
REPLACE NAME WITH 'MICHAEL'
REPLACE ST WITH 'IA'
REPLACE QUANTITY WITH 122
REPLACE RECEIVED WITH .T.
SELECT REPORT
APPEND BLANK
REPLACE NAME WITH 'MICHAEL'
REPLACE ST WITH 'IA'
REPLACE QUANTITY WITH 122
REPLACE RECEIVED WITH .T.
?RECNO()
APPEND BLANK
REPLACE NAME WITH 'PAUL'
REPLACE ST WITH 'IL'
REPLACE QUANTITY WITH 37
REPLACE RECEIVED WITH .F.
APPEND BLANK
REPLACE NAME WITH 'JOE'
REPLACE ST WITH 'IA'
REPLACE QUANTITY WITH 537
REPLACE RECEIVED WITH .T.
APPEND BLANK
REPLACE ('NAME') WITH 'SUBEXPR'
APPEND BLANK
REPLACE REPORT.NAME WITH 'TABLE SPECIFIED'
?RECNO()
?eof()
SKIP -5
?recno()
?eof()
?bof()
?RECNO()
?RECCOUNT()
SKIP 2
DELETE REST FOR RECEIVED = .T.
?DELETED()
PACK
INDEX ON NAME TAG NAME UNIQUE
REINDEX
ZAP
ZAP IN REPORT2
CLOSE TABLES
?RECCOUNT()
X = 'Hello Variable Scope'
?X
DO FORM SPLASH.SCX
local x
x = 'hi'
USE (this.tablename) in 0 shared
?inlist(x, 'hello', 'hola', 'aloha')
?inlist(x, 'hello')
?tan(pi()/4)
?bitclear(15, 3) &&should be 7
?bitset(7, 3) &&should be 15
?bittest(15, 3)
?bittest(7, 3)
SET STATUS ON
SET STATUS BAR ON
SET BELL ON
SET BELL OFF
SET BELL TO 'string'
SET CENTURY ON
SET CENTURY TO 19 ROLLOVER 99
SET SYSMENU ON
SET SYSMENU OFF
SET SYSMENU TO
SET SYSMENU TO 'string'
SET SYSMENU TO DEFAULT
SET SYSMENU SAVE
SET SYSMENU NOSAVE
SET DATE AMERICAN
SET DATE TO DATEFORMAT
SET EXACT ON
SET EXACT OFF
SET NOTIFY ON
SET NOTIFY OFF
SET NOTIFY CURSOR ON
SET FILTER TO
SET FILTER TO FILTER_VAL
SET ORDER TO ORDER_VAL
ON SHUTDOWN
ON SHUTDOWN DO SHUTDOWN IN SHUTDOWN
ON SHUTDOWN QUIT
PUSH KEY CLEAR
PUSH KEY
POP KEY ALL
POP KEY
ON KEY LABEL F12 ?'KEY PRESSED'
public publicvar
do helper_func in helpers with 'helper_func message with do'
set procedure to helpers
helper_func('helper_func message with standard call')
release procedure helpers
declare integer printf in c as c_printf string
declare integer printf in c string
c_printf('hello c_printf' + CHR(10))
printf('hello printf' + CHR(10))
private test
local obj, x
x = 1
dimension testarr(3, 7)
?alen(testarr)
?alen(testarr, 0)
?alen(testarr, 1)
?alen(testarr, 2)
dimension testarr(1, x+4)
testarr(1, 4) = 'Caption from array'
obj = createobject('testclass')
obj2 = createobject('test' + 'class2')
obj.show
?test
testarr(1, 3) = 4
?testarr(1, 3)
x = testarr(1, 3)
?(publicvar)
x = 0
?substr(publicvar, 2, x + 2)
x = 1 - 5
?asc(publicvar)
?buf2dword(repli(chr(0), 16))
x = 'Someone'
MESSAGEBOX(''+SPACE(10)+'The DLL is Missing!'+CHR(13)+''+CHR(13)+' Contact '+ALLTRIM(X)+'  at  '+ALLTRIM('your phone number')+' '+CHR(13)+''+CHR(13)+''+SPACE(10)+'For a Replacement File.',64,'File Missing')
local fhandle
fhandle = fcreate('file.txt')
fputs(fhandle, 'hello')
fputs(fhandle, 'hello', 3)
fwrite(fhandle, 'hello')
fwrite(fhandle, 'hello', 3)
fclose(fhandle)
fhandle = fopen('file.txt')
?fgets(fhandle)
?
?fread(fhandle, len('hello' + CHR(13) + CHR(10)))
fclose(fhandle)
fhandle = fopen('file.txt', 2)
fclose(fhandle)
?year(date())
?int(3.5)
?int('3')
?int(x)
?isnull(.null.)
?isnull(x)
?right('testing', 5)
?max(1, 2, 3, 3, 2, 1)
?min(1, 2, 3, 3, 2, 1)
?x + '' + x
?strtran('testing', 'sting')
?strtran('testing', 'sting', 'eth')
?strtran('testtesttest', 'test', 'fart', 1)
?strtran('testtesttest', 'test', 'fart', 2)
?strtran('testtesttest', 'test', 'fart', 1, 2)
?strtran('testtesttest', 'test', 'fart', 2, 2)
?strtran('testtesttest', 'test', 'fart', 1, 2, 0)
?sys(16)
?isblank(.null.)
?str(3278.24, 6, 1)
?str(5, 2)
?str(12, 2)

USE TABLE_NAME IN 0 SHARED
USE IN TABLE_NAME
USE

APPEND
APPEND BLANK
APPEND IN specialExpr NOMENU
APPEND IN specialExpr
APPEND BLANK IN specialExpr
APPEND FROM TABLE_NAME

GOTO 5 IN TABLE_NAME
GOTO 6

PACK

PACK IN (TABLE_NAME)
PACK IN  TABLE_NAME
PACK IN 'string'
PACK IN 'stri' + 'ng'

PACK DBF IN TABLE_NAME

PACK MEMO IN TABLE_NAME + '.DBF'
PACK MEMO IN (TABLE_NAME+DBFENDING)
PACK MEMO IN TABLE_NAME + DBFENDING

PACK TEST
PACK TEST IN TABLE_NAME
PACK DBF TEST IN TABLE_NAME

PACK DATABASE

SKIP TEST
SKIP TEST IN TEST

INDEX ON INDEX_FIELD TO INDEX_ALIAS ADDITIVE

REPLACE ALL TEST.FIELD_NAME WITH X FOR Y > 3

DELETE ALL IN TABLE_NAME NOOPTIMIZE
DELETE ALL IN TABLE_NAME

ZAP
ZAP IN TABLE_NAME

local today, now
today = date()
now = datetime()
?cdow(today)
?cmonth(today)
?sec(now)
local myval, lower_val, upper_val
?between(myval, lower_val, upper_val)
?sqrt(5)
?stuff('testing', 4, 0, 'ter')
?stuffc('testing', 4, 0, 'ter')
?directory('vfp2py')
?evl(myval, 'Default')
?nvl(myval, 0)
?justpath('.')
?justpath('./')
?justpath('c:\test\test.prg')
?justfname('c:\test\test.prg')
?proper('Visual FoxPro')
?quarter(date())
use in select('test')

PUBLIC X, Y, Z
LOCAL W
W = 32
RELEASE W, X, Y, Z
RELEASE ALL

LOCAL ARRAY T[3, 4]
T[2, 1] = 5
T[3, 2] = 5
?ASCAN(T, 5)
?ASCAN(T, 5, 9)
?ASCAN(T, 5, 6, 3)

ON ERROR DO ERROR_HANDLER IN TEST5 WITH MESSAGE(), MESSAGE(1), LINENO()
ERROR('test')
ON ERROR ??
ERROR
ON ERROR
ERROR

LOCAL X, N
X = 3
N = 4

SET BELL ON
?SET('BELL')
?SET('BELL', 1)
SET BELL TO C:\FOLDER
?SET('BELL')
?SET('BELL', 1)
SET CURSOR ON
?SET("CURSOR")
SET DELETED ON
?SET("DELETED")
SET EXACT ON
?SET("EXACT")
SET NEAR ON
?SET("NEAR")
SET STATUS ON
?SET("STATUS")
SET STATUS BAR ON
?SET("STATUS BAR")
SET UNIQUE ON
?SET("UNIQUE")

SET REFRESH TO (X)
?SET("REFRESH")
SET REFRESH TO (X), (N)
?SET("REFRESH")

?'NOTIFY'
?SET('NOTIFY')
?SET('NOTIFY', 1)
SET NOTIFY OFF
?SET('NOTIFY')
?SET('NOTIFY', 1)
SET NOTIFY CURSOR OFF
?SET('NOTIFY')
?SET('NOTIFY', 1)

SET PRINTER ON
SET PRINTER ON PROMPT
SET PRINTER OFF
SET PRINTER TO 'test'
SET PRINTER TO 'test' ADDITIVE
SET PRINTER TO NAME 'test'
SET PRINTER TO DEFAULT
SET PRINTER TO

SET CENTURY ON
SET CENTURY OFF
SET CENTURY TO
SET CENTURY TO 20
SET CENTURY TO 20 ROLLOVER 39
?SET('CENTURY')
?SET('CENTURY', 1)
?SET('CENTURY', 2)
?SET('CENTURY', 3)

?SET('MULTILOCKS')
SET MULTILOCKS ON
?SET('MULTILOCKS')

?CAST(.F. AS I)
?CAST(.F. AS INT)
?CAST(.F. AS INTEGER)
?CAST(2 AS L)
?CAST(2 AS LOGICAL)

LOCAL A, B
??createobject('PythonTuple', A, B)
LOCAL ARRAY xcarvar[1]
LOCAL xcarvar_list, pydict
xcarvar_list = CREATEOBJECT('PythonList', @xcarvar)
xcarvar_list.callmethod('append', 1)
?xcarvar_list.repr()
xcarvar_list.setitem(0, 0)
?xcarvar_list.getitem(0)
xcarvar_list = CREATEOBJECT('PythonList')
pydict = CREATEOBJECT('PythonDictionary')
pydict.setitem('test', .null.)
?pydict.getitem('test')
RELEASE xcarvar_list, pydict

local prog_file, func_name, someobject
prog_file = 'helpers'
func_name = 'helper_func'
do helper_func in helpers with 'message1'
do (func_name) in helpers with 'message2'
do helper_func in (prog_file) with 'message3'
do (func_name) in (prog_file) with 'message4'

someobject.method_name
release prog_file, func_name, someobject

LOCAL OLD_SELECT, A
OLD_SELECT = SELECT()

TRY
   a = 3
ENDTRY


TRY
   a = 3
catch
   a = 4
endtry

TRY
   a = 3
catch
   a = 4
finally
   a = 5
endtry

TRY
   USE nonexistant
CATCH TO err
   MESSAGEBOX(err.message)
FINALLY
   USE IN SELECT('NONEXISTANT')
   SELECT(OLD_SELECT)
endtry
RELEASE OLD_SELECT, A

?strconv('abcdef', 13)
?strconv('YWJjZGVm', 14)
?strconv(strconv('abcdef', 13), 14)

FUNCTION test
   parameters a, b
   ?a, b

FUNCTION REPLACE_TEST(TABLENAME, FIELD_VAL)
   IF FILE(TABLENAME + '.DBF')
      USE (TABLENAME) IN 0 SHARED
      SELECT (TABLENAME)
      SELECT('TABLENAME')
      SELECT * FROM (TABLENAME) WHERE ALLTRIM(CUSTNAME) = ALLTRIM(CUSTNAME_VALUE) INTO TABLE PATHNAME+'TEMPCUSTOMER.DBF'
      REPLACE ALL TEST WITH .T. FOR FIELD1 = FIELDVAL
      GO TOP
      SKIP -3
      SKIP 1
      GO BOTTOM
      GO 15
      DELETE ALL
      DELETE
      DELETE NEXT 1
      DELETE NEXT 10
      DELETE NEXT (THREE)
      SKIP -1
      RECALL
      SCAN
         ?CUSTNAME
      ENDSCAN
      SCAN FOR CUSTNAME = 'FRED'
         ?CUSTNAME
      ENDSCAN
      DELETE RECORD RECNUMBER+1
      DELETE RECORD (RECNUMBER+1)
      DELETE REST
      DELETE REST FOR FIELD1='3'
      DELETE REST WHILE FIELD1='3'
      USE IN SELECT(TABLENAME)
      USE IN SELECT('tablename')
      USE IN TABLENAME
      USE IN (TABLENAME)
      USE IN 'TABLENAME'
   ENDIF
   RETURN

DEFINE CLASS test as custom
   x = 3 && x is a thing in this class
   procedure init
      parameters initx, inity
      this.x = initx

   function athing(test)
      NODEFAULT
      return this.x
   endfunc
   && comment
ENDDEFINE

DEFINE CLASS test2 as form
   add object test as t with prop = 'hello'
   add object cbox as combobox
   x = 3
ENDDEFINE

define class testclass as custom
   caption = testarr(1, 4)

   add object btn1 as commandbutton with caption='button 1'
   btn1.caption = 'click'

   add object lb_lb as label with top=28, left=11, caption='caption'

   procedure btn1.click
      ?'button 1 clicked'
   endproc

   procedure test1

   *show function
   procedure show
      test = 'hello world'
      ?test
      ?testproc()
      return

   procedure init
      publicvar = 'testclass visited'
      ?3

   procedure test2(ok)
   procedure test3

enddefine

procedure testproc
   ?test
   x = 'testproc returned this value'
   if x < 0
      return 0
   endif
   return x

procedure testproc2
   return
   return
endproc

FUNCTION  buf2dword (lcBuffer)
RETURN;
    Asc(SUBSTR(lcBuffer, 1,1)) + ;
    Asc(SUBSTR(lcBuffer, 2,1)) * 256 +;
    Asc(SUBSTR(lcBuffer, 3,1)) * 65536 +;
    Asc(SUBSTR(lcBuffer, 4,1)) * 16777216

FUNCTION ERROR_HANDLER(MSG, CODE, LINE)
   ?'line ' + LINE + ':' + CODE
   ?MSG
