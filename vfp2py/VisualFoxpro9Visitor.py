# Generated from VisualFoxpro9.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .VisualFoxpro9Parser import VisualFoxpro9Parser
else:
    from VisualFoxpro9Parser import VisualFoxpro9Parser

# This class defines a complete generic visitor for a parse tree produced by VisualFoxpro9Parser.

class VisualFoxpro9Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorCode.
    def visitPreprocessorCode(self, ctx:VisualFoxpro9Parser.PreprocessorCodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorLines.
    def visitPreprocessorLines(self, ctx:VisualFoxpro9Parser.PreprocessorLinesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorIf.
    def visitPreprocessorIf(self, ctx:VisualFoxpro9Parser.PreprocessorIfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorDefine.
    def visitPreprocessorDefine(self, ctx:VisualFoxpro9Parser.PreprocessorDefineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorUndefine.
    def visitPreprocessorUndefine(self, ctx:VisualFoxpro9Parser.PreprocessorUndefineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorInclude.
    def visitPreprocessorInclude(self, ctx:VisualFoxpro9Parser.PreprocessorIncludeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#preprocessorJunk.
    def visitPreprocessorJunk(self, ctx:VisualFoxpro9Parser.PreprocessorJunkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#nonpreprocessorLine.
    def visitNonpreprocessorLine(self, ctx:VisualFoxpro9Parser.NonpreprocessorLineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#prg.
    def visitPrg(self, ctx:VisualFoxpro9Parser.PrgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lineComment.
    def visitLineComment(self, ctx:VisualFoxpro9Parser.LineCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#line.
    def visitLine(self, ctx:VisualFoxpro9Parser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lineEnd.
    def visitLineEnd(self, ctx:VisualFoxpro9Parser.LineEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#lines.
    def visitLines(self, ctx:VisualFoxpro9Parser.LinesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#nongreedyLines.
    def visitNongreedyLines(self, ctx:VisualFoxpro9Parser.NongreedyLinesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDefStart.
    def visitClassDefStart(self, ctx:VisualFoxpro9Parser.ClassDefStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classDef.
    def visitClassDef(self, ctx:VisualFoxpro9Parser.ClassDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#classProperty.
    def visitClassProperty(self, ctx:VisualFoxpro9Parser.ClassPropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameter.
    def visitParameter(self, ctx:VisualFoxpro9Parser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#parameters.
    def visitParameters(self, ctx:VisualFoxpro9Parser.ParametersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDefStart.
    def visitFuncDefStart(self, ctx:VisualFoxpro9Parser.FuncDefStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDef.
    def visitFuncDef(self, ctx:VisualFoxpro9Parser.FuncDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#ifStart.
    def visitIfStart(self, ctx:VisualFoxpro9Parser.IfStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#ifStmt.
    def visitIfStmt(self, ctx:VisualFoxpro9Parser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forStart.
    def visitForStart(self, ctx:VisualFoxpro9Parser.ForStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forEnd.
    def visitForEnd(self, ctx:VisualFoxpro9Parser.ForEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#forStmt.
    def visitForStmt(self, ctx:VisualFoxpro9Parser.ForStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#singleCase.
    def visitSingleCase(self, ctx:VisualFoxpro9Parser.SingleCaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#otherwise.
    def visitOtherwise(self, ctx:VisualFoxpro9Parser.OtherwiseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#caseStmt.
    def visitCaseStmt(self, ctx:VisualFoxpro9Parser.CaseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#whileStart.
    def visitWhileStart(self, ctx:VisualFoxpro9Parser.WhileStartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#whileStmt.
    def visitWhileStmt(self, ctx:VisualFoxpro9Parser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#withStmt.
    def visitWithStmt(self, ctx:VisualFoxpro9Parser.WithStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scanStmt.
    def visitScanStmt(self, ctx:VisualFoxpro9Parser.ScanStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#tryStmt.
    def visitTryStmt(self, ctx:VisualFoxpro9Parser.TryStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#controlStmt.
    def visitControlStmt(self, ctx:VisualFoxpro9Parser.ControlStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#addObject.
    def visitAddObject(self, ctx:VisualFoxpro9Parser.AddObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#programControl.
    def visitProgramControl(self, ctx:VisualFoxpro9Parser.ProgramControlContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atPos.
    def visitAtPos(self, ctx:VisualFoxpro9Parser.AtPosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcDo.
    def visitFuncDo(self, ctx:VisualFoxpro9Parser.FuncDoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assign.
    def visitAssign(self, ctx:VisualFoxpro9Parser.AssignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#declaration.
    def visitDeclaration(self, ctx:VisualFoxpro9Parser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#printStmt.
    def visitPrintStmt(self, ctx:VisualFoxpro9Parser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#waitCmd.
    def visitWaitCmd(self, ctx:VisualFoxpro9Parser.WaitCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deleteFile.
    def visitDeleteFile(self, ctx:VisualFoxpro9Parser.DeleteFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyMoveFile.
    def visitCopyMoveFile(self, ctx:VisualFoxpro9Parser.CopyMoveFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#chMkRmDir.
    def visitChMkRmDir(self, ctx:VisualFoxpro9Parser.ChMkRmDirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#returnStmt.
    def visitReturnStmt(self, ctx:VisualFoxpro9Parser.ReturnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#onStmt.
    def visitOnStmt(self, ctx:VisualFoxpro9Parser.OnStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#release.
    def visitRelease(self, ctx:VisualFoxpro9Parser.ReleaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setStmt.
    def visitSetStmt(self, ctx:VisualFoxpro9Parser.SetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#push.
    def visitPush(self, ctx:VisualFoxpro9Parser.PushContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pop.
    def visitPop(self, ctx:VisualFoxpro9Parser.PopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#keyboard.
    def visitKeyboard(self, ctx:VisualFoxpro9Parser.KeyboardContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#defineMenu.
    def visitDefineMenu(self, ctx:VisualFoxpro9Parser.DefineMenuContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#definePad.
    def visitDefinePad(self, ctx:VisualFoxpro9Parser.DefinePadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#definePopup.
    def visitDefinePopup(self, ctx:VisualFoxpro9Parser.DefinePopupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#defineBar.
    def visitDefineBar(self, ctx:VisualFoxpro9Parser.DefineBarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateWindow.
    def visitActivateWindow(self, ctx:VisualFoxpro9Parser.ActivateWindowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateScreen.
    def visitActivateScreen(self, ctx:VisualFoxpro9Parser.ActivateScreenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activateMenu.
    def visitActivateMenu(self, ctx:VisualFoxpro9Parser.ActivateMenuContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#activatePopup.
    def visitActivatePopup(self, ctx:VisualFoxpro9Parser.ActivatePopupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deactivate.
    def visitDeactivate(self, ctx:VisualFoxpro9Parser.DeactivateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modifyWindow.
    def visitModifyWindow(self, ctx:VisualFoxpro9Parser.ModifyWindowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modifyFile.
    def visitModifyFile(self, ctx:VisualFoxpro9Parser.ModifyFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#raiseError.
    def visitRaiseError(self, ctx:VisualFoxpro9Parser.RaiseErrorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#throwError.
    def visitThrowError(self, ctx:VisualFoxpro9Parser.ThrowErrorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#createTable.
    def visitCreateTable(self, ctx:VisualFoxpro9Parser.CreateTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#alterTable.
    def visitAlterTable(self, ctx:VisualFoxpro9Parser.AlterTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#select.
    def visitSelect(self, ctx:VisualFoxpro9Parser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#use.
    def visitUse(self, ctx:VisualFoxpro9Parser.UseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#locate.
    def visitLocate(self, ctx:VisualFoxpro9Parser.LocateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#continueLocate.
    def visitContinueLocate(self, ctx:VisualFoxpro9Parser.ContinueLocateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#retry.
    def visitRetry(self, ctx:VisualFoxpro9Parser.RetryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#replace.
    def visitReplace(self, ctx:VisualFoxpro9Parser.ReplaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#indexOn.
    def visitIndexOn(self, ctx:VisualFoxpro9Parser.IndexOnContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#count.
    def visitCount(self, ctx:VisualFoxpro9Parser.CountContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#sum.
    def visitSum(self, ctx:VisualFoxpro9Parser.SumContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#sortCmd.
    def visitSortCmd(self, ctx:VisualFoxpro9Parser.SortCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#deleteRecord.
    def visitDeleteRecord(self, ctx:VisualFoxpro9Parser.DeleteRecordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#appendFrom.
    def visitAppendFrom(self, ctx:VisualFoxpro9Parser.AppendFromContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#append.
    def visitAppend(self, ctx:VisualFoxpro9Parser.AppendContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#insert.
    def visitInsert(self, ctx:VisualFoxpro9Parser.InsertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#skipRecord.
    def visitSkipRecord(self, ctx:VisualFoxpro9Parser.SkipRecordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pack.
    def visitPack(self, ctx:VisualFoxpro9Parser.PackContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#reindex.
    def visitReindex(self, ctx:VisualFoxpro9Parser.ReindexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#seekRecord.
    def visitSeekRecord(self, ctx:VisualFoxpro9Parser.SeekRecordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#updateCmd.
    def visitUpdateCmd(self, ctx:VisualFoxpro9Parser.UpdateCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#goRecord.
    def visitGoRecord(self, ctx:VisualFoxpro9Parser.GoRecordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyToArray.
    def visitCopyToArray(self, ctx:VisualFoxpro9Parser.CopyToArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#copyTo.
    def visitCopyTo(self, ctx:VisualFoxpro9Parser.CopyToContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#zapTable.
    def visitZapTable(self, ctx:VisualFoxpro9Parser.ZapTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#browse.
    def visitBrowse(self, ctx:VisualFoxpro9Parser.BrowseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scatterExpr.
    def visitScatterExpr(self, ctx:VisualFoxpro9Parser.ScatterExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#gatherExpr.
    def visitGatherExpr(self, ctx:VisualFoxpro9Parser.GatherExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#closeStmt.
    def visitCloseStmt(self, ctx:VisualFoxpro9Parser.CloseStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#readEvent.
    def visitReadEvent(self, ctx:VisualFoxpro9Parser.ReadEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#unlockCmd.
    def visitUnlockCmd(self, ctx:VisualFoxpro9Parser.UnlockCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#clearStmt.
    def visitClearStmt(self, ctx:VisualFoxpro9Parser.ClearStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#report.
    def visitReport(self, ctx:VisualFoxpro9Parser.ReportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllDeclare.
    def visitDllDeclare(self, ctx:VisualFoxpro9Parser.DllDeclareContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#shellRun.
    def visitShellRun(self, ctx:VisualFoxpro9Parser.ShellRunContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#assert.
    def visitAssert(self, ctx:VisualFoxpro9Parser.AssertContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#compileCmd.
    def visitCompileCmd(self, ctx:VisualFoxpro9Parser.CompileCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#listStmt.
    def visitListStmt(self, ctx:VisualFoxpro9Parser.ListStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#saveToCmd.
    def visitSaveToCmd(self, ctx:VisualFoxpro9Parser.SaveToCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#restoreCmd.
    def visitRestoreCmd(self, ctx:VisualFoxpro9Parser.RestoreCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#zoomCmd.
    def visitZoomCmd(self, ctx:VisualFoxpro9Parser.ZoomCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#textBlock.
    def visitTextBlock(self, ctx:VisualFoxpro9Parser.TextBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#showCmd.
    def visitShowCmd(self, ctx:VisualFoxpro9Parser.ShowCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#hideCmd.
    def visitHideCmd(self, ctx:VisualFoxpro9Parser.HideCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#exprCmd.
    def visitExprCmd(self, ctx:VisualFoxpro9Parser.ExprCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#complexIdCmd.
    def visitComplexIdCmd(self, ctx:VisualFoxpro9Parser.ComplexIdCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#queryCondition.
    def visitQueryCondition(self, ctx:VisualFoxpro9Parser.QueryConditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#textChunk.
    def visitTextChunk(self, ctx:VisualFoxpro9Parser.TextChunkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArgs.
    def visitDllArgs(self, ctx:VisualFoxpro9Parser.DllArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#dllArg.
    def visitDllArg(self, ctx:VisualFoxpro9Parser.DllArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#tableField.
    def visitTableField(self, ctx:VisualFoxpro9Parser.TableFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#setCmd.
    def visitSetCmd(self, ctx:VisualFoxpro9Parser.SetCmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#declarationItem.
    def visitDeclarationItem(self, ctx:VisualFoxpro9Parser.DeclarationItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#asType.
    def visitAsType(self, ctx:VisualFoxpro9Parser.AsTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#asTypeOf.
    def visitAsTypeOf(self, ctx:VisualFoxpro9Parser.AsTypeOfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#argsItem.
    def visitArgsItem(self, ctx:VisualFoxpro9Parser.ArgsItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#args.
    def visitArgs(self, ctx:VisualFoxpro9Parser.ArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#specialArgs.
    def visitSpecialArgs(self, ctx:VisualFoxpro9Parser.SpecialArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#reference.
    def visitReference(self, ctx:VisualFoxpro9Parser.ReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#comparison.
    def visitComparison(self, ctx:VisualFoxpro9Parser.ComparisonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#castExpr.
    def visitCastExpr(self, ctx:VisualFoxpro9Parser.CastExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atomExpr.
    def visitAtomExpr(self, ctx:VisualFoxpro9Parser.AtomExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#subExpr.
    def visitSubExpr(self, ctx:VisualFoxpro9Parser.SubExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanNegation.
    def visitBooleanNegation(self, ctx:VisualFoxpro9Parser.BooleanNegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#unaryNegation.
    def visitUnaryNegation(self, ctx:VisualFoxpro9Parser.UnaryNegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanOr.
    def visitBooleanOr(self, ctx:VisualFoxpro9Parser.BooleanOrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#power.
    def visitPower(self, ctx:VisualFoxpro9Parser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#multiplication.
    def visitMultiplication(self, ctx:VisualFoxpro9Parser.MultiplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#modulo.
    def visitModulo(self, ctx:VisualFoxpro9Parser.ModuloContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#constantExpr.
    def visitConstantExpr(self, ctx:VisualFoxpro9Parser.ConstantExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#addition.
    def visitAddition(self, ctx:VisualFoxpro9Parser.AdditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#booleanAnd.
    def visitBooleanAnd(self, ctx:VisualFoxpro9Parser.BooleanAndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#andOp.
    def visitAndOp(self, ctx:VisualFoxpro9Parser.AndOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#orOp.
    def visitOrOp(self, ctx:VisualFoxpro9Parser.OrOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#complexId.
    def visitComplexId(self, ctx:VisualFoxpro9Parser.ComplexIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#atom.
    def visitAtom(self, ctx:VisualFoxpro9Parser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#funcCallTrailer.
    def visitFuncCallTrailer(self, ctx:VisualFoxpro9Parser.FuncCallTrailerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#identTrailer.
    def visitIdentTrailer(self, ctx:VisualFoxpro9Parser.IdentTrailerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pathname.
    def visitPathname(self, ctx:VisualFoxpro9Parser.PathnameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#pathElement.
    def visitPathElement(self, ctx:VisualFoxpro9Parser.PathElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#specialExpr.
    def visitSpecialExpr(self, ctx:VisualFoxpro9Parser.SpecialExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#numberOrCurrency.
    def visitNumberOrCurrency(self, ctx:VisualFoxpro9Parser.NumberOrCurrencyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#boolOrNull.
    def visitBoolOrNull(self, ctx:VisualFoxpro9Parser.BoolOrNullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#date.
    def visitDate(self, ctx:VisualFoxpro9Parser.DateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#string.
    def visitString(self, ctx:VisualFoxpro9Parser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#blob.
    def visitBlob(self, ctx:VisualFoxpro9Parser.BlobContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#idAttr2.
    def visitIdAttr2(self, ctx:VisualFoxpro9Parser.IdAttr2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#idAttr.
    def visitIdAttr(self, ctx:VisualFoxpro9Parser.IdAttrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#twoExpr.
    def visitTwoExpr(self, ctx:VisualFoxpro9Parser.TwoExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#arrayIndex.
    def visitArrayIndex(self, ctx:VisualFoxpro9Parser.ArrayIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#datatype.
    def visitDatatype(self, ctx:VisualFoxpro9Parser.DatatypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#scopeClause.
    def visitScopeClause(self, ctx:VisualFoxpro9Parser.ScopeClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by VisualFoxpro9Parser#identifier.
    def visitIdentifier(self, ctx:VisualFoxpro9Parser.IdentifierContext):
        return self.visitChildren(ctx)



del VisualFoxpro9Parser