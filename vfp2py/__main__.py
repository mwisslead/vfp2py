from __future__ import print_function

import sys
import os
import ntpath
import time
import datetime as dt
import re
import tempfile
from collections import OrderedDict
import shutil

import argparse

import random
import string

import dbf

import antlr4
import autopep8

from vfp2py import *

STDLIBS = ['import sys', 'import os', 'import math', 'import datetime as dt', 'import subprocess']
SEARCH_PATH = ['.']

if sys.version_info >= (3,):
    unicode=str

def import_key(module):
    if module in STDLIBS:
        return STDLIBS.index(module)
    else:
        return len(STDLIBS)

def which(filename):
    '''find file on path'''
    for path in SEARCH_PATH:
        testpath = os.path.join(path, filename)
        if os.path.isfile(testpath):
            return testpath
    return filename

def random_variable(length=10):
    return '_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

class Tic():
    def __init__(self):
        self.start = time.time()

    def tic(self):
        self.start = time.time()

    def toc(self):
        return time.time()-self.start

class CodeStr(unicode):
    def __repr__(self):
        return unicode(self)

    def __add__(self, val):
        return CodeStr('{} + {}'.format(self, repr(val)))

    def __sub__(self, val):
        return CodeStr('{} - {}'.format(self, repr(val)))

class PreprocessVisitor(VisualFoxpro9Visitor):
    def __init__(self):
        self.tokens = None
        self.memory = {}

    def visitPreprocessorCode(self, ctx):
        retval = []
        for child in ctx.getChildren():
            toks = self.visit(child)
            if toks:
                retval += toks
            elif toks is None:
                print('toks was None')
        return retval

    def visitPreprocessorDefine(self, ctx):
        name = ctx.identifier().getText().lower()
        namestart, _ = ctx.identifier().getSourceInterval()
        _, stop = ctx.getSourceInterval()
        tokens = ctx.parser._input.tokens[namestart+1:stop]
        while len(tokens) > 0 and tokens[0].type == ctx.parser.WS:
            tokens.pop(0)
        self.memory[name] = tokens
        return []

    def visitPreprocessorUndefine(self, ctx):
        name = ctx.identifier().getText().lower()
        self.memory.pop(name)
        return []

    def visitPreprocessorInclude(self, ctx):
        visitor = PythonConvertVisitor('')
        visitor.scope = {}
        filename = visitor.visit(ctx.specialExpr())
        if isinstance(filename, CodeStr):
            filename = eval(filename)
        filename = which(filename)
        include_visitor = preprocess_file(filename)
        self.memory.update(include_visitor.memory)
        return include_visitor.tokens

    def visitPreprocessorIf(self, ctx):
        if ctx.IF():
            visitor = PythonConvertVisitor('')
            visitor.scope = {}
            ifexpr = eval(repr(visitor.visit(ctx.expr())))
        else:
            name = ctx.identifier().getText().lower()
            ifexpr = name in self.memory
        if ifexpr:
            return self.visit(ctx.ifBody)
        elif ctx.ELSE():
            return self.visit(ctx.elseBody)
        else:
            return []

    def visitNonpreprocessorLine(self, ctx):
        start, stop = ctx.getSourceInterval()
        hidden_tokens = ctx.parser._input.getHiddenTokensToLeft(start)
        retval = []
        process_tokens = (hidden_tokens if hidden_tokens else []) + ctx.parser._input.tokens[start:stop+1]
        hidden_tokens = []
        for tok in process_tokens:
            if tok.text.lower() in self.memory:
                retval += self.memory[tok.text.lower()]
            else:
                if tok.type == ctx.parser.COMMENT:
                    tok.text = '*' + tok.text[2:] + '\n'
                    hidden_tokens.append(tok)
                    continue
                elif tok.type == ctx.parser.LINECOMMENT:
                    if tok.text.strip():
                        tok.text = re.sub(r';[ \t]*\r*\n', '\n', tok.text.strip())
                        lines = tok.text.split('\n')
                        lines = [re.sub(r'^\s*\*?', '*', line) + '\n' for line in lines]
                        tok.text = ''.join(lines)
                retval.append(tok)
        return hidden_tokens + retval

def add_indents(struct, num_indents):
    retval = []
    for item in struct:
        if isinstance(item, list):
            retval.append(add_indents(item, num_indents+1))
        elif item:
            retval.append(' '*4*num_indents + repr(item))
        else:
            retval.append('')
    return '\n'.join(retval)

def get_list(should_be_list):
    try:
        return list(should_be_list)
    except TypeError:
        return [should_be_list]

