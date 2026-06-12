# Generated from /Users/jeff/work/philterd/code/phisql/spec/v1.0/grammar/PhiSQL.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PhiSQLParser import PhiSQLParser
else:
    from PhiSQLParser import PhiSQLParser

# This class defines a complete listener for a parse tree produced by PhiSQLParser.
class PhiSQLListener(ParseTreeListener):

    # Enter a parse tree produced by PhiSQLParser#document.
    def enterDocument(self, ctx:PhiSQLParser.DocumentContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#document.
    def exitDocument(self, ctx:PhiSQLParser.DocumentContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#statement.
    def enterStatement(self, ctx:PhiSQLParser.StatementContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#statement.
    def exitStatement(self, ctx:PhiSQLParser.StatementContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#policyDecl.
    def enterPolicyDecl(self, ctx:PhiSQLParser.PolicyDeclContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#policyDecl.
    def exitPolicyDecl(self, ctx:PhiSQLParser.PolicyDeclContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#configureStmt.
    def enterConfigureStmt(self, ctx:PhiSQLParser.ConfigureStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#configureStmt.
    def exitConfigureStmt(self, ctx:PhiSQLParser.ConfigureStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#settingList.
    def enterSettingList(self, ctx:PhiSQLParser.SettingListContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#settingList.
    def exitSettingList(self, ctx:PhiSQLParser.SettingListContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#setting.
    def enterSetting(self, ctx:PhiSQLParser.SettingContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#setting.
    def exitSetting(self, ctx:PhiSQLParser.SettingContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#settingKey.
    def enterSettingKey(self, ctx:PhiSQLParser.SettingKeyContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#settingKey.
    def exitSettingKey(self, ctx:PhiSQLParser.SettingKeyContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#settingValue.
    def enterSettingValue(self, ctx:PhiSQLParser.SettingValueContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#settingValue.
    def exitSettingValue(self, ctx:PhiSQLParser.SettingValueContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#objectValue.
    def enterObjectValue(self, ctx:PhiSQLParser.ObjectValueContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#objectValue.
    def exitObjectValue(self, ctx:PhiSQLParser.ObjectValueContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#arrayValue.
    def enterArrayValue(self, ctx:PhiSQLParser.ArrayValueContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#arrayValue.
    def exitArrayValue(self, ctx:PhiSQLParser.ArrayValueContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#optionsClause.
    def enterOptionsClause(self, ctx:PhiSQLParser.OptionsClauseContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#optionsClause.
    def exitOptionsClause(self, ctx:PhiSQLParser.OptionsClauseContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#redactStmt.
    def enterRedactStmt(self, ctx:PhiSQLParser.RedactStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#redactStmt.
    def exitRedactStmt(self, ctx:PhiSQLParser.RedactStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#deidentifyStmt.
    def enterDeidentifyStmt(self, ctx:PhiSQLParser.DeidentifyStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#deidentifyStmt.
    def exitDeidentifyStmt(self, ctx:PhiSQLParser.DeidentifyStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#entityAssignment.
    def enterEntityAssignment(self, ctx:PhiSQLParser.EntityAssignmentContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#entityAssignment.
    def exitEntityAssignment(self, ctx:PhiSQLParser.EntityAssignmentContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#ignoreStmt.
    def enterIgnoreStmt(self, ctx:PhiSQLParser.IgnoreStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#ignoreStmt.
    def exitIgnoreStmt(self, ctx:PhiSQLParser.IgnoreStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#defineIdentifierStmt.
    def enterDefineIdentifierStmt(self, ctx:PhiSQLParser.DefineIdentifierStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#defineIdentifierStmt.
    def exitDefineIdentifierStmt(self, ctx:PhiSQLParser.DefineIdentifierStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#defineDictionaryStmt.
    def enterDefineDictionaryStmt(self, ctx:PhiSQLParser.DefineDictionaryStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#defineDictionaryStmt.
    def exitDefineDictionaryStmt(self, ctx:PhiSQLParser.DefineDictionaryStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#defineSectionStmt.
    def enterDefineSectionStmt(self, ctx:PhiSQLParser.DefineSectionStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#defineSectionStmt.
    def exitDefineSectionStmt(self, ctx:PhiSQLParser.DefineSectionStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#detectStmt.
    def enterDetectStmt(self, ctx:PhiSQLParser.DetectStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#detectStmt.
    def exitDetectStmt(self, ctx:PhiSQLParser.DetectStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#findPiiStmt.
    def enterFindPiiStmt(self, ctx:PhiSQLParser.FindPiiStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#findPiiStmt.
    def exitFindPiiStmt(self, ctx:PhiSQLParser.FindPiiStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#discoverEntitiesStmt.
    def enterDiscoverEntitiesStmt(self, ctx:PhiSQLParser.DiscoverEntitiesStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#discoverEntitiesStmt.
    def exitDiscoverEntitiesStmt(self, ctx:PhiSQLParser.DiscoverEntitiesStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#scanStmt.
    def enterScanStmt(self, ctx:PhiSQLParser.ScanStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#scanStmt.
    def exitScanStmt(self, ctx:PhiSQLParser.ScanStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#selectFindingsStmt.
    def enterSelectFindingsStmt(self, ctx:PhiSQLParser.SelectFindingsStmtContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#selectFindingsStmt.
    def exitSelectFindingsStmt(self, ctx:PhiSQLParser.SelectFindingsStmtContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#inClause.
    def enterInClause(self, ctx:PhiSQLParser.InClauseContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#inClause.
    def exitInClause(self, ctx:PhiSQLParser.InClauseContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#whereDiscovery.
    def enterWhereDiscovery(self, ctx:PhiSQLParser.WhereDiscoveryContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#whereDiscovery.
    def exitWhereDiscovery(self, ctx:PhiSQLParser.WhereDiscoveryContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#parenDiscoveryPredicate.
    def enterParenDiscoveryPredicate(self, ctx:PhiSQLParser.ParenDiscoveryPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#parenDiscoveryPredicate.
    def exitParenDiscoveryPredicate(self, ctx:PhiSQLParser.ParenDiscoveryPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#inDiscoveryPredicate.
    def enterInDiscoveryPredicate(self, ctx:PhiSQLParser.InDiscoveryPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#inDiscoveryPredicate.
    def exitInDiscoveryPredicate(self, ctx:PhiSQLParser.InDiscoveryPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#compareDiscoveryPredicate.
    def enterCompareDiscoveryPredicate(self, ctx:PhiSQLParser.CompareDiscoveryPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#compareDiscoveryPredicate.
    def exitCompareDiscoveryPredicate(self, ctx:PhiSQLParser.CompareDiscoveryPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#logicalDiscoveryPredicate.
    def enterLogicalDiscoveryPredicate(self, ctx:PhiSQLParser.LogicalDiscoveryPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#logicalDiscoveryPredicate.
    def exitLogicalDiscoveryPredicate(self, ctx:PhiSQLParser.LogicalDiscoveryPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#projectionList.
    def enterProjectionList(self, ctx:PhiSQLParser.ProjectionListContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#projectionList.
    def exitProjectionList(self, ctx:PhiSQLParser.ProjectionListContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#starProjection.
    def enterStarProjection(self, ctx:PhiSQLParser.StarProjectionContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#starProjection.
    def exitStarProjection(self, ctx:PhiSQLParser.StarProjectionContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#aggregateProjection.
    def enterAggregateProjection(self, ctx:PhiSQLParser.AggregateProjectionContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#aggregateProjection.
    def exitAggregateProjection(self, ctx:PhiSQLParser.AggregateProjectionContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#columnProjection.
    def enterColumnProjection(self, ctx:PhiSQLParser.ColumnProjectionContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#columnProjection.
    def exitColumnProjection(self, ctx:PhiSQLParser.ColumnProjectionContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#aggregate.
    def enterAggregate(self, ctx:PhiSQLParser.AggregateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#aggregate.
    def exitAggregate(self, ctx:PhiSQLParser.AggregateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#starAggArg.
    def enterStarAggArg(self, ctx:PhiSQLParser.StarAggArgContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#starAggArg.
    def exitStarAggArg(self, ctx:PhiSQLParser.StarAggArgContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#columnAggArg.
    def enterColumnAggArg(self, ctx:PhiSQLParser.ColumnAggArgContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#columnAggArg.
    def exitColumnAggArg(self, ctx:PhiSQLParser.ColumnAggArgContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#columnRef.
    def enterColumnRef(self, ctx:PhiSQLParser.ColumnRefContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#columnRef.
    def exitColumnRef(self, ctx:PhiSQLParser.ColumnRefContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#findingsRef.
    def enterFindingsRef(self, ctx:PhiSQLParser.FindingsRefContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#findingsRef.
    def exitFindingsRef(self, ctx:PhiSQLParser.FindingsRefContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#groupByClause.
    def enterGroupByClause(self, ctx:PhiSQLParser.GroupByClauseContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#groupByClause.
    def exitGroupByClause(self, ctx:PhiSQLParser.GroupByClauseContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#limitClause.
    def enterLimitClause(self, ctx:PhiSQLParser.LimitClauseContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#limitClause.
    def exitLimitClause(self, ctx:PhiSQLParser.LimitClauseContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#entityList.
    def enterEntityList(self, ctx:PhiSQLParser.EntityListContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#entityList.
    def exitEntityList(self, ctx:PhiSQLParser.EntityListContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#simpleEntityType.
    def enterSimpleEntityType(self, ctx:PhiSQLParser.SimpleEntityTypeContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#simpleEntityType.
    def exitSimpleEntityType(self, ctx:PhiSQLParser.SimpleEntityTypeContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#customIdentifier.
    def enterCustomIdentifier(self, ctx:PhiSQLParser.CustomIdentifierContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#customIdentifier.
    def exitCustomIdentifier(self, ctx:PhiSQLParser.CustomIdentifierContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#strategyExpr.
    def enterStrategyExpr(self, ctx:PhiSQLParser.StrategyExprContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#strategyExpr.
    def exitStrategyExpr(self, ctx:PhiSQLParser.StrategyExprContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#strategyName.
    def enterStrategyName(self, ctx:PhiSQLParser.StrategyNameContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#strategyName.
    def exitStrategyName(self, ctx:PhiSQLParser.StrategyNameContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#strategyArgs.
    def enterStrategyArgs(self, ctx:PhiSQLParser.StrategyArgsContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#strategyArgs.
    def exitStrategyArgs(self, ctx:PhiSQLParser.StrategyArgsContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#namedArg.
    def enterNamedArg(self, ctx:PhiSQLParser.NamedArgContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#namedArg.
    def exitNamedArg(self, ctx:PhiSQLParser.NamedArgContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#confidencePredicate.
    def enterConfidencePredicate(self, ctx:PhiSQLParser.ConfidencePredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#confidencePredicate.
    def exitConfidencePredicate(self, ctx:PhiSQLParser.ConfidencePredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#parenPredicate.
    def enterParenPredicate(self, ctx:PhiSQLParser.ParenPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#parenPredicate.
    def exitParenPredicate(self, ctx:PhiSQLParser.ParenPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#logicalPredicate.
    def enterLogicalPredicate(self, ctx:PhiSQLParser.LogicalPredicateContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#logicalPredicate.
    def exitLogicalPredicate(self, ctx:PhiSQLParser.LogicalPredicateContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#compareOp.
    def enterCompareOp(self, ctx:PhiSQLParser.CompareOpContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#compareOp.
    def exitCompareOp(self, ctx:PhiSQLParser.CompareOpContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#stringList.
    def enterStringList(self, ctx:PhiSQLParser.StringListContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#stringList.
    def exitStringList(self, ctx:PhiSQLParser.StringListContext):
        pass


    # Enter a parse tree produced by PhiSQLParser#literal.
    def enterLiteral(self, ctx:PhiSQLParser.LiteralContext):
        pass

    # Exit a parse tree produced by PhiSQLParser#literal.
    def exitLiteral(self, ctx:PhiSQLParser.LiteralContext):
        pass



del PhiSQLParser