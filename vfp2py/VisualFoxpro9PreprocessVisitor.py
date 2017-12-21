# Generated from vfp2py/VisualFoxpro9PreprocessParser.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by VisualFoxpro9PreprocessParser.

class VisualFoxpro9PreprocessVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#preprocessorCode.
    def visitPreprocessorCode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#preprocessorIf.
    def visitPreprocessorIf(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#preprocessorDefine.
    def visitPreprocessorDefine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#preprocessorUndefine.
    def visitPreprocessorUndefine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#preprocessorInclude.
    def visitPreprocessorInclude(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#nonpreprocessorLine.
    def visitNonpreprocessorLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9PreprocessParser#lineEnd.
    def visitLineEnd(self, ctx):
        return self.visitChildren(ctx)


