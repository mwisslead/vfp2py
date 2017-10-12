# Generated from VisualFoxpro9.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by VisualFoxpro9Parser.

class VisualFoxpro9Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorCode.
    def visitPreprocessorCode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorIf.
    def visitPreprocessorIf(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorDefine.
    def visitPreprocessorDefine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorUndefine.
    def visitPreprocessorUndefine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorInclude.
    def visitPreprocessorInclude(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#nonpreprocessorLine.
    def visitNonpreprocessorLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#prg.
    def visitPrg(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lineComment.
    def visitLineComment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#line.
    def visitLine(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lineEnd.
    def visitLineEnd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lines.
    def visitLines(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefStart.
    def visitClassDefStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDef.
    def visitClassDef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefAddObject.
    def visitClassDefAddObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefAssign.
    def visitClassDefAssign(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefLineComment.
    def visitClassDefLineComment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDefStart.
    def visitFuncDefStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDefEnd.
    def visitFuncDefEnd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameterDef.
    def visitParameterDef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDef.
    def visitFuncDef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameter.
    def visitParameter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameters.
    def visitParameters(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#ifStart.
    def visitIfStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#ifStmt.
    def visitIfStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forStart.
    def visitForStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forEnd.
    def visitForEnd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forStmt.
    def visitForStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#caseExpr.
    def visitCaseExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#singleCase.
    def visitSingleCase(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#otherwise.
    def visitOtherwise(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#caseElement.
    def visitCaseElement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#caseStmt.
    def visitCaseStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#whileStart.
    def visitWhileStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#whileStmt.
    def visitWhileStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#withStmt.
    def visitWithStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scanStmt.
    def visitScanStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#tryStmt.
    def visitTryStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#breakLoop.
    def visitBreakLoop(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#continueLoop.
    def visitContinueLoop(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#controlStmt.
    def visitControlStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#cmdStmt.
    def visitCmdStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#cmd.
    def visitCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#release.
    def visitRelease(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onKey.
    def visitOnKey(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pushKey.
    def visitPushKey(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#popKey.
    def visitPopKey(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#keyboard.
    def visitKeyboard(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#defineMenu.
    def visitDefineMenu(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#definePad.
    def visitDefinePad(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#definePopup.
    def visitDefinePopup(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#defineBar.
    def visitDefineBar(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onPad.
    def visitOnPad(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onBar.
    def visitOnBar(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onSelectionBar.
    def visitOnSelectionBar(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateWindow.
    def visitActivateWindow(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateMenu.
    def visitActivateMenu(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deactivate.
    def visitDeactivate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#raiseError.
    def visitRaiseError(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#throwError.
    def visitThrowError(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#createTable.
    def visitCreateTable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#alterTable.
    def visitAlterTable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#select.
    def visitSelect(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#use.
    def visitUse(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#locate.
    def visitLocate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#continueLocate.
    def visitContinueLocate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#replace.
    def visitReplace(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#indexOn.
    def visitIndexOn(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#count.
    def visitCount(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#sum.
    def visitSum(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deleteRecord.
    def visitDeleteRecord(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#appendFrom.
    def visitAppendFrom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#append.
    def visitAppend(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#insert.
    def visitInsert(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#skipRecord.
    def visitSkipRecord(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pack.
    def visitPack(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#reindex.
    def visitReindex(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#seekRecord.
    def visitSeekRecord(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#goRecord.
    def visitGoRecord(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyTo.
    def visitCopyTo(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#zapTable.
    def visitZapTable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#browse.
    def visitBrowse(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scatterExpr.
    def visitScatterExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#gatherExpr.
    def visitGatherExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#closeStmt.
    def visitCloseStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#readEvent.
    def visitReadEvent(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#clearStmt.
    def visitClearStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#report.
    def visitReport(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllDeclare.
    def visitDllDeclare(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#nodefault.
    def visitNodefault(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#shellRun.
    def visitShellRun(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assert.
    def visitAssert(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArgs.
    def visitDllArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArg.
    def visitDllArg(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#printStmt.
    def visitPrintStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#waitCmd.
    def visitWaitCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deleteFile.
    def visitDeleteFile(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyMoveFile.
    def visitCopyMoveFile(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#chMkRmDir.
    def visitChMkRmDir(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#quit.
    def visitQuit(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#returnStmt.
    def visitReturnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setup.
    def visitSetup(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onError.
    def visitOnError(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onShutdown.
    def visitOnShutdown(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setStmt.
    def visitSetStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setCmd.
    def visitSetCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#args.
    def visitArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#specialArgs.
    def visitSpecialArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDo.
    def visitFuncDo(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#reference.
    def visitReference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#argReplace.
    def visitArgReplace(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#comparison.
    def visitComparison(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#castExpr.
    def visitCastExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#unaryNegation.
    def visitUnaryNegation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atomExpr.
    def visitAtomExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#power.
    def visitPower(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#multiplication.
    def visitMultiplication(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanOperation.
    def visitBooleanOperation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#subExpr.
    def visitSubExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modulo.
    def visitModulo(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanNegation.
    def visitBooleanNegation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#constantExpr.
    def visitConstantExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#addition.
    def visitAddition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#complexId.
    def visitComplexId(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atom.
    def visitAtom(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcCallTrailer.
    def visitFuncCallTrailer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#identTrailer.
    def visitIdentTrailer(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pathname.
    def visitPathname(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pathElement.
    def visitPathElement(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#specialExpr.
    def visitSpecialExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#number.
    def visitNumber(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#boolean.
    def visitBoolean(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#null.
    def visitNull(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#date.
    def visitDate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#string.
    def visitString(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assign.
    def visitAssign(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#idAttr2.
    def visitIdAttr2(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#idAttr.
    def visitIdAttr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#twoExpr.
    def visitTwoExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#arrayIndex.
    def visitArrayIndex(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#datatype.
    def visitDatatype(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scopeClause.
    def visitScopeClause(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#identifier.
    def visitIdentifier(self, ctx):
        return self.visitChildren(ctx)


