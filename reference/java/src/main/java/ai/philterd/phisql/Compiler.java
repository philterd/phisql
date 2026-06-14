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
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Compiles a parsed PhiSQL document into a Phileas JSON policy.
 *
 * <p>The compiler is driven by {@link Catalog}, which loads the
 * spec/v1.0/catalog/*.yaml files. Translation rules are defined by those
 * files; this class implements the traversal.
 *
 * <p><b>Scope.</b> This compiler targets the redaction subset of PhiSQL
 * (REDACT, DEIDENTIFY, IGNORE, DEFINE IDENTIFIER, DEFINE DICTIONARY,
 * DEFINE SECTION, DETECT PHEYE, and the CONFIGURE forms) and emits Phileas
 * JSON. Discovery statements (FIND PII, DISCOVER ENTITIES, SCAN, SELECT FROM
 * findings) parse successfully but are silently ignored by this compiler; they
 * target a separate discovery-query JSON schema documented in the spec
 * examples, and a discovery compiler will land in a follow-up.
 */
public final class Compiler {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    /** Allowed values for the dictionary FUZZY SENSITIVITY clause (schema sensitivityLevel enum). */
    private static final Set<String> SENSITIVITY_LEVELS = Set.of("auto", "off", "low", "medium", "high");

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
     * (hyphens and underscores are treated as equivalent). Defined in
     * spec/v1.0/catalog/policy.yaml.
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
            } else if (stmt.defineDictionaryStmt() != null) {
                compileDefineDictionary(stmt.defineDictionaryStmt(), identifiers);
            } else if (stmt.defineSectionStmt() != null) {
                compileDefineSection(stmt.defineSectionStmt(), identifiers);
            } else if (stmt.detectStmt() != null) {
                compileDetect(stmt.detectStmt(), identifiers);
            } else if (stmt.configureStmt() != null) {
                compileConfigure(stmt.configureStmt(), policyJson);
            }
        }

        String policyName = resolvePolicyName(expectedName, declaredName);
        enforceDateOnlyStrategies(policyJson);
        return new CompileResult(policyName, description, policyJson);
    }

    /**
     * Date-only strategies (SHIFT, TRUNCATE_TO_YEAR, RELATIVE) may target only the
     * DATE entity. The catalog marks them dateFilterStrategy; reject them on any
     * other target (another entity, a custom identifier, a dictionary, a section,
     * or PhEye), which the Phileas runtime would not apply meaningfully.
     */
    private void enforceDateOnlyStrategies(ObjectNode policyJson) {
        java.util.Set<String> dateOnly = catalog.dateOnlyStrategyEnums();
        if (dateOnly.isEmpty()) return;
        Catalog.EntityType dateEntity = catalog.getEntity("DATE");
        String dateField = dateEntity != null ? dateEntity.phileasField() : "date";

        JsonNode identifiers = policyJson.get("identifiers");
        if (identifiers == null) return;
        java.util.Iterator<java.util.Map.Entry<String, JsonNode>> fields = identifiers.fields();
        while (fields.hasNext()) {
            java.util.Map.Entry<String, JsonNode> entry = fields.next();
            String key = entry.getKey();
            if (key.equals(dateField)) continue;

            java.util.List<JsonNode> filters = new java.util.ArrayList<>();
            if (entry.getValue().isArray()) entry.getValue().forEach(filters::add);
            else filters.add(entry.getValue());

            for (JsonNode filt : filters) {
                if (!filt.isObject()) continue;
                java.util.Iterator<java.util.Map.Entry<String, JsonNode>> ff = filt.fields();
                while (ff.hasNext()) {
                    java.util.Map.Entry<String, JsonNode> fe = ff.next();
                    if (!(fe.getKey().endsWith("FilterStrategies") && fe.getValue().isArray())) continue;
                    for (JsonNode strat : fe.getValue()) {
                        String enumVal = strat.path("strategy").asText(null);
                        if (enumVal != null && dateOnly.contains(enumVal)) {
                            String target = catalog.entityNameForField(key);
                            if (target == null) target = key;
                            throw new CompileException(
                                    enumVal + " is a date-only strategy and cannot be applied to " + target);
                        }
                    }
                }
            }
        }
    }

    /** Backwards-compatible single-arg form (no expected name). */
    public CompileResult compile(PhiSQLParser.DocumentContext document) {
        return compile(document, null);
    }

    /**
     * Compiles a CONFIGURE statement. The CRYPTO and FPE forms write the
     * policy's top-level {@code crypto}/{@code fpe} blocks, with secrets stored
     * as {@code env:} references Phileas resolves at runtime (never inline). The
     * SPLITTING/PDF/POSTFILTERS/ANALYSIS forms write the corresponding
     * {@code config} sub-block, and GRAPHICAL BOX appends a fixed bounding box
     * to {@code graphical.boundingBoxes}.
     */
    private void compileConfigure(PhiSQLParser.ConfigureStmtContext ctx, ObjectNode policyJson) {
        if (ctx.cryptoKeyEnv != null) {
            policyJson.putObject("crypto")
                    .put("key", "env:" + unquoteString(ctx.cryptoKeyEnv.getText()));
        } else if (ctx.fpeKeyEnv != null) {
            ObjectNode fpe = policyJson.putObject("fpe");
            fpe.put("key", "env:" + unquoteString(ctx.fpeKeyEnv.getText()));
            fpe.put("tweak", "env:" + unquoteString(ctx.fpeTweakEnv.getText()));
        } else if (ctx.configBlock != null) {
            String block = switch (ctx.configBlock.getType()) {
                case PhiSQLParser.SPLITTING -> "splitting";
                case PhiSQLParser.PDF -> "pdf";
                case PhiSQLParser.POSTFILTERS -> "postFilters";
                case PhiSQLParser.ANALYSIS -> "analysis";
                default -> throw new CompileException(
                        "Unknown config block: " + ctx.configBlock.getText());
            };
            ObjectNode config = getOrCreateObject(policyJson, "config");
            applySettings(getOrCreateObject(config, block), ctx.settingList());
        } else {
            // GRAPHICAL BOX ( ... ) — append a fixed bounding box.
            ObjectNode graphical = getOrCreateObject(policyJson, "graphical");
            ArrayNode boxes = graphical.has("boundingBoxes")
                    ? (ArrayNode) graphical.get("boundingBoxes")
                    : graphical.putArray("boundingBoxes");
            applySettings(boxes.addObject(), ctx.settingList());
        }
    }

    /**
     * Applies an optional {@code OPTIONS ( ... )} clause to the filter object a
     * statement produces. No-op when the clause is absent.
     */
    private void applyOptions(ObjectNode target, PhiSQLParser.OptionsClauseContext options) {
        if (options != null) {
            applySettings(target, options.settingList());
        }
    }

    /**
     * Writes each {@code key = value} setting onto {@code target}. Keys are the
     * Phileas schema property names (quoted when they collide with a keyword);
     * values may be scalars, nested objects {@code ( ... )}, or arrays
     * {@code [ ... ]}, so any schema structure is expressible. The schema (which
     * forbids additional properties) rejects an unknown key at validation time.
     */
    private void applySettings(ObjectNode target, PhiSQLParser.SettingListContext settings) {
        for (PhiSQLParser.SettingContext s : settings.setting()) {
            setOrMerge(target, settingKeyText(s.settingKey()), buildValue(s.settingValue()));
        }
    }

    /** Builds the JSON value for a setting: scalar, nested object, or array. */
    private JsonNode buildValue(PhiSQLParser.SettingValueContext value) {
        if (value.objectValue() != null) {
            ObjectNode obj = MAPPER.createObjectNode();
            applySettings(obj, value.objectValue().settingList());
            return obj;
        }
        if (value.arrayValue() != null) {
            ArrayNode arr = MAPPER.createArrayNode();
            for (PhiSQLParser.SettingValueContext element : value.arrayValue().settingValue()) {
                arr.add(buildValue(element));
            }
            return arr;
        }
        PhiSQLParser.LiteralContext literal = value.literal();
        if (literal.BOOLEAN_LITERAL() != null) {
            return MAPPER.getNodeFactory().booleanNode(Boolean.parseBoolean(literal.getText()));
        }
        if (literal.NUMERIC_LITERAL() != null) {
            String text = literal.getText();
            return text.contains(".")
                    ? MAPPER.getNodeFactory().numberNode(Double.parseDouble(text))
                    : MAPPER.getNodeFactory().numberNode(Integer.parseInt(text));
        }
        if (literal.STRING_LITERAL() != null) {
            return MAPPER.getNodeFactory().textNode(unquoteString(literal.getText()));
        }
        // Bare identifier — treated as a string value.
        return MAPPER.getNodeFactory().textNode(literal.getText());
    }

    /** Sets key=value, merging into an existing object (so DETECT's
     * phEyeConfiguration and an OPTIONS phEyeConfiguration combine, for example). */
    private void setOrMerge(ObjectNode target, String key, JsonNode value) {
        JsonNode existing = target.get(key);
        if (value.isObject() && existing != null && existing.isObject()) {
            ((ObjectNode) existing).setAll((ObjectNode) value);
        } else {
            target.set(key, value);
        }
    }

    private String settingKeyText(PhiSQLParser.SettingKeyContext key) {
        return key.ID() != null ? key.ID().getText() : unquoteString(key.STRING_LITERAL().getText());
    }

    private static ObjectNode getOrCreateObject(ObjectNode parent, String field) {
        return parent.has(field) ? (ObjectNode) parent.get(field) : parent.putObject(field);
    }

    /**
     * Resolves the filter object an entity reference maps to, so an OPTIONS
     * clause can set its leaf properties. A simple entity maps to its
     * {@code identifiers.<field>} object; a custom-identifier reference maps to
     * its entry in {@code identifiers.identifiers[]}.
     */
    private ObjectNode resolveFilterNode(ObjectNode identifiers,
                                         PhiSQLParser.EntityTypeContext entityCtx) {
        if (entityCtx instanceof PhiSQLParser.SimpleEntityTypeContext simple) {
            Catalog.EntityType entity = catalog.getEntity(simple.getText());
            if (entity == null) {
                throw new CompileException("Unknown entity type: " + simple.getText());
            }
            return getOrCreateObject(identifiers, entity.phileasField());
        }
        if (entityCtx instanceof PhiSQLParser.CustomIdentifierContext custom) {
            return getOrCreateIdentifierEntry(
                    identifiers, unquoteString(custom.STRING_LITERAL().getText()));
        }
        throw new CompileException("Unsupported entity type form: " + entityCtx.getText());
    }

    private ObjectNode getOrCreateIdentifierEntry(ObjectNode identifiers, String classification) {
        ArrayNode list = identifiers.has("identifiers")
                ? (ArrayNode) identifiers.get("identifiers")
                : identifiers.putArray("identifiers");
        for (int i = 0; i < list.size(); i++) {
            ObjectNode candidate = (ObjectNode) list.get(i);
            if (classification.equals(candidate.path("classification").asText())) {
                return candidate;
            }
        }
        ObjectNode entry = list.addObject();
        entry.put("classification", classification);
        return entry;
    }

    /**
     * Resolves the policy name from the expected name (typically a filename
     * basename) and the declared name (from the POLICY statement). Implements
     * the policy-naming rule defined in spec/v1.0/catalog/policy.yaml.
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
        ObjectNode strategyJson = null;
        if (ctx.strategyExpr() != null) {
            strategyJson = buildStrategyObject(ctx.strategyExpr());
            if (ctx.predicate() != null) {
                strategyJson.put("conditions", compilePredicate(ctx.predicate()));
            }
        }
        for (PhiSQLParser.EntityTypeContext entityCtx : ctx.entityList().entityType()) {
            if (strategyJson != null) {
                appendStrategy(identifiers, entityCtx, strategyJson.deepCopy());
            }
            if (ctx.optionsClause() != null) {
                applyOptions(resolveFilterNode(identifiers, entityCtx), ctx.optionsClause());
            }
        }
    }

    // ------------------------------------------------------------------
    // DEIDENTIFY
    // ------------------------------------------------------------------

    private void compileDeidentify(PhiSQLParser.DeidentifyStmtContext ctx, ObjectNode identifiers) {
        for (PhiSQLParser.EntityAssignmentContext assignment : ctx.entityAssignment()) {
            ObjectNode strategyJson = buildStrategyObject(assignment.strategyExpr());
            appendStrategy(identifiers, assignment.entityType(), strategyJson);
            if (assignment.optionsClause() != null) {
                applyOptions(resolveFilterNode(identifiers, assignment.entityType()),
                        assignment.optionsClause());
            }
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

        if (scoped && ctx.optionsClause() != null) {
            // A scoped IGNORE writes a bare string into the entity's `ignored`
            // array (or a {pattern} object); there is no object to carry options.
            throw new CompileException(
                    "OPTIONS is not supported on a scoped IGNORE ... FOR; set per-filter "
                            + "options on the entity's REDACT/DEIDENTIFY statement instead.");
        }

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
                // OPTIONS set the object's other leaf fields (name, caseSensitive, files).
                ArrayNode topLevel = policyJson.has("ignored")
                        ? (ArrayNode) policyJson.get("ignored")
                        : policyJson.putArray("ignored");
                ObjectNode termsObject = topLevel.addObject();
                ArrayNode termsArray = termsObject.putArray("terms");
                for (String term : terms) {
                    termsArray.add(term);
                }
                applyOptions(termsObject, ctx.optionsClause());
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
            ObjectNode patternObject = topLevel.addObject();
            patternObject.put("pattern", pattern);
            // OPTIONS set the ignoredPattern object's other leaf field (name).
            applyOptions(patternObject, ctx.optionsClause());
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
        applyOptions(entry, ctx.optionsClause());
    }

    // ------------------------------------------------------------------
    // DEFINE DICTIONARY (custom dictionary filters)
    // ------------------------------------------------------------------

    private void compileDefineDictionary(PhiSQLParser.DefineDictionaryStmtContext ctx,
                                         ObjectNode identifiers) {
        ArrayNode dictionaries = identifiers.has("dictionaries")
                ? (ArrayNode) identifiers.get("dictionaries")
                : identifiers.putArray("dictionaries");
        ObjectNode entry = dictionaries.addObject();
        entry.put("classification", unquoteString(ctx.classification.getText()));

        ArrayNode terms = entry.putArray("terms");
        for (TerminalNode t : ctx.stringList().STRING_LITERAL()) {
            terms.add(unquoteString(t.getText()));
        }

        if (ctx.FUZZY() != null) {
            entry.put("fuzzy", true);
            if (ctx.sensitivity != null) {
                String level = ctx.sensitivity.getText().toLowerCase(Locale.ROOT);
                if (!SENSITIVITY_LEVELS.contains(level)) {
                    throw new CompileException(
                            "SENSITIVITY must be one of " + SENSITIVITY_LEVELS + "; got '" + level + "'");
                }
                entry.put("sensitivity", level);
            }
        }
        if (ctx.capitalized != null) {
            entry.put("capitalized", true);
        }

        entry.putArray("customFilterStrategies").add(buildStrategyObject(ctx.strategyExpr()));
        applyOptions(entry, ctx.optionsClause());
    }

    // ------------------------------------------------------------------
    // DEFINE SECTION (start/end pattern redaction)
    // ------------------------------------------------------------------

    private void compileDefineSection(PhiSQLParser.DefineSectionStmtContext ctx,
                                      ObjectNode identifiers) {
        ArrayNode sections = identifiers.has("sections")
                ? (ArrayNode) identifiers.get("sections")
                : identifiers.putArray("sections");
        ObjectNode entry = sections.addObject();
        entry.put("startPattern", unquoteString(ctx.startPattern.getText()));
        entry.put("endPattern", unquoteString(ctx.endPattern.getText()));
        entry.putArray("sectionFilterStrategies").add(buildStrategyObject(ctx.strategyExpr()));
        applyOptions(entry, ctx.optionsClause());
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
        boolean hasModel = ctx.model != null;
        if (hasLabels || hasEndpoint || hasModel) {
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
            if (hasModel) {
                config.put("modelPath", unquoteString(ctx.model.getText()));
            }
        }
        applyOptions(pheye, ctx.optionsClause());
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
            if (arg != null && argCtx.settingValue().literal() != null) {
                // Catalogued argument with a scalar value: validate and map it
                // (handles aliases like days -> shiftDays and enum checks).
                placeArgValue(out, arg, argCtx.settingValue().literal());
            } else {
                // Any other strategy property (salt, condition, truncateDirection,
                // anonymizationCandidates, ...) passes through by its schema name.
                setOrMerge(out, argName, buildValue(argCtx.settingValue()));
            }
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
                "IGNORE clauses scoped to custom identifiers are not supported in v1.0.");
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
