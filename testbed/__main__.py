# coding=utf-8
from __future__ import absolute_import, division, print_function

import argparse

import antlr4

from conversion import *
from conversionLexer import *
from conversionVisitor import *


def add_indent(code, level):
    retval = ''
    for line in code:
        if isinstance(line, list):
            retval += add_indent(line, level+1)
        else:
            retval += '    '*level + line + '\n'
    return retval


def docstring(string):
    return "'''\n{}'''".format(string.replace('\\', '\\\\').replace('\'', '\\\''))


class TestsGenVisitor(conversionVisitor):
    '''Visitor that extracts conversion sections'''

    def visitConversionTests(self, ctx):
        t = '''
!       from __future__ import print_function
!       
!       import difflib
!       
!       import vfp2py
        '''.split('!       ')[1:]
        for i, test in enumerate(ctx.conversionTest()):
            foxlines, pylines = self.visit(test)
            test_func = '''
!           
!           
!           def Test{}():
!               input_str = {}.strip()
!               output_str = {}.strip()
!               test_output_str = {}.strip()
!               try:
!                   assert test_output_str == output_str
!               except AssertionError:
!                   diff = difflib.unified_diff((test_output_str + '\\n').splitlines(1), (output_str + '\\n').splitlines(1))
!                   print(''.join(diff))
!                   raise
            '''
            special_directive = str(test.FoxStart().symbol.text[13:].strip())
            if special_directive:
                test_output = 'vfp2py.vfp2py.prg2py(input_str, \'cp1252\', parser_start={}, prepend_data=\'\')'.format(repr(special_directive))
            else:
                test_output = 'vfp2py.vfp2py.prg2py(input_str, \'cp1252\')'
            test_func = test_func.format(i, docstring(foxlines), docstring(pylines), test_output)
            t += test_func.split('!           ')[1:]

        t = [l.rstrip() for l in t]

        return add_indent(t, 0)


    def visitConversionTest(self, ctx):
        foxlines = ''.join(tok.symbol.text for tok in ctx.FoxLine())
        pylines = ''.join(tok.symbol.text for tok in ctx.PyLine())
        return foxlines, pylines


def generate_tests(filename):
    with open(filename, 'rb') as fid:
        file_contents = fid.read().decode('utf-8')
    input_stream = antlr4.InputStream(file_contents)
    lexer = conversionLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = conversion(stream)
    tree = parser.conversionTests()
    visitor = TestsGenVisitor()
    return visitor.visit(tree)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Tool for generating vfp to python conversion tests from conversion file')
    parser.add_argument("infile", help="file of conversions", type=str)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    print(generate_tests(args.infile))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
