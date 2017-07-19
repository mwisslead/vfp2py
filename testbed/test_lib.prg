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
   assert dow(somedate) == 6
   assert cdow(somedate) == 'Friday'
endproc

procedure math_tests
   assert round(pi(), 2) == 3.14
   assert abs(tan(dtor(45)) - 1) < 0.001
   assert abs(sin(dtor(90)) - 1) < 0.001
   assert abs(cos(dtor(90)) - 0) < 0.001
   assert abs(cos(dtor(45)) - sqrt(2)/2) < 0.001
endproc

procedure string_tests
   cString = "AAA  aaa, BBB bbb, CCC ccc."
   assert GetWordCount(cString) == 6
   assert GetWordCount(cString, ",") = 3
   ASSERT GetWordCount(cString, ".") == 1
   assert GetWordNUM(cString, 2) == 'aaa,'
   assert GetWordNum(cString, 2, ",") = ' BBB bbb'
   ASSERT GETWORDNUM(cString, 2, ".") == ''
ENDPROC

procedure path_tests
   assert HOME() == curdir()
   CD ..
   assert HOME() != curdir()
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

procedure database_tests
   try
      CREATE TABLE REPORT FREE (NAME C(50), ST C(2), QUANTITY N(5, 0), RECEIVED L(1))
      ASSERT FILE('report.dbf')
      ASSERT USED('report')
      _add_db_record(0)
      _add_db_record(1)
      _add_db_record(2)
      _add_db_record(3)
      go top
      assert alltrim(name) == 'Norma Fisher' MESSAGE alltrim(name) + ' should be Norma Fisher'
      go bott
      assert alltrim(name) == 'Joshua Wood' MESSAGE alltrim(name) + ' should be Joshua Wood'
      goto 1
      assert alltrim(name) == 'Norma Fisher' MESSAGE alltrim(name) + ' should be Norma Fisher'
      count for quantity > 60 to countval
      assert countval = 2
      sum sqrt(quantity + 205) for quantity > 50 while quantity != 63 to sumval
      assert sumval == 17 + 16
      DELETE REST FOR QUANTITY > 60
      PACK
      go top
      assert reccount() == 2
      REPLACE REPORT.NAME WITH 'N/A'
      assert alltrim(name) == 'N/A'
      REPLACE ALL NAME WITH 'Not Available'
      assert alltrim(name) == 'Not Available'
   catch to err
      ?err.message
      browse
      throw
   finally
      DELETE FILE REPORT.DBF
   endtry
endproc
