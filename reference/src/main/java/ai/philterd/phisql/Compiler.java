/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 */
package ai.philterd.phisql;

import ai.philterd.phisql.grammar.PhiSQLParser;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.List;
import java.util.Locale;

/**
 * Compiles a parsed PhiSQL document into a Phileas JSON policy.
 *
 * <p>The compiler is driven by {@link Catalog}, which loads the
 * spec/v0.1/catalog/*.yaml files. Translation rules are defined by those
 * files; this class implements the traversal.
 */
public final class Compiler {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private final Catalog catalog;

    public Compiler() {
        this(Catalog.loadDefault());
    }

    public Compiler(Catalog catalog) {
        this.catalog = catalog;
    }

    public CompileResult compile(String source) {
        return compile(PhiSQL.parse(source));
    }

    public CompileResult compile(PhiSQLParser.DocumentContext document) {
        ObjectNode policyJson = MAPPER.createObjectNode();
        ObjectNode identifiers = policyJson.putObject("identifiers");

        String policyName = null;
        String description = null;

        for (PhiSQLParser.StatementContext stmt : document.statement()) {
            if (stmt.policyDecl() != null) {
                PhiSQLParser.PolicyDeclContext p = stmt.policyDecl();
                policyName = p.policyName.getText();
                if (p.description != null) {
                    description = unquoteString(p.description.getText());
                }
            } else if (stmt.redactStmt() != null) {
                compileRedact(stmt.redactStmt(), identifiers);
            } else if (stmt.deidentifyStmt() != null) {
                compileDeidentify(stmt.deidentifyStmt(), identifiers);
            } else if (stmt.ignoreStmt() != null) {
                compileIgnore(stmt.ignoreStmt(), identifiers, policyJson);
            }
        }

        return new CompileResult(policyName, description, policyJson);
    }

    // ------------------------------------------------------------------
    // REDACT
    // ------------------------------------------------------------------

    private void compileRedact(PhiSQLParser.RedactStmtContext ctx, ObjectNode identifiers) {
        ObjectNode strategyJson = buildStrategyObject(ctx.strategyExpr());
        if (ctx.predicate() != null) {
            strategyJson.put("conditions", compilePredicate(ctx.predicate()));
        }
        for (PhiSQLParser.EntityTypeContext entityCtx : ctx.entityList().entityType()) {
            appendStrategy(identifiers, entityCtx, strategyJson.deepCopy());
        }
    }

    // ------------------------------------------------------------------
    // DEIDENTIFY
    // ------------------------------------------------------------------

    private void compileDeidentify(PhiSQLParser.DeidentifyStmtContext ctx, ObjectNode identifiers) {
        for (PhiSQLParser.EntityAssignmentContext assignment : ctx.entityAssignment()) {
            ObjectNode strategyJson = buildStrategyObject(assignment.strategyExpr());
            appendStrategy(identifiers, assignment.entityType(), strategyJson);
        }
    }

    // ------------------------------------------------------------------
    // IGNORE
    // ------------------------------------------------------------------

