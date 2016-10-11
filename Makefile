Antlr=java -jar ~/antlr-4.5.3-complete.jar
#Antlr=antlr4

test: vfp2py/VisualFoxpro9Lexer.py vfp2py/VisualFoxpro9Parser.py vfp2py/VisualFoxpro9Visitor.py
	python -m vfp2py test.prg test.py

%Lexer.py %Parser.py %Visitor.py: %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python2 $^
	sed -i'' 's/_tokenStartCharPositionInLine/self._tokenStartColumn/g' $*Lexer.py
	sed -i'' 's/\(\s\)_input\./\1self._input./g' $*Parser.py

clean:
	rm vfp2py/VisualFoxpro9*.py vfp2py/*.tokens vfp2py/*.pyc
