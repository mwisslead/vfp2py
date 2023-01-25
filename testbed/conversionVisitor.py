# Generated from conversion.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .conversion import conversion
else:
    from conversion import conversion

# This class defines a complete generic visitor for a parse tree produced by conversion.

class conversionVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by conversion#conversionTests.
    def visitConversionTests(self, ctx:conversion.ConversionTestsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by conversion#conversionTest.
    def visitConversionTest(self, ctx:conversion.ConversionTestContext):
        return self.visitChildren(ctx)



del conversion