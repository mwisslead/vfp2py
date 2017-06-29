all: conversion.vfp2py conversionLexer.py conversion.py conversionVisitor.py conversionLexer.g4 conversion.g4 test_conversion.py test_lib.py

test_conversion.py: __main__.py conversion.vfp2py
	python __main__.py conversion.vfp2py > $@

test_lib.py: test_lib.prg
	python -m vfp2py test_lib.prg test_lib.py

.DELETE_ON_ERROR:

%Lexer.py: %Lexer.g4
	${Antlr} -Dlanguage=Python${PyVer} $^

%.py: %Lexer.g4 %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python${PyVer} $^

clean:
	rm -rf conversion*.py *.tokens *.pyc __pycache__ test_conversion.py test_lib.py
