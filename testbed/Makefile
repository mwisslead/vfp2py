AntlrJar=../antlr-4.7-complete.jar

Antlr=java -jar ${AntlrJar}
PyVer=$(shell python -c 'import sys; print(sys.version_info[0])')

all: build conversion.vfp2py

build: conversionLexer.py conversion.py conversionVisitor.py test_conversion.py

test_conversion.py: conversion.vfp2py
	python -m testbed conversion.vfp2py > test_conversion.py

%Lexer.py: %Lexer.g4
	${Antlr} -Dlanguage=Python${PyVer} $^

%.py: %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python${PyVer} $^

clean:
	rm -rf conversion*.py *.tokens *.pyc __pycache__ test_conversion.py
