procedure select_tests
   assert select() = 1
   assert select(0) = 1
   assert select(1) = 32767
   assert select(2) = 0
   assert select('test') = 0
ENDPROC

procedure chr_tests
   assert asc(chr(0)) = 0
endproc

procedure set_tests
   assert set('compatible') = 'OFF'
   assert set('compatible', 1) = 'PROMPT'
ENDPROC

procedure used_tests
   assert used('test') = .f.
endproc

procedure date_tests
   local somedate
   somedate = {^2017-6-30}
   assert somedate == Date(2017, 6, 30)
   assert dow(somedate) == 6
   assert cdow(somedate) == 'Friday'
   assert month(somedate) == 6
   assert cmonth(somedate) == 'June'
   assert dmy(somedate) == '30 June 2017'
   assert dtos(somedate) == '20170630'
   assert dtoc(somedate) == '06/30/2017'
   assert len(time()) == 8
   assert len(time(1)) == 11
   assert dtot(somedate) == Datetime(2017, 6, 30, 0)
   assert gomonth(somedate, -4) = date(2017, 2, 28)
   assert vartype(somedate) == 'D'
   assert vartype(dtot(somedate)) == 'T'
endproc

procedure math_tests
   local num_value
   num_value = pi()
   assert round(pi(), 2) == 3.14
   assert abs(tan(dtor(45)) - 1) < 0.001
   assert abs(sin(dtor(90)) - 1) < 0.001
   assert abs(cos(dtor(90)) - 0) < 0.001
   assert abs(cos(dtor(45)) - sqrt(2)/2) < 0.001
   assert 0 < rand() and rand() < 1
   assert mod(5, 2) == 1

   local stringval
   stringval = '1e5'
   assert val(stringval) = 100000
   assert vartype(num_value) == 'N'
   assert not ((.t. or .t.) and .f.)
   assert .t. or .f. and .t.
endproc

procedure string_tests
   cString = "AAA  aaa, BBB bbb, CCC ccc."
   assert vartype(cString) == 'C'
   assert GetWordCount(cString) == 6
   assert GetWordCount(cString, ",") = 3
   ASSERT GetWordCount(cString, ".") == 1
   assert GetWordNUM(cString, 2) == 'aaa,'
   assert GetWordNum(cString, 2, ",") = ' BBB bbb'
   ASSERT GETWORDNUM(cString, 2, ".") == ''
   assert like('Ab*t.???', 'About.txt')
   assert not like('Ab*t.???', 'about.txt')
   assert not isalpha('')
   assert isalpha('a123')
   assert not isalpha('1abc')
   assert not islower('')
   assert islower('test')
   assert not islower('Test')
   assert not isdigit('')
   assert isdigit('1abc')
   assert not isdigit('a123')
   assert not ISUPPER('')
   assert ISUPPER('Test')
   assert not ISUPPER('test')
   assert isblank('')
   assert not isblank('test')
   assert isblank({ / / })
   cString = ' AAA   '
   assert alltrim(cString) = 'AAA'
   assert rtrim(cString) = ' AAA'
   assert ltrim(cString) = 'AAA   '
   assert trim(cString) = rtrim(cString)
   assert strextract('This {{is}} a {{template}}', '{{', '}}') == 'is'
   assert strextract('This {{is}} a {{template}}', '{{', '}}', 2) == 'template'
   assert strextract('This {{is}} a {{template}}', '{{is}}') ==  ' a {{template}}'
   assert strextract('This {{is}} a {{template}}', '{{IS}}', '', 1, 1) ==  ' a {{template}}'
   assert atc('aab', '123AAbbB') == 4
   TEXT TO CSTRING NOSHOW
      123AAbbbB
      TESTTEST
      TEXTLINES
   ENDTEXT
   assert cstring == '123AAbbbBTESTTESTTEXTLINES'
   cstring = '123AAbbbB' + CHR(13) + CHR(10) + 'TESTTEST' + CHR(13) + CHR(10) + 'TEXTLINES'
   assert atline('T', cstring) == 2
   assert ratline('T', cstring) == 3
ENDPROC

