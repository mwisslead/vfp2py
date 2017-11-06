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

import isort

import antlr4

from VisualFoxpro9Visitor import VisualFoxpro9Visitor

import vfpfunc

class RedirectedBuiltin(object):
    def __init__(self, name):
        self.name = name
        self.func = getattr(__builtin__, name)

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except:
            return make_func_code(self.name, *args, **kwargs)

for func in ('chr', 'int', 'str', 'float'):
    globals()[func] = RedirectedBuiltin(func)

if sys.version_info >= (3,):
    unicode=str

def isinstance(obj, istype):
    if not __builtin__.isinstance(istype, tuple):
        istype = (istype,)
    istype = tuple(x.func if __builtin__.isinstance(x, RedirectedBuiltin) else x for x in istype)
    return __builtin__.isinstance(obj, istype)

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
        self.filesystem_caseless = True
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

    def visit_with_disabled_scope(self, ctx):
        self.enable_scope(False)
        retval = self.visit(ctx)
        self.enable_scope(True)
        return retval

    def getCtxText(self, ctx):
        start, stop = ctx.getSourceInterval()
        tokens = ctx.parser._input.tokens[start:stop+1]
        return ''.join(token.text for token in tokens)

    def visitPrg(self, ctx):
        self.scope = None

        if ctx.classDef():
            self.class_list = [self.visit(classDef.classDefStart())[0] for classDef in ctx.classDef()]
        if ctx.funcDef():
            self.function_list = [self.visit(funcdef.funcDefStart())[0] for funcdef in ctx.funcDef()]

        self.imports = ['from __future__ import division, print_function']
        defs = []

        for child in ctx.children:
            if isinstance(child, ctx.parser.FuncDefContext):
                self.used_scope = False
                funcname, parameters, funcbody = self.visit(child)
                defs += [CodeStr('def {}({}):'.format(funcname, ', '.join([str(repr(p)) + '=False' for p in parameters]))), funcbody]
            elif not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
                defs += self.visit(child)

        imports = isort.SortImports(file_contents='\n'.join(set(self.imports))).output.splitlines()
        return  [CodeStr(imp) for imp in imports] + defs

    def visitLine(self, ctx):
        try:
            retval = self.visitChildren(ctx)
            if retval is None:
                raise Exception('just to jump to except block')
        except:
            lines = self.getCtxText(ctx)
            print(lines)
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
        return self.visit(ctx.cmd() or ctx.setup())

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
        subclasses = {}
        for stmt in ctx.classDefProperty():
            assignment = self.visit(stmt)
            if isinstance(stmt, ctx.parser.ClassDefLineCommentContext) and assignment:
                assignments.append(assignment)
            elif isinstance(stmt, ctx.parser.ClassDefAddObjectContext):
                name, obj = assignment
                for stmt in ctx.classDefProperty():
                    if isinstance(stmt, ctx.parser.ClassDefAssignContext):
                        assignment = self.visit(stmt)
                        for (ident, value) in assignment:
                            if '.' in ident:
                                parent, ident = ident.split('.', 1)
                                if parent == name:
                                    obj['args'][ident] = CodeStr(value.replace(' = ', '', 1))
                obj['functions'] = {}
                for funcdef in ctx.funcDef():
                    self.used_scope = False
                    funcname, parameters, funcbody = self.visit(funcdef)
                    if '.' in funcname:
                        func_parent, funcname = funcname.rsplit('.', 1)
                        if func_parent == name:
                            parameters = [add_args_to_code('{}=False', (p,)) for p in parameters]
                            obj['functions'][funcname] = [parameters, funcbody]
                obj['args']['parent'] = CodeStr('self')
                obj['args']['name'] = name
                if obj['functions']:
                    subclass = 'SubClass' + name.title()
                    subclasses[subclass] = {key: obj[key] for key in ('parent_type', 'functions')}
                    obj['parent_type'] = 'self.' + subclass
                    self.class_list.append(obj['parent_type'])
                assignments.append(add_args_to_code('self.{} = {}', [CodeStr(name), self.func_call('createobject', obj['parent_type'], **obj['args'])]))
            else:
                for (ident, value) in assignment:
                    if '.' not in ident:
                        assignments.append(CodeStr('self.' + ident + value))
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
            parameters = [add_args_to_code('{}=False', (p,)) for p in parameters]
            if '.' not in funcname:
                funcs.update({funcname: [[CodeStr('self')] + parameters, funcbody, funcdef.start.line]})

        classname, supername = self.visit(ctx.classDefStart())

        self.used_scope = assign_scope
        funcbody = self.modify_func_body([CodeStr('{}._assign(self)'.format(supername))] + assignments)
        funcs['_assign'] = [[CodeStr('self'), CodeStr('*args'), CodeStr('**kwargs')], funcbody, float('inf')]

        retval = [CodeStr('class {}({}):'.format(classname, supername))]
        if funcs:
            for name in subclasses:
                subclass = subclasses[name]
                supername = CodeStr(subclass['parent_type'])
                if hasattr(vfpfunc, supername):
                    self.imports.append('from vfp2py import vfpfunc')
                    supername = add_args_to_code('{}.{}', (CodeStr('vfpfunc'), supername))
                elif supername not in self.class_list:
                    supername = add_args_to_code('vfpfunc.classes[{}]', (str(supername),))
                subclass_code = [CodeStr('class {}({}):'.format(name, supername))]
                for funcname in subclass['functions']:
                    parameters, funcbody = subclass['functions'][funcname]
                    parameters = [CodeStr('self')] + parameters
                    func = make_func_code(funcname, *parameters)
                    subclass_code.append([add_args_to_code('def {}:', (func,)), funcbody])
                retval.append(subclass_code)
            for funcname in funcs:
                parameters, funcbody, line_number = funcs[funcname]
                while comments and comments[0][1] < line_number:
                    retval.append([comments.pop(0)[0]])
                func = make_func_code(funcname, *parameters)
                retval.append([add_args_to_code('def {}:', (func,)), funcbody])
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
            raise Exception(str(classname) + ' is a reserved classname')
        if hasattr(vfpfunc, supername):
            self.imports.append('from vfp2py import vfpfunc')
            supername = add_args_to_code('{}.{}', (CodeStr('vfpfunc'), supername))
        elif supername not in self.class_list:
            supername = add_args_to_code('vfpfunc.classes[{}]', (str(supername),))
            pass
        return classname, supername

    def visitClassDefAssign(self, ctx):
        #FIXME - come up with a less hacky way to make this work
        args1 = self.visit_with_disabled_scope(ctx.assign())
        used_scope = self.used_scope
        args2 = self.visit(ctx.assign())
        args = []
        for arg1, arg2 in zip(args1, args2):
            ident = arg1[:arg1.find(' = ')]
            value = arg2[arg2.find(' = '):]
            if 'vfpvar' in value or 'vfpfunc.function' in value:
                used_scope = True
            args.append((ident, value))
        self.used_scope = used_scope
        return args

    def visitClassDefAddObject(self, ctx):
        name = str(self.visit_with_disabled_scope(ctx.identifier()))
        keywords = [self.visit_with_disabled_scope(idAttr) for idAttr in ctx.idAttr()[1:]]
        kwargs = {key: self.visit(expr) for key, expr in zip(keywords, ctx.expr())}
        objtype = create_string(self.visit_with_disabled_scope(ctx.idAttr()[0])).title()
        return name, {'parent_type': objtype, 'args': kwargs}

    def visitNodefault(self, ctx):
        return []

    def visitFuncDefStart(self, ctx):
        params = self.visit_with_disabled_scope(ctx.parameters()) or []
        params += self.visit_with_disabled_scope(ctx.parameterDef()) or []
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
                    newbody.append(CodeStr('return vfpvar.popscope({})'.format(return_value)))
                else:
                    newbody.append(line)
            return newbody
        self.imports.append('from vfp2py.vfpfunc import variable as vfpvar')
        body = [CodeStr('vfpvar.pushscope()')] + fix_returns(body)
        if isinstance(body[-1], CodeStr) and body[-1].startswith('return '):
            return body
        body.append(CodeStr('vfpvar.popscope()'))
        return body

    def visitFuncDef(self, ctx):
        name, parameters = self.visit(ctx.funcDefStart())
        self.new_scope()
        global FUNCNAME
        FUNCNAME = name
        self.scope.update({key: False for key in parameters})
        body = self.visit(ctx.lines())
        self.delete_scope()
        body = self.modify_func_body(body)
        return name, parameters, body

    def visitPrintStmt(self, ctx):
        kwargs = {}
        if len([child for child in ctx.children if child.getText() == '?']) > 1:
            kwargs['end'] = ''
        if ctx.DEBUGOUT():
            self.imports.append('import sys')
            kwargs['file'] = CodeStr('sys.stderr')
        return [make_func_code('print', *(self.visit(ctx.args()) or []), **kwargs)]

    def visitAtSay(self, ctx):
        if ctx.SAY() and len(ctx.SAY()) > 1:
            raise Exception('Invalid command')
        if ctx.SAY():
            return make_func_code('print', self.visit(ctx.sayExpr))

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
        retval = [self.visit(comment) for comment in ctx.lineComment()]

        items = [self.visit(elem) for elem in ctx.singleCase()]

        if not items:
            retval += [CodeStr('if True:'), [CodeStr('pass')]]
        else:
            expr, lines = items[0]
            retval += [CodeStr('if {}:'.format(expr)), lines]
            for expr, lines in items[1:]:
                retval += [CodeStr('elif {}:'.format(expr)), lines]

        if ctx.otherwise():
            retval += [CodeStr('else:'), self.visit(ctx.otherwise())]
        return retval

    def visitSingleCase(self, ctx):
        return self.visit(ctx.expr()), self.visit(ctx.lines())

    def visitOtherwise(self, ctx):
        return self.visit(ctx.lines())

    def visitForStart(self, ctx):
        loopvar = self.visit_with_disabled_scope(ctx.idAttr())
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
        kwargs = OrderedDict()
        if ctx.FOR():
            kwargs['condition'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr())])
        kwargs['scope'] = self.visit(ctx.scopeClause()) or ('rest',)
        func = make_func_code('vfpfunc.db.scanner', **kwargs)
        return [add_args_to_code('for _ in {}:', [func]), lines]

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
            names = [self.visit(ctx.identifier())]
            arrays = [make_func_code('vfpfunc.Array', *self.visit(ctx.arrayIndex()))]
            if ctx.LOCAL():
                for name in names:
                    self.scope[name] = False
                return [add_args_to_code('{} = {}', (name, array)) for name, array in zip(names, arrays)]
            func = 'vfpvar.add_public' if ctx.PUBLIC() else 'vfpvar.add_private'
            self.used_scope = True
            args = [str(name) for name in names]
            kwargs = {'{}_init_val'.format(name): array for name, array in zip(names, arrays)}
            return make_func_code(func, *args, **kwargs)
        else:
            names = self.visit_with_disabled_scope(ctx.parameters())
            if ctx.LOCAL():
                for name in names:
                    self.scope[name] = False
                return CodeStr(' = '.join([repr(arg) for arg in (names + [False])]) + ' #LOCAL Declaration')
            self.used_scope = True
            func = 'vfpvar.add_public' if ctx.PUBLIC() else 'vfpvar.add_private'
            return make_func_code(func, *[str(name) for name in names])

    def visitAssign(self, ctx):
        value = self.visit(ctx.expr())
        args = []
        for var in ctx.idAttr():
            trailer = self.visit(var.trailer()) or []
            if len(trailer) > 0 and isinstance(trailer[-1], list):
                identifier = self.visit(ctx.idAttr()[0].identifier())
                arg = self.createIdAttr(identifier, trailer[:-1])
                args.append('{}[{}]'.format(arg, ','.join(repr(x) for x in trailer[-1])))
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
        symbol_dict = {ctx.parser.GREATERTHAN: '>',
                       ctx.parser.GTEQ: '>=',
                       ctx.parser.LESSTHAN: '<',
                       ctx.parser.LTEQ: '<=',
                       ctx.parser.NOTEQUALS: '!=',
                       ctx.parser.HASH: '!=',
                       ctx.parser.EQUALS: '==',
                       ctx.parser.DOUBLEEQUALS: '==',
                       ctx.parser.DOLLAR: 'in',
                       ctx.parser.OR: 'or',
                       ctx.parser.AND: 'and'
                      }
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        symbol = symbol_dict[ctx.op.type]
        return CodeStr('{} {} {}'.format(repr(left), symbol, repr(right)))

    def visitBooleanOperation(self, ctx):
        return self.visitComparison(ctx)

    def visitUnaryNegation(self, ctx):
        return add_args_to_code('{}' if ctx.op.type == ctx.parser.PLUS_SIGN else '-{}', (self.visit(ctx.expr()),))

    def visitBooleanNegation(self, ctx):
        return CodeStr('not {}'.format(repr(self.visit(ctx.expr()))))

    def func_call(self, funcname, *args, **kwargs):
        if not kwargs and len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        args = list(args)
        funcname = {
            'at_c': 'at',
            'atcc': 'atc',
            'atcline': 'atline',
            'chrtranc': 'chrtran',
            'leftc': 'left',
            'lenc': 'len',
            'likec': 'like',
            'ratc': 'rat',
            'rightc': 'right',
            'select': 'select_function',
            'str': 'num_to_str',
            'stuffc': 'stuff',
            'substrc': 'substr',
            'sys': 'vfp_sys',
        }.get(funcname, funcname)
        if funcname == 'dodefault':
            return make_func_code('super(type(self), self).{}'.format(FUNCNAME), *args)
        if funcname in self.function_list:
            return make_func_code(funcname, *args)
        if funcname == 'chr' and len(args) == 1:
            return chr(int(args[0]))
        if funcname == 'val' and len(args) == 1:
            return float(args[0])
        if funcname == 'space' and len(args) == 1:
            args[0] = int(args[0])
            if isinstance(args[0], int) and args[0] > 8:
                args[0] = CodeStr(args[0])
            return args[0] * ' '
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
        if funcname == 'ains':
            return make_func_code(add_args_to_code('{}.insert', args[:1]), *([None] + args[1:]))
        if funcname == 'afields':
            localscode = make_func_code('locals')
            arrname = args.pop(0)
            if not args:
                args.append(None)
            if arrname.startswith('vfpvar['):
                arrname = CodeStr(arrname[7:-1]) #FIXME
            else:
                arrname = str(arrname)
            args.append(arrname)
            args.append((localscode, CodeStr('vfpvar')))
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
        if funcname in ('date', 'datetime', 'time', 'dtot'):
            self.imports.append('import datetime as dt')
            if len(args) == 0:
                if funcname == 'date':
                    return make_func_code('dt.datetime.now().date')
                elif funcname == 'datetime':
                    return make_func_code('dt.datetime.now')
                elif funcname == 'time':
                    return make_func_code('dt.datetime.now().time().strftime', '%H:%M:%S')
            else:
                if funcname == 'date':
                    return make_func_code('dt.date', *args)
                elif funcname == 'datetime':
                    return make_func_code('dt.datetime', *args)
                elif funcname == 'time':
                    return add_args_to_code('{}[:11]', [make_func_code('dt.datetime.now().time().strftime', '%H:%M:%S.%f')])
            if funcname == 'dtot':
                return make_func_code('dt.datetime.combine', args[0], make_func_code('dt.datetime.min.time'))
        if funcname in ('year', 'month', 'day', 'hour', 'minute', 'sec', 'dow', 'cdow', 'cmonth', 'dmy'):
            self.imports.append('import datetime as dt')
            funcname = {
                'sec': 'second',
                'dow': 'weekday()',
                'cdow': "strftime('%A')",
                'cmonth': "strftime('%B')",
                'dmy': "strftime('%d %B %Y')",
            }.get(funcname, funcname)
            retval = add_args_to_code('{}.{}', [args[0], CodeStr(funcname)])
            if funcname == 'weekday()':
                self.imports.append('from vfp2py import vfpfunc')
                return make_func_code('vfpfunc.dow_fix', retval, *args[1:])
            return retval
        if funcname in ('dtoc', 'dtos'):
            if len(args) == 1 or args[1] == 1:
                if len(args) < 2:
                    args.append('')
                if args[1] == 1 or funcname == 'dtos':
                    args[1] = add_args_to_code('\'%Y%m%d%H%M%S\' if hasattr({}, \'hour\') else \'%Y%m%d\'', [args[0]])
                else:
                    args[1] = add_args_to_code('\'%m/%d/%Y %H:%M:%S\' if hassattr({}, \'hour\') else \'%m/%d/%Y\'', [args[0]])
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
        if funcname in ('alltrim', 'ltrim', 'rtrim', 'trim', 'lower', 'upper', 'padr', 'padl', 'padc', 'proper'):
            funcname = {
                'alltrim': 'strip',
                'ltrim': 'rstrip',
                'rtrim': 'lstrip',
                'trim': 'lstrip',
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
        if funcname == 'getenv':
            args.append('')
            args[0] = args[0].upper() if string_type(args[0]) else add_args_to_code('{}.upper()', args[0])
            return make_func_code('os.environ.get', *args)
        if funcname == 'getwordcount':
            if len(args) < 2:
                args.append(CodeStr(''))
            return add_args_to_code('len([w for w in {}.split({}) if w])', args)
        if funcname == 'rand':
            self.imports.append('import random')
            return make_func_code('random.random')
        if funcname in ('ceiling', 'exp', 'log', 'log10', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 'pi', 'sqrt', 'dtor', 'rtod'):
            self.imports.append('import math')
            if funcname == 'pi':
                return CodeStr('math.pi')
            funcname = {
                'ceiling': 'ceil',
                'atn2': 'atan2',
                'rtod': 'degrees',
                'dtor': 'radians',
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
        if funcname in ('isalpha', 'islower', 'isdigit', 'isupper'):
            return add_args_to_code('{}[:1].{}()', [args[0], funcname])
        if funcname == 'inlist':
            return add_args_to_code('({} in {})', [args[0], tuple(args[1:])])
        if funcname == 'pythonfunctioncall' and len(args) == 3 and isinstance(args[2], tuple):
            self.imports.append('import {}'.format(args[0]))
            return make_func_code('{}.{}'.format(args[0], args[1]), *args[2])
        if funcname == 'createobject':
            if len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythontuple':
                return tuple(args[1:])
            elif len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythonlist':
                if len(args) > 1 and isinstance(args[1], list):
                    return add_args_to_code('{}.data[:]', args[1])
                return []
            elif len(args) > 0 and string_type(args[0]) and args[0].lower() == 'pythondictionary':
                return {}
            elif len(args) > 0 and string_type(args[0]):
                objtype = args[0]
                if not objtype.startswith('self.'):
                    objtype = objtype.title()
                args = args[1:]
                if objtype in self.class_list:
                    return make_func_code(objtype, *args, **kwargs)
                elif hasattr(vfpfunc, objtype):
                    self.imports.append('from vfp2py import vfpfunc')
                    objtype = 'vfpfunc.{}'.format(objtype)
                    return make_func_code(objtype, *args, **kwargs)
                else:
                    self.imports.append('from vfp2py import vfpfunc')
                    return make_func_code('vfpfunc.create_object', *([objtype] + args), **kwargs)
            else:
                return make_func_code('vfpfunc.create_object', *args, **kwargs)
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
        if funcname in ('file', 'directory', 'justdrive', 'justpath', 'justfname', 'juststem', 'justext', 'forceext', 'addbs', 'curdir'):
            if self.filesystem_caseless:
                args = [arg.lower() if string_type(arg) else arg for arg in args]
            self.imports.append('import os')
            operation = {
                'file': [make_func_code, ['os.path.isfile'] + args],
                'directory': [make_func_code, ['os.path.isdir'] + args],
                'justdrive': [add_args_to_code, ('os.path.splitdrive({})[0]', args)],
                'justpath': [make_func_code, ['os.path.dirname'] + args],
                'justfname': [make_func_code, ['os.path.basename'] + args],
                'juststem': [add_args_to_code, ('os.path.splitext(os.path.basename({}))[0]', args)],
                'justext': [add_args_to_code, ('os.path.splitext({})[1][1:]', args)],
                'forceext': [add_args_to_code, ('os.path.splitext({})[0] + \'.\' + {}', args)],
                'addbs': [make_func_code, ['os.path.join'] + args + ['']],
                'curdir': [make_func_code, ['os.getcwd']],
            }[funcname]
            return operation[0](*operation[1])
        if funcname == 'set' and len(args) > 0 and string_type(args[0]):
            args[0] = args[0].lower()
        if funcname == 'select_function' and not args:
            args = (add_args_to_code('{} if {} else {}', (0, CodeStr('vfpfunc.set(\'compatible\') == \'OFF\''), None)),)
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
            self.imports.append('from vfp2py.vfpfunc import variable as vfpvar')
            return add_args_to_code('vfpvar[{}]', [str(identifier)])
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
        elif trailer and len(trailer) > 1 and trailer[-2] == 'callmethod' and isinstance(trailer[-1], list) and len(trailer[-1]) == 2:
            trailer[-1][0] = CodeStr(trailer[-1][0])
            func = add_args_to_code('{}.{}', [self.createIdAttr(identifier, trailer[:-2])] + trailer[-1][:1])
            return make_func_code(func, *trailer[-1][1])
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
        retval = [self.visit_with_disabled_scope(ctx.identifier())]
        return retval + trailer

    def visitIdAttr(self, ctx):
        identifier = self.visit(ctx.identifier())
        trailer = self.visit(ctx.trailer())
        if ctx.PERIOD() and self.withid:
            trailer = [identifier] + (trailer or [])
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
        trailer = self.visit(ctx.trailer())
        if ctx.PERIOD() and self.withid:
            trailer = [atom] + (trailer or [])
            atom = self.withid

        if trailer and len(trailer) > 0 and not isinstance(trailer[-1], list) and isinstance(atom, CodeStr) and isinstance(ctx.parentCtx, ctx.parser.CmdContext):
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

    def visitCopyMoveFile(self, ctx):
        self.imports.append('import shutil')
        args = [self.visit(arg) for arg in ctx.specialExpr()] #args = [fromFile, toFile]
        if ctx.RENAME():
            return make_func_code('shutil.move', *args)
        else:
            return make_func_code('shutil.copyfile', *args)

    def visitChMkRmDir(self, ctx):
        self.imports.append('import os')
        funcname = 'os.' + {
            ctx.parser.CHDIR: 'chdir',
            ctx.parser.MKDIR: 'mkdir',
            ctx.parser.RMDIR: 'rmdir',
        }[ctx.children[0].symbol.type]
        return make_func_code(funcname, self.visit(ctx.specialExpr()))

    def visitSpecialExpr(self, ctx):
        expr = self.visit(ctx.pathname() or ctx.constant() or ctx.expr())
        return expr.lower() if string_type(expr) else expr

    def visitPathname(self, ctx):
        return create_string(ctx.getText())

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

    def visitCurrency(self, ctx):
        return round(float(ctx.NUMBER_LITERAL().getText()), 4)

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

    def visitAddition(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    def visitModulo(self, ctx):
        return self.operationExpr(ctx, '%')

    def extract_args_from_addbs(self, ctx):
        if not isinstance(ctx, ctx.parser.AdditionContext):
            return [self.visit(ctx)]
        leftctx, rightctx = ctx.expr()
        if isinstance(leftctx, ctx.parser.AtomExprContext) and self.visit(leftctx.atom()) == 'addbs' and isinstance(leftctx.trailer(), ctx.parser.FuncCallTrailerContext):
            args = self.extract_args_from_addbs(leftctx.trailer().args().expr(0))
        else:
            args = [self.visit(leftctx)]
        args.append(self.visit(rightctx))
        return args

    def operationExpr(self, ctx, operation):
        if operation == ctx.parser.PLUS_SIGN:
            args = self.extract_args_from_addbs(ctx)
            if len(args) > 2 or args[0] != self.visit(ctx.expr(0)):
                return make_func_code('os.path.join', *args)
        def add_parens(parent, child):
            expr = self.visit(child)
            if isinstance(child, ctx.parser.SubExprContext):
                return add_args_to_code('({})', (expr,))
            return expr
        left, right = [add_parens(ctx, expr) for expr in ctx.expr()]
        symbols = {
            '**': '**',
            '%': '%',
            ctx.parser.ASTERISK: '*',
            ctx.parser.FORWARDSLASH: '/',
            ctx.parser.PLUS_SIGN: '+',
            ctx.parser.MINUS_SIGN: '-'
        }
        if string_type(left) and string_type(right) and operation == ctx.parser.PLUS_SIGN:
            return left + right
        return add_args_to_code('{} {} {}', (left, CodeStr(symbols[operation]), right))

    def visitSubExpr(self, ctx):
        return add_args_to_code('{}', [self.visit(ctx.expr())])

    def visitFuncDo(self, ctx):
        func = self.visit(ctx.specialExpr(0))
        namespace = self.visit(ctx.specialExpr(1)) if ctx.IN() else ''
        args = self.visit(ctx.args()) if ctx.WITH() else []

        if ctx.FORM():
            func = func.replace('.', '_')
            return make_func_code('{}._program_main'.format(func))

        if os.path.splitext(namespace)[0] == self.filename:
            namespace = ''

        if not namespace:
            if func in self.function_list:
                return make_func_code(func, *args)

            if os.path.splitext(func)[1] in ('.prg', '.mpr', '.spr'):
                namespace = os.path.splitext(func)[0]
                if os.path.splitext(func)[1] in ('.mpr', '.spr'):
                    namespace += os.path.splitext(func)[1].replace('.', '_')
                func = '_program_main'
            else:
                self.imports.append('from vfp2py import vfpfunc')
                namespace = 'vfpfunc'
                func = create_string(add_args_to_code('function[{}]', [func]))

        if namespace.endswith('.prg'):
            namespace = namespace[:-4]

        if string_type(namespace) and re.match(tokenize.Name + '$', namespace) and not keyword.iskeyword(namespace):
            namespace = ntpath.normpath(ntpath.splitext(namespace)[0]).replace(ntpath.sep, '.')
            if namespace != 'vfpfunc':
                self.imports.append('import ' + namespace)
            mod = CodeStr(namespace)
        else:
            if string_type(namespace):
                namespace = CodeStr(repr(namespace))
            mod = make_func_code('vfpfunc.module', namespace)
        if string_type(func):
            func = CodeStr(func)
            func = add_args_to_code('{}.{}', (mod, func))
            if string_type(namespace):
                return make_func_code(func, *args)
        else:
            func = make_func_code('getattr', mod, func)

        return make_func_code(func, *args)

    def visitDoForm(self, ctx):
        form = self.visit_with_disabled_scope(ctx.specialExpr())

    def visitMethodCall(self, ctx):
        return self.visit(ctx.idAttr()) + '.' + self.visit(ctx.identifier()) + '()'

    def visitClearStmt(self, ctx):
        command = None
        args = []
        if len(ctx.children) > 1:
            if ctx.expr():
                args.append(self.visit(ctx.expr()))
            elif ctx.specialExpr():
                args.append(self.visit(ctx.specialExpr()))
            elif ctx.specialArgs():
                args += self.visit(ctx.specialArgs())
            elif ctx.ALL():
                args.append('all')
            if not ctx.ALL() or ctx.READ():
                command = create_string(ctx.children[1].getText().lower())
        return make_func_code('vfpfunc.clear', command, *args)

    def visitDllDeclare(self, ctx):
        dll_name = self.visit_with_disabled_scope(ctx.specialExpr())
        funcname = str(self.visit_with_disabled_scope(ctx.identifier()[0]))
        alias = str(self.visit_with_disabled_scope(ctx.alias)) if ctx.alias else None
        return make_func_code('vfpfunc.function.dll_declare', dll_name, funcname, alias)

    def visitReadEvent(self, ctx):
        return CodeStr('vfpfunc.read_events()')

    def on_event(self, ctx, func_prefix):
        func = self.visit(ctx.cmd())
        if func:
            if isinstance(func, list) and len(func) == 1:
                func = func[0]
            func = add_args_to_code('lambda: {}', (func,))
        return [add_args_to_code('{} = {}', (CodeStr(func_prefix), func),)]

    def visitOnError(self, ctx):
        return self.on_event(ctx, 'vfpfunc.error_func')

    def visitOnShutdown(self, ctx):
        return self.on_event(ctx, 'vfpfunc.shutdown_func')

    def visitRaiseError(self, ctx):
        expr = [self.visit(ctx.expr())] or []
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

    def visitFile(self, ctx):
        return ctx.getText()

    def visitRelease(self, ctx):
        scoped_args = []
        if ctx.ALL():
            args = []
        else:
            args = self.visit_with_disabled_scope(ctx.args())
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
                retval.append(make_func_code('vfpvar.release'))
            else:
                thisargs = [arg for arg in args if arg in ('this', 'thisform')]
                args = [arg for arg in args if arg not in ('this', 'thisform')]
                for arg in thisargs:
                    if arg == 'this':
                        retval.append(make_func_code('self.release()'))
                    if arg == 'thisform':
                        retval.append(make_func_code('self.parentform.release()'))
                if args:
                    self.imports.append('from vfp2py.vfpfunc import variable as vfpvar')
                    args = [add_args_to_code('vfpvar[{}]', [arg]) for arg in args]
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
        message = self.visit(ctx.message) or ''
        to_expr = self.visit(ctx.toExpr) if ctx.TO() else None
        window = ([self.visit(ctx.atExpr1), self.visit(ctx.atExpr2)] if ctx.AT() else [-1, -1]) if ctx.WINDOW() else []
        nowait = ctx.NOWAIT() != None
        noclear = ctx.NOCLEAR() != None
        timeout = self.visit(ctx.timeout) if ctx.TIMEOUT() else -1
        return make_func_code('vfpfunc.wait', message, to=to_expr, window=window, nowait=nowait, noclear=noclear, timeout=timeout)

    def visitOnKey(self, ctx):
        keys = [repr(str(self.visit(i))) for i in ctx.identifier()]
        return self.on_event(ctx, 'vfpfunc.on_key[{}]'.format(', '.join(keys)))

    def visitDeactivate(self, ctx):
        if ctx.MENU():
            func = 'vfpfunc.deactivate_menu'
        else:
            func = 'vfpfunc.deactivate_popup'
        args = self.visit_with_disabled_scope(ctx.parameters()) if not ctx.ALL() else []
        return make_func_code(func, *[str(arg) for arg in args])

    def visitThrowError(self, ctx):
        if ctx.expr():
            return add_args_to_code('raise {}', [self.visit(ctx.expr())])
        return CodeStr('raise')

    def visitCreateTable(self, ctx):
        if ctx.TABLE():
            func = 'vfpfunc.db.create_table'
        elif ctx.DBF():
            func = 'vfpfunc.db.create_dbf'
        elif ctx.CURSOR():
            func = 'vfpfunc.db.create_cursor'
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

    def visitAlterTable(self, ctx):
        tablename = self.visit(ctx.specialExpr())
        if ctx.ADD():
            tablesetup = zip(ctx.identifier()[::2], ctx.identifier()[1::2], [ctx.arrayIndex()])
            tablesetup = ((self.visit(id1), self.visit(id2), self.visit(size)) for id1, id2, size in tablesetup)
            setupstring = []
            for id1, id2, size in tablesetup:
                if id2.upper() == 'L' and len(size) == 1 and size[0] == 1:
                    setupstring.append('{} {}'.format(id1, id2))
                else:
                    setupstring.append('{} {}({})'.format(id1, id2, ', '.join(str(int(i)) for i in size)))
            setupstring = '; '.join(setupstring)
        else:
            setupstring = str(self.visit(ctx.identifier(0)))
        return make_func_code('vfpfunc.db.alter_table', tablename, 'add' if ctx.ADD() else 'drop', setupstring)

    def visitSelect(self, ctx):
        if ctx.tablename:
            return make_func_code('vfpfunc.db.select', self.visit(ctx.tablename))
        else:
            args = [arg for arg in self.visit(ctx.specialArgs())] if ctx.specialArgs() else ('*',)
            from_table = self.visit(ctx.fromExpr)
            into_table = self.visit(ctx.intoExpr)
            where_expr = self.visit(ctx.whereExpr)
            order_by = self.visit(ctx.orderbyid)
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
        kwargs = OrderedDict()
        shared = ctx.SHARED()
        exclusive = ctx.EXCLUSIVE()
        if shared and exclusive:
            raise Exception('cannot combine shared and exclusive')
        elif shared:
            opentype = 'shared'
        elif exclusive:
            opentype = 'exclusive'
        else:
            opentype = None
        if ctx.aliasExpr:
            kwargs['alias'] = self.visit(ctx.aliasExpr)
        name = self.visit(ctx.name)
        workarea = self.visit(ctx.workArea)
        if isinstance(workarea, float):
            workarea = int(workarea)
        return make_func_code('vfpfunc.db.use', name, workarea, opentype, **kwargs)

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

    def visitContinueLocate(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        return make_func_code('vfpfunc.db.continue_locate')

    def visitAppendFrom(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        if ctx.ARRAY():
            return make_func_code('vfpfunc.db.insert', None, self.visit(ctx.expr()))
        sourcename = self.visit(ctx.specialExpr(0))
        kwargs = {}
        if ctx.FOR():
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr())])
        if ctx.typeExpr:
            kwargs['filetype'] = self.visit(ctx.typeExpr)
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
        scope = self.visit(ctx.scopeClause()) or ('next', 1)
        field = self.visit_with_disabled_scope(ctx.specialExpr())
        if string_type(field):
            field = field.lower().rsplit('.', 1)
            tablename = field[0] if len(field) == 2 else None
            field = field[-1]
        else:
            tablename = None
        return make_func_code('vfpfunc.db.replace', tablename, scope, field, value)

    def visitSkipRecord(self, ctx):
        table = self.visit(ctx.specialExpr())
        skipnum = self.visit(ctx.expr()) or 1
        return make_func_code('vfpfunc.db.skip', table, skipnum)

    def visitCopyTo(self, ctx):
        copyTo = self.visit(ctx.specialExpr())
        if ctx.STRUCTURE():
            return make_func_code('vfpfunc.db.copy_structure', copyTo)

    def visitDeleteRecord(self, ctx):
        kwargs = OrderedDict()
        scope = self.visit(ctx.scopeClause()) or ('next', 1)
        name = self.visit(ctx.inExpr)
        if ctx.forExpr:
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.forExpr)])
        if ctx.whileExpr:
            kwargs['while_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.whileExpr)])
        if ctx.RECALL():
            kwargs['recall'] = True
        return make_func_code('vfpfunc.db.delete_record', name, scope, **kwargs)

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

    def visitCount(self, ctx):
        kwargs = OrderedDict()
        scope = self.visit(ctx.scopeClause()) or (('rest',) if ctx.whileExpr else ('all',))
        if ctx.forExpr:
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.forExpr)])
        if ctx.whileExpr:
            kwargs['while_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.whileExpr)])
        return add_args_to_code('{} = {}', (self.visit(ctx.toExpr), make_func_code('vfpfunc.db.count', None, scope, **kwargs)))

    def visitSum(self, ctx):
        kwargs = OrderedDict()
        scope = self.visit(ctx.scopeClause()) or (('rest',) if ctx.whileExpr else ('all',))
        if ctx.forExpr:
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.forExpr)])
        if ctx.whileExpr:
            kwargs['while_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.whileExpr)])
        sumexpr = add_args_to_code('lambda: {}', [self.visit(ctx.sumExpr)])
        return add_args_to_code('{} = {}', (self.visit(ctx.toExpr), make_func_code('vfpfunc.db.sum', None, scope, sumexpr, **kwargs)))

    def visitReindex(self, ctx):
        return make_func_code('vfpfunc.db.reindex', not not ctx.COMPACT())

    def visitSeekRecord(self, ctx):
        tablename = self.visit(ctx.tablenameExpr)
        seek_expr = self.visit(ctx.seekExpr)
        kwargs = OrderedDict()
        if ctx.orderExpr or ctx.tagName:
            kwargs['key_index'] = self.visit(ctx.orderExpr or ctx.tagName)
        if ctx.cdxFileExpr or ctx.idxFileExpr:
            kwargs['key_index_file'] = self.visit(ctx.cdxFileExpr or ctx.idxFileExpr)
        if ctx.DESCENDING():
            kwargs['descending'] = True
        return make_func_code('vfpfunc.db.seek', tablename, seek_expr, **kwargs)

    def visitZapTable(self, ctx):
        return make_func_code('vfpfunc.db.zap', self.visit(ctx.specialExpr()))

    def visitBrowse(self, ctx):
        self.imports.append('from vfp2py import vfpfunc')
        return make_func_code('vfpfunc.db.browse')

    def visitScatterExpr(self, ctx):
        pass

    def visitGatherExpr(self, ctx):
        pass

    def visitScopeClause(self, ctx):
        if ctx.ALL():
            return 'all',
        elif ctx.NEXT():
            return 'next', self.visit(ctx.expr())
        elif ctx.RECORD():
            return 'record', self.visit(ctx.expr())
        elif ctx.REST():
            return 'rest',

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
        elif setword in ('cursor', 'deleted', 'exact', 'multilocks', 'near', 'status', 'status bar', 'tableprompt', 'unique'):
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
        elif setword == 'classlib':
            args = (self.visit(ctx.specialExpr(0)),)
            if ctx.IN():
                kwargs['in'] = self.visit(ctx.specialExpr(1))
            if ctx.ALIAS():
                kwargs['alias'] = self.visit(ctx.specialExpr(2 if ctx.IN() else 1))
            if ctx.ADDITIVE():
                kwargs['additive'] = True
        elif setword == 'compatible':
            args = ('ON' if ctx.ON() or ctx.DB4() else 'OFF',)
            if ctx.PROMPT() or ctx.NOPROMPT():
                args = (args[0], 'PROMPT' if ctx.PROMPT() else 'NOPROMPT')
        elif setword == 'sysmenu':
            args = [x.symbol.text.lower() for x in (ctx.ON(), ctx.OFF(), ctx.TO(), ctx.SAVE(), ctx.NOSAVE()) if x]
            if ctx.expr():
                args += [self.visit(ctx.expr()[0])]
            elif ctx.DEFAULT():
                args += ['default']
        elif setword == 'date':
            args = (str(self.visit_with_disabled_scope(ctx.identifier())),)
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
            of_expr = self.visit(ctx.ofExpr)
            in_expr = self.visit(ctx.inExpr)
            kwargs.update({'descending': True} if ctx.DESCENDING() else {})
            kwargs.update({'tag': True} if ctx.TAG() else {})
            args = (order, of_expr, in_expr)
        elif setword == 'index':
            args = (self.visit(ctx.specialExpr(0)),)
        else:
            return
        return make_func_code('vfpfunc.set', setword, *args, **kwargs)

    def visitShellRun(self, ctx):
        start, stop = ctx.getSourceInterval()
        if ctx.identifier():
            pass #Add /N options
            start = ctx.identifier().getSourceInterval()[0]
        tokens = ctx.parser._input.tokens[start + 1:stop + 1]
        # FIXME: Need more cleanup on the arguments.
        command = ''.join(create_string(tok.text if tok.type != ctx.parser.STRING_LITERAL else tok.text[1:-1]) for tok in tokens).strip().split()
        for i, arg in enumerate(command):
            if arg.startswith('&'):
                command[i] = CodeStr(arg[1:])
        self.imports.append('import subprocess')
        return make_func_code('subprocess.call', command)

    def visitReturnStmt(self, ctx):
        if not ctx.expr():
            return [CodeStr('return')]
        return [add_args_to_code('return {}', [self.visit(ctx.expr())])]

    def visitAssert(self, ctx):
        if ctx.expr(1):
            return add_args_to_code('assert {}, {}', (self.visit(ctx.expr(0)), self.visit(ctx.expr(1))))
        else:
            return add_args_to_code('assert {}', (self.visit(ctx.expr(0)),))
