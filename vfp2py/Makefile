test: VisualFoxpro9Lexer.py VisualFoxpro9Parser.py VisualFoxpro9Visitor.py vfp2py.py vfpfunc.py

%Lexer.py %Parser.py %Visitor.py: %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python${PyVer} $^

clean:
	rm -rf VisualFoxpro9*.py *.tokens *.pyc __pycache__
