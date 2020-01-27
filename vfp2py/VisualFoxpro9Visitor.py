# Generated from VisualFoxpro9.g4 by ANTLR 4.8
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by VisualFoxpro9Parser.

class VisualFoxpro9Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorCode.
    def visitPreprocessorCode(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorLines.
    def visitPreprocessorLines(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorJunk.
    def visitPreprocessorJunk(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#nongreedyLines.
    def visitNongreedyLines(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefStart.
    def visitClassDefStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDef.
    def visitClassDef(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classProperty.
    def visitClassProperty(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameter.
    def visitParameter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameters.
    def visitParameters(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDefStart.
    def visitFuncDefStart(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDef.
    def visitFuncDef(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#singleCase.
    def visitSingleCase(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#otherwise.
    def visitOtherwise(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#controlStmt.
    def visitControlStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#addObject.
    def visitAddObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#programControl.
    def visitProgramControl(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atPos.
    def visitAtPos(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDo.
    def visitFuncDo(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assign.
    def visitAssign(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#declaration.
    def visitDeclaration(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#returnStmt.
    def visitReturnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onStmt.
    def visitOnStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#release.
    def visitRelease(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setStmt.
    def visitSetStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#push.
    def visitPush(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pop.
    def visitPop(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#activateWindow.
    def visitActivateWindow(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateScreen.
    def visitActivateScreen(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateMenu.
    def visitActivateMenu(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activatePopup.
    def visitActivatePopup(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deactivate.
    def visitDeactivate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modifyWindow.
    def visitModifyWindow(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modifyFile.
    def visitModifyFile(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#retry.
    def visitRetry(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#sortCmd.
    def visitSortCmd(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#updateCmd.
    def visitUpdateCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#goRecord.
    def visitGoRecord(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyToArray.
    def visitCopyToArray(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#unlockCmd.
    def visitUnlockCmd(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#shellRun.
    def visitShellRun(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assert.
    def visitAssert(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#compileCmd.
    def visitCompileCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#listStmt.
    def visitListStmt(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#saveToCmd.
    def visitSaveToCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#restoreCmd.
    def visitRestoreCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#zoomCmd.
    def visitZoomCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#textBlock.
    def visitTextBlock(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#showCmd.
    def visitShowCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#hideCmd.
    def visitHideCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#exprCmd.
    def visitExprCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#complexIdCmd.
    def visitComplexIdCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#queryCondition.
    def visitQueryCondition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#textChunk.
    def visitTextChunk(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArgs.
    def visitDllArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArg.
    def visitDllArg(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#tableField.
    def visitTableField(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setCmd.
    def visitSetCmd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#declarationItem.
    def visitDeclarationItem(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#asType.
    def visitAsType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#asTypeOf.
    def visitAsTypeOf(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#argsItem.
    def visitArgsItem(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#args.
    def visitArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#specialArgs.
    def visitSpecialArgs(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#reference.
    def visitReference(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#comparison.
    def visitComparison(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#castExpr.
    def visitCastExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atomExpr.
    def visitAtomExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#subExpr.
    def visitSubExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanNegation.
    def visitBooleanNegation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#unaryNegation.
    def visitUnaryNegation(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanOr.
    def visitBooleanOr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#power.
    def visitPower(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#multiplication.
    def visitMultiplication(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modulo.
    def visitModulo(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#constantExpr.
    def visitConstantExpr(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#addition.
    def visitAddition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanAnd.
    def visitBooleanAnd(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#andOp.
    def visitAndOp(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#orOp.
    def visitOrOp(self, ctx):
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


    # Visit a parse tree produced by VisualFoxpro9Parser#numberOrCurrency.
    def visitNumberOrCurrency(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#boolOrNull.
    def visitBoolOrNull(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#date.
    def visitDate(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#string.
    def visitString(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#blob.
    def visitBlob(self, ctx):
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


