# Generated from vfp2py/VisualFoxpro9PreprocessParser.g4 by ANTLR 4.7
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO
import sys

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3")
        buf.write(u"\17D\4\2\t\2\4\3\t\3\4\4\t\4\3\2\7\2\n\n\2\f\2\16\2\r")
        buf.write(u"\13\2\3\3\3\3\7\3\21\n\3\f\3\16\3\24\13\3\3\3\3\3\5\3")
        buf.write(u"\30\n\3\3\3\3\3\3\3\3\3\3\3\5\3\37\n\3\3\3\3\3\3\3\3")
        buf.write(u"\3\3\3\3\3\7\3\'\n\3\f\3\16\3*\13\3\3\3\3\3\3\3\3\3\3")
        buf.write(u"\3\3\3\7\3\62\n\3\f\3\16\3\65\13\3\3\3\3\3\3\3\7\3:\n")
        buf.write(u"\3\f\3\16\3=\13\3\3\3\5\3@\n\3\3\4\3\4\3\4\2\2\5\2\4")
        buf.write(u"\6\2\3\3\3\16\16\2K\2\13\3\2\2\2\4?\3\2\2\2\6A\3\2\2")
        buf.write(u"\2\b\n\5\4\3\2\t\b\3\2\2\2\n\r\3\2\2\2\13\t\3\2\2\2\13")
        buf.write(u"\f\3\2\2\2\f\3\3\2\2\2\r\13\3\2\2\2\16\22\7\3\2\2\17")
        buf.write(u"\21\7\17\2\2\20\17\3\2\2\2\21\24\3\2\2\2\22\20\3\2\2")
        buf.write(u"\2\22\23\3\2\2\2\23\30\3\2\2\2\24\22\3\2\2\2\25\26\7")
        buf.write(u"\4\2\2\26\30\7\f\2\2\27\16\3\2\2\2\27\25\3\2\2\2\30\31")
        buf.write(u"\3\2\2\2\31\32\7\16\2\2\32\36\5\2\2\2\33\34\7\5\2\2\34")
        buf.write(u"\35\7\16\2\2\35\37\5\2\2\2\36\33\3\2\2\2\36\37\3\2\2")
        buf.write(u"\2\37 \3\2\2\2 !\7\6\2\2!\"\5\6\4\2\"@\3\2\2\2#$\7\7")
        buf.write(u"\2\2$(\7\f\2\2%\'\7\17\2\2&%\3\2\2\2\'*\3\2\2\2(&\3\2")
        buf.write(u"\2\2()\3\2\2\2)+\3\2\2\2*(\3\2\2\2+@\5\6\4\2,-\7\b\2")
        buf.write(u"\2-.\7\f\2\2.@\5\6\4\2/\63\7\t\2\2\60\62\7\17\2\2\61")
        buf.write(u"\60\3\2\2\2\62\65\3\2\2\2\63\61\3\2\2\2\63\64\3\2\2\2")
        buf.write(u"\64\66\3\2\2\2\65\63\3\2\2\2\66@\5\6\4\2\67;\7\13\2\2")
        buf.write(u"8:\7\17\2\298\3\2\2\2:=\3\2\2\2;9\3\2\2\2;<\3\2\2\2<")
        buf.write(u">\3\2\2\2=;\3\2\2\2>@\5\6\4\2?\27\3\2\2\2?#\3\2\2\2?")
        buf.write(u",\3\2\2\2?/\3\2\2\2?\67\3\2\2\2@\5\3\2\2\2AB\t\2\2\2")
        buf.write(u"B\7\3\2\2\2\n\13\22\27\36(\63;?")
        return buf.getvalue()


