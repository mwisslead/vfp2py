AntlrJar=../antlr-4.7-complete.jar

Antlr=java -jar ${AntlrJar}
PyVer=$(shell python -c 'import sys; print(sys.version_info[0])')

all: conversion.vfp2py conversionLexer.py conversion.py conversionVisitor.py test_conversion.py conversionLexer.g4 conversion.g4

test_conversion.py: __main__.py conversion.vfp2py
	python -m testbed conversion.vfp2py > test_conversion.py

%Lexer.py: %Lexer.g4
	${Antlr} -Dlanguage=Python${PyVer} $^

%.py: %Lexer.g4 %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python${PyVer} $^

clean:
	rm -rf conversion*.py *.tokens *.pyc __pycache__ test_conversion.py
