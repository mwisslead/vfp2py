AntlrJar=antlr-4.11.1-complete.jar
Antlr=java -jar $(shell realpath $(AntlrJar))
PyVer=$(shell python -c 'import sys; print(sys.version_info[0])')

all: ${AntlrJar} vfp2py.egg-info
	make -C vfp2py Antlr="${Antlr}" PyVer=${PyVer}
	make -C testbed Antlr="${Antlr}" PyVer=${PyVer}
	python setup.py test

vfp2py.egg-info:
	python setup.py develop

antlr%.jar:
	wget http://www.antlr.org/download/$@

install-vim-syntax: extras/vfp2py.vim
	mkdir -p ~/.vim/syntax
	cp $^ ~/.vim/syntax

clean:
	rm -rf ${AntlrJar} vfp2py.egg-info
	make -C vfp2py clean
	make -C testbed clean
