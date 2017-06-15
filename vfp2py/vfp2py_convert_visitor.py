from __future__ import print_function

import __builtin__

import sys
import os
import ntpath
import datetime as dt
import re
import tokenize
import keyword
from collections import OrderedDict

import random
import string

import antlr4

from VisualFoxpro9Lexer import VisualFoxpro9Lexer
from VisualFoxpro9Parser import VisualFoxpro9Parser
from VisualFoxpro9Visitor import VisualFoxpro9Visitor

import vfpfunc

STDLIBS = ['import sys', 'import os', 'import math', 'import datetime as dt', 'import subprocess', 'import base64']

class RedirectedBuiltin(object):
    def __init__(self, name):
        self.name = name
        self.func = getattr(__builtin__, name)

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except:
            return make_func_code(self.name, *args, **kwargs)

for func in ('chr', 'int', 'str'):
    globals()[func] = RedirectedBuiltin(func)

if sys.version_info >= (3,):
    unicode=str

def isinstance(obj, istype):
    if not __builtin__.isinstance(istype, tuple):
        istype = (istype,)
    istype = tuple(x.func if __builtin__.isinstance(x, RedirectedBuiltin) else x for x in istype)
    return __builtin__.isinstance(obj, istype)

def import_key(module):
    if module in STDLIBS:
        return STDLIBS.index(module)
    else:
        return len(STDLIBS)

def random_variable(length=10):
    return '_' + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

class CodeStr(unicode):
    def __repr__(self):
        return unicode(self)

    def __add__(self, val):
        return CodeStr('{} + {}'.format(self, repr(val)))

    def __sub__(self, val):
        return CodeStr('{} - {}'.format(self, repr(val)))

    def __mul__(self, val):
        return CodeStr('{} * {}'.format(self, repr(val)))

def get_list(should_be_list):
    try:
        return list(should_be_list)
    except TypeError:
        return [should_be_list]

def make_func_code(funcname, *args, **kwargs):
    args = [repr(x) for x in args]
    args += ['{}={}'.format(key, repr(kwargs[key])) for key in kwargs]
    return CodeStr('{}({})'.format(funcname, ', '.join(args)))

def string_type(val):
    return isinstance(val, (str, unicode)) and not isinstance(val, CodeStr)

def create_string(val):
    try:
        return str(val)
    except UnicodeEncodeError: #can this happen?
        return val

def add_args_to_code(codestr, args):
    return CodeStr(codestr.format(*[repr(arg) for arg in args]))