class PythonConvertVisitor(VisualFoxpro9Visitor):
    def __init__(self, filename):
        super(PythonConvertVisitor, self).__init__()
        self.vfpclassnames = {'custom': 'vfpfunc.Custom',
                              'form': 'vfpfunc.Form',
                              'label': 'vfpfunc.Label',
                              'textbox': 'vfpfunc.Textbox',
                              'checkbox': 'vfpfunc.Checkbox',
                              'combobox': 'vfpfunc.Combobox',
                              'spinner': 'vfpfunc.Spinner',
                              'shape': 'vfpfunc.Shape',
                              'commandbutton': 'vfpfunc.CommandButton'
                             }
        self.filename = filename
        self.imports = []
        self.scope = None
        self._saved_scope = None
        self._scope_count = 0
        self.withid = ''
        self.class_list = []
        self.function_list = []
        self.used_scope = False

    @staticmethod
    def make_func_code(funcname, *args, **kwargs):
        args = [repr(x) for x in args]
        args += ['{}={}'.format(key, repr(kwargs[key])) for key in kwargs]
        return CodeStr('{}({})'.format(funcname, ', '.join(args)))

    @staticmethod
    def to_int(expr):
        try:
            return int(expr)
        except:
            return PythonConvertVisitor.make_func_code('int', expr)

    @staticmethod
    def string_type(val):
        return isinstance(val, (str, unicode)) and not isinstance(val, CodeStr)

    @staticmethod
    def create_string(val):
        try:
            return str(val)
        except UnicodeEncodeError: #can this happen?
            return val

    @staticmethod
    def add_args_to_code(codestr, args):
        return CodeStr(codestr.format(*[repr(arg) for arg in args]))

    def enable_scope(self, enabled):
        self._scope_count = max(self._scope_count + 1 - 2*int(enabled), 0)
        if enabled and self._scope_count == 0:
            if self._saved_scope:
                self.scope = self._saved_scope
            else:
                self.new_scope()
            self.scope
        else:
            if self.scope:
                self._saved_scope = self.scope
            self.scope = None

    def new_scope(self):
        self._scope_count = 0
        self.scope = {}

    def delete_scope(self):
        self._scope_count = 0
        self.scope = None

    def has_scope(self):
        return self.scope is not None

    def getCtxText(self, ctx):
        return ''.join(t.text for t in ctx.parser._input.tokens[start:stop+1])

    def visitPrg(self, ctx):
        if ctx.classDef():
            self.class_list = [self.visit(classDef.classDefStart().identifier()[0]) for classDef in ctx.classDef()]
        if ctx.funcDef():
            self.function_list = [self.visit(funcdef.funcDefStart().idAttr2()) for funcdef in ctx.funcDef()]

        self.imports = []
        defs = []

        for child in ctx.children:
            if isinstance(child, VisualFoxpro9Parser.FuncDefContext):
                self.used_scope = False
                funcname, parameters, funcbody = self.visit(child)
                defs += [CodeStr('def {}({}):'.format(funcname, ', '.join([str(repr(p)) + '=False' for p in parameters]))), funcbody]
            else:
                defs += self.visit(child)

        self.imports = sorted(set(self.imports), key=import_key)
        imports = []
        for n, module in enumerate(self.imports):
            if n != 0 and module not in STDLIBS:
                imports.append('')
            imports.append(module)

        imports.insert(0, '')
        imports.insert(0, 'from __future__ import division, print_function')
        return  [CodeStr(imp) for imp in imports] + defs

    def visitLine(self, ctx):
        retval = self.visitChildren(ctx)
        if retval is None:
            start, stop = ctx.getSourceInterval()
            lines = ''.join(t.text for t in ctx.parser._input.tokens[start:stop+1])
            print(lines, file=sys.stderr)
            retval = [CodeStr('#FIX ME: {}'.format(line)) for line in lines.split('\n') if line]
        return retval if isinstance(retval, list) else [retval]

    andfix = re.compile('^&&')
    frontfix = re.compile('^\**')
    endfix = re.compile('\**$')

    def visitLineComment(self, ctx):
        repl = lambda x: '#' * len(x.group())
        comment = ctx.getText().split('\n')[0].strip()
        if len(comment) == 0:
            return ''
        comment = self.andfix.sub('', comment)
        comment = self.frontfix.sub(repl, comment)
        return [CodeStr(self.endfix.sub(repl, comment))]

    def visitCmdStmt(self, ctx):
        return self.visit(ctx.cmd()) if ctx.cmd() else self.visit(ctx.setup())

    def visitLines(self, ctx):
        retval = sum((self.visit(line) for line in ctx.line()), [])
        def badline(line):
            return line.startswith('#') or not line if hasattr(line, 'startswith') else not line
        if not retval or all(badline(l) for l in retval):
            retval.append(CodeStr('pass'))
        return retval

    def visitClassDef(self, ctx):
        assignments = []
        self.used_scope = False
        for stmt in ctx.classDefProperty():
            assignment = self.visit(stmt)
            if isinstance(stmt, VisualFoxpro9Parser.ClassDefLineCommentContext) and assignment:
                assignments.append(assignment)
            else:
                assignments += assignment
        assign_scope = self.used_scope

        comments = []
        for comment in ctx.lineComment():
            comments.append(self.visit(comment) + [comment.start.line])

        funcs = OrderedDict()
        for funcdef in ctx.funcDef():
            self.used_scope = False
            funcname, parameters, funcbody = self.visit(funcdef)
            if funcname == 'init' and assign_scope and not self.used_scope:
                self.used_scope = True
                funcname, parameters, funcbody = self.visit(funcdef)
            parameters = [CodeStr('self')] + parameters
            if '.' in funcname:
                newfuncname = funcname.replace('.', '_')
                assignments.append(CodeStr('def {}({}):'.format(newfuncname, ', '.join(parameters))))
                assignments.append(funcbody)
                assignments.append(CodeStr('self.{} = {}'.format(funcname, newfuncname)))
            else:
                funcs.update({funcname: [parameters, funcbody, funcdef.start.line]})

        if assignments and 'init' not in funcs:
            funcs['init'] = [[CodeStr('self')], [], float('inf')]

        funcbody = funcs['init'][1]
        if funcbody:
            funcs['init'][1] = [funcbody[0]] + assignments + funcbody[1:]
        else:
            self.used_scope = assign_scope
            funcs['init'][1] = self.modify_func_body(assignments)

        classname, supername = self.visit(ctx.classDefStart())
        retval = [CodeStr('class {}({}):'.format(classname, supername))]
        for funcname in funcs:
            parameters, funcbody, line_number = funcs[funcname]
            while comments and comments[0][1] < line_number:
                retval.append([comments.pop(0)[0]])
            retval.append([CodeStr('def {}({}):'.format(funcname, ', '.join([str(repr(p)) + '=False' for p in parameters]))), funcbody])
        while comments:
            retval.append([comments.pop(0)[0]])

        return retval

    def visitClassDefStart(self, ctx):
        names = [self.visit(identifier) for identifier in ctx.identifier()]
        classname = names[0]
        if classname in self.vfpclassnames:
            raise Exception(classname + ' is a reserved classname')
        supername = names[1] if len(names) > 0 else 'custom'
        if supername in self.vfpclassnames:
            self.imports.append('from vfp2py import vfpfunc')
            supername = self.vfpclassnames[supername]
        return classname, supername

    def visitClassDefAssign(self, ctx):
        #FIXME - come up with a less hacky way to make this work
        self.enable_scope(False)
        args1 = self.visit(ctx.assign())
        self.enable_scope(True)
        used_scope = self.used_scope
        args2 = self.visit(ctx.assign())
        args = []
        for arg1, arg2 in zip(args1, args2):
            ident = arg1[:arg1.find(' = ')]
            value = arg2[arg2.find(' = '):]
            if 'vfpfunc.variable' in value or 'vfpfunc.function' in value:
                used_scope = True
            args.append(ident + value)
        self.used_scope = used_scope
        return [CodeStr('self.' + arg) for arg in args]

    def visitClassDefAddObject(self, ctx):
        self.enable_scope(False)
        name = self.visit(ctx.identifier())
        objtype = self.visit(ctx.idAttr()[0])
        if objtype in self.vfpclassnames:
            self.imports.append('from vfp2py import vfpfunc')
            objtype = CodeStr(self.vfpclassnames[objtype])
        keywords = [self.visit(idAttr) for idAttr in ctx.idAttr()[1:]]
        self.enable_scope(True)
        kwargs = {key: self.visit(expr) for key, expr in zip(keywords, ctx.expr())}
        funcname = self.add_args_to_code('self.{} = {}', (name, objtype))
        retval = [self.make_func_code(funcname, **kwargs)]
        retval.append(self.add_args_to_code('self.add_object(self.{})', [name]))
        return retval

    def visitNodefault(self, ctx):
        return []

    def visitFuncDefStart(self, ctx):
        self.enable_scope(False)
        params = self.visit(ctx.parameters()) if ctx.parameters() else []
        params += self.visit(ctx.parameterDef()) if ctx.parameterDef() else []
        self.enable_scope(True)
        return self.visit(ctx.idAttr2()), params

    def visitParameterDef(self, ctx):
        return self.visit(ctx.parameters())

    def visitParameter(self, ctx):
        return self.visit(ctx.idAttr()[0])

    def visitParameters(self, ctx):
        return [self.visit(parameter) for parameter in ctx.parameter()]

    def modify_func_body(self, body):
        while len(body) > 0 and (not body[-1] or (isinstance(body[-1], CodeStr) and (body[-1] == 'return'))):
            body.pop()
        if len(body) == 0:
            body.append(CodeStr('pass'))
        if not self.used_scope:
            return body
        while CodeStr('pass') in body:
            body.pop(body.index(CodeStr('pass')))
        def fix_returns(lines):
            newbody = []
            for line in lines:
                if isinstance(line, list):
                    newbody.append(fix_returns(line))
                elif isinstance(line, CodeStr) and line.startswith('return '):
                    return_value = CodeStr(line[7:])
                    if 'vfpfunc.variable[' in return_value or 'vfpfunc.function[' in return_value:
                        newbody.append(self.add_args_to_code('function_return_value = {}', [return_value]))
                        newbody.append(CodeStr('vfpfunc.popscope()'))
                        newbody.append(CodeStr('return function_return_value'))
                    else:
                        newbody.append(CodeStr('vfpfunc.popscope()'))
                        newbody.append(line)
                else:
                    newbody.append(line)
            return newbody
        body = [CodeStr('vfpfunc.pushscope()')] + fix_returns(body)
        if isinstance(body[-1], CodeStr) and body[-1].startswith('return '):
            return body
        body.append(CodeStr('vfpfunc.popscope()'))
        return body

    def visitFuncDef(self, ctx):
        name, parameters = self.visit(ctx.funcDefStart())
        self.new_scope()
        self.scope.update({key: False for key in parameters})
        body = self.visit(ctx.lines())
        self.delete_scope()
        body = self.modify_func_body(body)
        return name, parameters, body

    def visitPrintStmt(self, ctx):
        return [self.make_func_code('print', *(self.visit(ctx.args()) if ctx.args() else []))]

    def visitIfStart(self, ctx):
        return self.visit(ctx.expr())

    def visitIfStmt(self, ctx):
        evaluation = self.visit(ctx.ifStart())

        ifBlock = self.visit(ctx.ifBody)
        retval = [CodeStr('if {}:'.format(evaluation)), ifBlock]

        if ctx.elseBody:
            elseBlock = self.visit(ctx.elseBody)
            retval += [CodeStr('else:'), elseBlock]

        return retval

    def visitCaseStmt(self, ctx):
        n = 0
        retval = []
        for elem in ctx.caseElement():
            if elem.lineComment():
                retval += self.visit(elem.lineComment())
            else:
                expr, lines = self.visit(elem.singleCase())
                if n == 0:
                    retval += [CodeStr('if {}:'.format(expr)), lines]
                else:
                    retval += [CodeStr('elif {}:'.format(expr)), lines]
                n += 1
        if n == 0:
            retval += [CodeStr('if True:'), [CodeStr('pass')]]
        if ctx.otherwise():
            retval += [CodeStr('else:'), self.visit(ctx.otherwise())]
        return retval

    def visitSingleCase(self, ctx):
        return self.visit(ctx.caseExpr()), self.visit(ctx.lines())

    def visitCaseExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitOtherwise(self, ctx):
        return self.visit(ctx.lines())

    def visitForStart(self, ctx):
        self.enable_scope(False)
        loopvar = self.visit(ctx.idAttr())
        self.enable_scope(True)
        self.scope[loopvar] = False
        if ctx.EACH():
            iterator = self.visit(ctx.expr(0))
            return self.add_args_to_code('for {} in {}:', (loopvar, iterator))
        loop_start = self.to_int(self.visit(ctx.loopStart))
        loop_stop = self.to_int(self.visit(ctx.loopStop)) + 1
        if ctx.loopStep:
            loop_step = self.to_int(self.visit(ctx.loopStep))
            return CodeStr('for {} in range({}, {}, {}):'.format(loopvar, loop_start, loop_stop, loop_step))
        else:
            return CodeStr('for {} in range({}, {}):'.format(loopvar, loop_start, loop_stop))

    def visitForStmt(self, ctx):
        return [self.visit(ctx.forStart()), self.visit(ctx.lines())]

    def visitWhileStart(self, ctx):
        return CodeStr('while {}:'.format(self.visit(ctx.expr())))

    def visitWhileStmt(self, ctx):
        return [self.visit(ctx.whileStart()), self.visit(ctx.lines())]

    def visitWithStmt(self, ctx):
        self.withid = self.visit(ctx.idAttr())
        lines = self.visit(ctx.lines())
        self.withid = ''
        return lines

    def visitScanStmt(self, ctx):
        lines = self.visit(ctx.lines())
        lines.append(self.make_func_code('vfpfunc.db.skip', None, 1))
        if ctx.FOR():
            condition = self.visit(ctx.expr())
            lines = [self.add_args_to_code('if not {}:', [condition]), [CodeStr('continue')]] + lines
        save_variable_name = CodeStr(random_variable(length=10) + '_current_record')
        save_recno = CodeStr('{} = {}'.format(save_variable_name, 'vfpfunc.db.recno()'))
        return_recno = self.make_func_code('vfpfunc.db.goto', None, CodeStr(save_variable_name))
        return [save_recno, CodeStr('while not vfpfunc.db.eof():'), lines, return_recno]

    def visitBreakLoop(self, ctx):
        return CodeStr('break')

    def visitContinueLoop(self, ctx):
        return CodeStr('continue')

    def visitDeclaration(self, ctx):
        if ctx.ARRAY() or ctx.DIMENSION() or ctx.DEFINE():
            name = self.visit(ctx.identifier())
            value = self.visit(ctx.arrayIndex())
            if ctx.LOCAL():
                self.scope[name] = False
                array = self.make_func_code('vfpfunc.Array', *value)
                return [
                    self.add_args_to_code('{} = {}', [name, array])
                ]
            func = 'vfpfunc.array'
            kwargs = {'public': True} if ctx.PUBLIC() else {}
            self.used_scope = True
            return self.make_func_code(func, *([str(name)] + value), **kwargs)
        else:
            self.enable_scope(False)
            names = self.visit(ctx.parameters())
            self.enable_scope(True)
            if ctx.LOCAL():
                for name in names:
                    self.scope[name] = False
                return CodeStr(' = '.join([repr(arg) for arg in (names + [False])]) + ' #LOCAL Declaration')
            self.used_scope = True
            func = 'vfpfunc.variable.add_public' if ctx.PUBLIC() else 'vfpfunc.variable.add_private'
            return self.make_func_code(func, *[str(name) for name in names])

    def visitAssign(self, ctx):
        value = self.visit(ctx.expr())
        while isinstance(value, CodeStr):
            if not (value.startswith('(') and value.endswith(')')):
                break
            value = CodeStr(value[1:-1])
        args = []
        for var in ctx.idAttr():
            trailer = self.visit(var.trailer()) if var.trailer() else []
            if len(trailer) > 0 and isinstance(trailer[-1], list):
                identifier = self.visit(ctx.idAttr()[0].identifier())
                arg = self.createIdAttr(identifier, trailer[:-1] + [[]])
                args.append('{}[{}]'.format(arg[:-2], ','.join(repr(x) for x in trailer[-1])))
            else:
                args.append(self.visit(var))
        if len(args) == 1:
            try:
                if isinstance(value, CodeStr):
                    for op in ('+', '-', '*', '/'):
                        start = str(args[0]) + ' ' + op + ' '
                        if value.startswith(start):
                            return [CodeStr('{} {}= {}'.format(args[0], op, value[len(start):]))]
            except Exception as e:
                pass
        return [CodeStr(' = '.join(args + [repr(value)]))]

    def visitArgs(self, ctx):
        return [self.visit(c) for c in ctx.expr()]

    def visitSpecialArgs(self, ctx):
        return [self.visit(c) for c in ctx.specialExpr()]

    def visitComparison(self, ctx):
        symbol_dict = {VisualFoxpro9Lexer.GREATERTHAN: '>',
                       VisualFoxpro9Lexer.GTEQ: '>=',
                       VisualFoxpro9Lexer.LESSTHAN: '<',
                       VisualFoxpro9Lexer.LTEQ: '<=',
                       VisualFoxpro9Lexer.NOTEQUALS: '!=',
                       VisualFoxpro9Lexer.HASH: '!=',
                       VisualFoxpro9Lexer.EQUALS: '==',
                       VisualFoxpro9Lexer.DOUBLEEQUALS: '==',
                       VisualFoxpro9Lexer.DOLLAR: 'in',
                       VisualFoxpro9Lexer.OR: 'or',
                       VisualFoxpro9Lexer.AND: 'and'
                      }
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        symbol = symbol_dict[ctx.op.type]
        return CodeStr('{} {} {}'.format(repr(left), symbol, repr(right)))

    def visitUnaryNegation(self, ctx):
        if ctx.op.type == VisualFoxpro9Lexer.PLUS_SIGN:
            return CodeStr('{}'.format(repr(self.visit(ctx.expr()))))
        return CodeStr('-{}'.format(repr(self.visit(ctx.expr()))))

    def visitBooleanNegation(self, ctx):
        return CodeStr('not {}'.format(repr(self.visit(ctx.expr()))))

    def func_call(self, funcname, args):
        if funcname in self.function_list:
            return self.make_func_code(funcname, *args)
        funcname = {
            'stuffc': 'stuff',
        }.get(funcname, funcname)
        if funcname == 'chr' and len(args) == 1 and isinstance(args[0], int):
            return chr(args[0])
        if funcname == 'space' and len(args) == 1 and isinstance(args[0], int):
            return ' '*args[0]
        if funcname == 'asc':
            return self.make_func_code('ord', CodeStr(str(repr(args[0])) + '[0]'))
        if funcname == 'len':
            return self.make_func_code('len', *args)
        if funcname == 'alen':
            if len(args) == 1:
                return self.make_func_code('len', *args)
            else:
                args[1] = self.to_int(args[1])
                return self.add_args_to_code('{}.alen({})', args)
        if funcname == 'ascan':
            if len(args) == 3:
                args = [self.add_args_to_code('{}[{}:]', [args[0], args[2]]), args[1]]
            elif len(args) == 4:
                args = [self.add_args_to_code('{}[{}:({} + {})]', [args[0], args[2], args[2], args[3]]), args[1]]
            if len(args) == 2:
                return self.add_args_to_code('{}.index({})', args)
        if funcname == 'empty':
            return self.add_args_to_code('(not {} if {} is not None else False)', args + args)
        if funcname == 'occurs':
            return self.add_args_to_code('{}.count({})', reversed(args))
        if funcname in ('at', 'rat'):
            funcname = {
                'at': 'find',
                'rat': 'rfind',
            }[funcname]
            return self.add_args_to_code('({}.{}({}) + 1)', [args[1], CodeStr(funcname), args[0]])
        if funcname in ('repli', 'replicate'):
            args[1:] = [self.to_int(arg) for arg in args[1:]]
            return self.add_args_to_code('({} * {})', args)
        if funcname in ('date', 'datetime', 'time') and len(args) == 0:
            self.imports.append('import datetime as dt')
            if funcname == 'date':
                return self.make_func_code('dt.datetime.now().date')
            elif funcname == 'datetime':
                return self.make_func_code('dt.datetime.now')
            elif funcname == 'time':
                return self.make_func_code('dt.datetime.now().time().strftime', '%H:%M:%S')
        if funcname in ('year', 'month', 'day', 'hour', 'minute', 'sec', 'cdow', 'cmonth'):
            funcname = {
                'sec': 'second',
                'cdow': "strftime('%A')",
                'cmonth': "strftime('%B')",
            }.get(funcname, funcname)
            return self.add_args_to_code('{}.{}', [args[0], CodeStr(funcname)])
        if funcname == 'dtoc':
            if len(args) == 1 or args[1] == 1:
                if len(args) > 1 and args[1] == 1:
                    args[1] = '%Y%m%d'
                else:
                    args.append('%m/%d/%Y')
                return self.make_func_code('{}.{}'.format(args[0], 'strftime'), args[1])
        if funcname == 'iif' and len(args) == 3:
            return self.add_args_to_code('({} if {} else {})', [args[i] for i in (1, 0, 2)])
        if funcname == 'between':
            return self.add_args_to_code('({} <= {} <= {})', [args[i] for i in (1, 0, 2)])
        if funcname == 'nvl':
            return self.add_args_to_code('({} if {} is not None else {})', [args[0], args[0], args[1]])
        if funcname == 'evl':
            return self.add_args_to_code('({} or {})', args)
        if funcname == 'sign':
            return self.add_args_to_code('1 if {} > 0 else (-1 if {} < 0 else 0)', [args[0], args[0]])
        if funcname in ('alltrim', 'ltrim', 'rtrim', 'lower', 'upper', 'padr', 'padl', 'padc'):
            funcname = {
                'alltrim': 'strip',
                'ltrim': 'lstrip',
                'rtrim': 'rstrip',
                'padr': 'ljust',
                'padl': 'rjust',
                'padc': 'center',
            }.get(funcname, funcname)
            funcname = '{}.{}'.format(repr(args[0]), funcname)
            return self.make_func_code(funcname, *args[1:])
        if funcname == 'strtran':
            args = args[:6]
            if len(args) > 3:
                args[3:] = [self.to_int(arg) for arg in args[3:]]
            if len(args) == 6 and int(args[5]) in (0, 2):
                args.pop()
            if len(args) == 2:
                args.append('')
            str_replace = self.add_args_to_code('{}.replace', [args[0]])
            if len(args) == 3:
                return self.make_func_code(str_replace, *args[1:])
            elif len(args) == 4 and args[3] < 2:
                args.pop()
                return self.make_func_code(str_replace, *args[1:])
            elif len(args) == 5 and args[3] < 2:
                args[3] = args[4]
                args.pop()
                return self.make_func_code(str_replace, *args[1:])
        if funcname == 'right':
            args[1] = self.to_int(args[1])
            return self.add_args_to_code('{}[-{}:]', args)
        if funcname == 'left' and len(args) == 2:
            args[1] = self.to_int(args[1])
            return self.add_args_to_code('{}[:{}]', args)
        if funcname == 'substr':
            args[1:] = [self.to_int(arg) for arg in args[1:]]
            args[1] -= 1
            if len(args) < 3:
                return self.add_args_to_code('{}[{}:]', args)
            if args[2] == 1:
                return self.add_args_to_code('{}[{}]', args[:2])
            args[2] += args[1]
            return self.add_args_to_code('{}[{}:{}]', args)
        if funcname == 'proper':
            return self.add_args_to_code('{}.title()', args)
        if funcname in ('ceiling', 'exp', 'log', 'log10', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'pi', 'sqrt'):
            self.imports.append('import math')
            if funcname == 'pi':
                return CodeStr('math.pi')
            funcname = {
                'ceiling': 'ceil',
                'atn2': 'atan2'
            }.get(funcname, funcname)
            funcname = 'math.' + funcname
            return self.make_func_code(funcname, *args)
        if funcname in ('bitand', 'bitclear', 'bitlshift', 'bitnot', 'bitor', 'bitrshift', 'bitset', 'bittest', 'bitxor'):
            op = {
                'bitand': '({} & {})',
                'bitclear': '({} & ((1 << {}) ^ 0xffffffff))',
                'bitlshift': '({} << {})',
                'bitnot': '~{}',
                'bitor': '({} | {})',
                'bitrshift': '({} >> {})',
                'bitset': '({} | (1 << {}))',
                'bittest': '(({} & (1 << {})) > 0)',
                'bitxor': '({} ^ {})'
            }
            return self.add_args_to_code(op[funcname], [self.to_int(arg) for arg in args])
        if funcname == 'str':
            funcname = 'num_to_str'
        if funcname in ('file', 'directory'):
            self.imports.append('import os')
            funcname = {
                'file': 'os.path.isfile',
                'directory': 'os.path.isdir',
            }[funcname]
            return self.make_func_code(funcname, *args)
        if funcname == 'used':
            self.imports.append('from vfp2py import vfpfunc')
            return self.make_func_code('vfpfunc.used', *args)
        if funcname in ('abs', 'round', 'max', 'min'):
            return self.make_func_code(funcname, *args)
        if funcname == 'int':
            return self.to_int(args[0])
        if funcname == 'isnull':
            return self.add_args_to_code('{} == {}', [args[0], None])
        if funcname == 'inlist':
            return self.add_args_to_code('({} in {})', [args[0], tuple(args[1:])])
        if funcname == 'pythonfunctioncall' and len(args) == 3:
            self.imports.append('import {}'.format(args[0]))
            return self.make_func_code('{}.{}'.format(args[0], args[1]), *args[2])
        if funcname == 'createobject':
            if len(args) > 0 and self.string_type(args[0]) and args[0].lower() in self.class_list:
                return self.make_func_code(args[0].lower(), *args[1:])
            elif len(args) > 0 and self.string_type(args[0]) and args[0].lower() == 'pythontuple':
                return tuple(args[1:])
            else:
                return self.make_func_code('vfpfunc.create_object', *args)
        if funcname in ('fcreate', 'fopen'):
            opentypes = ('w', 'r') if funcname == 'fcreate' else ('r', 'w', 'r+')
            if len(args) > 1 and args[1] <= len(opentypes):
                args[1] = self.to_int(args[1])
                if isinstance(args[1], int):
                    args[1] = opentypes[args[1]]
                else:
                    args[1] = self.add_args_to_code({}[{}]).format(opentypes, args[1])
            else:
                args.append(opentypes[0])
            return self.make_func_code('open', *args)
        if funcname == 'fclose':
            return self.add_args_to_code('{}.close()', args)
        if funcname in ('fputs', 'fwrite'):
            if len(args) == 3:
                args[2] = self.to_int(args[2])
                args[1] = self.add_args_to_code('{}[:{}]', args[1:])
            if funcname == 'fputs':
                args[1] += '\r\n'
            return self.add_args_to_code('{}.write({})', args)
        if funcname in ('fgets', 'fread'):
            if funcname == 'fgets':
                code = '{}.readline({}).strip(\'\\r\\n\')'
            else:
                code = '{}.read({})'
            if len(args) < 2:
                args.append(CodeStr(''))
            else:
                args[1] = self.to_int(args[1])
            return self.add_args_to_code(code, args)
        if funcname == 'justpath':
            return self.make_func_code('os.path.dirname', *args)
        if funcname == 'sys':
            funcname = 'vfp_sys'
        if funcname in ('bof', 'eof', 'deleted'):
            funcname = 'vfpfunc.db.' + funcname
        elif funcname in dir(vfpfunc):
            self.imports.append('from vfp2py import vfpfunc')
            funcname = 'vfpfunc.' + funcname
        else:
            funcname = self.scopeId(funcname, 'func')
        return self.make_func_code(funcname, *args)

    def scopeId(self, identifier, vartype):
        if not self.has_scope() or identifier in self.scope:
            return identifier
        if identifier == 'this':
            return CodeStr('self')
        if identifier == 'thisform':
            return CodeStr('self.parentform')
        self.imports.append('from vfp2py import vfpfunc')
        self.used_scope = True
        if vartype == 'val':
            return self.add_args_to_code('vfpfunc.variable[{}]', [str(identifier)])
        elif vartype == 'func':
            return self.add_args_to_code('vfpfunc.function[{}]', [str(identifier)])

    def createIdAttr(self, identifier, trailer):
        if trailer and len(trailer) == 1 and isinstance(trailer[0], list):
            args = trailer[0]
            return self.func_call(identifier, args)
        if trailer:
            trailer = self.convert_trailer_args(trailer)
        else:
            trailer = CodeStr('')
        identifier = self.scopeId(identifier, 'val')
        return self.add_args_to_code('{}{}', (identifier, trailer))

    def convert_trailer_args(self, trailers):
        retval = ''
        for trailer in trailers:
            if isinstance(trailer, list):
                retval += '({})'.format(', '.join(repr(t) for t in trailer))
            else:
                retval += '.' + trailer
        return CodeStr(retval)

    def visitTrailer(self, ctx):
        trailer = self.visit(ctx.trailer()) if ctx.trailer() else []
        if ctx.args():
            retval = [[x for x in self.visit(ctx.args())]]
        elif ctx.identifier():
            self.enable_scope(False)
            retval = [self.visit(ctx.identifier())]
            self.enable_scope(True)
        else:
            retval = [[]]
        return retval + trailer

    def visitIdAttr(self, ctx):
        identifier = self.visit(ctx.identifier())
        trailer = self.visit(ctx.trailer()) if ctx.trailer() else None
        if ctx.PERIOD() and self.withid:
            trailer = [identifier] + (trailer if trailer else [])
            identifier = self.withid
        return self.createIdAttr(identifier, trailer)

    def visitIdAttr2(self, ctx):
        return CodeStr('.'.join(([self.withid] if ctx.startPeriod else []) + [self.visit(identifier) for identifier in ctx.identifier()]))

    def visitAtomExpr(self, ctx):
        atom = self.visit(ctx.atom())
        trailer = self.visit(ctx.trailer()) if ctx.trailer() else None
        if ctx.PERIOD() and self.withid:
            trailer = [atom] + (trailer if trailer else [])
            atom = self.withid

        if trailer and len(trailer) > 0 and not isinstance(trailer[-1], list) and isinstance(atom, CodeStr) and isinstance(ctx.parentCtx, VisualFoxpro9Parser.CmdContext):
            return self.make_func_code('vfpfunc.call_if_callable', self.createIdAttr(atom, trailer))
        if isinstance(atom, CodeStr):
            return self.createIdAttr(atom, trailer)
        elif trailer:
            for i, t in enumerate(trailer):
                if isinstance(t, list):
                    trailer[i] = self.add_args_to_code('({})', t)
                else:
                    trailer[i] = '.' + trailer[i]
            return CodeStr(''.join([repr(self.visit(ctx.atom()))] + trailer))
        else:
            return self.visit(ctx.atom())

    def visitComplexId(self, ctx):
        return self.visitAtomExpr(ctx)

    def visitIdList(self, ctx):
        return [self.visit(i) for i in get_list(ctx.idAttr())]

    def visitAddRemoveDirectory(self, ctx):
        self.imports.append('import os')
        if ctx.MD() or ctx.MKDIR():
            funcname = 'mkdir'
        if ctx.RD() or ctx.RMDIR():
            funcname = 'rmdir'
        return self.make_func_code('os.' + funcname, self.visit(ctx.specialExpr()))

    def visitSpecialExpr(self, ctx):
        if ctx.pathname():
            return self.visit(ctx.pathname())
        elif ctx.expr():
            self.enable_scope(False)
            expr = self.visit(ctx.expr())
            self.enable_scope(True)
            start, stop = ctx.getSourceInterval()
            raw_expr = ''.join(t.text for t in ctx.parser._input.tokens[start:stop+1])
            if raw_expr.lower() == expr and isinstance(ctx.expr(), VisualFoxpro9Parser.AtomExprContext) and (not ctx.expr().trailer() or not any(isinstance(arg, list) for arg in self.visit(ctx.expr().trailer()))):
                return self.create_string(raw_expr).lower()
            return self.visit(ctx.expr())

    def visitPathname(self, ctx):
        return self.create_string(ctx.getText()).lower()

    def visitNumber(self, ctx):
        num = ctx.NUMBER_LITERAL().getText()
        if num[-1:].lower() == 'e':
            num += '0'
        try:
            return int(num)
        except:
            return float(num)

    def visitBoolean(self, ctx):
        if ctx.T():
            return True
        if ctx.Y():
            return True
        if ctx.F():
            return False
        if ctx.N():
            return False
        raise Exception('Can\'t convert boolean:' + ctx.getText())

    def visitNull(self, ctx):
        return None

    def visitDate(self, ctx):
        if ctx.NULLDATE_LITERAL():
            return None
        raise Exception('Date constants not implemented for none null dates')
        innerstr = ctx.getText()[1:-1]
        if ctx.DATE_LITERAL():
            m, d, y = innerstr.split('/')
            if len(y) == 2:
                y = '19'+y
            if len(y) != 4:
                raise Exception('year must be 2 or 4 digits in date constant: ' + ctx.getText())
            try:
                return dt.date(int(y), int(m), int(d))
            except ValueError as e:
                raise Exception('invalid date constant: ' + ctx.getText())
        return dt.dateime(1, 1, 1, 0, 0, 0)

    def visitString(self, ctx):
        return self.create_string(ctx.getText()[1:-1])

    def visitPower(self, ctx):
        return self.operationExpr(ctx, '**')

    def visitMultiplication(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    def walkAdditions(self, ctx):
        retval = []
        for expr in ctx.expr():
            if isinstance(expr, VisualFoxpro9Parser.AdditionContext):
                retval += self.walkAdditions(expr)
            else:
                retval.append(self.visit(expr))
        return retval

    def visitAddition(self, ctx):
        if ctx.op.type == VisualFoxpro9Parser.MINUS_SIGN:
            return self.operationExpr(ctx, ctx.op.type)
        exprs = self.walkAdditions(ctx)
        exprs2 = [exprs[0]]
        for expr in exprs[1:]:
            if self.string_type(expr) and self.string_type(exprs2[-1]):
                exprs2[-1] += expr
            elif expr:
                exprs2.append(expr)
        if len(exprs2) == 1:
            return exprs2[0]
        exprs2 = [expr for expr in exprs2 if expr != '']
        if len(exprs2) == 0:
            return ''
        return CodeStr('(' + ' + '.join(repr(expr) for expr in exprs2) + ')')

    def visitModulo(self, ctx):
        return self.operationExpr(ctx, '%')

    def operationExpr(self, ctx, operation):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        symbols = {
            '**': '**',
            '%': '%',
            VisualFoxpro9Parser.ASTERISK: '*',
            VisualFoxpro9Parser.FORWARDSLASH: '/',
            VisualFoxpro9Parser.PLUS_SIGN: '+',
            VisualFoxpro9Parser.MINUS_SIGN: '-'
        }
        return CodeStr('({} {} {})'.format(repr(left), symbols[operation], repr(right)))

    def visitSubExpr(self, ctx):
        return self.add_args_to_code('({})', [self.visit(ctx.expr())])

    def visitFuncDo(self, ctx):
        self.enable_scope(False)
        func = self.visit(ctx.specialExpr()[0])
        self.enable_scope(True)
        if ctx.FORM():
            func = func.lower()
            func = func.replace('.', '_')
            return self.make_func_code('{}._program_main'.format(func))
        args = self.visit(ctx.args()) if ctx.args() else []
        if func.endswith('.mpr'):
            func = func[:-4]
            args = [func] + args
            self.imports.append('from vfp2py import vfpfunc')
            return self.make_func_code('vfpfunc.mprfile', *args)
        namespace = self.visit(ctx.specialExpr()[1]) if ctx.IN() else None
        if (not namespace or os.path.splitext(namespace)[0] == self.filename) and func in self.function_list:
            return self.make_func_code(func, *args)
        if not namespace:
            namespace = func
            func = '_program_main'
        return self.make_func_code('vfpfunc.do_command', func, namespace, *args)

    def visitDoForm(self, ctx):
        self.enable_scope(False)
        form = self.visit(ctx.specialExpr())
        self.enable_scope(True)

    def visitMethodCall(self, ctx):
        return self.visit(ctx.idAttr()) + '.' + self.visit(ctx.identifier()) + '()'

    def visitClearStmt(self, ctx):
        if ctx.ALL():
            return CodeStr('vfpfunc.clearall()')
        elif ctx.DLLS():
            return self.make_func_code('vfpfunc.cleardlls', *self.visit(ctx.args()))
        elif ctx.MACROS():
            return CodeStr('vfpfunc.clearmacros()')
        elif ctx.EVENTS():
            return CodeStr('vfpfunc.clearevents()')
        elif ctx.PROGRAM():
            return CodeStr('vfpfunc.clearprogram()')
        else:
            return CodeStr('vfpfunc.clear()')

    def visitDllDeclare(self, ctx):
        self.enable_scope(False)
        dll_name = self.visit(ctx.specialExpr())
        funcname = str(self.visit(ctx.identifier()[0]))
        alias = str(self.visit(ctx.alias)) if ctx.alias else None
        self.enable_scope(True)
        return self.make_func_code('vfpfunc.function.dll_declare', dll_name, funcname, alias)

    def visitReadEvent(self, ctx):
        return CodeStr('vfpfunc.read_events()')

    def on_event(self, ctx, func_prefix):
        if ctx.cmd():
            func = self.visit(ctx.cmd())
            if isinstance(func, list) and len(func) == 1:
                func = func[0]
            func = CodeStr('lambda: ' + repr(func))
        else:
            func = None
        return [CodeStr(func_prefix + ' = ' + repr(func))]

    def visitOnError(self, ctx):
        return self.on_event(ctx, 'vfpfunc.error_func')

    def visitOnShutdown(self, ctx):
        return self.on_event(ctx, 'vfpfunc.shutdown_func')

    def visitIdentifier(self, ctx):
        altermap = {
            'class': 'classtype'
        }
        identifier = ctx.getText().lower()
        identifier = altermap.get(identifier, identifier)
        return CodeStr(identifier)

    def visitReference(self, ctx):
        return [self.visit(ctx.idAttr())]

    def visitArrayIndex(self, ctx):
        if ctx.twoExpr():
            return self.visit(ctx.twoExpr())
        else:
            return [self.visit(ctx.expr())]

    def visitTwoExpr(self, ctx):
        return [self.visit(expr) for expr in ctx.expr()]

    def visitQuit(self, ctx):
        return [CodeStr('vfpfunc.quit()')]

    def visitDeleteFile(self, ctx):
        if ctx.specialExpr():
            filename = self.visit(ctx.specialExpr())
        else:
            filename = None
        if ctx.RECYCLE():
            return self.make_func_code('vfpfunc.delete_file', filename, True)
        else:
            self.imports.append('import os')
            return self.make_func_code('os.remove', filename)

    def visitFile(self, ctx):
        return ctx.getText()

    def visitRelease(self, ctx):
        scoped_args = []
        if ctx.ALL():
            args = []
        else:
            self.enable_scope(False)
            args = self.visit(ctx.args())
            self.enable_scope(True)
            final_args = []
            for arg in args:
                if arg in self.scope:
                    scoped_args.append(arg)
                else:
                    final_args.append(str(arg))
            args = final_args if final_args else None
        retval = []
        if scoped_args:
            for arg in scoped_args:
                self.scope.pop(arg)
            retval.append(CodeStr('del {}'.format(', '.join(scoped_args))))
        if args is not None:
            if ctx.PROCEDURE():
                retval.append(self.make_func_code('vfpfunc.function.release_procedure', *args))
            elif ctx.POPUPS():
                kwargs = {}
                if ctx.EXTENDED():
                    kwargs['extended'] = True
                retval.append(self.make_func_code('vfpfunc.function.release_popups', *args, **kwargs))
            elif ctx.ALL():
                retval.append(self.make_func_code('vfpfunc.release'))
            else:
                thisargs = [arg for arg in args if arg in ('this', 'thisform')]
                args = [arg for arg in args if arg not in ('this', 'thisform')]
                for arg in thisargs:
                    if arg == 'this':
                        retval.append(self.make_func_code('self.release()'))
                    if arg == 'thisform':
                        retval.append(self.make_func_code('self.parentform.release()'))
                if args:
                    args = [self.add_args_to_code('vfpfunc.variable[{}]', arg) for arg in args]
                    retval.append(CodeStr('del {}'.format(', '.join(args))))
        return retval

    def visitCloseStmt(self, ctx):
        allflag = not not ctx.ALL()
        if ctx.TABLES():
            return self.make_func_code('vfpfunc.db.close_tables', allflag)
        if ctx.INDEXES():
            return self.make_func_code('vfpfunc.db.close_indexes', allflag)
        if ctx.DATABASES():
            return self.make_func_code('vfpfunc.db.close_databases', allflag)
        return self.make_func_code('vfpfunc.db.close_all')

    def visitWaitCmd(self, ctx):
        message = repr(self.visit(ctx.message) if ctx.message else '')
        to_expr = repr(self.visit(ctx.toExpr) if ctx.TO() else None)
        if ctx.WINDOW():
            if ctx.AT():
                window=[self.visit(ctx.atExpr1), self.visit(ctx.atExpr2)]
            else:
                window = [-1, -1]
        else:
            window = []
        window = repr(window)
        nowait = repr(ctx.NOWAIT() != None)
        noclear = repr(ctx.NOCLEAR() != None)
        timeout = repr(self.visit(ctx.timeout)) if ctx.TIMEOUT() else -1
        code = 'vfpfunc.wait({}, to={}, window={}, nowait={}, noclear={}, timeout={})'
        return CodeStr(code.format(message, to_expr, window, nowait, noclear, timeout))

    def visitOnKey(self, ctx):
        keys = [repr(str(self.visit(i))) for i in ctx.identifier()]
        return self.on_event(ctx, 'vfpfunc.on_key[{}]'.format(', '.join(keys)))

    def visitDeactivate(self, ctx):
        if ctx.MENU():
            func = 'vfpfunc.deactivate_menu'
        else:
            func = 'vfpfunc.deactivate_popup'
        self.enable_scope(False)
        args = self.visit(ctx.parameters()) if not ctx.ALL() else []
        self.enable_scope(True)
        return self.make_func_code(func, *[str(arg) for arg in args])

    def visitCreateTable(self, ctx):
        if ctx.TABLE():
            func = 'vfpfunc.db.create_table'
        elif ctx.DBF():
            func = 'vfpfunc.db.create_dbf'
        tablename = self.visit(ctx.specialExpr())
        tablesetup = zip(ctx.identifier()[::2], ctx.identifier()[1::2], ctx.arrayIndex())
        tablesetup = ((self.visit(id1), self.visit(id2), self.visit(size)) for id1, id2, size in tablesetup)
        setupstring = []
        for id1, id2, size in tablesetup:
            if id2.upper() == 'L' and len(size) == 1 and size[0] == 1:
                setupstring.append('{} {}'.format(id1, id2))
            else:
                setupstring.append('{} {}({})'.format(id1, id2, ', '.join(str(int(i)) for i in size)))
        setupstring = '; '.join(setupstring)
        free = 'free' if ctx.FREE() else ''
        return self.make_func_code(func, tablename, setupstring, free)

    def visitSelect(self, ctx):
        if ctx.tablename:
            return self.make_func_code('vfpfunc.db.select', self.visit(ctx.tablename))
        else:
            args = [arg for arg in self.visit(ctx.specialArgs())] if ctx.specialArgs() else ('*',)
            from_table = self.visit(ctx.fromExpr) if ctx.fromExpr else None
            into_table = self.visit(ctx.intoExpr) if ctx.intoExpr else None
            where_expr = self.visit(ctx.whereExpr) if ctx.whereExpr else None
            order_by = self.visit(ctx.orderbyid) if ctx.orderbyid else None
            distinct = 'distinct' if ctx.DISTINCT() else None
            return self.make_func_code('vfpfunc.db.sqlselect', args, from_table, into_table, where_expr, order_by, distinct)

    def visitGoRecord(self, ctx):
        if ctx.TOP():
            record = 0
        elif ctx.BOTTOM():
            record = -1
        else:
            record = self.visit(ctx.expr())
        if ctx.idAttr():
            name = self.visit(ctx.idAttr)
        else:
            name = None
        return self.make_func_code('vfpfunc.db.goto', name, record)

    def visitUse(self, ctx):
        shared = ctx.SHARED()
        exclusive = ctx.EXCL() or ctx.EXCLUSIVE()
        if shared and exclusive:
            raise Exception('cannot combine shared and exclusive')
        elif shared:
            opentype = 'shared'
        elif exclusive:
            opentype = 'exclusive'
        else:
            opentype = None
        if ctx.name:
            name = self.visit(ctx.name)
        else:
            name = None
        if ctx.workArea:
            workarea = self.visit(ctx.workArea)
            if isinstance(workarea, float):
                workarea = int(workarea)
        else:
            workarea = None
        return self.make_func_code('vfpfunc.db.use', name, workarea, opentype)

    def visitAppend(self, ctx):
        if ctx.FROM():
            pass #NEED TO ADD - APPEND FROM
        else:
            menupopup = not ctx.BLANK()
            if ctx.IN():
                tablename = self.visit(ctx.idAttr())
            else:
                tablename = None
            return self.make_func_code('vfpfunc.db.append', tablename, menupopup)

    def visitReplace(self, ctx):
        value = self.visit(ctx.expr(0))
        if ctx.scopeClause():
            scope = self.visit(ctx.scopeClause())
        else:
            scope = None
        self.enable_scope(False)
        field = self.visit(ctx.specialExpr())
        self.enable_scope(True)
        return self.make_func_code('vfpfunc.db.replace', field, value, scope)

    def visitSkipRecord(self, ctx):
        if len(ctx.expr()) > 1:
            table = self.visit(ctx.expr()[1])
        else:
            table = None
        skipnum = self.visit(ctx.expr()[0])
        return self.make_func_code('vfpfunc.db.skip', table, skipnum)

    def visitCopyTo(self, ctx):
        copyTo = self.visit(ctx.specialExpr())
        if ctx.STRUCTURE():
            return self.make_func_code('vfpfunc.db.copy_structure', copyTo)

    def visitDeleteRecord(self, ctx):
        kwargs = OrderedDict()
        if ctx.scopeClause():
            scopetype, num = self.visit(ctx.scopeClause())
        else:
            scopetype = 'next'
            num = 1
        if ctx.IN():
            name = self.visit(ctx.inExpr)
        else:
            name = None
        if ctx.forExpr:
            kwargs['for_cond'] = self.add_args_to_code('lambda: {}', [self.visit(ctx.forExpr)])
        if ctx.whileExpr:
            kwargs['while_cond'] = self.add_args_to_code('lambda: {}', [self.visit(ctx.whileExpr)])
        if ctx.RECALL():
            kwargs['recall'] = True
        return self.make_func_code('vfpfunc.db.delete_record', scopetype, num, **kwargs)

    def visitPack(self, ctx):
        if ctx.DBF():
            pack = 'dbf'
        elif ctx.MEMO():
            pack = 'memo'
        else:
            pack = 'both'
        tablename = self.visit(ctx.tableName) if ctx.tableName else None
        workarea = self.visit(ctx.workArea) if ctx.workArea else None
        return self.make_func_code('vfpfunc.db.pack', pack, tablename, workarea)

    def visitIndexOn(self, ctx):
        field = self.visit(ctx.specialExpr()[0])
        indexname = self.visit(ctx.specialExpr()[1])
        tag_flag = not not ctx.TAG()
        compact_flag = not not ctx.COMPACT()
        if ctx.ASCENDING() and ctx.DESCENDING():
            raise Exception('Invalid statement: {}'.format(self.getCtxText(ctx)))
        order = 'descending' if ctx.DESCENDING() else 'ascending'
        unique_flag = not not ctx.UNIQUE()
        return self.make_func_code('vfpfunc.db.index_on', field, indexname, order, tag_flag, compact_flag, unique_flag)

    def visitReindex(self, ctx):
        return self.make_func_code('vfpfunc.db.reindex', not not ctx.COMPACT())

    def visitPackDatabase(self, ctx):
        return self.make_func_code('vfpfunc.db.pack_database')

    def visitZapTable(self, ctx):
        return self.make_func_code('vfpfunc.db.zap', self.visit(ctx.expr()) if ctx.expr() else None)

    def visitScopeClause(self, ctx):
        if ctx.ALL():
            return 'all', -1
        elif ctx.NEXT():
            return 'next', self.visit(ctx.expr())
        elif ctx.RECORD():
            return 'record', self.visit(ctx.expr())
        elif ctx.REST():
            return 'rest', -1

    def visitReport(self, ctx):
        if ctx.specialExpr():
            formname = self.visit(ctx.specialExpr())
        else:
            formname = None
        return self.make_func_code('vfpfunc.report_form', formname)

    def visitSetCmd(self, ctx):
        setword = ctx.setword.text.lower()
        if ctx.BAR():
            setword += ' bar'
        if setword == 'printer':
            args=['printer']
            if ctx.ON():
                args.append(1)
                if ctx.PROMPT():
                    args.append(True)
            elif ctx.OFF():
                args.append(0)
            elif ctx.TO():
                if ctx.DEFAULT():
                    args.append(['Default', None])
                elif ctx.NAME():
                    args.append(['Name', self.visit(ctx.specialExpr()[0])])
                elif ctx.specialExpr():
                    args.append(['File', self.visit(ctx.specialExpr()[0])])
                    args.append(ctx.ADDITIVE() != None)
            return self.make_func_code('vfpfunc.set', *args)
        elif setword == 'typeahead':
            return self.make_func_code('vfpfunc.set', 'typeahead', self.visit(ctx.expr()[0]))
        elif setword == 'procedure':
            kwargs = {'additive': True} if ctx.ADDITIVE() else {}
            return self.make_func_code('vfpfunc.function.set_procedure', *[self.visit(expr) for expr in ctx.specialExpr()], **kwargs)
        elif setword == 'bell':
            if ctx.TO():
                return self.make_func_code('vfpfunc.set', setword, self.visit(ctx.specialExpr()[0]))
            else:
                return self.make_func_code('vfpfunc.set', setword, not ctx.OFF())
        elif setword in ('cursor', 'deleted', 'exact', 'near', 'status', 'status bar', 'unique'):
            return self.make_func_code('vfpfunc.set', setword, not ctx.OFF())
        elif setword == 'century':
            if ctx.TO():
                args = [None] + [self.visit(expr) for expr in ctx.expr()]
            else:
                args = [not ctx.OFF()]
            return self.make_func_code('vfpfunc.set', setword, *args)
        elif setword == 'sysmenu':
            args = [x.symbol.text.lower() for x in (ctx.ON(), ctx.OFF(), ctx.TO(), ctx.SAVE(), ctx.NOSAVE()) if x]
            if ctx.expr():
                args += [self.visit(ctx.expr()[0])]
            elif ctx.DEFAULT():
                args += ['default']
            return self.make_func_code('vfpfunc.set', setword, *args)
        elif setword == 'date':
            self.enable_scope(False)
            date_format = str(self.visit(ctx.identifier()))
            self.enable_scope(True)
            return self.make_func_code('vfpfunc.set', setword, date_format)
        elif setword == 'refresh':
            args = [self.visit(expr) for expr in ctx.expr()]
            return self.make_func_code('vfpfunc.set', setword, *args)
        elif setword == 'notify':
            return self.make_func_code('vfpfunc.set', setword, not not ctx.CURSOR(), not ctx.OFF())
        elif setword == 'clock':
            args = [x.symbol.text.lower() for x in (ctx.ON(), ctx.OFF(), ctx.TO(), ctx.STATUS()) if x]
            if ctx.expr():
                args += [self.visit(expr) for expr in ctx.expr()]
            return self.make_func_code('vfpfunc.set', setword, *args)
        elif setword == 'memowidth':
            return self.make_func_code('vfpfunc.set', setword, self.visit(ctx.expr()[0]))
        elif setword == 'library':
            kwargs = {'additive': True} if ctx.ADDITIVE() else {}
            return self.make_func_code('vfpfunc.function.set_library', *[self.visit(expr) for expr in ctx.specialExpr()], **kwargs)
        elif setword == 'filter':
            args = [self.visit(expr) for expr in ctx.specialExpr()]
            return self.make_func_code('vfpfunc.set', setword, *args)
        elif setword == 'order':
            order = self.visit(ctx.specialExpr(0))
            of_expr = self.visit(ctx.ofExpr) if ctx.ofExpr else None
            in_expr = self.visit(ctx.inExpr) if ctx.inExpr else None
            kwargs = {'descending': True} if ctx.DESCENDING() else {}
            kwargs.update({'tag': True} if ctx.TAG() else {})
            return self.make_func_code('vfpfunc.set', setword, order, of_expr, in_expr, **kwargs)

    def visitShellRun(self, ctx):
        if ctx.identifier():
            pass
        command = ''
        for expr in ctx.specialExpr():
            start, stop = expr.getSourceInterval()
            tokens = ctx.parser._input.tokens[start:stop+1]
            command += ''.join(tok.text for tok in tokens) + ' '
        command = [t for t in command.split() if t]
        self.imports.append('import subprocess')
        return self.make_func_code('subprocess.call', command)

    def visitReturnStmt(self, ctx):
        if not ctx.expr():
            return [CodeStr('return')]
        return [self.add_args_to_code('return {}', [self.visit(ctx.expr())])]

def convert(codestr):
    input_stream = antlr4.InputStream(codestr)
    lexer = VisualFoxpro9Lexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = VisualFoxpro9Parser(stream)
    tree = parser.expr()
    visitor = PythonConvertVisitor()
    return visitor.visit(tree)

def evaluateCode(codestr):
    return eval(convert(codestr))

def preprocess_code(data):
    input_stream = antlr4.InputStream(data)
    lexer = VisualFoxpro9Lexer(input_stream)
    stream = MultichannelTokenStream(lexer)
    parser = VisualFoxpro9Parser(stream)
    tree = parser.preprocessorCode()
    visitor = PreprocessVisitor()
    visitor.tokens = visitor.visit(tree)
    return visitor

def preprocess_file(filename):
    import codecs
    fid = codecs.open(filename, 'r', 'ISO-8859-1')
    data = fid.read()
    fid.close()

    return preprocess_code(data)

class MultichannelTokenStream(antlr4.CommonTokenStream):
    def __init__(self, lexer, channel=antlr4.Token.DEFAULT_CHANNEL):
        super(MultichannelTokenStream, self).__init__(lexer)
        self.channels = [channel]

    def nextTokenOnChannel(self, i, channel):
        self.sync(i)
        if i>=len(self.tokens):
            return -1
        token = self.tokens[i]
        while token.channel not in self.channels:
            if token.type==antlr4.Token.EOF:
                return -1
            i += 1
            self.sync(i)
            token = self.tokens[i]
        return i

    def previousTokenOnChannel(self, i, channel):
        while i>=0 and self.tokens[i].channel not in self.channels:
            i -= 1
        return i

    def enableChannel(self, channel):
        if channel not in self.channels:
            self.channels.append(channel)
            self.channels = sorted(self.channels)

    def disableChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)

