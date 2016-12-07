from __future__ import print_function

import sys
import os
import time
import datetime
import re
import tempfile
from collections import OrderedDict

import argparse

import antlr4
import autopep8

from vfp2py import *

STDLIBS = ['import sys', 'import os', 'import math', 'import datetime']
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

class Tic():
    def __init__(self):
        self.start = time.time()

    def tic(self):
        self.start = time.time()

    def toc(self):
        return time.time()-self.start

class CodeStr(str):
    def __repr__(self):
        return self

    def __add__(self, val):
        return CodeStr('{} + {}'.format(self, repr(val)))

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
        visitor = PythonConvertVisitor()
        filename = visitor.visit(ctx.specialExpr())
        if isinstance(filename, CodeStr):
            filename = eval(filename)
        filename = which(filename)
        include_visitor = preprocess_file(filename)
        self.memory.update(include_visitor.memory)
        return include_visitor.tokens

    def visitPreprocessorIf(self, ctx):
        if ctx.IF():
            visitor = PythonConvertVisitor()
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
    def __init__(self):
        super(PythonConvertVisitor, self).__init__()
        self.vfpclassnames = {'custom': 'object',
                              'form': 'vfpfunc.Form',
                              'label': 'vfpfunc.Label',
                              'textbox': 'vfpfunc.Textbox',
                              'checkbox': 'vfpfunc.Checkbox',
                              'combobox': 'vfpfunc.Combobox',
                              'spinner': 'vfpfunc.Spinner',
                              'shape': 'vfpfunc.Shape',
                              'commandbutton': 'vfpfunc.CommandButton'
                             }
        self.imports = []
        self.scope = None
        self._saved_scope = None
        self._scope_count = 0
        self.withid = ''
        self.function_list = []

    @staticmethod
    def make_func_code(funcname, *args, **kwargs):
        args = [repr(x) for x in args]
        args += ['{}={}'.format(key, repr(kwargs[key])) for key in kwargs]
        return CodeStr('{}({})'.format(funcname, ', '.join(args)))

    @staticmethod
    def to_int(expr):
        if isinstance(expr, float):
            return int(expr)
        else:
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

    def visitPrg(self, ctx):
        self.imports = []
        if ctx.funcDef():
            for funcDef in get_list(ctx.funcDef()):
                self.function_list.append(self.visit(ctx.funcDef()[0].funcDefStart().idAttr2()))
            self.function_list = list(set(self.function_list))

        defs = []
        if ctx.classDef():
            for classDef in get_list(ctx.classDef()):
                defs += self.visit(classDef) + [[]]

        if ctx.funcDef():
            for funcDef in get_list(ctx.funcDef()):
                funcname, parameters, funcbody = self.visit(funcDef)
                defs.append(CodeStr('def {}({}):'.format(funcname, ', '.join(parameters))))
                defs += [funcbody] + [[]]

        main = []
        if ctx.line():
            self.new_scope()
            line_structure = []
            for line in get_list(ctx.line()):
                line_structure += self.visit(line)
            if not line_structure:
                line_structure = [CodeStr('pass')]
            main = [CodeStr('def main(argv):'), [CodeStr('vfpfunc.pushscope()')]]
            main += [line_structure]
            main.append([CodeStr('vfpfunc.popscope()')])
            main.append([])
            main += [CodeStr('if __name__ == \'__main__\':'), [CodeStr('main(sys.argv)')]]
            self.imports.append('import sys')
            self.delete_scope()

        self.imports = sorted(set(self.imports), key=import_key)
        imports = []
        for n, module in enumerate(self.imports):
            if n != 0 and module not in STDLIBS:
                imports.append('')
            imports.append(module)
        if imports:
            imports.append('')
        return  [CodeStr(imp) for imp in imports] + defs + main

    def visitLine(self, ctx):
        retval = self.visitChildren(ctx)
        if retval is None:
            print(ctx.getText())
            return []
        if not isinstance(retval, list):
            return [retval]
        return retval

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
        return CodeStr(self.endfix.sub(repl, comment))

    def visitCmdStmt(self, ctx):
        if ctx.cmd():
            return self.visit(ctx.cmd())
        else:
            return self.visit(ctx.setup())

    def visitLines(self, ctx):
        retval = []
        for line in ctx.line():
            retval += self.visit(line)
        def badline(line):
            return line.startswith('#') if hasattr(line, 'startswith') else not line
        if not retval or all(badline(l) for l in retval):
            retval.append(CodeStr('pass'))
        return retval

    def visitClassDef(self, ctx):
        classname, supername = self.visit(ctx.classDefStart())
        retval = [CodeStr('class {}({}):'.format(classname, supername))]
        assignments = []
        funcs = {}
        for stmt in ctx.classDefStmt():
            if isinstance(stmt, VisualFoxpro9Parser.ClassDefAssignContext):
                assignments += self.visit(stmt)
            elif isinstance(stmt, VisualFoxpro9Parser.ClassDefAddObjectContext):
                assignments += self.visit(stmt)
            elif isinstance(stmt, VisualFoxpro9Parser.ClassDefLineCommentContext):
                assignments += [self.visit(stmt)]
            else:
                funcs.update(self.visit(stmt))

        for funcname in funcs:
            parameters, funcbody = funcs[funcname]
            if '.' in funcname:
                newfuncname = funcname.replace('.', '_')
                assignments.append(CodeStr('def {}({}):'.format(newfuncname, ', '.join(parameters))))
                assignments.append(funcbody)
                assignments.append(CodeStr('self.{} = {}'.format(funcname, newfuncname)))

        if '__init__' in funcs:
            funcs['__init__'][1] = [CodeStr('super({}, self).__init__()'.format(classname))] + assignments + funcs['__init__'][1]
        else:
            funcs['__init__'] = [[CodeStr('self')], [CodeStr('super({}, self).__init__()'.format(classname))] + assignments]

        for funcname in funcs:
            parameters, funcbody = funcs[funcname]
            if '.' not in funcname:
                retval.append([CodeStr('def {}({}):'.format(funcname, ', '.join(parameters))), funcbody])

        #retval += ['vfpfunc.classes[%s] = %s' % (repr(classname), classname)]
        return retval

    def visitClassDefStart(self, ctx):
        # DEFINE CLASS identifier (AS identifier)? NL
        #print(ctx.getText())
        names = [self.visit(identifier) for identifier in ctx.identifier()]
        #print(names)
        #exit()
        classname = names[0]
        if classname in self.vfpclassnames:
            raise Exception(classname + ' is a reserved classname')
        supername = names[1] if len(names) > 0 else 'custom'
        if supername in self.vfpclassnames:
            self.imports.append('from vfp2py import vfpfunc')
            supername = self.vfpclassnames[supername]
        return classname, supername

    def visitClassDefAssign(self, ctx):
        return [CodeStr('self.' + arg) for arg in self.visit(ctx.assign())]

    def visitClassDefAddObject(self, ctx):
        #ADD OBJECT identifier AS idAttr (WITH idAttr '=' expr (',' idAttr '=' expr)*)?
        name = self.visit(ctx.identifier())
        objtype = self.visit(ctx.idAttr()[0])
        if objtype in self.vfpclassnames:
            self.imports.append('from vfp2py import vfpfunc')
            objtype = CodeStr(self.vfpclassnames[objtype])
        args = [self.add_args_to_code('{}={}', (self.visit(idAttr), self.visit(expr))) for idAttr, expr in zip(ctx.idAttr()[1:], ctx.expr())]
        funcname = self.add_args_to_code('self.{} = {}', (name, objtype))
        retval = []
        retval.append(self.make_func_code(funcname, *args))
        retval.append(self.add_args_to_code('self.add_object(self.{})', [name]))
        return retval

    def visitClassDefFuncDef(self, ctx):
        funcname, parameters, funcbody = self.visit(ctx.funcDef())
        if funcname == 'init':
            funcname = '__init__'
        return {funcname: [['self'] + parameters, funcbody]}

    def visitFuncDefStart(self, ctx):