class PythonConvertVisitor(VisualFoxpro9Visitor):
    def __init__(self, filename):
        super(PythonConvertVisitor, self).__init__()
        self.filename = filename
        self.imports = []
        self.scope = {}
        self._saved_scope = None
        self._scope_count = 0
        self.withid = ''
        self.class_list = []
        self.function_list = []
        self.used_scope = False

    def visit(self, ctx):
        if ctx:
            return super(type(self), self).visit(ctx)

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
        self.scope = None

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

        try:
            funcbody = funcs['init'][1]
            if funcbody:
                funcs['init'][1] = [funcbody[0]] + assignments + funcbody[1:]
            else:
                self.used_scope = assign_scope
                funcs['init'][1] = self.modify_func_body(assignments)
        except KeyError:
            pass

        classname, supername = self.visit(ctx.classDefStart())
        retval = [CodeStr('class {}({}):'.format(classname, supername))]
        if funcs:
            for funcname in funcs:
                parameters, funcbody, line_number = funcs[funcname]
                while comments and comments[0][1] < line_number:
                    retval.append([comments.pop(0)[0]])
                retval.append([CodeStr('def {}({}):'.format(funcname, ', '.join([str(repr(p)) + '=False' for p in parameters]))), funcbody])
        else:
            retval.append([CodeStr('pass')])
        while comments:
            retval.append([comments.pop(0)[0]])

        return retval

    def visitClassDefStart(self, ctx):
        names = [CodeStr(self.visit(identifier).title()) for identifier in ctx.identifier()]
        if len(names) < 2:
            names.append('Custom')
        classname, supername = names
        if hasattr(vfpfunc, classname):
            raise Exception(classname + ' is a reserved classname')
        if hasattr(vfpfunc, supername):
            self.imports.append('from vfp2py import vfpfunc')
            supername = add_args_to_code('{}.{}', (CodeStr('vfpfunc'), supername))
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
        objtype = CodeStr(self.visit(ctx.idAttr()[0]).title())
        if hasattr(vfpfunc, objtype):
            self.imports.append('from vfp2py import vfpfunc')
        keywords = [self.visit(idAttr) for idAttr in ctx.idAttr()[1:]]
        self.enable_scope(True)
        kwargs = {key: self.visit(expr) for key, expr in zip(keywords, ctx.expr())}
        funcname = add_args_to_code('self.{} = {}', (name, objtype))
        retval = [make_func_code(funcname, **kwargs)]
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
                        newbody.append(add_args_to_code('function_return_value = {}', [return_value]))
                        newbody.append(CodeStr('vfpfunc.variable.popscope()'))
                        newbody.append(CodeStr('return function_return_value'))
                    else:
                        newbody.append(CodeStr('vfpfunc.variable.popscope()'))
                        newbody.append(line)
                else:
                    newbody.append(line)
            return newbody
        body = [CodeStr('vfpfunc.variable.pushscope()')] + fix_returns(body)
        if isinstance(body[-1], CodeStr) and body[-1].startswith('return '):
            return body
        body.append(CodeStr('vfpfunc.variable.popscope()'))
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
        kwargs = {}
        if len([child for child in ctx.children if child.getText() == '?']) > 1:
            kwargs['end'] = ''
        return [make_func_code('print', *(self.visit(ctx.args()) if ctx.args() else []), **kwargs)]

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
            return add_args_to_code('for {} in {}:', (loopvar, iterator))
        loop_start = int(self.visit(ctx.loopStart))
        loop_stop = int(self.visit(ctx.loopStop)) + 1
        if ctx.loopStep:
            loop_step = int(self.visit(ctx.loopStep))
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
        lines.append(make_func_code('vfpfunc.db.skip', None, 1))
        if ctx.FOR():
            condition = self.visit(ctx.expr())
            lines = [add_args_to_code('if not {}:', [condition]), [CodeStr('continue')]] + lines
        save_variable_name = CodeStr(random_variable(length=10) + '_current_record')
        save_recno = CodeStr('{} = {}'.format(save_variable_name, 'vfpfunc.db.recno()'))
        return_recno = make_func_code('vfpfunc.db.goto', None, CodeStr(save_variable_name))
        return [save_recno, CodeStr('while not vfpfunc.db.eof():'), lines, return_recno]

    def visitTryStmt(self, ctx):
        try_lines = self.visit(ctx.tryLines)
        finally_lines = self.visit(ctx.finallyLines) or []
        if not ctx.CATCH():
            return try_lines + finally_lines

        identifier = self.visit(ctx.identifier())
        if identifier:
            self.scope[identifier] = False

        try_lines = [CodeStr('try:'), try_lines]

        if identifier:
            catch_lines = [CodeStr('except Exception as {}:'.format(identifier))]
            catch_lines.append(make_func_code('#vfpfunc.pyexception_to_foxexception', identifier))
        else:
            catch_lines = [CodeStr('except:')]
        catch_lines.append(self.visit(ctx.catchLines))

        finally_lines = [CodeStr('finally:'), finally_lines] if finally_lines else []

        if ctx.identifier():
            del self.scope[identifier]

        return try_lines + catch_lines + finally_lines

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
                array = make_func_code('vfpfunc.Array', *value)
                return [
                    add_args_to_code('{} = {}', [name, array])
                ]
            func = 'vfpfunc.array'
            kwargs = {'public': True} if ctx.PUBLIC() else {}
            self.used_scope = True
            return make_func_code(func, *([str(name)] + value), **kwargs)
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
            return make_func_code(func, *[str(name) for name in names])

    def visitAssign(self, ctx):
        value = self.visit(ctx.expr())
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

    def visitBooleanOperation(self, ctx):
        return self.visitComparison(ctx)

    def visitUnaryNegation(self, ctx):
        if ctx.op.type == VisualFoxpro9Lexer.PLUS_SIGN:
            return CodeStr('{}'.format(repr(self.visit(ctx.expr()))))
        return CodeStr('-{}'.format(repr(self.visit(ctx.expr()))))

    def visitBooleanNegation(self, ctx):
        return CodeStr('not {}'.format(repr(self.visit(ctx.expr()))))

    def func_call(self, funcname, args):
        if funcname in self.function_list:
            return make_func_code(funcname, *args)
        if funcname == 'chr' and len(args) == 1:
            return chr(int(args[0]))
        if funcname == 'space' and len(args) == 1:
            return int(args[0]) * ' '
        if funcname == 'asc':
            return make_func_code('ord', CodeStr(str(repr(args[0])) + '[0]'))
        if funcname == 'len':
            return make_func_code('len', *args)
        if funcname == 'alen':
            if len(args) == 1:
                return make_func_code('len', *args)
            else:
                args[1] = int(args[1])
                return add_args_to_code('{}.alen({})', args)
        if funcname == 'ascan':
            if len(args) == 3:
                args = [add_args_to_code('{}[{}:]', [args[0], args[2]]), args[1]]
            elif len(args) == 4:
                args = [add_args_to_code('{}[{}:({} + {})]', [args[0], args[2], args[2], args[3]]), args[1]]
            if len(args) == 2:
                return add_args_to_code('{}.index({})', args)
        if funcname == 'empty':
            return add_args_to_code('(not {} if {} is not None else False)', args + args)
        if funcname == 'occurs':
            return add_args_to_code('{}.count({})', reversed(args))
        if funcname in ('at', 'rat'):
            funcname = {
                'at': 'find',
                'rat': 'rfind',
            }[funcname]
            return add_args_to_code('{}.{}({})', [args[1], CodeStr(funcname), args[0]]) + 1
        if funcname in ('repli', 'replicate'):
            args[1:] = [int(arg) for arg in args[1:]]
            return add_args_to_code('({} * {})', args)
        if funcname in ('date', 'datetime', 'time') and len(args) == 0:
            self.imports.append('import datetime as dt')
            if funcname == 'date':
                return make_func_code('dt.datetime.now().date')
            elif funcname == 'datetime':
                return make_func_code('dt.datetime.now')
            elif funcname == 'time':
                return make_func_code('dt.datetime.now().time().strftime', '%H:%M:%S')
        if funcname in ('year', 'month', 'day', 'hour', 'minute', 'sec', 'dow', 'cdow', 'cmonth'):
            funcname = {
                'sec': 'second',
                'dow': 'weekday()',
                'cdow': "strftime('%A')",
                'cmonth': "strftime('%B')",
            }.get(funcname, funcname)
            retval = add_args_to_code('{}.{}', [args[0], CodeStr(funcname)])
            if funcname in ('weekday()'):
                self.imports.append('from vfp2py import vfpfunc')
                return make_func_code('vfpfunc.dow_fix', retval, *args[1:])
            return retval
        if funcname == 'dtoc':
            if len(args) == 1 or args[1] == 1:
                if len(args) > 1 and args[1] == 1:
                    args[1] = '%Y%m%d'
                else:
                    args.append('%m/%d/%Y')
                return make_func_code('{}.{}'.format(args[0], 'strftime'), args[1])
        if funcname == 'iif' and len(args) == 3:
            return add_args_to_code('({} if {} else {})', [args[i] for i in (1, 0, 2)])
        if funcname == 'between':
            return add_args_to_code('({} <= {} <= {})', [args[i] for i in (1, 0, 2)])
        if funcname == 'nvl':
            return add_args_to_code('({} if {} is not None else {})', [args[0], args[0], args[1]])
        if funcname == 'evl':
            return add_args_to_code('({} or {})', args)
        if funcname == 'sign':
            return add_args_to_code('1 if {} > 0 else (-1 if {} < 0 else 0)', [args[0], args[0]])
        if funcname in ('alltrim', 'ltrim', 'rtrim', 'lower', 'upper', 'padr', 'padl', 'padc', 'proper'):
            funcname = {
                'alltrim': 'strip',
                'ltrim': 'lstrip',
                'rtrim': 'rstrip',
                'padr': 'ljust',
                'padl': 'rjust',
                'padc': 'center',
                'proper': 'title',
            }.get(funcname, funcname)
            funcname = '{}.{}'.format(repr(args[0]), funcname)
            return make_func_code(funcname, *args[1:])
        if funcname == 'strtran':
            args = args[:6]
            if len(args) > 3:
                args[3:] = [int(arg) for arg in args[3:]]
            if len(args) == 6 and int(args[5]) in (0, 2):
                args.pop()
            if len(args) == 2:
                args.append('')
            str_replace = add_args_to_code('{}.replace', [args[0]])
            if len(args) == 3:
                return make_func_code(str_replace, *args[1:])
            elif len(args) == 4 and args[3] < 2:
                args.pop()
                return make_func_code(str_replace, *args[1:])
            elif len(args) == 5 and args[3] < 2:
                args[3] = args[4]
                args.pop()
                return make_func_code(str_replace, *args[1:])
        if funcname == 'strconv' and len(args) == 2:
            self.imports.append('import base64')
            if args[1] == 13:
                return make_func_code('base64.b64encode', args[0])
            if args[1] == 14:
                return make_func_code('base64.b64decode', args[0])
        if funcname == 'right':
            args[1] = int(args[1])
            return add_args_to_code('{}[-{}:]', args)
        if funcname == 'left' and len(args) == 2:
            args[1] = int(args[1])
            return add_args_to_code('{}[:{}]', args)
        if funcname == 'substr':
            args[1:] = [int(arg) for arg in args[1:]]
            args[1] -= 1
            if len(args) < 3:
                return add_args_to_code('{}[{}:]', args)
            if args[2] == 1:
                return add_args_to_code('{}[{}]', args[:2])
            args[2] += args[1]
            return add_args_to_code('{}[{}:{}]', args)
        if funcname in ('ceiling', 'exp', 'log', 'log10', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'pi', 'sqrt'):
            self.imports.append('import math')
            if funcname == 'pi':
                return CodeStr('math.pi')
            funcname = {
                'ceiling': 'ceil',
                'atn2': 'atan2'
            }.get(funcname, funcname)
            funcname = 'math.' + funcname
            return make_func_code(funcname, *args)
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
            return add_args_to_code(op[funcname], [int(arg) for arg in args])
        if funcname in ('abs', 'round', 'max', 'min'):
            return make_func_code(funcname, *args)
        if funcname == 'int':
            return int(args[0])
        if funcname == 'isnull':
            return add_args_to_code('{} == {}', [args[0], None])
        if funcname == 'inlist':
            return add_args_to_code('({} in {})', [args[0], tuple(args[1:])])
        if funcname == 'pythonfunctioncall' and len(args) == 3:
            self.imports.append('import {}'.format(args[0]))
            return make_func_code('{}.{}'.format(args[0], args[1]), *args[2])
        if funcname == 'createobject':
            if len(args) > 0 and string_type(args[0]) and args[0].lower() in self.class_list:
                return make_func_code(args[0].lower(), *args[1:])
            elif len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythontuple':
                return tuple(args[1:])
            elif len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythonlist':
                if len(args) > 1 and isinstance(args[1], list):
                    return add_args_to_code('{}.data[:]', args[1])
                return []
            elif len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythondictionary':
                return {}
            else:
                return make_func_code('vfpfunc.create_object', *args)
        if funcname in ('fcreate', 'fopen'):
            opentypes = ('w', 'r') if funcname == 'fcreate' else ('r', 'w', 'r+')
            if len(args) > 1 and args[1] <= len(opentypes):
                args[1] = int(args[1])
                if isinstance(args[1], int):
                    args[1] = opentypes[args[1]]
                else:
                    args[1] = add_args_to_code({}[{}]).format(opentypes, args[1])
            else:
                args.append(opentypes[0])
            return make_func_code('open', *args)
        if funcname == 'fclose':
            return add_args_to_code('{}.close()', args)
        if funcname in ('fputs', 'fwrite'):
            if len(args) == 3:
                args[2] = int(args[2])
                args[1] = add_args_to_code('{}[:{}]', args[1:])
            if funcname == 'fputs':
                args[1] += '\r\n'
            return add_args_to_code('{}.write({})', args)
        if funcname in ('fgets', 'fread'):
            if funcname == 'fgets':
                code = '{}.readline({}).strip(\'\\r\\n\')'
            else:
                code = '{}.read({})'
            if len(args) < 2:
                args.append(CodeStr(''))
            else:
                args[1] = int(args[1])
            return add_args_to_code(code, args)
        if funcname == 'fseek':
            funcname = '{}.seek'.format(args[0])
            return make_func_code(funcname, *args[1:])
        if funcname in ('file', 'directory', 'justdrive', 'justpath', 'juststem', 'justext'):
            self.imports.append('import os')
            operation = {
                'file': [make_func_code, ['os.path.isfile'] + args],
                'directory': [make_func_code, ['os.path.isdir'] + args],
                'justdrive': [add_args_to_code, ('os.path.splitdrive({})[0]', args)],
                'justpath': [make_func_code, ['os.path.dirname'] + args],
                'justfname': [make_func_code, ['os.path.basename'] + args],
                'juststem': [add_args_to_code, ('os.path.splitext(os.path.basename({}))[0]', args)],
                'justext': [add_args_to_code, ('os.path.splitext({})[1][1:]', args)],
            }[funcname]
            return operation[0](*operation[1])
        if funcname == 'set' and len(args) > 0 and string_type(args[0]):
            args[0] = args[0].lower()
        funcname = {
            'sys': 'vfp_sys',
            'stuffc': 'stuff',
            'str': 'num_to_str',
        }.get(funcname, funcname)
        if funcname in dir(vfpfunc):
            self.imports.append('from vfp2py import vfpfunc')
            funcname = 'vfpfunc.' + funcname
        elif funcname in dir(vfpfunc.db):
            self.imports.append('from vfp2py import vfpfunc')
            funcname = 'vfpfunc.db.' + funcname
        else:
            funcname = self.scopeId(funcname, 'func')
        return make_func_code(funcname, *args)

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
            return add_args_to_code('vfpfunc.variable[{}]', [str(identifier)])
        elif vartype == 'func':
            return add_args_to_code('vfpfunc.function[{}]', [str(identifier)])

    def createIdAttr(self, identifier, trailer):
        if trailer and len(trailer) == 1 and isinstance(trailer[0], list):
            args = trailer[0]
            return self.func_call(identifier, args)
        elif trailer and len(trailer) > 1 and trailer[-2] == 'setitem' and isinstance(trailer[-1], list) and len(trailer[-1]) == 2:
            return add_args_to_code('{}[{}] = {}', [self.createIdAttr(identifier, trailer[:-2])] + trailer[-1])
        elif trailer and len(trailer) > 1 and trailer[-2] == 'getitem' and isinstance(trailer[-1], list) and len(trailer[-1]) == 1:
            return add_args_to_code('{}[{}]', [self.createIdAttr(identifier, trailer[:-2])] +  trailer[-1])
        elif trailer:
            trailer = self.convert_trailer_args(trailer)
        else:
            trailer = CodeStr('')
        identifier = self.scopeId(identifier, 'val')
        return add_args_to_code('{}{}', (identifier, trailer))

    def convert_trailer_args(self, trailers):
        retval = ''
        for trailer in trailers:
            if isinstance(trailer, list):
                retval += '({})'.format(', '.join(repr(t) for t in trailer))
            else:
                retval += '.' + trailer
        return CodeStr(retval)

    def visitFuncCallTrailer(self, ctx):
        trailer = self.visit(ctx.trailer()) or []
        retval = [[x for x in self.visit(ctx.args()) or []]]
        return retval + trailer

    def visitIdentTrailer(self, ctx):
        trailer = self.visit(ctx.trailer()) or []
        self.enable_scope(False)
        retval = [self.visit(ctx.identifier())]
        self.enable_scope(True)
        return retval + trailer

    def visitIdAttr(self, ctx):
        identifier = self.visit(ctx.identifier())
        trailer = self.visit(ctx.trailer())
        if ctx.PERIOD() and self.withid:
            trailer = [identifier] + (trailer if trailer else [])
            identifier = self.withid
        return self.createIdAttr(identifier, trailer)

    def visitIdAttr2(self, ctx):
        return CodeStr('.'.join(([self.withid] if ctx.startPeriod else []) + [self.visit(identifier) for identifier in ctx.identifier()]))

    def visitCastExpr(self, ctx):
        func = {
            'integer': 'int',
            'logical': 'bool',
        }[self.visit(ctx.datatype())]
        expr = self.visit(ctx.expr())
        return make_func_code(func, expr)

    def visitDatatype(self, ctx):
        name_map = {
            'w': 'blob',
            'blob': 'blob',
            'c': 'character',
            'char': 'character',
            'character': 'character',
            'y': 'currency',
            'currency': 'currency',
            'd': 'date',
            'date': 'date',
            't': 'datetime',
            'datetime': 'datetime',
            'b': 'double',
            'double': 'double',
            'f': 'float',
            'float': 'float',
            'g': 'general',
            'general': 'general',
            'i': 'integer',
            'int': 'integer',
            'integer': 'integer',
            'l': 'logical',
            'logical': 'logical',
            'm': 'memo',
            'memo': 'memo',
            'n': 'numeric',
            'num': 'numeric',
            'numeric': 'numeric',
            'q': 'varbinary',
            'varbinary': 'varbinary',
            'v': 'varchar',
            'varchar': 'varchar',
        }
        dtype = self.visit(ctx.identifier())
        try:
            return name_map[dtype]
        except KeyError:
            raise ValueError("invalid datatype '{}'".format(dtype))

    def visitAtomExpr(self, ctx):
        atom = self.visit(ctx.atom())
        trailer = self.visit(ctx.trailer()) if ctx.trailer() else None
        if ctx.PERIOD() and self.withid:
            trailer = [atom] + (trailer if trailer else [])
            atom = self.withid

        if trailer and len(trailer) > 0 and not isinstance(trailer[-1], list) and isinstance(atom, CodeStr) and isinstance(ctx.parentCtx, VisualFoxpro9Parser.CmdContext):
            return make_func_code(self.createIdAttr(atom, trailer))
        if isinstance(atom, CodeStr):
            return self.createIdAttr(atom, trailer)
        elif trailer:
            for i, t in enumerate(trailer):
                if isinstance(t, list):
                    trailer[i] = add_args_to_code('({})', t)
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
        return make_func_code('os.' + funcname, self.visit(ctx.specialExpr()))

    def visitSpecialExpr(self, ctx):
        expr = self.visit(ctx.pathname() or ctx.constant() or ctx.expr())
        if string_type(expr):
            expr = expr.lower()
        return expr

    def visitPathname(self, ctx):
        start, stop = ctx.getSourceInterval()
        tokens = ctx.parser._input.tokens[start:stop+1]
        data = ''.join(t.text for t in tokens)
        input_stream = antlr4.InputStream(data)
        lexer = VisualFoxpro9Lexer(input_stream)
        stream = antlr4.CommonTokenStream(lexer)
        parser = VisualFoxpro9Parser(stream)
        exprctx = parser.expr()
        if len(ctx.children) != stop - start + 1:
            return self.visit(exprctx)
        if isinstance(exprctx, VisualFoxpro9Parser.AtomExprContext) and \
            isinstance(exprctx.trailer(), VisualFoxpro9Parser.FuncCallTrailerContext):
            return self.visit(exprctx)

        return create_string(ctx.getText()).lower()

    def convert_number(self, num_literal):
        num = num_literal.getText()
        if num[-1:].lower() == 'e':
            num += '0'
        try:
            return int(num).real
        except:
            return float(num)

    def visitNumber(self, ctx):
        return self.convert_number(ctx.NUMBER_LITERAL())

    def visitBoolean(self, ctx):
        if ctx.T() or ctx.Y() or ctx.F() or ctx.N():
            return not (ctx.F() or ctx.N())
        raise Exception('Can\'t convert boolean:' + ctx.getText())

    def visitNull(self, ctx):
        return None

    def visitDate(self, ctx):
        if not ctx.NUMBER_LITERAL():
            return None
        numbers = [self.convert_number(num) for num in ctx.NUMBER_LITERAL()]
        am_pm = (self.visit(ctx.identifier()) or '').lower()
        if any(not isinstance(num, int) for num in numbers) or am_pm not in ('', 'a', 'am', 'p', 'pm'):
            raise ValueError('invalid date/datetime')
        if am_pm in ('p', 'pm'):
            numbers[3] += 12
        if len(numbers) < 4:
            return make_func_code('dt.date', *numbers)
        return make_func_code('dt.datetime', *numbers)

    def visitString(self, ctx):
        return create_string(ctx.getText()[1:-1])

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
            if string_type(expr) and string_type(exprs2[-1]):
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
        return add_args_to_code('({})', [self.visit(ctx.expr())])

    def visitFuncDo(self, ctx):
        self.enable_scope(False)
        func = self.visit(ctx.specialExpr()[0])
        self.enable_scope(True)
        if ctx.FORM():
            func = func.lower()
            func = func.replace('.', '_')
            return make_func_code('{}._program_main'.format(func))
        args = self.visit(ctx.args()) if ctx.args() else []
        if func.endswith('.mpr'):
            func = func[:-4]
            args = [func] + args
            self.imports.append('from vfp2py import vfpfunc')
            return make_func_code('vfpfunc.mprfile', *args)
        namespace = self.visit(ctx.specialExpr()[1]) if ctx.IN() else None
        if (not namespace or os.path.splitext(namespace)[0] == self.filename) and func in self.function_list:
            return make_func_code(func, *args)
        if not namespace:
            namespace = func
            func = '_program_main'
        if string_type(namespace) and re.match(tokenize.Name + '$', namespace) and not keyword.iskeyword(namespace):
            namespace = ntpath.normpath(ntpath.splitext(namespace)[0]).replace(ntpath.sep, '.')
            self.imports.append('import ' + namespace)
            mod = CodeStr(namespace)
        else:
            if string_type(namespace):
                namespace = CodeStr(repr(namespace))
            mod = make_func_code('__import__', namespace)
        if string_type(func):
            func = CodeStr(func)
            func = add_args_to_code('{}.{}', (mod, func))
            if string_type(namespace):
                return make_func_code(func, *args)
        else:
            func = make_func_code('getattr', mod, func)

        return add_args_to_code('{} #{}', [make_func_code(func, *args), CodeStr('NOTE: function call here may not work')])

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
            return make_func_code('vfpfunc.cleardlls', *self.visit(ctx.args()))
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
        return make_func_code('vfpfunc.function.dll_declare', dll_name, funcname, alias)

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

    def visitRaiseError(self, ctx):
        expr = [self.visit(ctx.expr())] if ctx.expr() else []
        return make_func_code('raise Exception', *expr)

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
            return make_func_code('vfpfunc.delete_file', filename, True)
        else:
            self.imports.append('import os')
            return make_func_code('os.remove', filename)

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
            args = final_args or None
        retval = []
        if scoped_args:
            for arg in scoped_args:
                self.scope.pop(arg)
            retval.append(CodeStr('del {}'.format(', '.join(scoped_args))))
        if args is not None:
            if ctx.PROCEDURE():
                retval.append(make_func_code('vfpfunc.function.release_procedure', *args))
            elif ctx.POPUPS():
                kwargs = {}
                if ctx.EXTENDED():
                    kwargs['extended'] = True
                retval.append(make_func_code('vfpfunc.function.release_popups', *args, **kwargs))
            elif ctx.ALL():
                retval.append(make_func_code('vfpfunc.variable.release'))
            else:
                thisargs = [arg for arg in args if arg in ('this', 'thisform')]
                args = [arg for arg in args if arg not in ('this', 'thisform')]
                for arg in thisargs:
                    if arg == 'this':
                        retval.append(make_func_code('self.release()'))
                    if arg == 'thisform':
                        retval.append(make_func_code('self.parentform.release()'))
                if args:
                    args = [add_args_to_code('vfpfunc.variable[{}]', [arg]) for arg in args]
                    retval.append(CodeStr('del {}'.format(', '.join(args))))
        return retval

    def visitCloseStmt(self, ctx):
        allflag = not not ctx.ALL()
        if ctx.TABLES():
            return make_func_code('vfpfunc.db.close_tables', allflag)
        if ctx.INDEXES():
            return make_func_code('vfpfunc.db.close_indexes', allflag)
        if ctx.DATABASES():
            return make_func_code('vfpfunc.db.close_databases', allflag)
        return make_func_code('vfpfunc.db.close_all')

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
        return make_func_code(func, *[str(arg) for arg in args])

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
        return make_func_code(func, tablename, setupstring, free)

    def visitSelect(self, ctx):
        if ctx.tablename:
            return make_func_code('vfpfunc.db.select', self.visit(ctx.tablename))
        else:
            args = [arg for arg in self.visit(ctx.specialArgs())] if ctx.specialArgs() else ('*',)
            from_table = self.visit(ctx.fromExpr) if ctx.fromExpr else None
            into_table = self.visit(ctx.intoExpr) if ctx.intoExpr else None
            where_expr = self.visit(ctx.whereExpr) if ctx.whereExpr else None
            order_by = self.visit(ctx.orderbyid) if ctx.orderbyid else None
            distinct = 'distinct' if ctx.DISTINCT() else None
            return make_func_code('vfpfunc.db.sqlselect', args, from_table, into_table, where_expr, order_by, distinct)

    def visitGoRecord(self, ctx):
        if ctx.TOP():
            record = 0
        elif ctx.BOTTOM():
            record = -1
        else:
            record = self.visit(ctx.expr())
        name = self.visit(ctx.specialExpr())
        return make_func_code('vfpfunc.db.goto', name, record)

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
        name = self.visit(ctx.name)
        workarea = self.visit(ctx.workArea)
        if isinstance(workarea, float):
            workarea = int(workarea)
        return make_func_code('vfpfunc.db.use', name, workarea, opentype)

    def visitLocate(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        kwargs = OrderedDict()
        if ctx.FOR() and ctx.WHILE():
            raise Exception('cannont have both FOR and WHILE in LOCATE command')
        if ctx.FOR():
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr(0))])
        if ctx.WHILE():
            kwargs['while_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr(0))])
        kwargs['nooptimize'] = ctx.NOOPTIMIZE()
        return make_func_code('vfpfunc.db.locate', **kwargs)

    def visitAppendFrom(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        sourcename = self.visit(ctx.specialExpr())
        kwargs = {}
        if ctx.FOR():
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr())])
        return make_func_code('vfpfunc.db.append_from', None, sourcename, **kwargs)

    def visitAppend(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        menupopup = not ctx.BLANK()
        tablename = self.visit(ctx.specialExpr())
        return make_func_code('vfpfunc.db.append', tablename, menupopup)

    def visitInsert(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        table = self.visit(ctx.specialExpr())
        if ctx.ARRAY() or ctx.NAME() or ctx.MEMVAR():
            values = self.visit(ctx.expr())
        else:
            values = self.visit(ctx.args())
            fields = self.visit(ctx.specialArgs())
            if fields:
                if len(fields) != len(values):
                    raise Exception('number of fields must match number of values')
                values = {field: value for field, value in zip(fields, values)}
            else:
                values = tuple(values)
        return make_func_code('vfpfunc.db.insert', table, values)

    def visitReplace(self, ctx):
        value = self.visit(ctx.expr(0))
        scope = self.visit(ctx.scopeClause())
        self.enable_scope(False)
        field = self.visit(ctx.specialExpr())
        self.enable_scope(True)
        return make_func_code('vfpfunc.db.replace', field, value, scope)

    def visitSkipRecord(self, ctx):
        table = self.visit(ctx.specialExpr())
        skipnum = self.visit(ctx.expr())
        return make_func_code('vfpfunc.db.skip', table, skipnum)

    def visitCopyTo(self, ctx):
        copyTo = self.visit(ctx.specialExpr())
        if ctx.STRUCTURE():
            return make_func_code('vfpfunc.db.copy_structure', copyTo)

    def visitDeleteRecord(self, ctx):
        kwargs = OrderedDict()
        scopetype, num = self.visit(ctx.scopeClause()) or ('next', 1)
        name = self.visit(ctx.inExpr)
        if ctx.forExpr:
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.forExpr)])
        if ctx.whileExpr:
            kwargs['while_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.whileExpr)])
        if ctx.RECALL():
            kwargs['recall'] = True
        return make_func_code('vfpfunc.db.delete_record', scopetype, num, **kwargs)

    def visitPack(self, ctx):
        if ctx.DATABASE():
            return make_func_code('vfpfunc.db.pack_database')
        elif ctx.DBF():
            pack = 'dbf'
        elif ctx.MEMO():
            pack = 'memo'
        else:
            pack = 'both'
        tablename = self.visit(ctx.tableName)
        workarea = self.visit(ctx.workArea)
        return make_func_code('vfpfunc.db.pack', pack, tablename, workarea)

    def visitIndexOn(self, ctx):
        field = self.visit(ctx.specialExpr()[0])
        indexname = self.visit(ctx.specialExpr()[1])
        tag_flag = not not ctx.TAG()
        compact_flag = not not ctx.COMPACT()
        if ctx.ASCENDING() and ctx.DESCENDING():
            raise Exception('Invalid statement: {}'.format(self.getCtxText(ctx)))
        order = 'descending' if ctx.DESCENDING() else 'ascending'
        unique_flag = not not ctx.UNIQUE()
        return make_func_code('vfpfunc.db.index_on', field, indexname, order, tag_flag, compact_flag, unique_flag)

    def visitReindex(self, ctx):
        return make_func_code('vfpfunc.db.reindex', not not ctx.COMPACT())

    def visitZapTable(self, ctx):
        return make_func_code('vfpfunc.db.zap', self.visit(ctx.specialExpr()))

    def visitBrowse(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        return make_func_code('vfpfunc.db.browse')

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
        return make_func_code('vfpfunc.report_form', formname)

    def visitSetCmd(self, ctx):
        setword = ctx.setword.text.lower()
        kwargs = {'set_value': True}
        args = ()
        if ctx.BAR():
            setword += ' bar'
        if setword == 'printer':
            if ctx.TO():
                if ctx.DEFAULT():
                    kwargs.update({'Default': True})
                elif ctx.NAME():
                    kwargs.update({'Name': self.visit(ctx.specialExpr()[0])})
                elif ctx.specialExpr():
                    kwargs.update({'File': self.visit(ctx.specialExpr()[0])})
                    if ctx.ADDITIVE():
                        kwargs.update({'additive': True})
            else:
                args = ('ON' if ctx.ON() else 'OFF',)
                kwargs.update({'prompt': True} if ctx.PROMPT() else {})
        elif setword == 'typeahead':
            args = (self.visit(ctx.expr()[0]),)
        elif setword == 'procedure':
            kwargs.update({'additive': True} if ctx.ADDITIVE() else {})
            args = [self.visit(expr) for expr in ctx.specialExpr()]
        elif setword == 'bell':
            args = ('TO', self.visit(ctx.specialExpr()[0])) if ctx.TO() else ('ON' if ctx.ON() else 'OFF',)
        elif setword in ('cursor', 'deleted', 'exact', 'multilocks', 'near', 'status', 'status bar', 'unique'):
            args = ('ON' if ctx.ON() else 'OFF',)
        elif setword == 'century':
            if ctx.TO():
                if len(ctx.expr()) > 0:
                    kwargs.update({'century': self.visit(ctx.expr()[0])})
                else:
                    kwargs.update({'century': 19})
                if len(ctx.expr()) > 1:
                    kwargs.update({'rollover': self.visit(ctx.expr()[1])})
                else:
                    kwargs.update({'rollover': 67})
            else:
                args = ('ON' if ctx.ON() else 'OFF',)
        elif setword == 'sysmenu':
            args = [x.symbol.text.lower() for x in (ctx.ON(), ctx.OFF(), ctx.TO(), ctx.SAVE(), ctx.NOSAVE()) if x]
            if ctx.expr():
                args += [self.visit(ctx.expr()[0])]
            elif ctx.DEFAULT():
                args += ['default']
        elif setword == 'date':
            self.enable_scope(False)
            args = (str(self.visit(ctx.identifier())),)
            self.enable_scope(True)
        elif setword == 'refresh':
            args = [self.visit(expr) for expr in ctx.expr()]
            if len(args) < 2:
                args.append(5)
        elif setword == 'notify':
            arg = 'ON' if ctx.ON() else 'OFF'
            if ctx.CURSOR():
                kwargs.update({'cursor': arg})
            else:
                args = (arg,)
        elif setword == 'clock':
            args = [x.symbol.text.lower() for x in (ctx.ON(), ctx.OFF(), ctx.TO(), ctx.STATUS()) if x]
            if ctx.expr():
                args += [self.visit(expr) for expr in ctx.expr()]
        elif setword == 'memowidth':
            args = (self.visit(ctx.expr()[0]),)
        elif setword == 'library':
            kwargs.update({'additive': True} if ctx.ADDITIVE() else {})
            args = [self.visit(expr) for expr in ctx.specialExpr()]
        elif setword == 'filter':
            args = [self.visit(expr) for expr in ctx.specialExpr()]
        elif setword == 'order':
            order = self.visit(ctx.specialExpr(0))
            of_expr = self.visit(ctx.ofExpr) if ctx.ofExpr else None
            in_expr = self.visit(ctx.inExpr) if ctx.inExpr else None
            kwargs.update({'descending': True} if ctx.DESCENDING() else {})
            kwargs.update({'tag': True} if ctx.TAG() else {})
            args = (order, of_expr, in_expr)
        elif setword == 'index':
            args = (self.visit(ctx.specialExpr(0)),)
        else:
            return
        return make_func_code('vfpfunc.set', setword, *args, **kwargs)

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
        return make_func_code('subprocess.call', command)

    def visitReturnStmt(self, ctx):
        if not ctx.expr():
            return [CodeStr('return')]
        return [add_args_to_code('return {}', [self.visit(ctx.expr())])]