def find_file_ignore_case(filename, directories):
    for directory in directories:
        for testfile in os.listdir(directory):
            if testfile.lower() == filename.lower():
                return os.path.join(directory, testfile)

def memo_filename(filename, ext):
    directory = os.path.dirname(filename) or '.'
    basename = os.path.basename(filename)
    memofile = os.path.splitext(basename)[0] + '.' + ext
    return find_file_ignore_case(memofile, [directory])

def copy_obscured_dbf(filename, memo_ext, dbf_basename):
    memofile = memo_filename(filename, memo_ext)
    dbffile = dbf_basename + '.dbf'
    shutil.copy(filename, dbffile)
    if memofile:
        shutil.copy(memofile, dbf_basename + '.fpt')
    return dbffile

def convert_scx_to_vfp_code(scxfile):
    with tempfile.NamedTemporaryFile() as tmpfile:
        pass
    tmpfile = tmpfile.name
    dbffile = copy_obscured_dbf(scxfile, 'sct', tmpfile)

    table = dbf.Table(dbffile)
    table.open()

    children = [list() for record in table]
    names = [record.objname for record in table]
    for record in table:
        if record['class'].lower() == 'form':
            form = record.objname
        parent = record.parent
        if not parent:
            continue
        parent_ind = names.index(parent)
        children[parent_ind].append(record)

    code = [l.format(form, form) for l in ('local {}', '{} = createObject("{}")', '{}.show()')]
    for record, child in zip(table, children):
        if not record.objname or record.parent or record['class'].lower() == 'dataenvironment':
            continue

        code.append('DEFINE CLASS {} AS {}'.format(record.objname, record['class']))
        subcode = []
        for line in record.properties.split('\r\n'):
            subcode.append(line)
        for child_record in child:
            subcode.append('ADD OBJECT {} AS {}'.format(child_record.objname, child_record['class']))
            for line in child_record.properties.split('\r\n'):
                line = line.strip()
                if not line:
                    continue
                prop, value = line.split(' = ')
                if prop == 'Picture':
                    value = '"{}"'.format(value)
                elif prop.endswith('Color'):
                    value = 'RGB({})'.format(value)
                subcode.append(child_record.objname + '.' + prop + ' = ' + value)
            subcode.append('')

        for line in record.methods.split('\r\n'):
            subcode.append(line)
        subcode.append('')
        for child_record in child:
            for line in child_record.methods.split('\r\n'):
                if not line:
                    continue
                line = re.sub(r'PROCEDURE ', 'PROCEDURE {}.'.format(child_record.objname), line)
                subcode.append(line)
            subcode.append('')
        code.append(subcode)
        code.append('ENDDEFINE')
        code.append('')

    def add_indent(code, level):
        retval = ''
        for line in code:
            if isinstance(line, list):
                retval += add_indent(line, level+1)
            else:
                retval += '   '*level + line + '\n'
        return retval

    code = add_indent(code, 0)

    code = re.sub(r'(\n\s*)+\n+', '\n\n', code)
    return code