procedure path_tests
   assert HOME() == curdir()
   handle = fcreate('test_lib_file')
   fclose(handle)
   assert not isblank(locfile('test_lib_file'))
   CD ..
   assert HOME() != curdir()
   assert not isblank(locfile('test_lib_file'))
   delete file ADDBS(HOME()) + 'test_lib_file'
endproc

procedure misc_tests
   assert version() == 'Not FoxPro 9'
   assert version(4) == version()
   assert version(5) == 900
endproc

procedure _add_db_record(seed)
   LOCAL fake, fake_name, fake_st, fake_quantity, fake_received
   fake = pythonfunctioncall('faker', 'Faker', createobject('pythontuple'))
   fake.callmethod('seed', createobject('pythontuple', seed))
   fake_name = fake.callmethod('name', createobject('pythontuple'))
   fake_st = fake.callmethod('state_abbr', createobject('pythontuple'))
   fake_quantity = fake.callmethod('random_int', createobject('pythontuple', 0, 100))
   fake_received = fake.callmethod('boolean', createobject('pythontuple'))
   insert into report values (fake_name, fake_st, fake_quantity, fake_received)
endproc

procedure _sqlexec_add_record(sqlconn, seed)
   LOCAL fake, fake_name, fake_st, fake_quantity, fake_received
   fake = pythonfunctioncall('faker', 'Faker', createobject('pythontuple'))
   fake.callmethod('seed', createobject('pythontuple', seed))
   fake_name = fake.callmethod('name', createobject('pythontuple'))
   fake_st = fake.callmethod('state_abbr', createobject('pythontuple'))
   fake_quantity = fake.callmethod('random_int', createobject('pythontuple', 0, 100))
   fake_received = fake.callmethod('boolean', createobject('pythontuple'))
   sqlcmd = "insert into REPORT values ('" + fake_name + "','" + fake_st + "'," + alltrim(str(fake_quantity)) + ',' + alltrim(str(cast(fake_received as int))) + ')'
   ?sqlcmd
   return sqlexec(sqlconn, sqlcmd)
endproc

