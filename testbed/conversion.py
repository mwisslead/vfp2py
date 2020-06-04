# Generated from conversion.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("\36\4\2\t\2\4\3\t\3\3\2\7\2\b\n\2\f\2\16\2\13\13\2\3\3")
        buf.write("\3\3\7\3\17\n\3\f\3\16\3\22\13\3\3\3\3\3\3\3\7\3\27\n")
        buf.write("\3\f\3\16\3\32\13\3\3\3\3\3\3\3\2\2\4\2\4\2\2\2\36\2\t")
        buf.write("\3\2\2\2\4\f\3\2\2\2\6\b\5\4\3\2\7\6\3\2\2\2\b\13\3\2")
        buf.write("\2\2\t\7\3\2\2\2\t\n\3\2\2\2\n\3\3\2\2\2\13\t\3\2\2\2")
        buf.write("\f\20\7\3\2\2\r\17\7\7\2\2\16\r\3\2\2\2\17\22\3\2\2\2")
        buf.write("\20\16\3\2\2\2\20\21\3\2\2\2\21\23\3\2\2\2\22\20\3\2\2")
        buf.write("\2\23\24\7\6\2\2\24\30\7\4\2\2\25\27\7\t\2\2\26\25\3\2")
        buf.write("\2\2\27\32\3\2\2\2\30\26\3\2\2\2\30\31\3\2\2\2\31\33\3")
        buf.write("\2\2\2\32\30\3\2\2\2\33\34\7\b\2\2\34\5\3\2\2\2\5\t\20")
        buf.write("\30")
        return buf.getvalue()


class conversion ( Parser ):

    grammarFileName = "conversion.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [  ]

    symbolicNames = [ "<INVALID>", "FoxStart", "PyStart", "Line", "FoxEnd", 
                      "FoxLine", "PyEnd", "PyLine" ]

    RULE_conversionTests = 0
    RULE_conversionTest = 1

    ruleNames =  [ "conversionTests", "conversionTest" ]

    EOF = Token.EOF
    FoxStart=1
    PyStart=2
    Line=3
    FoxEnd=4
    FoxLine=5
    PyEnd=6
    PyLine=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ConversionTestsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conversionTest(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(conversion.ConversionTestContext)
            else:
                return self.getTypedRuleContext(conversion.ConversionTestContext,i)


        def getRuleIndex(self):
            return conversion.RULE_conversionTests

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConversionTests" ):
                return visitor.visitConversionTests(self)
            else:
                return visitor.visitChildren(self)




    def conversionTests(self):

        localctx = conversion.ConversionTestsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_conversionTests)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 7
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==conversion.FoxStart:
                self.state = 4
                self.conversionTest()
                self.state = 9
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConversionTestContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FoxStart(self):
            return self.getToken(conversion.FoxStart, 0)

        def FoxEnd(self):
            return self.getToken(conversion.FoxEnd, 0)

        def PyStart(self):
            return self.getToken(conversion.PyStart, 0)

        def PyEnd(self):
            return self.getToken(conversion.PyEnd, 0)

        def FoxLine(self, i:int=None):
            if i is None:
                return self.getTokens(conversion.FoxLine)
            else:
                return self.getToken(conversion.FoxLine, i)

        def PyLine(self, i:int=None):
            if i is None:
                return self.getTokens(conversion.PyLine)
            else:
                return self.getToken(conversion.PyLine, i)

        def getRuleIndex(self):
            return conversion.RULE_conversionTest

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConversionTest" ):
                return visitor.visitConversionTest(self)
            else:
                return visitor.visitChildren(self)




    def conversionTest(self):

        localctx = conversion.ConversionTestContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_conversionTest)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self.match(conversion.FoxStart)
            self.state = 14
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==conversion.FoxLine:
                self.state = 11
                self.match(conversion.FoxLine)
                self.state = 16
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 17
            self.match(conversion.FoxEnd)
            self.state = 18
            self.match(conversion.PyStart)
            self.state = 22
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==conversion.PyLine:
                self.state = 19
                self.match(conversion.PyLine)
                self.state = 24
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 25
            self.match(conversion.PyEnd)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





