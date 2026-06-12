# Generated from spec/v1.0/grammar/PhiSQL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PhiSQLParser import PhiSQLParser
else:
    from PhiSQLParser import PhiSQLParser

# This class defines a complete generic visitor for a parse tree produced by PhiSQLParser.

class PhiSQLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PhiSQLParser#document.
    def visitDocument(self, ctx:PhiSQLParser.DocumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#statement.
    def visitStatement(self, ctx:PhiSQLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#policyDecl.
    def visitPolicyDecl(self, ctx:PhiSQLParser.PolicyDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#configureStmt.
    def visitConfigureStmt(self, ctx:PhiSQLParser.ConfigureStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#settingList.
    def visitSettingList(self, ctx:PhiSQLParser.SettingListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#setting.
    def visitSetting(self, ctx:PhiSQLParser.SettingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#settingKey.
    def visitSettingKey(self, ctx:PhiSQLParser.SettingKeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#settingValue.
    def visitSettingValue(self, ctx:PhiSQLParser.SettingValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#objectValue.
    def visitObjectValue(self, ctx:PhiSQLParser.ObjectValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#arrayValue.
    def visitArrayValue(self, ctx:PhiSQLParser.ArrayValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#optionsClause.
    def visitOptionsClause(self, ctx:PhiSQLParser.OptionsClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#redactStmt.
    def visitRedactStmt(self, ctx:PhiSQLParser.RedactStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#deidentifyStmt.
    def visitDeidentifyStmt(self, ctx:PhiSQLParser.DeidentifyStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#entityAssignment.
    def visitEntityAssignment(self, ctx:PhiSQLParser.EntityAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#ignoreStmt.
    def visitIgnoreStmt(self, ctx:PhiSQLParser.IgnoreStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#defineIdentifierStmt.
    def visitDefineIdentifierStmt(self, ctx:PhiSQLParser.DefineIdentifierStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#defineDictionaryStmt.
    def visitDefineDictionaryStmt(self, ctx:PhiSQLParser.DefineDictionaryStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#defineSectionStmt.
    def visitDefineSectionStmt(self, ctx:PhiSQLParser.DefineSectionStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#detectStmt.
    def visitDetectStmt(self, ctx:PhiSQLParser.DetectStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#findPiiStmt.
    def visitFindPiiStmt(self, ctx:PhiSQLParser.FindPiiStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#discoverEntitiesStmt.
    def visitDiscoverEntitiesStmt(self, ctx:PhiSQLParser.DiscoverEntitiesStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#scanStmt.
    def visitScanStmt(self, ctx:PhiSQLParser.ScanStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#selectFindingsStmt.
    def visitSelectFindingsStmt(self, ctx:PhiSQLParser.SelectFindingsStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#inClause.
    def visitInClause(self, ctx:PhiSQLParser.InClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#whereDiscovery.
    def visitWhereDiscovery(self, ctx:PhiSQLParser.WhereDiscoveryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#parenDiscoveryPredicate.
    def visitParenDiscoveryPredicate(self, ctx:PhiSQLParser.ParenDiscoveryPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#inDiscoveryPredicate.
    def visitInDiscoveryPredicate(self, ctx:PhiSQLParser.InDiscoveryPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#compareDiscoveryPredicate.
    def visitCompareDiscoveryPredicate(self, ctx:PhiSQLParser.CompareDiscoveryPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#logicalDiscoveryPredicate.
    def visitLogicalDiscoveryPredicate(self, ctx:PhiSQLParser.LogicalDiscoveryPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#projectionList.
    def visitProjectionList(self, ctx:PhiSQLParser.ProjectionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#starProjection.
    def visitStarProjection(self, ctx:PhiSQLParser.StarProjectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#aggregateProjection.
    def visitAggregateProjection(self, ctx:PhiSQLParser.AggregateProjectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#columnProjection.
    def visitColumnProjection(self, ctx:PhiSQLParser.ColumnProjectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#aggregate.
    def visitAggregate(self, ctx:PhiSQLParser.AggregateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#starAggArg.
    def visitStarAggArg(self, ctx:PhiSQLParser.StarAggArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#columnAggArg.
    def visitColumnAggArg(self, ctx:PhiSQLParser.ColumnAggArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#columnRef.
    def visitColumnRef(self, ctx:PhiSQLParser.ColumnRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#findingsRef.
    def visitFindingsRef(self, ctx:PhiSQLParser.FindingsRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#groupByClause.
    def visitGroupByClause(self, ctx:PhiSQLParser.GroupByClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#limitClause.
    def visitLimitClause(self, ctx:PhiSQLParser.LimitClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#entityList.
    def visitEntityList(self, ctx:PhiSQLParser.EntityListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#simpleEntityType.
    def visitSimpleEntityType(self, ctx:PhiSQLParser.SimpleEntityTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#customIdentifier.
    def visitCustomIdentifier(self, ctx:PhiSQLParser.CustomIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#strategyExpr.
    def visitStrategyExpr(self, ctx:PhiSQLParser.StrategyExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#strategyName.
    def visitStrategyName(self, ctx:PhiSQLParser.StrategyNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#strategyArgs.
    def visitStrategyArgs(self, ctx:PhiSQLParser.StrategyArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#namedArg.
    def visitNamedArg(self, ctx:PhiSQLParser.NamedArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#confidencePredicate.
    def visitConfidencePredicate(self, ctx:PhiSQLParser.ConfidencePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#parenPredicate.
    def visitParenPredicate(self, ctx:PhiSQLParser.ParenPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#logicalPredicate.
    def visitLogicalPredicate(self, ctx:PhiSQLParser.LogicalPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#compareOp.
    def visitCompareOp(self, ctx:PhiSQLParser.CompareOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#stringList.
    def visitStringList(self, ctx:PhiSQLParser.StringListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PhiSQLParser#literal.
    def visitLiteral(self, ctx:PhiSQLParser.LiteralContext):
        return self.visitChildren(ctx)



del PhiSQLParser