class VisualFoxpro9PreprocessParser ( Parser ):

    grammarFileName = "VisualFoxpro9PreprocessParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                     u"'\n'" ]

    symbolicNames = [ u"<INVALID>", u"PREPROC_IF", u"PREPROC_IFDEF", u"PREPROC_ELSE", 
                      u"PREPROC_ENDIF", u"PREPROC_DEFINE", u"PREPROC_UNDEFINE", 
                      u"PREPROC_INCLUDE", u"OTHER_WS", u"OTHER_CMD", u"ID", 
                      u"WS", u"NL", u"UNMATCHED" ]

    RULE_preprocessorCode = 0
    RULE_preprocessorLine = 1
    RULE_lineEnd = 2

    ruleNames =  [ u"preprocessorCode", u"preprocessorLine", u"lineEnd" ]

    EOF = Token.EOF
    PREPROC_IF=1
    PREPROC_IFDEF=2
    PREPROC_ELSE=3
    PREPROC_ENDIF=4
    PREPROC_DEFINE=5
    PREPROC_UNDEFINE=6
    PREPROC_INCLUDE=7
    OTHER_WS=8
    OTHER_CMD=9
    ID=10
    WS=11
    NL=12
    UNMATCHED=13

    def __init__(self, input, output=sys.stdout):
        super(VisualFoxpro9PreprocessParser, self).__init__(input, output=output)
        self.checkVersion("4.7")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class PreprocessorCodeContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(VisualFoxpro9PreprocessParser.PreprocessorCodeContext, self).__init__(parent, invokingState)
            self.parser = parser

        def preprocessorLine(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            else:
                return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.PreprocessorLineContext,i)


        def getRuleIndex(self):
            return VisualFoxpro9PreprocessParser.RULE_preprocessorCode

        def accept(self, visitor):
            if hasattr(visitor, "visitPreprocessorCode"):
                return visitor.visitPreprocessorCode(self)
            else:
                return visitor.visitChildren(self)




    def preprocessorCode(self):

        localctx = VisualFoxpro9PreprocessParser.PreprocessorCodeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_preprocessorCode)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << VisualFoxpro9PreprocessParser.PREPROC_IF) | (1 << VisualFoxpro9PreprocessParser.PREPROC_IFDEF) | (1 << VisualFoxpro9PreprocessParser.PREPROC_DEFINE) | (1 << VisualFoxpro9PreprocessParser.PREPROC_UNDEFINE) | (1 << VisualFoxpro9PreprocessParser.PREPROC_INCLUDE) | (1 << VisualFoxpro9PreprocessParser.OTHER_CMD))) != 0):
                self.state = 6
                self.preprocessorLine()
                self.state = 11
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PreprocessorLineContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(VisualFoxpro9PreprocessParser.PreprocessorLineContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return VisualFoxpro9PreprocessParser.RULE_preprocessorLine

     
        def copyFrom(self, ctx):
            super(VisualFoxpro9PreprocessParser.PreprocessorLineContext, self).copyFrom(ctx)



    class NonpreprocessorLineContext(PreprocessorLineContext):

        def __init__(self, parser, ctx): # actually a VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            super(VisualFoxpro9PreprocessParser.NonpreprocessorLineContext, self).__init__(parser)
            self.copyFrom(ctx)

        def OTHER_CMD(self):
            return self.getToken(VisualFoxpro9PreprocessParser.OTHER_CMD, 0)
        def lineEnd(self):
            return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.LineEndContext,0)

        def UNMATCHED(self, i=None):
            if i is None:
                return self.getTokens(VisualFoxpro9PreprocessParser.UNMATCHED)
            else:
                return self.getToken(VisualFoxpro9PreprocessParser.UNMATCHED, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitNonpreprocessorLine"):
                return visitor.visitNonpreprocessorLine(self)
            else:
                return visitor.visitChildren(self)


    class PreprocessorUndefineContext(PreprocessorLineContext):

        def __init__(self, parser, ctx): # actually a VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            super(VisualFoxpro9PreprocessParser.PreprocessorUndefineContext, self).__init__(parser)
            self.copyFrom(ctx)

        def PREPROC_UNDEFINE(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_UNDEFINE, 0)
        def ID(self):
            return self.getToken(VisualFoxpro9PreprocessParser.ID, 0)
        def lineEnd(self):
            return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.LineEndContext,0)


        def accept(self, visitor):
            if hasattr(visitor, "visitPreprocessorUndefine"):
                return visitor.visitPreprocessorUndefine(self)
            else:
                return visitor.visitChildren(self)


    class PreprocessorIfContext(PreprocessorLineContext):

        def __init__(self, parser, ctx): # actually a VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            super(VisualFoxpro9PreprocessParser.PreprocessorIfContext, self).__init__(parser)
            self.ifBody = None # PreprocessorCodeContext
            self.elseBody = None # PreprocessorCodeContext
            self.copyFrom(ctx)

        def NL(self, i=None):
            if i is None:
                return self.getTokens(VisualFoxpro9PreprocessParser.NL)
            else:
                return self.getToken(VisualFoxpro9PreprocessParser.NL, i)
        def PREPROC_ENDIF(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_ENDIF, 0)
        def lineEnd(self):
            return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.LineEndContext,0)

        def preprocessorCode(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(VisualFoxpro9PreprocessParser.PreprocessorCodeContext)
            else:
                return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.PreprocessorCodeContext,i)

        def PREPROC_IF(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_IF, 0)
        def PREPROC_IFDEF(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_IFDEF, 0)
        def ID(self):
            return self.getToken(VisualFoxpro9PreprocessParser.ID, 0)
        def PREPROC_ELSE(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_ELSE, 0)
        def UNMATCHED(self, i=None):
            if i is None:
                return self.getTokens(VisualFoxpro9PreprocessParser.UNMATCHED)
            else:
                return self.getToken(VisualFoxpro9PreprocessParser.UNMATCHED, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitPreprocessorIf"):
                return visitor.visitPreprocessorIf(self)
            else:
                return visitor.visitChildren(self)


    class PreprocessorDefineContext(PreprocessorLineContext):

        def __init__(self, parser, ctx): # actually a VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            super(VisualFoxpro9PreprocessParser.PreprocessorDefineContext, self).__init__(parser)
            self.copyFrom(ctx)

        def PREPROC_DEFINE(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_DEFINE, 0)
        def ID(self):
            return self.getToken(VisualFoxpro9PreprocessParser.ID, 0)
        def lineEnd(self):
            return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.LineEndContext,0)

        def UNMATCHED(self, i=None):
            if i is None:
                return self.getTokens(VisualFoxpro9PreprocessParser.UNMATCHED)
            else:
                return self.getToken(VisualFoxpro9PreprocessParser.UNMATCHED, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitPreprocessorDefine"):
                return visitor.visitPreprocessorDefine(self)
            else:
                return visitor.visitChildren(self)


    class PreprocessorIncludeContext(PreprocessorLineContext):

        def __init__(self, parser, ctx): # actually a VisualFoxpro9PreprocessParser.PreprocessorLineContext)
            super(VisualFoxpro9PreprocessParser.PreprocessorIncludeContext, self).__init__(parser)
            self.copyFrom(ctx)

        def PREPROC_INCLUDE(self):
            return self.getToken(VisualFoxpro9PreprocessParser.PREPROC_INCLUDE, 0)
        def lineEnd(self):
            return self.getTypedRuleContext(VisualFoxpro9PreprocessParser.LineEndContext,0)

        def UNMATCHED(self, i=None):
            if i is None:
                return self.getTokens(VisualFoxpro9PreprocessParser.UNMATCHED)
            else:
                return self.getToken(VisualFoxpro9PreprocessParser.UNMATCHED, i)

        def accept(self, visitor):
            if hasattr(visitor, "visitPreprocessorInclude"):
                return visitor.visitPreprocessorInclude(self)
            else:
                return visitor.visitChildren(self)



    def preprocessorLine(self):

        localctx = VisualFoxpro9PreprocessParser.PreprocessorLineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_preprocessorLine)
        self._la = 0 # Token type
        try:
            self.state = 61
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [VisualFoxpro9PreprocessParser.PREPROC_IF, VisualFoxpro9PreprocessParser.PREPROC_IFDEF]:
                localctx = VisualFoxpro9PreprocessParser.PreprocessorIfContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 21
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [VisualFoxpro9PreprocessParser.PREPROC_IF]:
                    self.state = 12
                    self.match(VisualFoxpro9PreprocessParser.PREPROC_IF)
                    self.state = 16
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while _la==VisualFoxpro9PreprocessParser.UNMATCHED:
                        self.state = 13
                        self.match(VisualFoxpro9PreprocessParser.UNMATCHED)
                        self.state = 18
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)

                    pass
                elif token in [VisualFoxpro9PreprocessParser.PREPROC_IFDEF]:
                    self.state = 19
                    self.match(VisualFoxpro9PreprocessParser.PREPROC_IFDEF)
                    self.state = 20
                    self.match(VisualFoxpro9PreprocessParser.ID)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 23
                self.match(VisualFoxpro9PreprocessParser.NL)
                self.state = 24
                localctx.ifBody = self.preprocessorCode()
                self.state = 28
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==VisualFoxpro9PreprocessParser.PREPROC_ELSE:
                    self.state = 25
                    self.match(VisualFoxpro9PreprocessParser.PREPROC_ELSE)
                    self.state = 26
                    self.match(VisualFoxpro9PreprocessParser.NL)
                    self.state = 27
                    localctx.elseBody = self.preprocessorCode()


                self.state = 30
                self.match(VisualFoxpro9PreprocessParser.PREPROC_ENDIF)
                self.state = 31
                self.lineEnd()
                pass
            elif token in [VisualFoxpro9PreprocessParser.PREPROC_DEFINE]:
                localctx = VisualFoxpro9PreprocessParser.PreprocessorDefineContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 33
                self.match(VisualFoxpro9PreprocessParser.PREPROC_DEFINE)
                self.state = 34
                self.match(VisualFoxpro9PreprocessParser.ID)
                self.state = 38
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==VisualFoxpro9PreprocessParser.UNMATCHED:
                    self.state = 35
                    self.match(VisualFoxpro9PreprocessParser.UNMATCHED)
                    self.state = 40
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 41
                self.lineEnd()
                pass
            elif token in [VisualFoxpro9PreprocessParser.PREPROC_UNDEFINE]:
                localctx = VisualFoxpro9PreprocessParser.PreprocessorUndefineContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 42
                self.match(VisualFoxpro9PreprocessParser.PREPROC_UNDEFINE)
                self.state = 43
                self.match(VisualFoxpro9PreprocessParser.ID)
                self.state = 44
                self.lineEnd()
                pass
            elif token in [VisualFoxpro9PreprocessParser.PREPROC_INCLUDE]:
                localctx = VisualFoxpro9PreprocessParser.PreprocessorIncludeContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 45
                self.match(VisualFoxpro9PreprocessParser.PREPROC_INCLUDE)
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==VisualFoxpro9PreprocessParser.UNMATCHED:
                    self.state = 46
                    self.match(VisualFoxpro9PreprocessParser.UNMATCHED)
                    self.state = 51
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 52
                self.lineEnd()
                pass
            elif token in [VisualFoxpro9PreprocessParser.OTHER_CMD]:
                localctx = VisualFoxpro9PreprocessParser.NonpreprocessorLineContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 53
                self.match(VisualFoxpro9PreprocessParser.OTHER_CMD)
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==VisualFoxpro9PreprocessParser.UNMATCHED:
                    self.state = 54
                    self.match(VisualFoxpro9PreprocessParser.UNMATCHED)
                    self.state = 59
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 60
                self.lineEnd()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class LineEndContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(VisualFoxpro9PreprocessParser.LineEndContext, self).__init__(parent, invokingState)
            self.parser = parser

        def NL(self):
            return self.getToken(VisualFoxpro9PreprocessParser.NL, 0)

        def EOF(self):
            return self.getToken(VisualFoxpro9PreprocessParser.EOF, 0)

        def getRuleIndex(self):
            return VisualFoxpro9PreprocessParser.RULE_lineEnd

        def accept(self, visitor):
            if hasattr(visitor, "visitLineEnd"):
                return visitor.visitLineEnd(self)
            else:
                return visitor.visitChildren(self)




    def lineEnd(self):

        localctx = VisualFoxpro9PreprocessParser.LineEndContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_lineEnd)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 63
            _la = self._input.LA(1)
            if not(_la==VisualFoxpro9PreprocessParser.EOF or _la==VisualFoxpro9PreprocessParser.NL):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





