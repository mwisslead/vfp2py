AntlrJar=antlr-4.7-complete.jar
Antlr=java -jar $(shell realpath $(AntlrJar))
PyVer=$(shell python -c 'import sys; print(sys.version_info[0])')

all: ${AntlrJar}
	make -C vfp2py Antlr="${Antlr}" PyVer=${PyVer}
	make -C testbed Antlr="${Antlr}" PyVer=${PyVer}
	nosetests

antlr%.jar:
	wget http://www.antlr.org/download/$@

clean:
	make -C vfp2py clean
	make -C testbed clean
