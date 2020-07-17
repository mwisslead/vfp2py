# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import logging
import ntpath
import datetime as dt
import re
import tokenize
import keyword
from collections import OrderedDict

import isort

import antlr4

from .VisualFoxpro9Visitor import VisualFoxpro9Visitor

from . import vfpfunc
from .vfpfunc import DB

from .function_abbreviations import expander as function_expander

if sys.version_info < (3,):
    str=unicode
    CHR = chr
    def chr(x):
        return CHR(x).decode('ascii')

class CodeStr(str):
    def __repr__(self):
        return str(self)

    def __add__(self, val):
        return CodeStr('{} + {}'.format(self, repr(val)))

    def __radd__(self, val):
        return CodeStr('{} + {}'.format(repr(val), self))

    def __sub__(self, val):
        return CodeStr('{} - {}'.format(self, repr(val)))

    def __rsub__(self, val):
        return CodeStr('{} - {}'.format(repr(val), self))

    def __mul__(self, val):
        return CodeStr('{} * {}'.format(self, repr(val)))

    def __rmul__(self, val):
        return CodeStr('{} * {}'.format(repr(val), self))
PASS = CodeStr('pass')

class RedirectedBuiltin(object):
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except:
            return make_func_code(self.name, *args, **kwargs)

for func in (chr, int, str, float):
    globals()[func.__name__] = RedirectedBuiltin(func)

real_isinstance = isinstance
def isinstance(obj, istype):
    if not real_isinstance(istype, tuple):
        istype = (istype,)
    istype = tuple(x.func if real_isinstance(x, RedirectedBuiltin) else x for x in istype)
    return real_isinstance(obj, istype)

class OperatorExpr(object):
    precedence = -1
    operator = '?'

    def __init__(self, *args):
        self.args = args

    def wrap_arg(self, arg):
        if isinstance(arg, OperatorExpr) and arg.precedence < self.precedence:
            return '({})'.format(repr(arg))
        return arg

    def __repr__(self):
        args = [self.wrap_arg(arg) for arg in self.args]
        if len(args) == 1:
            return '{}{}'.format(self.operator, args[0])
        else:
            return '{}{}{}'.format(args[0], self.operator, args[1])

class OrExpr(OperatorExpr):
    precedence = 0
    operator = ' or '

class AndExpr(OperatorExpr):
    precedence = 1
    operator = ' and '

class NotExpr(OperatorExpr):
    precedence = 2
    operator = 'not '

def make_func_code(funcname, *args, **kwargs):
    args = [repr(x) for x in args]
    if not all(valid_identifier(name) for name in kwargs):
        args.append(add_args_to_code('**{}', [kwargs]))
    else:
        args += ['{}={}'.format(key, repr(kwargs[key])) for key in kwargs]
    return CodeStr('{}({})'.format(funcname, ', '.join(args)))

def string_type(val):
    return isinstance(val, str) and not isinstance(val, CodeStr)

def create_string(val):
    try:
        return str(val)
    except UnicodeEncodeError: #can this happen?
        return val

def add_args_to_code(codestr, args):
    return CodeStr(codestr.format(*[repr(arg) for arg in args]))

def valid_identifier(name):
    return re.match(tokenize.Name + '$', name) and not keyword.iskeyword(name)