    private void compileIgnore(PhiSQLParser.IgnoreStmtContext ctx,
                               ObjectNode identifiers,
                               ObjectNode policyJson) {
        boolean isTerms = ctx.TERMS() != null;
        boolean scoped = ctx.entityList() != null;

        if (isTerms) {
            List<String> terms = ctx.stringList().STRING_LITERAL().stream()
                    .map(TerminalNode::getText)
                    .map(Compiler::unquoteString)
                    .toList();
            if (!scoped) {
                throw new CompileException(
                        "IGNORE TERMS requires a FOR <entity> clause; "
                                + "scope-less IGNORE TERMS has no Phileas JSON equivalent.");
            }
            for (PhiSQLParser.EntityTypeContext entityCtx : ctx.entityList().entityType()) {
                ObjectNode entityNode = getOrCreateEntityNode(identifiers, entityCtx);
                ArrayNode ignored = entityNode.has("ignored")
                        ? (ArrayNode) entityNode.get("ignored")
                        : entityNode.putArray("ignored");
                for (String term : terms) {
                    ignored.add(term);
                }
            }
            return;
        }

        // PATTERN
        String pattern = unquoteString(ctx.STRING_LITERAL().getText());
        if (scoped) {
            for (PhiSQLParser.EntityTypeContext entityCtx : ctx.entityList().entityType()) {
                ObjectNode entityNode = getOrCreateEntityNode(identifiers, entityCtx);
                ArrayNode ignoredPatterns = entityNode.has("ignoredPatterns")
                        ? (ArrayNode) entityNode.get("ignoredPatterns")
                        : entityNode.putArray("ignoredPatterns");
                ignoredPatterns.addObject().put("pattern", pattern);
            }
        } else {
            ArrayNode topLevel = policyJson.has("ignoredPatterns")
                    ? (ArrayNode) policyJson.get("ignoredPatterns")
                    : policyJson.putArray("ignoredPatterns");
            topLevel.addObject().put("pattern", pattern);
        }
    }

    // ------------------------------------------------------------------
    // Strategy translation
    // ------------------------------------------------------------------

    private ObjectNode buildStrategyObject(PhiSQLParser.StrategyExprContext ctx) {
        String strategyName = ctx.strategyName().getText();
        Catalog.Strategy strategy = catalog.getStrategy(strategyName);
        if (strategy == null) {
            throw new CompileException("Unknown strategy: " + strategyName);
        }

        ObjectNode out = MAPPER.createObjectNode();
        out.put("strategy", strategy.phileasEnum());

        if (ctx.strategyArgs() == null) {
            return out;
        }

        for (PhiSQLParser.NamedArgContext argCtx : ctx.strategyArgs().namedArg()) {
            String argName = argCtx.argName.getText();
            Catalog.StrategyArg arg = strategy.findArg(argName);
            if (arg == null) {
                throw new CompileException(
                        "Strategy " + strategyName + " does not accept argument '" + argName + "'");
            }
            placeArgValue(out, arg, argCtx.literal());
        }
        return out;
    }

    private void placeArgValue(ObjectNode strategyObj,
                               Catalog.StrategyArg arg,
                               PhiSQLParser.LiteralContext literal) {
        String text = literal.getText();
        String type = arg.type() == null ? "string" : arg.type();

        switch (type) {
            case "string" -> strategyObj.put(arg.phileasField(), parseStringLiteral(text));
            case "integer" -> strategyObj.put(arg.phileasField(), Integer.parseInt(text));
            case "boolean" -> strategyObj.put(arg.phileasField(), Boolean.parseBoolean(text));
            case "enum" -> {
                String value = stripQuotesIfPresent(text).toUpperCase(Locale.ROOT);
                if (!arg.enumValues().contains(value)) {
                    throw new CompileException(
                            "Argument '" + arg.name() + "' must be one of "
                                    + arg.enumValues() + "; got '" + value + "'");
                }
                strategyObj.put(arg.phileasField(), value);
            }
            default -> throw new CompileException("Unsupported argument type: " + type);
        }
    }

    // ------------------------------------------------------------------
    // Entity placement
    // ------------------------------------------------------------------

