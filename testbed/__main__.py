from __future__ import print_function

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
    return "'''{}'''".format(string.replace('\\', '\\\\').replace('\'', '\\\''))


class TestsGenVisitor(conversionVisitor):
    '''Visitor that extracts conversion sections'''

    def visitConversionTests(self, ctx):
        return [self.visit(test) for test in ctx.conversionTest()]

    def visitConversionTest(self, ctx):
        foxlines = ''.join(tok.symbol.text for tok in ctx.FoxLine())
        pylines = ''.join(tok.symbol.text for tok in ctx.PyLine())
        return foxlines, pylines


def generate_tests(filename):
    with open(filename) as fid:
        file_contents = fid.read().decode('utf-8')
    input_stream = antlr4.InputStream(file_contents)
    lexer = conversionLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = conversion(stream)
    tree = parser.conversionTests()
    visitor = TestsGenVisitor()
    tests = visitor.visit(tree)
    t = ['from __future__ import print_function',
         '',
         'import difflib',
         '',
         'import vfp2py',
         '', 
         '',
         'CMP = difflib.Differ().compare',
    ]
    for i, test in enumerate(tests):
        t += ['', '', 'def Test{}():'.format(i)]
        func_body = []
        func_body.append('input_str = {}'.format(docstring(test[0])))
        func_body.append('output_str = {}'.format(docstring(test[1])))
        func_body.append('test_output_str = vfp2py.vfp2py.prg2py(input_str)')
        func_body.append('try:')
        func_body.append(['assert test_output_str == output_str'])
        func_body.append('except AssertionError:')
        except_block = []
        except_block.append('diff = CMP(test_output_str.splitlines(1), output_str.splitlines(1))')
        except_block.append('print(\'\'.join(diff))')
        except_block.append('raise')
        func_body.append(except_block)
        t.append(func_body)

    
    return add_indent(t, 0)


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
