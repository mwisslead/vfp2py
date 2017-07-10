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