def find_full_path(pathname, start_directory):
    name_parts = ntpath.split(pathname)
    while ntpath.split(name_parts[0])[1]:
        name_parts = ntpath.split(name_parts[0]) + name_parts[1:]
    pathname = start_directory
    for part in name_parts:
        if part in ('..', '.', ''):
            pathname = os.path.abspath(os.path.join(pathname, part))
            continue
        next_part = find_file_ignore_case(part, [pathname])
        if next_part is None:
            badind = name_parts.index(part)
            return os.path.join(pathname, *name_parts[badind:]), True
        pathname = next_part
    return pathname, False

def read_vfp_project(pjxfile):
    directory = os.path.dirname(pjxfile)
    with tempfile.NamedTemporaryFile() as tmpfile:
        pass
    tmpfile = tmpfile.name
    dbffile = copy_obscured_dbf(pjxfile, 'pjt', tmpfile)

    table = dbf.Table(dbffile)
    table.open()

    files = {}
    main_file = ''
    for record in table[1:]:
        name, failed = find_full_path(record.name.rstrip('\x00'), directory)
        if failed:
            files[name] = None
        else:
            files[os.path.basename(name).lower()] = name
        if record.mainprog:
            main_file = os.path.basename(name).lower()

    return files, main_file

def convert_project(infile, directory):
    project_files, main_file = read_vfp_project(infile)
    global SEARCH_PATH
    search = SEARCH_PATH
    search += [project_files[name] for name in project_files]
    if not os.path.isdir(directory):
        os.mkdir(directory)
    directory = os.path.join(directory, os.path.basename(directory))
    if not os.path.isdir(directory):
        os.mkdir(directory)
    for name in project_files:
        outfile = directory
        args = [project_files[name], outfile] + search
        try:
            main(args)
        except:
            print('failed to convert {}'.format(name))
    if 'config.fpw' in project_files:
        with open(project_files['config.fpw']) as fid:
            import ConfigParser
            import io
            config_data = io.StringIO('[config]\r\n' + fid.read().decode('utf-8'))
        config = ConfigParser.RawConfigParser()
        config.readfp(config_data)
        config = {x[0]: x[1] for x in config.items('config')}
    else:
        config = {}
    name = os.path.splitext(main_file)[0]
    with open(os.path.join(directory, '__main__.py'), 'wb') as fid:
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        print('import {}'.format(name, name), file=fid)
        print(file=fid)
        print('config = {}'.format(pp.pformat(config)), file=fid)
        print(file=fid)
        print('{}._program_main()'.format(name), file=fid)
    with open(os.path.join(directory, '__init__.py'), 'wb') as fid:
        pass
    directory = os.path.dirname(directory)
    with open(os.path.join(directory, 'setup.py'), 'wb') as fid:
        pass

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Tool for rewriting Foxpro code in Python')
    parser.add_argument("infile", help="file to convert", type=str)
    parser.add_argument("outfile", help="file to output to", type=str)
    parser.add_argument("search", help="directories to search for included files", type=str, nargs='*')
    return parser.parse_args(argv)