class PythonConvertVisitor(VisualFoxpro9Visitor):
    def __init__(self, filename):
        super(PythonConvertVisitor, self).__init__()
        self.filename = filename
        self.filesystem_caseless = True
        self.imports = []
        self.scope = True
        self.withid = ''
        self.class_list = []
        self.function_list = []
        self.skip_extract = False

    def visit(self, ctx):
        if ctx:
            return super(type(self), self).visit(ctx)

    def visit_with_disabled_scope(self, ctx):
        self.scope = False
        retval = self.visit(ctx)
        self.scope = True
        return retval

    def list_visit(self, list_ctx):
        return [self.visit(x) for x in list_ctx]

    def getCtxText(self, ctx):
        start, stop = ctx.getSourceInterval()
        tokens = ctx.parser._input.tokens[start:stop+1]
        return ''.join(token.text for token in tokens)

    def visitPrg(self, ctx):
        if ctx.classDef():
            self.class_list = [self.visit(classDef.classDefStart())[0] for classDef in ctx.classDef()]
        if ctx.funcDef():
            self.function_list = [self.visit(funcdef.funcDefStart())[0] for funcdef in ctx.funcDef()]

        self.imports = ['from __future__ import division, print_function']
        self.imports.append('from vfp2py import vfpfunc')
        self.imports.append('from vfp2py.vfpfunc import DB, Array, C, F, M, S')
        self.imports.append('from vfp2py.vfpfunc import parameters, lparameters, vfpclass')
        defs = []

        for i, child in enumerate(ctx.children):
            if isinstance(child, ctx.parser.FuncDefContext):
                funcname, decorator, funcbody = self.visit(child)
                if i == 0 and funcname == '_program_main':
                    funcname = CodeStr('MAIN')
                defs += [
                    add_args_to_code('@{}', (decorator,)),
                    add_args_to_code('def {}():', (funcname,)),
                    funcbody
                ]
                if child.lineComment():
                    defs += sum((self.visit(comment) for comment in child.lineComment()), [])
            elif not isinstance(child, antlr4.tree.Tree.TerminalNodeImpl):
                defs += self.visit(child)

        imports = isort.SortImports(file_contents='\n'.join(set(self.imports)), line_length=100000).output.splitlines()
        return  [CodeStr(imp) for imp in imports] + defs

    def visitLine(self, ctx):
        try:
            retval = self.visit(ctx.cmd() or ctx.controlStmt() or ctx.lineComment())
            if retval is None:
                if ctx.MACROLINE():
                    retval = make_func_code('vfpfunc.macro_eval', create_string(ctx.MACROLINE().getText()))
                else:
                    raise Exception('just to jump to except block')
        except Exception as err:
            logging.getLogger(__name__).exception(str(err))
            lines = self.getCtxText(ctx)
            print(lines)
            retval = [CodeStr('#FIX ME: {}'.format(line)) for line in lines.split('\n') if line]
        return retval if isinstance(retval, list) else [retval]

    def visitLineComment(self, ctx):
        fixer = re.compile('^\s*(&&|\*!\*|\**)(.*[^*; ]\s*|.*[^* ];\s*|;\s*)?(\**)\s*;*$')
        def repl(match):
            groups = match.groups()
            if not any(groups):
                return ''
            start = '*' if not groups[0] or groups[0] in ('&&', '*!*') else groups[0]
            middle = groups[1] or ''
            end = groups[2] or ''
            if len(start) == 1 and not end:
                middle = middle.strip()
            return ('#' * len(start) + middle + '#' * len(end)).strip()
        comments = [comment.strip() for comment in self.getCtxText(ctx).splitlines()]
        return [CodeStr(fixer.sub(repl, comment)) for comment in comments]

    def visitLines(self, ctx):
        retval = sum((self.visit(line) for line in ctx.line()), [])
        def badline(line):
            return line.startswith('#') or not line if hasattr(line, 'startswith') else not line
        if not retval or all(badline(l) for l in retval):
            retval.append(PASS)
        return retval

    def visitNongreedyLines(self, ctx):
        return self.visitLines(ctx)

    def modify_superclass(self, supername):
        if hasattr(vfpfunc, supername):
            supername = add_args_to_code('{}.{}', (CodeStr('vfpfunc'), supername))
        elif supername in self.class_list:
            supername = add_args_to_code('{}Type()', (supername,))
        else:
            supername = add_args_to_code('C[{}]', (str(supername),))
        return supername

    def visitClassDef(self, ctx):
        assignments = []
        subclasses = {}

        funcdefs = [x.funcDef() for x in ctx.classProperty() if x.funcDef()]
        classassigns = [self.visitClassAssign(stmt.cmd()) for stmt in ctx.classProperty() if isinstance(stmt.cmd(), ctx.parser.AssignContext)]
        for stmt in ctx.classProperty():
            stmt = stmt.lineComment() or stmt.cmd()
            if isinstance(stmt, ctx.parser.LineCommentContext):
                assignments += self.visit(stmt)
            elif isinstance(stmt, ctx.parser.AssignContext):
                assignments += [CodeStr('self.' + ident + value) for (ident, value) in self.visitClassAssign(stmt) if '.' not in ident]
            elif isinstance(stmt, ctx.parser.AddObjectContext):
                name, obj = self.visit(stmt)
                for assignment in classassigns:
                    for (ident, value) in assignment:
                        if '.' in ident:
                            parent, ident = ident.split('.', 1)
                            if parent == name:
                                obj['args'][ident] = CodeStr(value.replace(' = ', '', 1))
                obj['functions'] = {}
                for funcdef in funcdefs:
                    funcname, decorator, funcbody = self.visit(funcdef)
                    if '.' in funcname:
                        func_parent, funcname = funcname.rsplit('.', 1)
                        if func_parent == name:
                            obj['functions'][funcname] = [decorator, funcbody]
                obj['args']['parent'] = CodeStr('self')
                obj['args']['name'] = name
                if obj['functions']:
                    subclass = 'SubClass' + name.title()
                    subclasses[subclass] = {key: obj[key] for key in ('parent_type', 'functions')}
                    obj['parent_type'] = 'self.' + str(subclass)
                    self.class_list.append(obj['parent_type'])
                assignments.append(add_args_to_code('self.{} = {}', [CodeStr(name), self.func_call('createobject', obj['parent_type'], **obj['args'])]))


        funcs = OrderedDict((
            ('_assign', [None, None, float('inf')]),
        ))
        for funcdef in funcdefs:
            funcname, decorator, funcbody = self.visit(funcdef)
            if '.' not in funcname:
                funcs[funcname] = [decorator, funcbody, funcdef.start.line]
            assignments += sum((self.visit(comment) for comment in funcdef.lineComment()), [])

        classname, supername = self.visit(ctx.classDefStart())

        funcbody = [CodeStr('BaseClass._assign(self)')] + assignments
        self.modify_func_body(funcbody)
        funcs['_assign'][1] = funcbody
        funcs['_assign'][0] = make_func_code('lparameters')

        retval = [
            add_args_to_code('BaseClass = {}', (supername,)),
            CodeStr('class {}(BaseClass):'.format(classname)),
        ]
        if funcs:
            for name in subclasses:
                subclass = subclasses[name]
                supername = self.modify_superclass(CodeStr(subclass['parent_type']))
                subclass_code = [CodeStr('class {}({}):'.format(name, supername))]
                for funcname in subclass['functions']:
                    decorator, funcbody = subclass['functions'][funcname]
                    subclass_code.append([
                        add_args_to_code('@{}', (decorator,)),
                        add_args_to_code('def {}(self):', (CodeStr(funcname),)),
                        funcbody,
                    ])
                retval.append(subclass_code)
            for funcname in funcs:
                decorator, funcbody, line_number = funcs[funcname]
                retval.append([
                    add_args_to_code('@{}', (decorator,)),
                    add_args_to_code('def {}(self):', (CodeStr(funcname),)),
                    funcbody,
                ])
        else:
            retval.append([PASS])
        retval.append(add_args_to_code('return {}', (classname,)))
        retval = [
            CodeStr('@vfpclass'),
            add_args_to_code('def {}():', (classname,)),
            retval,
        ]

        return retval + sum((self.visit(comment) for comment in ctx.lineComment()), [])

    def visitClassDefStart(self, ctx):
        names = [self.visit(ctx.identifier())] + [self.visit(ctx.asTypeOf())[0]]
        names = [CodeStr(name.title()) for name in names]
        if len(names) < 2:
            names.append('Custom')
        classname, supername = names
        if hasattr(vfpfunc, classname):
            raise Exception(str(classname) + ' is a reserved classname')
        supername = self.modify_superclass(supername)
        return classname, supername

    def visitClassAssign(self, assign):
        #FIXME - come up with a less hacky way to make this work
        args1 = self.visit_with_disabled_scope(assign)
        args2 = self.visit(assign)
        args = []
        for arg1, arg2 in zip(args1, args2):
            ident = arg1[:arg1.find(' = ')]
            value = arg2[arg2.find(' = '):]
            args.append((ident, value))
        return args

    def visitAddObject(self, ctx):
        name = str(self.visit_with_disabled_scope(ctx.identifier()))
        keywords = [self.visit_with_disabled_scope(idAttr) for idAttr in ctx.idAttr()]
        kwargs = {key: self.visit(expr) for key, expr in zip(keywords, ctx.expr())}
        objtype = create_string(self.visit_with_disabled_scope(ctx.asType())).title()
        return name, {'parent_type': objtype, 'args': kwargs}

    def visitFuncDefStart(self, ctx):
        params = self.visit_with_disabled_scope(ctx.parameters()) or []
        return self.visit(ctx.idAttr2()), params

    def visitParameter(self, ctx):
        return self.visit(ctx.idAttr())

    def visitParameters(self, ctx):
        return self.list_visit(ctx.parameter())

    def modify_func_body(self, body):
        while len(body) > 0 and (not body[-1] or (isinstance(body[-1], CodeStr) and (body[-1] == 'return'))):
            body.pop()
        if len(body) == 0:
            body.append(PASS)
        while PASS in body:
            body.pop(body.index(PASS))
        if not body:
            body.append(PASS)

    def visitFuncDef(self, ctx):
        name, parameters = self.visit(ctx.funcDefStart())
        if parameters:
            parameter_type = 'l'
        else:
            try:
                parameter_line = next(line for line in ctx.lines().line() if not line.lineComment())
                parameter_cmd = parameter_line.cmd()
                parameter_type = parameter_cmd.PARAMETER().symbol.text.lower()[0]
                parameters = [self.visit_with_disabled_scope(p)[0] for p in parameter_cmd.declarationItem()]
                lines = ctx.lines()
                children = [c for c in lines.children if c is not parameter_line]
                while lines.children:
                    lines.removeLastChild()
                for child in children:
                    lines.addChild(child)
            except (StopIteration, AttributeError):
                parameters = []
                parameter_type = 'l'
        if parameter_type != 'l':
            parameter_type = ''
        parameter_type += 'parameters'
        parameters = [str(p) for p in parameters]
        decorator = make_func_code(parameter_type, *parameters)
        global FUNCNAME
        FUNCNAME = name
