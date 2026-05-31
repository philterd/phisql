/*
 * Copyright 2026 Philterd, LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ai.philterd.phisql;

import ai.philterd.phisql.grammar.PhiSQLParser;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
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

    /**
     * Compiles PhiSQL from a string with no filename context. The policy name
     * comes from the {@code POLICY} declaration if present; otherwise null.
     */
    public CompileResult compile(String source) {
        return compile(PhiSQL.parse(source), null);
    }

    /**
     * Compiles PhiSQL from a file. The policy name is the file's basename
     * (with {@code .phisql} stripped). If the file contains a {@code POLICY}
     * declaration, its name must match the basename after normalization
     * (hyphens and underscores are treated as equivalent).
     *
     * @throws CompileException on a POLICY/filename mismatch.
     */
    public CompileResult compile(Path file) throws IOException {
        String source = Files.readString(file);
        return compile(PhiSQL.parse(source), basenameWithoutExtension(file));
    }

    /**
     * Compiles PhiSQL from a string with an explicit expected name. This is
     * the form used when the source did not come from a file but the caller
     * still knows what the policy should be named (e.g., an HTTP upload
     * carrying a {@code name} parameter).
     */
    public CompileResult compile(String source, String expectedName) {
        return compile(PhiSQL.parse(source), expectedName);
    }

    public CompileResult compile(PhiSQLParser.DocumentContext document, String expectedName) {
        ObjectNode policyJson = MAPPER.createObjectNode();
        ObjectNode identifiers = policyJson.putObject("identifiers");

        String declaredName = null;
        String description = null;

        for (PhiSQLParser.StatementContext stmt : document.statement()) {
            if (stmt.policyDecl() != null) {
                PhiSQLParser.PolicyDeclContext p = stmt.policyDecl();
                declaredName = p.policyName.getText();
                if (p.description != null) {
                    description = unquoteString(p.description.getText());
                }
            } else if (stmt.redactStmt() != null) {
                compileRedact(stmt.redactStmt(), identifiers);
            } else if (stmt.deidentifyStmt() != null) {
                compileDeidentify(stmt.deidentifyStmt(), identifiers);
            } else if (stmt.ignoreStmt() != null) {
                compileIgnore(stmt.ignoreStmt(), identifiers, policyJson);
            } else if (stmt.defineIdentifierStmt() != null) {
                compileDefineIdentifier(stmt.defineIdentifierStmt(), identifiers);
            } else if (stmt.detectStmt() != null) {
                compileDetect(stmt.detectStmt(), identifiers);
            } else if (stmt.configureStmt() != null) {
                compileConfigure(stmt.configureStmt(), policyJson);
            }
        }

        String policyName = resolvePolicyName(expectedName, declaredName);
        return new CompileResult(policyName, description, policyJson);
    }

    /** Backwards-compatible single-arg form (no expected name). */
    public CompileResult compile(PhiSQLParser.DocumentContext document) {
        return compile(document, null);
    }

    /**
     * Compiles a CONFIGURE statement into the policy's top-level {@code crypto} or {@code fpe} block.
     * The supplied environment-variable name is written with the {@code env:} prefix that Phileas
     * resolves at runtime, so the actual secret is never stored in the policy.
     */
    private void compileConfigure(PhiSQLParser.ConfigureStmtContext ctx, ObjectNode policyJson) {
        if (ctx.cryptoKeyEnv != null) {
            policyJson.putObject("crypto")
                    .put("key", "env:" + unquoteString(ctx.cryptoKeyEnv.getText()));
        } else {
            ObjectNode fpe = policyJson.putObject("fpe");
            fpe.put("key", "env:" + unquoteString(ctx.fpeKeyEnv.getText()));
            fpe.put("tweak", "env:" + unquoteString(ctx.fpeTweakEnv.getText()));
        }
    }

    /**
     * Resolves the policy name from the expected name (typically a filename
     * basename) and the declared name (from the POLICY statement). Implements
     * the v0.1 policy-naming rule defined in spec/v0.1/catalog/policy.yaml.
     */
    private static String resolvePolicyName(String expected, String declared) {
        if (expected != null && declared != null) {
            if (!normalizePolicyName(expected).equals(normalizePolicyName(declared))) {
                throw new CompileException(
                        "POLICY declaration name '" + declared
                                + "' does not match the expected name '" + expected
                                + "'. Either omit the POLICY statement or change it to match.");
            }
            return expected;
        }
        if (expected != null) return expected;
        return declared;
    }

    private static String normalizePolicyName(String name) {
        return name.replace('-', '_');
    }

    private static String basenameWithoutExtension(Path file) {
        String name = file.getFileName().toString();
        int dot = name.lastIndexOf('.');
        return dot > 0 ? name.substring(0, dot) : name;
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
            if (scoped) {
                for (PhiSQLParser.EntityTypeContext entityCtx : ctx.entityList().entityType()) {
                    ObjectNode entityNode = getOrCreateEntityNode(identifiers, entityCtx);
                    ArrayNode ignored = entityNode.has("ignored")
                            ? (ArrayNode) entityNode.get("ignored")
                            : entityNode.putArray("ignored");
                    for (String term : terms) {
                        ignored.add(term);
                    }
                }
            } else {
                // Scope-less IGNORE TERMS compiles to the top-level `ignored` array,
                // which is a list of named term-list objects per the Phileas schema.
                ArrayNode topLevel = policyJson.has("ignored")
                        ? (ArrayNode) policyJson.get("ignored")
                        : policyJson.putArray("ignored");
                ObjectNode termsObject = topLevel.addObject();
                ArrayNode termsArray = termsObject.putArray("terms");
                for (String term : terms) {
                    termsArray.add(term);
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
    // DEFINE IDENTIFIER (custom regex identifiers)
    // ------------------------------------------------------------------

    private void compileDefineIdentifier(PhiSQLParser.DefineIdentifierStmtContext ctx,
                                         ObjectNode identifiers) {
        String classification = unquoteString(ctx.classification.getText());
        String pattern = unquoteString(ctx.pattern.getText());

        ObjectNode strategyJson = buildStrategyObject(ctx.strategyExpr());
        if (ctx.predicate() != null) {
            strategyJson.put("conditions", compilePredicate(ctx.predicate()));
        }

        ArrayNode identifierList = identifiers.has("identifiers")
                ? (ArrayNode) identifiers.get("identifiers")
                : identifiers.putArray("identifiers");

        // Reuse an existing entry with this classification if present.
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
        entry.put("pattern", pattern);
        if (ctx.groupNumber != null) {
            entry.put("groupNumber", Integer.parseInt(ctx.groupNumber.getText()));
        }
        if (ctx.sensitivity != null) {
            entry.put("caseSensitive", ctx.sensitivity.getType() == PhiSQLParser.SENSITIVE);
        }

        ArrayNode strategies = entry.has("identifierFilterStrategies")
                ? (ArrayNode) entry.get("identifierFilterStrategies")
                : entry.putArray("identifierFilterStrategies");
        strategies.add(strategyJson);
    }

    // ------------------------------------------------------------------
    // DETECT PHEYE (AI / NER detection)
    // ------------------------------------------------------------------

    private void compileDetect(PhiSQLParser.DetectStmtContext ctx, ObjectNode identifiers) {
        ObjectNode strategyJson = buildStrategyObject(ctx.strategyExpr());
        if (ctx.predicate() != null) {
            strategyJson.put("conditions", compilePredicate(ctx.predicate()));
        }

        ArrayNode pheyes = identifiers.has("pheyes")
                ? (ArrayNode) identifiers.get("pheyes")
                : identifiers.putArray("pheyes");
        ObjectNode pheye = pheyes.addObject();
        pheye.putArray("phEyeFilterStrategies").add(strategyJson);

        boolean hasLabels = ctx.stringList() != null;
        boolean hasEndpoint = ctx.endpoint != null;
        if (hasLabels || hasEndpoint) {
            ObjectNode config = pheye.putObject("phEyeConfiguration");
            if (hasEndpoint) {
                config.put("endpoint", unquoteString(ctx.endpoint.getText()));
            }
            if (hasLabels) {
                ArrayNode labels = config.putArray("labels");
                for (TerminalNode t : ctx.stringList().STRING_LITERAL()) {
                    labels.add(unquoteString(t.getText()));
                }
            }
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