def convert_file(infile, outfile):
    tic = Tic()
    if infile.lower().endswith('.pjx'):
        convert_project(infile, outfile)
        return
    elif infile.lower().endswith('.fpw'):
        return
    elif infile.lower().endswith('.h'):
        return
    elif infile.lower().endswith('.scx'):
        if os.path.isdir(outfile):
            name = (os.path.splitext(os.path.basename(infile).lower())[0] + '.py').lower()
            outfile = os.path.join(outfile, name)
        data = convert_scx_to_vfp_code(infile)
        tokens = preprocess_code(data).tokens
    elif infile.lower().endswith('.vcx'):
        print('.vcx files not currently supported')
        return
    elif infile.lower().endswith('.frx'):
        print('.frx files not currently supported')
        return
    elif infile.lower().endswith('.mnx'):
        print('.mnx files not currently supported')
        return
    elif infile.lower().endswith('.fll'):
        print('.fll files not currently supported')
        return
    elif infile.lower().endswith('.app'):
        print('.app can\'t be converted')
        return
    elif infile.lower().endswith('.prg'):
        if os.path.isdir(outfile):
            name = (os.path.splitext(os.path.basename(infile).lower())[0] + '.py').lower()
            outfile = os.path.join(outfile, name)
        tokens = preprocess_file(infile).tokens
    else:
        if os.path.isdir(outfile):
            name = os.path.basename(infile).lower()
            shutil.copy(infile, os.path.join(outfile, name))
        return
    print(tic.toc())
    tic.tic()
    data = 'procedure _program_main\n' + ''.join(token.text.replace('\r', '') for token in tokens)
    with tempfile.NamedTemporaryFile(suffix='.prg') as fid:
        pass
    with open(fid.name, 'wb') as fid:
        fid.write(data.encode('utf-8'))
    input_stream = antlr4.InputStream(data)
    lexer = VisualFoxpro9Lexer(input_stream)
    stream = MultichannelTokenStream(lexer)
    parser = VisualFoxpro9Parser(stream)
    print(tic.toc())
    tic.tic()
    tree = parser.prg()
    print(tic.toc())
    visitor = PythonConvertVisitor(os.path.splitext(os.path.basename(infile))[0])
    output_tree = visitor.visit(tree)
    output = add_indents(output_tree, 0)
    with open(outfile, 'wb') as fid:
        fid.write(output.encode('utf-8'))
    autopep8.main([__file__, '--in-place', outfile])

def main(argv=None):
    args = parse_args(argv)
    global SEARCH_PATH
    SEARCH_PATH = args.search
    convert_file(args.infile, args.outfile)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
