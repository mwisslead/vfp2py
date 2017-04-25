AntlrJar=antlr-4.7-complete.jar

Antlr=java -jar ${AntlrJar}
PyVer=$(shell python -c 'import sys; print(sys.version_info[0])')

test: ${AntlrJar} vfp2py/VisualFoxpro9Lexer.py vfp2py/VisualFoxpro9Parser.py vfp2py/VisualFoxpro9Visitor.py
	python -m vfp2py test.prg test.py

%Lexer.py %Parser.py %Visitor.py: %.g4
	${Antlr} -visitor -no-listener -Dlanguage=Python${PyVer} $^
	sed -i'' 's/_tokenStartCharPositionInLine/self._tokenStartColumn/g' $*Lexer.py
	sed -i'' 's/\(\s\)_input\./\1self._input./g' $*Parser.py

antlr%.jar:
	wget http://www.antlr.org/download/$@

clean:
	rm -rf vfp2py/VisualFoxpro9*.py vfp2py/*.tokens vfp2py/*.pyc vfp2py/__pycache__