procedure database_tests
   SET SAFETY OFF
   SET ASSERTS ON
   try
      CREATE TABLE REPORT FREE (NAME C(50), ST C(2), QUANTITY N(5, 0), RECEIVED L(1))
      ASSERT FILE('report.dbf')
      ASSERT USED('report')
      try
         USE report in 0 shared
         assert .f.
      catch to oerr
         ?oerr.message
         assert oerr.message == 'File is in use.'
      endtry
      _add_db_record(0)
      _add_db_record(1)
      _add_db_record(2)
      _add_db_record(3)
      assert cpdbf() = 0
      ASSERT FCOUNT() == 4
      ALTER TABLE REPORT ADD COLUMN AGE N(3, 0)
      ASSERT FCOUNT() == 5
      assert field(2) == 'st'
      assert not found()
      go top
      local loopcount
      loopcount = 0
      scan
         assert len(alltrim(name)) > 0
         loopcount = loopcount + 1
      endscan
      assert loopcount == 4
      go 3
      loopcount = 0
      scan all for alltrim(st) = 'ID'
         assert len(alltrim(name)) > 0
         loopcount = loopcount + 1
      endscan
      assert loopcount == 2
      loopcount = 0
      scan rest for alltrim(st) = 'ID'
         assert len(alltrim(name)) > 0
         loopcount = loopcount + 1
      endscan
      assert loopcount == 0
      go top
      loopcount = 0
      scan for alltrim(st) = 'ID'
         assert len(alltrim(name)) > 0
         loopcount = loopcount + 1
      endscan
      assert loopcount == 2
      release loopcount
      assert alltrim(name) == 'Norma Fisher' MESSAGE alltrim(name) + ' should be Norma Fisher'
      assert recno() == 1
      scatter name report_record
      assert alltrim(report_record.name) == 'Norma Fisher' MESSAGE alltrim(report_record.name) + ' should be Norma Fisher'
      go bott
      assert alltrim(name) == 'Joshua Wood' MESSAGE alltrim(name) + ' should be Joshua Wood'
      assert alltrim(report_record.name) == 'Norma Fisher' MESSAGE alltrim(report_record.name) + ' should be Norma Fisher'
      assert recno() == 4
      goto 1
      locate for st == 'ID'
      assert alltrim(name) == 'Norma Fisher' MESSAGE alltrim(name) + ' should be Norma Fisher'
      assert found()
      continue
      assert alltrim(name) == 'Ryan Gallagher' MESSAGE alltrim(name) + ' should be Ryan Gallagher'
      continue
      assert EOF()
      assert recno() == reccount() + 1
      assert not found()
      count for quantity > 60 to countval
      assert countval = 2
      assert eof()
      sum sqrt(quantity + 205) for quantity > 50 while quantity != 63 to sumval
      assert sumval == 0
      go top
      sum sqrt(quantity + 205) for quantity > 50 while quantity != 63 to sumval
      assert sumval == 17 + 16
      index on st tag st
      seek 'CA'
      assert alltrim(st) == 'CA'
      go top
      DELETE REST FOR QUANTITY > 60
      PACK
      goto top
      assert reccount() == 2
      REPLACE REPORT.NAME WITH 'N/A'
      assert alltrim(name) == 'N/A'
      REPLACE ALL NAME WITH 'Not Available'
      assert recno() == reccount() + 1
      GO BOTT
      assert alltrim(name) == 'Not Available'
      ZAP
      ASSERT RECCOUNT() == 0
      copy structure to report2
      USE report2 in 0 shared alias somethingelse
      assert alias() == 'report'
      SELECT report2
      assert alias() == 'somethingelse'
      ASSERT FCOUNT() == 5
      ALTER TABLE REPORT2 DROP COLUMN ST
      ASSERT FCOUNT() == 4
      assert alltrim(report_record.name) == 'Norma Fisher' MESSAGE alltrim(report_record.name) + ' should be Norma Fisher'
      append blank
      gather from report_record
      assert alltrim(name) == 'Norma Fisher' MESSAGE alltrim(name) + ' should be Norma Fisher'
      assert dbf() == 'report2.dbf'
      use in select('report2')
      use in select('report')
      DELETE FILE REPORT2.DBF
   catch to err
      ?err.message
      browse
      throw
   finally
      DELETE FILE REPORT.DBF
   endtry
   sqlconn = sqlconnect('testodbc')
   assert sqlconn > 0
   assert sqlexec(sqlconn, 'CREATE TABLE REPORT (NAME varchar(50), ST char(2), QUANTITY int(5), RECEIVED bit)') > 0
   assert _sqlexec_add_record(sqlconn, 0) > 0
   assert _sqlexec_add_record(sqlconn, 1) > 0
   assert _sqlexec_add_record(sqlconn, 2) > 0
   assert _sqlexec_add_record(sqlconn, 3) > 0
   assert sqlexec(sqlconn, 'SELECT * FROM REPORT')
   select sqlresult
   assert alltrim(name) == 'Norma Fisher'
   sqlcommit(sqlconn)
   sqldisconnect(sqlconn)
   sqlconn = sqlstringconnect('dsn=testodbc')
   assert sqlconn > 0
   assert sqltables(sqlconn) > 0
   select sqlresult
   assert lower(alltrim(table_name)) == 'report'
   assert sqlexec(sqlconn, 'DELETE FROM REPORT;')
   assert sqlrollback(sqlconn)
   assert sqlexec(sqlconn, 'SELECT * FROM REPORT')
   select sqlresult
   assert alltrim(name) == 'Norma Fisher'
   assert sqlexec(sqlconn, 'DROP TABLE REPORT') > 0
   sqlcommit(sqlconn)
   sqldisconnect(sqlconn)
   close tables
endproc

procedure user_defined_function(arg1, arg2)
   assert pcount() == 1
   assert parameters() == 1
   user_defined_function2()
   assert parameters() == 0
   assert pcount() == 1
endproc

procedure user_defined_function2(arg1)
endproc

procedure scope_tests
   PUBLIC ARRAY somearray[2, 5]
   public array def[10]
   assert def[1] == .F.
   SOMEARRAY(1, 4) = 3
   assert somearray[1, 4] == 3
   PRIVATE TEST, somearray[2, 5]
   RELEASE nonexistantvariable

   set procedure to time
   ?localtime()

   set procedure to argparse
   t = createobject('namespace')

   user_defined_function(.F.)
ENDPROC

define class someclass as custom
enddefine

procedure class_tests
   obj = createobject('someclass')
endproc