#        body = self.modify_func_body(self.visit(ctx.lines()))
        body = self.visit(ctx.lines())
        return name, decorator, body

    def visitPrintStmt(self, ctx):
        kwargs = {}
        if len([child for child in ctx.children if child.getText() == '?']) > 1:
            kwargs['end'] = ''
        if ctx.DEBUGOUT():
            self.imports.append('import sys')
            kwargs['file'] = CodeStr('sys.stderr')
        return [make_func_code('print', *(self.visit(ctx.args()) or []), **kwargs)]

    def visitAtPos(self, ctx):
        if ctx.SAY() and len(ctx.SAY()) > 1:
            raise Exception('Invalid command')
        if ctx.sayExpr:
            func = make_func_code('print', self.visit(ctx.sayExpr))
        else:
            func = make_func_code('print')
        return add_args_to_code('{} # {}', [func, CodeStr(self.getCtxText(ctx))])

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
        retval = self.list_visit(ctx.lineComment())

        items = self.list_visit(ctx.singleCase())

        if not items:
            retval += [CodeStr('if True:'), [PASS]]
        else:
            expr, lines = items[0]
            retval += [CodeStr('if {}:'.format(expr)), lines]
            for expr, lines in items[1:]:
                retval += [CodeStr('elif {}:'.format(expr)), lines]

        if ctx.otherwise():
            retval += [CodeStr('else:'), self.visit(ctx.otherwise())]
        return retval

    def visitSingleCase(self, ctx):
        return self.visit(ctx.expr()), self.visit(ctx.nongreedyLines())

    def visitOtherwise(self, ctx):
        return self.visit(ctx.lines())

    def visitForStart(self, ctx):
        loopvar = self.visit(ctx.idAttr())
        if ctx.EACH():
            iterator = self.visit(ctx.expr(0))
        else:
            args = [int(self.visit(ctx.loopStart)), int(self.visit(ctx.loopStop)) + 1]
            if ctx.loopStep:
                args.append(int(self.visit(ctx.loopStep)))
            iterator = make_func_code('range', *args)
        return add_args_to_code('for {} in {}:', (loopvar, iterator))

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
        func = make_func_code('DB.scanner', **kwargs)
        return [add_args_to_code('for _ in {}:', [func]), lines]

    def visitTryStmt(self, ctx):
        try_lines = self.visit(ctx.tryLines)
        finally_lines = self.visit(ctx.finallyLines) or []
        if not ctx.CATCH():
            return try_lines + finally_lines

        try_lines = [CodeStr('try:'), try_lines]

        if ctx.identifier():
            identifier = add_args_to_code('S.{}', (self.visit(ctx.identifier()[0]),))

            catch_lines = [CodeStr('except Exception as err:')]
            catch_lines.append([add_args_to_code('{} = {}', [identifier, make_func_code('vfpfunc.Exception.from_pyexception', CodeStr('err'))])])
        else:
            catch_lines = [CodeStr('except Exception:')]
        if ctx.expr():
            when = self.visit(ctx.expr()[0])
            catch_lines.append([add_args_to_code('if not ({}):', (when,)), [CodeStr('raise')]])
        catch_lines.append(self.visit(ctx.catchLines))

        finally_lines = [CodeStr('finally:'), finally_lines] if finally_lines else []

        return try_lines + catch_lines + finally_lines

    def visitProgramControl(self, ctx):
        action = ctx.PROGRAMCONTROL().symbol.text.lower()
        action = {
            'loop': 'continue',
            'exit': 'break',
            'quit': 'vfpfunc.quit()',
        }.get(action, None)
        return CodeStr(action) if action else None

    def visitDeclaration(self, ctx):
        if ctx.EXTERNAL():
            return
        scope = ctx.SCOPE().getText().lower() if ctx.SCOPE() else None
        if ctx.PARAMETER():
            return
        names = [self.visit_with_disabled_scope(x)[0] for x in ctx.declarationItem()]
        inds = [self.visit(x)[1] for x in ctx.declarationItem()]
        if ctx.ARRAY() or ctx.DIMENSION() or ctx.DECLARE():
            inds = [ind or (1,) for ind in inds]

        if scope in ('hidden', 'protected'):
            names = [add_args_to_code('self.{}', [name]) if valid_identifier(name) else CodeStr('getattr(self, {}'.format(name)) for name in names]

        arrays = [(name, make_func_code('Array', *ind)) for name, ind in zip(names, inds) if ind]

        if scope in ('public', 'private', 'local'):
            func = 'M.add_'  + scope
            kwargs = {str(name): array for name, array in arrays}
            names = [str(name) for name, ind in zip(names, inds) if not ind]
            return make_func_code(func, *names, **kwargs)
        else:
            names = [name for name, ind in zip(names, inds) if not ind]
            return [CodeStr(' = '.join(repr(arg) for arg in (names + [False])))] if names else [] + \
                   [add_args_to_code('{} = {}', (name, array)) for name, array in arrays]

    def visitDeclarationItem(self, ctx):
        return self.visit(ctx.idAttr() or ctx.idAttr2()), self.visit(ctx.arrayIndex())

    def visitAsTypeOf(self, ctx):
        return self.visit(ctx.asType()), self.visit(ctx.specialExpr())

    def visitAsType(self, ctx):
        return self.visit_with_disabled_scope(ctx.datatype().idAttr())

    def visitAssign(self, ctx):
        value = self.visit(ctx.expr())
        args = []
        for var in ctx.idAttr():
            trailer = self.visit(var.trailer()) or []
            if len(trailer) > 0 and isinstance(trailer[-1], list):
                identifier = self.visit(var.identifier())
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
        exprs = [ctx.expr()] + [arg.expr() for arg in ctx.argsItem()]
        return [self.visit(expr) if expr else False for expr in exprs]

    def visitSpecialArgs(self, ctx):
        return self.list_visit(ctx.specialExpr())

    def visitComparison(self, ctx):
        symbol_dict = {
            ctx.parser.GREATERTHAN: '>',
            ctx.parser.GTEQ: '>=',
            ctx.parser.LESSTHAN: '<',
            ctx.parser.LTEQ: '<=',
            ctx.parser.NOTEQUALS: '!=',
            ctx.parser.HASH: '!=',
            ctx.parser.EQUALS: '==',
            ctx.parser.DOUBLEEQUALS: '==',
            ctx.parser.DOLLAR: 'in',
            ctx.parser.OR: 'or',
            ctx.parser.OTHEROR: 'or',
            ctx.parser.AND: 'and',
            ctx.parser.OTHERAND: 'and',
        }
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        symbol = symbol_dict[ctx.op.type]
        return CodeStr('{} {} {}'.format(repr(left), symbol, repr(right)))

    def visitBooleanOr(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        return OrExpr(left, right)

    def visitBooleanAnd(self, ctx):
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        return AndExpr(left, right)

    def visitUnaryNegation(self, ctx):
        return add_args_to_code('{}' if ctx.op.type == ctx.parser.PLUS_SIGN else '-{}', (self.visit(ctx.expr()),))

    def visitBooleanNegation(self, ctx):
        return NotExpr(self.visit(ctx.expr()))

    def func_call(self, funcname, *args, **kwargs):
        funcname = str(funcname)
        funcname = function_expander.get(funcname, funcname)
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
            replace_string = 'S.'
            if arrname.startswith(replace_string):
                arrname = str(arrname[len(replace_string):]) #FIXME
            else:
                arrname = str(arrname)
            args.append(arrname)
            args.append((localscode, CodeStr('S')))
        if funcname == 'acopy':
            func = add_args_to_code('{}.copy', (args[0],))
            arrname = args[1]
            replace_string = 'S.'
            if arrname.startswith(replace_string):
                arrname = str(arrname[len(replace_string):]) #FIXME
            else:
                arrname = str(arrname)
            return make_func_code(func, arrname, *args[2:])
        if funcname == 'empty':
            return add_args_to_code('(not {} if {} is not None else False)', args + args)
        if funcname == 'occurs':
            return add_args_to_code('{}.count({})', reversed(args))
        if funcname in ('atc',):
            funcname = funcname[:-1]
            args[0] = add_args_to_code('{}.lower()', [args[0]])
            args[1] = add_args_to_code('{}.lower()', [args[1]])
        if funcname in ('at', 'rat'):
            funcname = {
                'at': 'find',
                'rat': 'rfind',
            }[funcname]
            return add_args_to_code('{}.{}({})', [args[1], CodeStr(funcname), args[0]]) + 1
        if funcname == 'replicate' and len(args) == 2:
            args[1] = int(args[1])
            return add_args_to_code('{}', args[:1]) * add_args_to_code('{}', args[1:])
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
                return make_func_code('vfpfunc.dow_fix', retval, *args[1:])
            return retval
        if funcname in ('dtoc', 'dtos'):
            if len(args) == 1 or args[1] == 1:
                if len(args) < 2:
                    args.append('')
                if args[1] == 1 or funcname == 'dtos':
                    if args[0] == 'dt.datetime.now()':
                        args[1] = '%Y%m%d%H%M%S'
                    elif args[0] == 'dt.datetime.now().date()':
                        args[0] = CodeStr('dt.datetime.now()')
                        args[1] = '%Y%m%d'
                    else:
                        return make_func_code('vfpfunc.dtos', args[0])
                else:
                    return make_func_code('vfpfunc.dtoc', args[0])
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
            if args[1] == 0:
               return add_args_to_code('{}[:{}]', (args[0], args[2]))
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
        if funcname == 'mod':
            return add_args_to_code('({} % {})', args)
        if funcname == 'int':
            return int(args[0])
        if funcname == 'isnull':
            return add_args_to_code('{} == {}', [args[0], None])
        if funcname in ('isalpha', 'islower', 'isdigit', 'isupper'):
            return add_args_to_code('{}[:1].{}()', [args[0], CodeStr(funcname)])
        if funcname == 'inlist':
            return add_args_to_code('({} in {})', [args[0], tuple(args[1:])])
        if funcname == 'parameters':
            return CodeStr('vfpfunc.PARAMETERS')
        if funcname == 'pythonfunctioncall' and len(args) == 3:
            self.imports.append('import {}'.format(args[0]))
            if isinstance(args[2], tuple):
                return make_func_code('{}.{}'.format(args[0], args[1]), *args[2])
            else:
                return make_func_code('{}.{}'.format(args[0], args[1]), add_args_to_code('*{}', (args[2],)))
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
                    objtype = 'vfpfunc.{}'.format(objtype)
                    return make_func_code(objtype, *args, **kwargs)
                else:
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
            funcname = 'vfpfunc.' + funcname
        elif funcname in dir(DB):
            funcname = 'DB.' + funcname
        else:
            funcname = self.scopeId(funcname, 'func')
        return make_func_code(funcname, *args)

    def scopeId(self, identifier, vartype):
        scope = CodeStr({
            'val': 'S',
            'func': 'F',
        }[vartype])
        if scope != 'F':
            if not self.scope:
                return identifier
            elif identifier == 'this':
                return CodeStr('self')
            elif identifier == 'thisform':
                return CodeStr('self.parentform')
        if valid_identifier(identifier):
            return add_args_to_code('{}.{}', [scope, CodeStr(identifier)])
        else:
            return add_args_to_code('{}[{}]', [scope, identifier])

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
        else:
            trailer = [self.convert_trailer_args(t) for t in trailer or ()]
            trailer = CodeStr(''.join(trailer))
        if identifier.islower():
            identifier = self.scopeId(identifier, 'val')
        return add_args_to_code('{}{}', (identifier, trailer))

    def convert_trailer_args(self, trailer):
        if isinstance(trailer, list):
            return make_func_code('', *trailer)
        else:
            return add_args_to_code('.{}', (trailer,))

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
        return CodeStr('.'.join(([self.withid] if ctx.startPeriod else []) + self.list_visit(ctx.identifier())))

    datatypes_map = {
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

    def visitCastExpr(self, ctx):
        func = {
            'character': 'str',
            'varchar': 'str',
            'memo': 'str',
            'general': 'str',
            'numeric': 'float',
            'currency': 'float',
            'float': 'float',
            'double': 'float',
            'integer': 'int',
            'logical': 'bool',
            'blob': 'bytearray',
            'varbinary': 'bytearray',
            'date': 'dt.date',
            'datetime': 'dt.datetime',
        }[self.datatypes_map[self.visit(ctx.asType())]]
        expr = self.visit(ctx.expr())
        return make_func_code(func, expr)

    def visitDatatype(self, ctx):
        dtype = self.visit_with_disabled_scope(ctx.idAttr())
        try:
            return self.datatypes_map[dtype]
        except KeyError:
            raise ValueError("invalid datatype '{}'".format(dtype))

    def visitAtomExpr(self, ctx):
        atom = self.visit(ctx.atom())
        trailer = self.visit(ctx.trailer())
        if ctx.PERIOD() and self.withid:
            trailer = [atom] + (trailer or [])
            atom = self.withid

        if ctx.idAttr():
            trailer = [atom] + (trailer or [])
            atom = CodeStr(self.visit_with_disabled_scope(ctx.idAttr()).title())

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
        filename = self.visit(ctx.specialExpr())
        if not filename:
            filename = make_func_code('vfpfunc.getfile', '', 'Select file to', 'Delete', 0, 'Delete')
        if ctx.RECYCLE():
            self.imports.append('from send2trash import send2trash')
            return make_func_code('send2trash', filename)
        else:
            self.imports.append('import os')
            return make_func_code('os.remove', filename)

    def visitCopyMoveFile(self, ctx):
        self.imports.append('import shutil')
        args = self.list_visit(ctx.specialExpr()) #args = [fromFile, toFile]
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
        expr = self.visit(ctx.pathname() or ctx.expr())
        return expr.lower() if string_type(expr) else expr

    def visitPathname(self, ctx):
        return create_string(ctx.getText())

    def convert_number(self, num_literal):
        num = num_literal.getText().lower()
        if 'x' in num or 'e' in num:
            if ('x' not in num and num[-1] == 'e') or ('x' in num and len(num) == 2):
                num += '0'
            return CodeStr(num)

        try:
            return int(num).real
        except:
            return float(num)

    def visitNumberOrCurrency(self, ctx):
        if ctx.children[0].symbol.type == ctx.parser.DOLLAR:
            return round(float(ctx.NUMBER_LITERAL().getText()), 4)
        return self.convert_number(ctx.NUMBER_LITERAL())

    def visitBlob(self, ctx):
        blob = ctx.BLOB_LITERAL().getText()[2:]
        if len(blob) % 2:
            blob = '0' + blob
        blob_iter = iter(blob)
        return bytearray([int(x + y, 16) for x, y in zip(blob_iter, blob_iter)])

    def visitBoolOrNull(self, ctx):
        if ctx.NULL():
            return None
        txt = ctx.BOOLEANCHAR().getText().lower()
        if len(txt) == 1 and txt in 'fnty':
            return txt in 'ty'
        raise Exception('Can\'t convert boolean:' + ctx.getText())

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
        return create_string(self.getCtxText(ctx)[1:-1])

    def visitPower(self, ctx):
        return self.operationExpr(ctx, '**')

    def visitMultiplication(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    def visitAddition(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    def visitModulo(self, ctx):
        return self.operationExpr(ctx, '%')

    def extract_args_from_addbs(self, ctx):
        leftctx, rightctx = ctx.expr()
        if isinstance(leftctx, ctx.parser.AtomExprContext) and self.visit(leftctx.atom()) == 'addbs' and isinstance(leftctx.trailer(), ctx.parser.FuncCallTrailerContext):
            leftctx = leftctx.trailer().args().expr()
            if isinstance(leftctx, ctx.parser.AdditionContext):
                return self.extract_args_from_addbs(leftctx) + [rightctx]
        return [leftctx, rightctx]

    def operationExpr(self, ctx, operation):
        if not self.skip_extract and operation == ctx.parser.PLUS_SIGN:
            args = self.extract_args_from_addbs(ctx)
            self.skip_extract = True
            args = [self.visit(arg) for arg in args]
            check_expr = self.visit(ctx.expr(0))
            self.skip_extract = False
            if len(args) > 2 or args[0] != check_expr:
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
        return self.visit(ctx.expr())

    def visitFuncDo(self, ctx):
        func = self.visit(ctx.specialExpr(0))
        namespace = self.visit(ctx.specialExpr(1)) if ctx.IN() else ''
        args = self.visit(ctx.args(0)) or []
        kwargs = {}

        if ctx.FORM():
            if ctx.NAME():
                kwargs['name'] = str(self.visit(ctx.nameId))
                if ctx.LINKED():
                    kwargs['linked'] = True
            if args:
                kwargs['args'] = args
            if ctx.NOSHOW():
                kwargs['noshow'] = True
            form_call = make_func_code('vfpfunc.do_form', func, **kwargs)
            if ctx.TO():
                return add_args_to_code('{} = {}', (self.visit(ctx.toId), form_call))
            else:
                return form_call

        if os.path.splitext(namespace)[0] == self.filename:
            namespace = ''

        if not namespace:
            if func in self.function_list:
                return make_func_code(func, *args)

            if os.path.splitext(func)[1] in ('.prg', '.mpr', '.spr'):
                namespace = os.path.splitext(func)[0]
                if os.path.splitext(func)[1] in ('.mpr', '.spr'):
                    namespace += os.path.splitext(func)[1].replace('.', '_')
                func = 'MAIN'
            else:
                func = self.scopeId(func, 'func')
                return make_func_code(func, *args)

        if namespace.endswith('.prg'):
            namespace = namespace[:-4]

        if string_type(namespace) and valid_identifier(namespace):
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

    def visitClearStmt(self, ctx):
        command = None
        args = []
        if len(ctx.children) > 1:
            if ctx.DLLS():
                args = self.visit(ctx.specialArgs())
                return make_func_code('F.dll_clear', *args)
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
        return make_func_code('F.dll_declare', dll_name, funcname, alias)

    def visitReadEvent(self, ctx):
        if ctx.EVENTS():
            return make_func_code('vfpfunc.read_events')

    def on_event(self, ctx, func_prefix):
        func = self.visit(ctx.cmd())
        if func:
            if isinstance(func, list) and len(func) == 1:
                func = func[0]
            if isinstance(ctx.cmd(), ctx.parser.AssignContext):
                import ast
                x = ast.parse(func).body[0]
                def pull_item(item):
                    return func[item.col_offset:item.end_col_offset]
                val = CodeStr(pull_item(x.value))
                assigns = []
                for target in x.targets:
                    if isinstance(target, ast.Attribute):
                        base = CodeStr(pull_item(target.value))
                        assigns.append(make_func_code('setattr', base, target.attr, val))
                    elif isinstance(target, ast.Subscript):
                        assigns.append(make_func_code(pull_item(target.value) + '.__setitem__', CodeStr(pull_item(target.slice.value)), val))
                    else:
                        raise Exception('huh?')
                func = CodeStr(' and '.join(assigns))
            func = add_args_to_code('lambda: {}', (func,))
        return [add_args_to_code('{} = {}', (CodeStr(func_prefix), func),)]

    def visitOnStmt(self, ctx):
        if ctx.KEY():
            keys = [repr(str(self.visit(i))) for i in ctx.identifier()]
            return self.on_event(ctx, 'vfpfunc.on_key[{}]'.format(', '.join(keys)))
        elif ctx.SELECTION():
            return
        elif ctx.PAD() or ctx.BAR():
            if ctx.PAD():
                args = ['pad', self.visit(ctx.specialExpr(0)), self.visit(ctx.specialExpr(1))]
            else:
                args = ['bar', self.convert_number(ctx.NUMBER_LITERAL()), self.visit(ctx.specialExpr(0))]
            if ctx.ACTIVATE():
                args.append(('popup' if ctx.POPUP() else 'menu', self.visit(ctx.specialExpr()[-1])))
            return make_func_code('vfpfunc.on_pad_bar', *args)

        event = self.visit(ctx.identifier(0))
        if event == 'error':
            return self.on_event(ctx, 'vfpfunc.error_func')
        elif event == 'shutdown':
            return self.on_event(ctx, 'vfpfunc.shutdown_func')
        elif event == 'escape':
            return self.on_event(ctx, 'vfpfunc.escape_func')

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
        return self.list_visit(ctx.expr())

    def visitFile(self, ctx):
        return ctx.getText()

    def visitRelease(self, ctx):
        if ctx.ALL():
            args = []
        else:
            args = self.visit_with_disabled_scope(ctx.args())
            args = [str(arg) for arg in args] or None
        retval = []
        if args is not None:
            if ctx.PROCEDURE():
                retval.append(make_func_code('F.release_procedure', *args))
            elif ctx.POPUP():
                kwargs = {}
                if ctx.EXTENDED():
                    kwargs['extended'] = True
                retval.append(make_func_code('F.release_popups', *args, **kwargs))
            elif ctx.ALL():
                retval.append(make_func_code('M.release'))
            else:
                thisargs = [arg for arg in args if arg in ('this', 'thisform')]
                args = [arg for arg in args if arg not in ('this', 'thisform')]
                for arg in thisargs:
                    if arg == 'this':
                        retval.append(make_func_code('self.release()'))
                    if arg == 'thisform':
                        retval.append(make_func_code('self.parentform.release()'))
                if args:
                    args = [add_args_to_code('M.{}', [CodeStr(arg)]) for arg in args]
                    retval.append(CodeStr('del {}'.format(', '.join(args))))
        return retval

    def visitCloseStmt(self, ctx):
        allflag = not not ctx.ALL()
        if ctx.TABLES():
            return make_func_code('DB.close_tables', allflag)
        if ctx.INDEXES():
            return make_func_code('DB.close_indexes', allflag)
        if ctx.DATABASE():
            return make_func_code('DB.close_databases', allflag)
        return make_func_code('DB.close_all')

    def visitWaitCmd(self, ctx):
        message = self.visit(ctx.message) or ''
        to_expr = self.visit(ctx.toExpr) if ctx.TO() else None
        window = ([self.visit(ctx.atExpr1), self.visit(ctx.atExpr2)] if ctx.AT() else [-1, -1]) if ctx.WINDOW() else []
        nowait = ctx.NOWAIT() != None
        noclear = ctx.NOCLEAR() != None
        timeout = self.visit(ctx.timeout) if ctx.TIMEOUT() else -1
        return make_func_code('vfpfunc.wait', message, to=to_expr, window=window, nowait=nowait, noclear=noclear, timeout=timeout)

    def visitDeactivate(self, ctx):
        if ctx.MENU():
            func = 'vfpfunc.deactivate_menu'
        else:
            func = 'vfpfunc.deactivate_popup'
        args = self.visit_with_disabled_scope(ctx.parameters()) if not ctx.ALL() else []
        return make_func_code(func, *[str(arg) for arg in args])

    def visitThrowError(self, ctx):
        return self.visitRaiseError(ctx) if ctx.expr() else CodeStr('raise')

    def visitCreateTable(self, ctx):
        if ctx.TABLE():
            func = 'DB.create_table'
        elif ctx.DBF():
            func = 'DB.create_dbf'
        elif ctx.CURSOR():
            func = 'DB.create_cursor'
        tablename = self.visit(ctx.specialExpr())
        setupstring = '; '.join(self.visit(f) for f in ctx.tableField())
        free = 'free' if ctx.FREE() else ''
        return make_func_code(func, tablename, setupstring, free)

    def visitTableField(self, ctx):
        fieldname = self.visit(ctx.identifier(0))
        fieldtype = self.visit(ctx.identifier(1))
        fieldsize = self.visit(ctx.arrayIndex()) or (1,)
        if fieldtype.upper() == 'L' and len(fieldsize) == 1 and fieldsize[0] == 1:
            return '{} {}'.format(fieldname, fieldtype)
        else:
            return '{} {}({})'.format(fieldname, fieldtype, ', '.join(str(int(i)) for i in fieldsize))

    def visitAlterTable(self, ctx):
        tablename = self.visit(ctx.specialExpr())
        if ctx.ADD():
            setupstring = '; '.join(self.visit(f) for f in ctx.tableField())
        else:
            setupstring = str(self.visit(ctx.identifier(0)))
        return make_func_code('DB.alter_table', tablename, 'add' if ctx.ADD() else 'drop', setupstring)

    def visitSelect(self, ctx):
        if ctx.tablename:
            return make_func_code('DB.select', self.visit(ctx.tablename))
        else:
            args = [arg for arg in self.visit(ctx.specialArgs())] if ctx.specialArgs() else ('*',)
            from_table = self.visit(ctx.fromExpr)
            into_table = self.visit(ctx.intoExpr)
            where_expr = self.visit(ctx.whereExpr)
            order_by = self.visit(ctx.orderbyid)
            distinct = 'distinct' if ctx.DISTINCT() else None
            return make_func_code('DB.sqlselect', args, from_table, into_table, where_expr, order_by, distinct)

    def visitGoRecord(self, ctx):
        if ctx.TOP():
            record = 0
        elif ctx.BOTTOM():
            record = -1
        else:
            record = self.visit(ctx.expr())
        name = self.visit(ctx.specialExpr())
        return make_func_code('DB.goto', name, record)

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
        return make_func_code('DB.use', name, workarea, opentype, **kwargs)

    def visitLocate(self, ctx):
        kwargs = OrderedDict()
        scope, for_cond, while_cond, nooptimize = self.getQueryConditions(ctx.queryCondition())
        if for_cond:
            kwargs['for_cond'] = for_cond
        if while_cond:
            kwargs['while_cond'] = while_cond
            scope = scope or ('rest',)
        else:
            scope = scope or ('all',)
        if nooptimize:
            kwargs['nooptimize'] = True
        return make_func_code('DB.locate', **kwargs)

    def visitContinueLocate(self, ctx):
        return make_func_code('DB.continue_locate')

    def visitAppendFrom(self, ctx):
        if ctx.ARRAY():
            return make_func_code('DB.insert', None, self.visit(ctx.expr()))
        sourcename = self.visit(ctx.specialExpr(0))
        kwargs = {}
        if ctx.FOR():
            kwargs['for_cond'] = add_args_to_code('lambda: {}', [self.visit(ctx.expr())])
        if ctx.typeExpr:
            kwargs['filetype'] = self.visit(ctx.typeExpr)
        return make_func_code('DB.append_from', None, sourcename, **kwargs)

    def visitAppend(self, ctx):
        menupopup = not ctx.BLANK()
        tablename = self.visit(ctx.specialExpr())
        return make_func_code('DB.append', tablename, menupopup)

    def visitInsert(self, ctx):
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
        return make_func_code('DB.insert', table, values)

    def visitReplace(self, ctx):
        value = self.visit(ctx.expr(0))
        field = self.visit_with_disabled_scope(ctx.specialExpr(0))
        scope, for_cond, while_cond, nooptimize = self.getQueryConditions(ctx.queryCondition())
        scope = scope or ('next', 1)
        if string_type(field):
            field = field.lower().rsplit('.', 1)
            tablename = field[0] if len(field) == 2 else None
            field = field[-1]
        else:
            tablename = None
        return make_func_code('DB.replace', tablename, scope, field, value)

    def visitSkipRecord(self, ctx):
        table = self.visit(ctx.specialExpr())
        skipnum = self.visit(ctx.expr()) or 1
        return make_func_code('DB.skip', table, skipnum)

    def visitCopyTo(self, ctx):
        copyTo = self.visit(ctx.specialExpr())
        if ctx.STRUCTURE():
            return make_func_code('DB.copy_structure', copyTo)

    def visitDeleteRecord(self, ctx):
        kwargs = OrderedDict()
        scope, for_cond, while_cond, nooptimize = self.getQueryConditions(ctx.queryCondition())
        scope = scope or ('next', 1)
        name = self.visit(ctx.inExpr)
        if for_cond:
            kwargs['for_cond'] = for_cond
        if while_cond:
            kwargs['while_cond'] = while_cond
        if ctx.RECALL():
            kwargs['recall'] = True
        return make_func_code('DB.delete_record', name, scope, **kwargs)

    def visitPack(self, ctx):
        if ctx.DATABASE():
            return make_func_code('DB.pack_database')
        elif ctx.DBF():
            pack = 'dbf'
        elif ctx.MEMO():
            pack = 'memo'
        else:
            pack = 'both'
        tablename = self.visit(ctx.tableName)
        workarea = self.visit(ctx.workArea)
        return make_func_code('DB.pack', pack, tablename, workarea)

    def visitIndexOn(self, ctx):
        field = self.visit(ctx.specialExpr()[0])
        indexname = self.visit(ctx.specialExpr()[1])
        tag_flag = not not ctx.TAG()
        compact_flag = not not ctx.COMPACT()
        if ctx.ASCENDING() and ctx.DESCENDING():
            raise Exception('Invalid statement: {}'.format(self.getCtxText(ctx)))
        order = 'descending' if ctx.DESCENDING() else 'ascending'
        unique_flag = not not ctx.UNIQUE()
        return make_func_code('DB.index_on', field, indexname, order, tag_flag, compact_flag, unique_flag)

    def visitCount(self, ctx):
        kwargs = OrderedDict()
        scope, for_cond, while_cond, nooptimize = self.getQueryConditions(ctx.queryCondition())
        if for_cond:
            kwargs['for_cond'] = for_cond
        if while_cond:
            kwargs['while_cond'] = while_cond
            scope = scope or ('rest',)
        else:
            scope = scope or ('all',)
        if nooptimize:
            kwargs['nooptimize'] = True
        return add_args_to_code('{} = {}', (self.visit(ctx.toExpr), make_func_code('DB.count', None, scope, **kwargs)))

    def visitSum(self, ctx):
        kwargs = OrderedDict()
        scope, for_cond, while_cond, nooptimize = self.getQueryConditions(ctx.queryCondition())
        if for_cond:
            kwargs['for_cond'] = for_cond
        if while_cond:
            kwargs['while_cond'] = while_cond
            scope = scope or ('rest',)
        else:
            scope = scope or ('all',)
        if nooptimize:
            kwargs['nooptimize'] = True
        sumexpr = add_args_to_code('lambda: {}', [self.visit(ctx.sumExpr)])
        return add_args_to_code('{} = {}', (self.visit(ctx.toExpr), make_func_code('DB.sum', None, scope, sumexpr, **kwargs)))

    def getQueryConditions(self, conditions):
        scope, for_cond, while_cond, nooptimize = None, None, None, None
        condition_types = [(condition.FOR() or condition.WHILE() or condition.NOOPTIMIZE() or type(condition.scopeClause())) for condition in conditions]
        condition_types = [condition_type or condition_type.symbol.type for condition_type in condition_types]
        if len(set(condition_types)) < len(condition_types):
            raise Exception('Bad Query Condition')
        for condition in conditions:
            if condition.FOR():
                for_cond = add_args_to_code('lambda: {}', [self.visit(condition.expr())])
            if condition.WHILE():
                while_cond = add_args_to_code('lambda: {}', [self.visit(condition.expr())])
            if condition.scopeClause():
                scope = self.visit(condition.scopeClause())
            if condition.NOOPTIMIZE():
                nooptimize = True
        return scope, for_cond, while_cond, nooptimize


    def visitReindex(self, ctx):
        return make_func_code('DB.reindex', not not ctx.COMPACT())

    def visitUpdateCmd(self, ctx):
        table = self.visit(ctx.tableExpr)
        set_fields = [(str(self.visit_with_disabled_scope(i)), self.visit(e)) for i, e in zip(ctx.identifier(), ctx.expr())]
        kwargs = {}
        if ctx.whereExpr:
            kwargs['where'] = add_args_to_code('lambda: {}', [self.visit(ctx.whereExpr)])
        if ctx.joinArgs:
            kwargs['join'] = self.visit(ctx.joinArgs)
        if ctx.fromArgs:
            kwargs['from_args'] = self.visit(ctx.fromArgs)
        return make_func_code('DB.update', table, set_fields, **kwargs)

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
        return make_func_code('DB.seek', tablename, seek_expr, **kwargs)

    def visitZapTable(self, ctx):
        return make_func_code('DB.zap', self.visit(ctx.specialExpr()))

    def visitBrowse(self, ctx):
        return make_func_code('DB.browse')

    def visitScatterExpr(self, ctx):
        kwargs = {}
        if ctx.FIELDS():
            fields = self.visit(ctx.args(0))
            if ctx.LIKE():
                kwargs['type'] = 'like'
            elif ctx.EXCEPT():
                kwargs['type'] = 'except'
            kwargs['fields'] = fields
        if ctx.MEMO():
            kwargs['memo'] = True
        if ctx.BLANK():
            kwargs['blank'] = True
        if ctx.NAME():
            name = self.visit(ctx.expr(0))
            if ctx.ADDITIVE():
                kwargs['additive'] = name
            kwargs['totype'] = 'name'
        elif ctx.TO():
            name = self.visit(ctx.expr(0))
            kwargs['totype'] = 'array'
        func = make_func_code('vfpfunc.scatter', **kwargs)
        if not ctx.MEMVAR():
            return add_args_to_code('{} = {}', (name, func))
        return func

    def visitGatherExpr(self, ctx):
        kwargs = {}
        if ctx.FIELDS():
            kwargs['fields'] = self.visit(ctx.args(0))
            if ctx.LIKE():
                kwargs['type'] = 'like'
            elif ctx.EXCEPT():
                kwargs['type'] = 'except'
        if ctx.MEMO():
            kwargs['memo'] = True
        if ctx.NAME() or ctx.FROM():
            kwargs['val'] = self.visit(ctx.expr(0))
        return make_func_code('vfpfunc.gather', **kwargs)

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
        return make_func_code('vfpfunc.report_form', self.visit(ctx.specialExpr()))

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
            args = self.list_visit(ctx.specialExpr())
        elif setword == 'bell':
            args = ('TO', self.visit(ctx.specialExpr()[0])) if ctx.TO() else ('ON' if ctx.ON() else 'OFF',)
        elif setword in ('cursor', 'deleted', 'escape', 'exact', 'exclusive', 'multilocks', 'near', 'status', 'status bar', 'tableprompt', 'talk', 'unique'):
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
                kwargs['class_file'] = self.visit(ctx.specialExpr(1))
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
            args = self.list_visit(ctx.expr())
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
                args += self.list_visit(ctx.expr())
        elif setword == 'memowidth':
            args = (self.visit(ctx.expr()[0]),)
        elif setword == 'library':
            kwargs.update({'additive': True} if ctx.ADDITIVE() else {})
            args = self.list_visit(ctx.specialExpr())
        elif setword == 'filter':
            args = self.list_visit(ctx.specialExpr())
        elif setword == 'order':
            order = self.visit(ctx.specialExpr(0))
            of_expr = self.visit(ctx.ofExpr)
            in_expr = self.visit(ctx.inExpr)
            kwargs.update({'descending': True} if ctx.DESCENDING() else {})
            kwargs.update({'tag': True} if ctx.TAG() else {})
            args = (order, of_expr, in_expr)
        elif setword == 'index':
            args = (self.visit(ctx.specialExpr(0)),)
        elif setword == 'udfparms':
            args = ['value' if ctx.VALUE() else 'reference']
        else:
            return
        return make_func_code('vfpfunc.set', setword, *args, **kwargs)

    def visitPush(self, ctx):
        pass

    def visitPop(self, ctx):
        pass

    def visitShellRun(self, ctx):
        start, stop = ctx.getSourceInterval()
        if ctx.identifier():
            pass #Add /N options
            start = ctx.identifier().getSourceInterval()[0]
        tokens = ctx.parser._input.tokens[start + 1:stop + 1]
        # FIXME: Need more cleanup on the arguments.
        command = ''.join(create_string(tok.text) for tok in tokens).strip().split()
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

    def visitListStmt(self, ctx):
        pass

    def visitSaveToCmd(self, ctx):
        pass

    def visitUnlockCmd(self, ctx):
        pass

    def visitCompileCmd(self, ctx):
        pass

    def visitSortCmd(self, ctx):
        pass

    def visitCopyToArray(self, ctx):
        pass

    def visitRestoreCmd(self, ctx):
        pass

    def visitZoomCmd(self, ctx):
        pass

    def visitTextBlock(self, ctx):
        kwargs = {}
        if ctx.NOSHOW():
            kwargs['show'] = False
        text = self.visit(ctx.textChunk())
        val = make_func_code('vfpfunc.text', text, **kwargs)
        if ctx.TO():
            name = self.visit(ctx.idAttr(0))
            return add_args_to_code('{} = {}', [name, val])
        else:
            return val

    def visitTextChunk(self, ctx):
        start, stop = ctx.getSourceInterval()
        ltoks = ctx.parser._input.getHiddenTokensToLeft(start) or []
        rtoks = ctx.parser._input.getHiddenTokensToRight(stop) or []
        toks = ctx.parser._input.tokens[start:stop+1]
        text = ''.join(t.text for t in ltoks + toks + rtoks)
        return CodeStr('[' + ',\n'.join(repr(l) for l in text.splitlines()) + ']')

    def visitDefineMenu(self, ctx):
        menu_name = self.visit(ctx.specialExpr()[0])
        kwargs = {}
        if len(ctx.specialExpr()) > 1:
            kwargs['window'] = self.visit(ctx.specialExpr()[1])
        elif ctx.SCREEN():
            kwargs['window'] = CodeStr('vfpfunc.SCREEN')
        if ctx.BAR():
            kwargs['bar'] = True
            if ctx.NUMBER_LITERAL():
                kwargs['line'] = self.convert_number(ctx.NUMBER_LITERAL())
        if ctx.NOMARGIN():
            kwargs['nomargin'] = True
        return make_func_code('vfpfunc.define_menu', menu_name, **kwargs)

    def visitDefinePad(self, ctx):
        if ctx.AT() or ctx.BEFORE() or ctx.AFTER() or ctx.NEGOTIATE() or ctx.FONT() or not ctx.MESSAGE() or not ctx.KEY() or ctx.MARK() or ctx.SKIPKW() or not ctx.COLOR():
            pass
        pad_name = str(self.visit(ctx.specialExpr(0)))
        menu_name = str(self.visit(ctx.specialExpr(1)))
        prompt = str(self.visit(ctx.expr(0)))
        kwargs = {}
        kwargs['message'] = self.visit(ctx.expr(1))
        kwargs['key'] = tuple(['+'.join(self.visit(identifier) for identifier in ctx.identifier())] + [self.visit(ctx.expr(2))] if len(ctx.expr()) > 2 else [])
        kwargs['color_scheme'] = self.convert_number(ctx.NUMBER_LITERAL(0))
        return make_func_code('vfpfunc.define_pad', pad_name, menu_name, prompt, **kwargs)

    def visitDefinePopup(self, ctx):
        popup_name = self.visit(ctx.specialExpr())
        kwargs = {}
        if ctx.SHADOW():
            kwargs['shadow'] = True
        if ctx.MARGIN():
            kwargs['margin'] = True
        if ctx.RELATIVE():
            kwargs['relative'] = True
        if ctx.NUMBER_LITERAL():
            kwargs['color_scheme'] = self.convert_number(ctx.NUMBER_LITERAL())
        return make_func_code('vfpfunc.define_popup', popup_name, **kwargs)

    def visitDefineBar(self, ctx):
        bar_number = self.convert_number(ctx.NUMBER_LITERAL())
        menu_name = self.visit(ctx.specialExpr())
        prompt = self.visit(ctx.expr(0))
        kwargs = {}
        if ctx.MESSAGE():
            kwargs['message'] = self.visit(ctx.expr(1))
        return make_func_code('vfpfunc.define_bar', bar_number, menu_name, prompt, **kwargs)

    def visitActivateWindow(self, ctx):
        pass

    def visitActivateScreen(self, ctx):
        pass

    def visitActivateMenu(self, ctx):
        menu_name = self.visit(ctx.specialExpr(0))
        kwargs = {}
        if ctx.NOWAIT():
            kwargs['nowait'] = True
        if ctx.PAD():
            kwargs['pad'] = self.visit(ctx.specialExpr(1))
        return make_func_code('vfpfunc.activate_menu', menu_name, **kwargs)

    def visitActivatePopup(self, ctx):
        pass

    def visitShowCmd(self, ctx):
        pass

    def visitHideCmd(self, ctx):
        pass

    def visitModifyWindow(self, ctx):
        pass

    def visitModifyFile(self, ctx):
        pass