#funcDefStart: (PROCEDURE | FUNCTION) idAttr ('(' parameters? ')')? NL parameterDef?;
        return self.visit(ctx.idAttr2()), (self.visit(ctx.parameters()) if ctx.parameters() else []) + (self.visit(ctx.parameterDef()) if ctx.parameterDef() else [])

    def visitParameterDef(self, ctx):
#parameterDef: (LPARAMETER | LPARAMETERS | PARAMETERS) parameters NL;
        return self.visit(ctx.parameters())

    def visitParameter(self, ctx):
#parameter: idAttr (AS idAttr)?;
        return self.visit(ctx.idAttr()[0])

    def visitParameters(self, ctx):
        return [self.visit(parameter) for parameter in ctx.parameter()]

    def visitFuncDef(self, ctx):
#funcDef:  funcDefStart line* funcDefEnd?;
        name, parameters = self.visit(ctx.funcDefStart())
        self.imports.append('from vfp2py import vfpfunc')
        body = [CodeStr('vfpfunc.pushscope()')]
        self.new_scope()
        self.scope.update({key: False for key in parameters})
        body += self.visit(ctx.lines())
        self.delete_scope()
        body.append(CodeStr('vfpfunc.popscope()'))
        return name, parameters, body

    def visitPrintStmt(self, ctx):
        return [self.make_func_code('print', *self.visit(ctx.args()))]

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
        #doCase caseElement* otherwise? ENDCASE
        n = 0
        retval = []
        for elem in ctx.caseElement():
            if elem.lineComment():
                retval.append(self.visit(elem.lineComment()))
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
        #caseExpr line*
        return self.visit(ctx.caseExpr()), self.visit(ctx.lines())

    def visitCaseExpr(self, ctx):
        #CASE expr NL
        return self.visit(ctx.expr())

    def visitOtherwise(self, ctx):
        #OTHERWISE NL line*;
        return self.visit(ctx.lines())

    def visitForStart(self, ctx):
        self.enable_scope(False)
        loopvar = self.visit(ctx.idAttr())
        self.enable_scope(True)
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

    def visitBreakLoop(self, ctx):
        return CodeStr('break')

    def visitDeclaration(self, ctx):
        if ctx.PUBLIC():
            func = 'vfpfunc.publicvar'
        if ctx.PRIVATE():
            func = 'vfpfunc.privatevar'
        if ctx.LOCAL():
            self.enable_scope(False)
            names = self.visit(ctx.parameters())
            self.enable_scope(True)
            for name in names:
                self.scope[name] = False
            return CodeStr('#Added {} to scope'.format(', '.join(names)))
        if ctx.ARRAY():
            func = 'vfp.addarray'
            values = [self.visit(ctx.arrayIndex())]
            args = [self.visit(ctx.identifier())]
            return [self.make_func_code(func, name, value) for name, value in zip(args, values)]
        else:
            return [self.make_func_code(func, name) for name in self.visit(ctx.parameters())]

    def visitAssign(self, ctx):
        if ctx.STORE():
            value = self.visit(ctx.expr())
            args = [self.visit(var) for var in ctx.idAttr()] + [repr(value)]
            return CodeStr(' = '.join(args))
        else:
            name = self.visit(ctx.idAttr()[0])
            value = self.visit(ctx.expr())
            try:
                if value.startswith(name + ' + '):
                    return [CodeStr('{} += {}'.format(name, repr(value[len(name + ' + '):])))]
            except Exception as e:
                pass
            return [CodeStr('{} = {}'.format(name, repr(value)))]

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
                       VisualFoxpro9Lexer.EQUALS: '==',
                       VisualFoxpro9Lexer.DOUBLEEQUALS: '==',
                       VisualFoxpro9Lexer.DOLLAR: 'in',
                       VisualFoxpro9Lexer.OR: 'or',
                       VisualFoxpro9Lexer.AND: 'and'
                      }
        left = self.visit(ctx.expr(0))
        right = self.visit(ctx.expr(1))
        if isinstance(right, float) and right == int(right):
            right = int(right)
        symbol = symbol_dict[ctx.op.type]
        return CodeStr('{} {} {}'.format(repr(left), symbol, repr(right)))

    def visitUnaryNegation(self, ctx):
        return CodeStr('-{}'.format(repr(self.visit(ctx.expr()))))

    def visitBooleanNegation(self, ctx):
        return CodeStr('not {}'.format(repr(self.visit(ctx.expr()))))

    def func_call(self, funcname, args):
        if funcname == 'chr' and len(args) == 1 and isinstance(args[0], float):
            return chr(int(args[0]))
        if funcname == 'space' and len(args) == 1 and isinstance(args[0], float):
            return ' '*int(args[0])
        if funcname == 'date' and len(args) == 0:
            self.imports.append('import datetime')
            return self.make_func_code('datetime.datetime.now().date')
        if funcname == 'iif' and len(args) == 3:
            return self.add_args_to_code('({} if {} else {})', [args[i] for i in (1, 0, 2)])
        if funcname == 'alltrim' and len(args) == 1:
            return self.add_args_to_code('{}.strip()', args)
        if funcname == 'strtran' and len(args) == 3:
            return self.make_func_code('{}.replace'.format(args[0]), *args[1:])
        if funcname == 'left' and len(args) == 2:
            args[1] = self.to_int(args[1])
            return self.add_args_to_code('{}[:{}]', args)
        if funcname == 'ceiling' and len(args) == 1:
            self.imports.append('import math')
            return self.make_func_code('math.ceil', *args)
        if funcname == 'str':
            self.imports.append('from vfp2py import vfpfunc')
            return self.make_func_code('vfpfunc.num_to_str', *args)
        if funcname == 'file':
            self.imports.append('import os')
            return self.make_func_code('os.path.isfile', *args)
        if funcname == 'used':
            self.imports.append('from vfp2py import vfpfunc')
            return self.make_func_code('vfpfunc.used', *args)
        if funcname == 'round':
            return self.make_func_code(funcname, *args)
        if funcname in dir(vfpfunc):
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
        return CodeStr('.'.join([self.withid] if ctx.PERIOD() else [] + [self.visit(identifier) for identifier in ctx.identifier()]))

    def visitAtomExpr(self, ctx):
        atom = self.visit(ctx.atom())
        trailer = self.visit(ctx.trailer()) if ctx.trailer() else None
        if ctx.PERIOD() and self.withid:
            trailer = [atom] + (trailer if trailer else [])
            atom = self.withid
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

    def visitIdList(self, ctx):
        return [self.visit(i) for i in get_list(ctx.idAttr())]

    #(MD | MKDIR | RD | RMDIR) specialExpr #Directory
    def visitAddRemoveDirectory(self, ctx):
        self.imports.append('import os')
        if ctx.MD() or ctx.MKDIR():
            funcname = 'mkdir'
        if ctx.RD() or ctx.RMDIR():
            funcname = 'rmdir'
        return self.make_func_code('os.' + funcname, self.visit(ctx.specialExpr()))

    #specialExpr: pathname | expr;
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
            return expr
            if isinstance(expr, CodeStr):
                return self.scopeId(expr, 'val')
            else:
                return expr

    def visitPathname(self, ctx):
        return self.create_string(ctx.getText()).lower()

    def visitNumber(self, ctx):
        num = ctx.NUMBER_LITERAL().getText()
        if num[-1:].lower() == 'e':
            num += '0'
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
                return datetime.date(int(y), int(m), int(d))
            except ValueError as e:
                raise Exception('invalid date constant: ' + ctx.getText())
        #if ctx.TIME_LITERAL():
        #    hour, minute, second
        #    if innerstr[-2:].upper() in ('AM', 'PM'):
        #
        return datetime.dateime(1, 1, 1, 0, 0, 0)

    def visitString(self, ctx):
        return self.create_string(ctx.getText()[1:-1])

    # expr op=('**'|'^') expr */
    def visitPower(self, ctx):
        return self.operationExpr(ctx, '**')

    # expr op=('*'|'/') expr */
    def visitMultiplication(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    # expr op=('+'|'-') expr */
    def visitAddition(self, ctx):
        return self.operationExpr(ctx, ctx.op.type)

    # expr '%' expr #Modulo
    def visitModulo(self, ctx):
        return self.operationExpr(ctx, '%')

    def operationExpr(self, ctx, operation):
        left = self.visit(ctx.expr(0))  # get value of left subexpression
        right = self.visit(ctx.expr(1)) # get value of right subexpression
        symbols = {
            '**': '**',
            '%': '%',
            VisualFoxpro9Parser.ASTERISK: '*',
            VisualFoxpro9Parser.FORWARDSLASH: '/',
            VisualFoxpro9Parser.PLUS_SIGN: '+',
            VisualFoxpro9Parser.MINUS_SIGN: '-'
        }
        if self.string_type(left) and self.string_type(right) and operation == VisualFoxpro9Parser.PLUS_SIGN:
            return left + right
        return CodeStr('({} {} {})'.format(repr(left), symbols[operation], repr(right)))

    def visitSubExpr(self, ctx):
        return self.add_args_to_code('({})', [self.visit(ctx.expr())])

    def visitFuncDo(self, ctx):
        self.enable_scope(False)
        func = self.visit(ctx.specialExpr()[0])
        self.enable_scope(True)
        args = self.visit(ctx.args()) if ctx.args() else []
        if func.endswith('.mpr'):
            func = func[:-4]
            args = [func] + args
            self.imports.append('from vfp2py import vfpfunc')
            return self.make_func_code('vfpfunc.mprfile', *args)
        if ctx.IN():
            namespace = self.visit(ctx.specialExpr()[1])
        else:
            if func in self.function_list:
                return self.make_func_code(func, *args)
            namespace = func
            func = 'main'

        return self.make_func_code('vfpfunc.do_command', namespace, func, *args)

    def visitMethodCall(self, ctx):
        return self.visit(ctx.idAttr()) + '.' + self.visit(ctx.identifier()) + '()'

    def visitClearStmt(self, ctx):
        if ctx.ALL:
            return 'vfpfunc.clearall()'
        if ctx.DLLS:
            return 'vfpfunc.cleardlls(' + self.visit(ctx.args()) + ')'
        if ctx.MACROS:
            return 'vfpfunc.clearmacros()'
        if ctx.EVENTS:
            return 'vfpfunc.clearevents()'

    def visitOnError(self, ctx):
        if ctx.cmd():
            func = self.visit(ctx.cmd())
        else:
            return [CodeStr('vfp.error_func = None')]
        return [CodeStr('vfp.error_func = lambda: ' + func)]

    def visitIdentifier(self, ctx):
        altermap = {
            'class': 'classtype'
        }
        identifier = ctx.getText().lower()
        identifier = altermap.get(identifier, identifier)
        return CodeStr(identifier)

    def visitArrayIndex(self, ctx):
        if ctx.twoExpr():
            return self.visit(ctx.twoExpr())
        else:
            return [self.visit(ctx.expr())]

    def visitTwoExpr(self, ctx):
        return [self.visit(expr) for expr in ctx.expr()]

    def visitQuit(self, ctx):
        return [CodeStr('vfp.quit()')]

    def visitDeleteFile(self, ctx):
        if ctx.specialExpr():
            filename = self.visit(ctx.specialExpr())
        else:
            filename = None
        if ctx.RECYCLE():
            return self.make_func_code('vfp.delete_file', filename, True)
        else:
            self.imports.append('import os')
            return self.make_func_code('os.remove', filename)

    def visitFile(self, ctx):
        return ctx.getText()

    def visitRelease(self, ctx):
        #RELEASE vartype=(PROCEDURE|CLASSLIB)? args #release
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
            retval.append(CodeStr('#Released {}'.format(', '.join(scoped_args))))
        if args is not None:
            retval.append(self.make_func_code('vfpfunc.release', *args))
        return retval

    def visitCloseStmt(self, ctx):
        allflag = not not ctx.ALL()
        if ctx.TABLES():
            return self.make_func_code('vfpfunc.db.close_tables', allflag)

    def visitWaitCmd(self, ctx):
        #WAIT (TO toExpr=expr | WINDOW (AT atExpr1=expr ',' atExpr2=expr)? | NOWAIT | CLEAR | NOCLEAR | TIMEOUT timeout=expr | message=expr)*
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
        field = self.visit(ctx.idAttr()).split('.')
        self.enable_scope(True)
        if len(field) > 1:
            if len(field) == 2:
                table = str(field[0])
            else:
                table = CodeStr('.'.join(field[:-1]))
            field = str(field[-1])
        else:
            field = field[0]
            table = None
        return self.make_func_code('vfpfunc.db.replace', table, field, value, scope)

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
        return self.make_func_code('vfpfunc.db.delete_record', name, scopetype, num, **kwargs)

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

    def visitPackDatabase(self, ctx):
        return self.make_func_code('vfpfunc.db.pack_database')

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
        if ctx.setword.text.lower() == 'printer':
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
        if ctx.setword.text.lower() == 'typeahead':
            return self.make_func_code('vfpfunc.set', 'typeahead', self.visit(ctx.expr()[0]))

    def visitReturnStmt(self, ctx):
        retval = [CodeStr('vfpfunc.popscope()')]
        if ctx.expr():
            args = self.visit(ctx.expr())
            return retval + [self.add_args_to_code('return {}', (args,))]
        else:
            return retval + [CodeStr('return')]

def print_tokens(stream):
    stream.fill()
    for t in stream.tokens:
        if t.channel != 0:
            continue
        #if token.type == VisualFoxpro9Lexer.WS or (token.type > 0 and token.channel==0):
        #    print(token.text, end='')
        out = (t.tokenIndex, t.start, t.stop, repr(str(t.text)), t.type, t.line, t.column, t.channel)
        print('[@%d,%d:%d=%s,<%d>,%d:%d,%d]' % out)
    stream.reset()

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

def preprocess_file(filename):
    import codecs
    fid = codecs.open(filename, 'r', 'ISO-8859-1')
    data = fid.read()
    fid.close()

    input_stream = antlr4.InputStream(data)
    lexer = VisualFoxpro9Lexer(input_stream)
    stream = MultichannelTokenStream(lexer)
    #print_tokens(stream)
    #exit()
    parser = VisualFoxpro9Parser(stream)
    tree = parser.preprocessorCode()
    visitor = PreprocessVisitor()
    visitor.tokens = visitor.visit(tree)
    return visitor

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
            #print('added channel %s: %s' % (repr(channel), repr(self.channels)))

    def disableChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            #print('removed channel %s: %s' % (repr(channel), repr(self.channels)))

class just_raise_an_error:
    def __init__(self):
        pass

    @staticmethod
    def reportAttemptingFullContext(ctx, arg2, arg3, arg4, arg5, arg6):
        pass#raise Exception('error')

    @staticmethod
    def reportAmbiguity(ctx, arg2, arg3, arg4, arg5, arg6, arg7):
        pass#raise Exception('error')

    @staticmethod
    def reportContextSensitivity(ctx, arg2, arg3, arg4, arg5, arg6):
        pass#raise Exception('error')

    @staticmethod
    def syntaxError(ctx, arg2, arg3, arg4, arg5, arg6):
        raise Exception('error')

def time_lines(data):
    testdata = data.split('\n')
    if not testdata[-1]:
        testdata.pop()
    retval = []
    input_string = ''
    while testdata:
        input_string += testdata.pop(0) + '\n'
        try:
            #print('trying: %s' % repr(input_string)[:50] + '... ' + repr(input_string)[-50:] )
            input_stream = antlr4.InputStream(input_string)
            lexer = VisualFoxpro9Lexer(input_stream)
            stream = MultichannelTokenStream(lexer)
            #print_tokens(stream)
            parser = VisualFoxpro9Parser(stream)
            parser.removeErrorListeners()
            parser.addErrorListener(just_raise_an_error)
            tic = Tic()
            tree = parser.prg()
            retval.append([tic.toc(), input_string])
            input_string = ''
        except Exception as e:
            pass
    return retval

def main(argv):
    global SEARCH_PATH
    if len(argv) > 3:
        SEARCH_PATH += argv[3:]
    tic = Tic()
    tokens = preprocess_file(argv[1]).tokens
    print(tic.toc())
    tic.tic()
    data = ''.join(token.text.replace('\r', '') for token in tokens)
    with tempfile.NamedTemporaryFile() as fid:
        pass
    with open(fid.name, 'wb') as fid:
        fid.write(data.encode('utf-8'))
    input_stream = antlr4.InputStream(data)
    lexer = VisualFoxpro9Lexer(input_stream)
    stream = MultichannelTokenStream(lexer)
    #print_tokens(stream)
    parser = VisualFoxpro9Parser(stream)
    print(tic.toc())
    tic.tic()
    tree = parser.prg()
    print(tic.toc())
    #timed_lines = time_lines(data)
    #print(sum(item[0] for item in timed_lines))
    #for item in time_lines(data):
    #    print(item[0])
    #    print(add_indents([item[1]], 0))
    visitor = PythonConvertVisitor()
    output_tree = visitor.visit(tree)
    output = add_indents(output_tree, 0)
    output = re.sub(r'\'\s*\+\s*\'', '', output)
    with open(argv[2], 'wb') as fid:
        fid.write(output)
    autopep8.main([argv[0], '--in-place', '--aggressive', '--aggressive', argv[2]])

if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
