# Generated from conversion.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,7,28,2,0,7,0,2,1,7,1,1,0,5,0,6,8,0,10,0,12,0,9,9,0,1,1,1,1,5,
        1,13,8,1,10,1,12,1,16,9,1,1,1,1,1,1,1,5,1,21,8,1,10,1,12,1,24,9,
        1,1,1,1,1,1,1,0,0,2,0,2,0,0,28,0,7,1,0,0,0,2,10,1,0,0,0,4,6,3,2,
        1,0,5,4,1,0,0,0,6,9,1,0,0,0,7,5,1,0,0,0,7,8,1,0,0,0,8,1,1,0,0,0,
        9,7,1,0,0,0,10,14,5,1,0,0,11,13,5,5,0,0,12,11,1,0,0,0,13,16,1,0,
        0,0,14,12,1,0,0,0,14,15,1,0,0,0,15,17,1,0,0,0,16,14,1,0,0,0,17,18,
        5,4,0,0,18,22,5,2,0,0,19,21,5,7,0,0,20,19,1,0,0,0,21,24,1,0,0,0,
        22,20,1,0,0,0,22,23,1,0,0,0,23,25,1,0,0,0,24,22,1,0,0,0,25,26,5,
        6,0,0,26,3,1,0,0,0,3,7,14,22
    ]

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
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ConversionTestsContext(ParserRuleContext):
        __slots__ = 'parser'

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
            while _la==1:
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
        __slots__ = 'parser'

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
            while _la==5:
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
            while _la==7:
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





