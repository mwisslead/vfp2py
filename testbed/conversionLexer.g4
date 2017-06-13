lexer grammar conversionLexer;

FoxStart: '@begin=vfp@' ('&&' [A-Za-z_0-9]*)? '\r'? '\n' -> pushMode(Fox);
PyStart: '@begin=python@' '\r'? '\n' -> pushMode(Py);
Line: .*? '\r'? '\n' -> skip;

mode Fox;
FoxEnd: '@end=vfp@' '\r'? '\n' -> popMode;
FoxLine: .*? '\r'? '\n';

mode Py;
PyEnd: '@end=python@' '\r'? '\n' -> popMode;
PyLine: .*? '\r'? '\n';