    private void appendStrategy(ObjectNode identifiers,
                                PhiSQLParser.EntityTypeContext entityCtx,
                                ObjectNode strategyObj) {
        if (entityCtx instanceof PhiSQLParser.SimpleEntityTypeContext simple) {
            Catalog.EntityType entity = catalog.getEntity(simple.getText());
            if (entity == null) {
                throw new CompileException("Unknown entity type: " + simple.getText());
            }
            ObjectNode entityNode = (ObjectNode) identifiers.get(entity.phileasField());
            if (entityNode == null) {
                entityNode = identifiers.putObject(entity.phileasField());
            }
            ArrayNode strategies = entityNode.has(entity.phileasStrategiesField())
                    ? (ArrayNode) entityNode.get(entity.phileasStrategiesField())
                    : entityNode.putArray(entity.phileasStrategiesField());
            strategies.add(strategyObj);
            return;
        }
        if (entityCtx instanceof PhiSQLParser.CustomIdentifierContext custom) {
            String classification = unquoteString(custom.STRING_LITERAL().getText());
            ArrayNode identifierList = identifiers.has("identifiers")
                    ? (ArrayNode) identifiers.get("identifiers")
                    : identifiers.putArray("identifiers");
            // Reuse the entry with this classification if it already exists.
            ObjectNode entry = null;
            for (int i = 0; i < identifierList.size(); i++) {
                ObjectNode candidate = (ObjectNode) identifierList.get(i);
                if (classification.equals(candidate.path("classification").asText())) {
                    entry = candidate;
                    break;
                }
            }
            if (entry == null) {
                entry = identifierList.addObject();
                entry.put("classification", classification);
            }
            ArrayNode strategies = entry.has("identifierFilterStrategies")
                    ? (ArrayNode) entry.get("identifierFilterStrategies")
                    : entry.putArray("identifierFilterStrategies");
            strategies.add(strategyObj);
            return;
        }
        throw new CompileException("Unsupported entity type form: " + entityCtx.getText());
    }

    private ObjectNode getOrCreateEntityNode(ObjectNode identifiers,
                                             PhiSQLParser.EntityTypeContext entityCtx) {
        if (entityCtx instanceof PhiSQLParser.SimpleEntityTypeContext simple) {
            Catalog.EntityType entity = catalog.getEntity(simple.getText());
            if (entity == null) {
                throw new CompileException("Unknown entity type: " + simple.getText());
            }
            ObjectNode entityNode = (ObjectNode) identifiers.get(entity.phileasField());
            if (entityNode == null) {
                entityNode = identifiers.putObject(entity.phileasField());
            }
            return entityNode;
        }
        throw new CompileException(
                "IGNORE clauses scoped to custom identifiers are not supported in v0.1.");
    }

    // ------------------------------------------------------------------
    // Predicate translation
    // ------------------------------------------------------------------

    private String compilePredicate(PhiSQLParser.PredicateContext ctx) {
        if (ctx instanceof PhiSQLParser.ConfidencePredicateContext c) {
            return "confidence " + c.compareOp().getText() + " " + c.NUMERIC_LITERAL().getText();
        }
        if (ctx instanceof PhiSQLParser.ParenPredicateContext p) {
            return "( " + compilePredicate(p.predicate()) + " )";
        }
        if (ctx instanceof PhiSQLParser.LogicalPredicateContext l) {
            String op = l.AND() != null ? "and" : "or";
            return compilePredicate(l.predicate(0)) + " " + op + " " + compilePredicate(l.predicate(1));
        }
        throw new CompileException("Unsupported predicate form: " + ctx.getText());
    }

    // ------------------------------------------------------------------
    // Helpers
    // ------------------------------------------------------------------

    private static String unquoteString(String text) {
        if (text.length() >= 2 && text.charAt(0) == '\'' && text.charAt(text.length() - 1) == '\'') {
            String inner = text.substring(1, text.length() - 1);
            return inner.replace("\\'", "'").replace("\\n", "\n").replace("\\\\", "\\");
        }
        return text;
    }

    private static String parseStringLiteral(String text) {
        if (text.length() >= 2 && text.startsWith("'") && text.endsWith("'")) {
            return unquoteString(text);
        }
        return text;
    }

    private static String stripQuotesIfPresent(String text) {
        if (text.length() >= 2 && text.charAt(0) == '\'' && text.charAt(text.length() - 1) == '\'') {
            return text.substring(1, text.length() - 1);
        }
        return text;
    }

    /** Thrown when a parsed PhiSQL document cannot be compiled. */
    public static final class CompileException extends RuntimeException {
        public CompileException(String message) { super(message); }
    }
}
