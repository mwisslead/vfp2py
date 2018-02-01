# vfp2py
vfp2py is an attempt to create a tool to automatically create python code from
foxpro 9 code.

Many but not nearly all commands are currently supported with missing commands
to be added as need arises. Conversion can be done on individual prg files or
whole projects pjx files.

## Features
- Translates code comments
- Handles preprocessor commands
- Support for reading and writing dbf files via Ethan Furman's dbf package
- Many functions are inlined in the generated python code.
- Many complex functions and commands are available through a runtime - vfpfunc.py
- Somewhat functioning gui using PySide

## Future work
- Improve gui
- Rework scoping to facilitate operation of some commands.
- Add missing code conversion for some commands currently supported by parser
- Add more runtime functions
- Put package on pypi for easier install

## Installation
`python setup.py install`

## Usage
```
    $ python -m vfp2py --help
    usage: __main__.py [-h] [--logging] infile outfile [search [search ...]]
    
    Tool for rewriting Foxpro code in Python
    
    positional arguments:
      infile      file to convert
      outfile     file to output to
      search      directories to search for included files
    
    optional arguments:
      -h, --help  show this help message and exit
      --logging   file to convert`
```

To convert a file simply run `python -m vfp2py --logging input_file.prg output_file.py`
