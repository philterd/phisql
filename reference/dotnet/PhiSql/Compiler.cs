// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System.Globalization;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization.Metadata;
using Philterd.PhiSql.Ast;

namespace Philterd.PhiSql;

/// <summary>
/// Result of compiling a PhiSQL document. <see cref="PolicyName"/> is the name
/// from the POLICY declaration (or the filename basename); <see cref="Description"/>
/// is the DESCRIPTION text; <see cref="PolicyJson"/> is the compiled Phileas JSON.
/// </summary>
public sealed class CompileResult
{
    private static readonly JsonSerializerOptions Pretty = new()
    {
        WriteIndented = true,
        Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        // Required when a custom options instance serializes the JsonValue<T>
        // instances we build for array elements (e.g. string lists).
        TypeInfoResolver = new DefaultJsonTypeInfoResolver(),
    };

    public CompileResult(string? policyName, string? description, JsonObject policyJson)
    {
        PolicyName = policyName;
        Description = description;
        PolicyJson = policyJson;
    }

    public string? PolicyName { get; }
    public string? Description { get; }
    public JsonObject PolicyJson { get; }

    /// <summary>Returns the policy JSON as a pretty-printed string.</summary>
    public string ToJsonString() => PolicyJson.ToJsonString(Pretty);
}

/// <summary>
/// Compiles a parsed PhiSQL document into a Phileas JSON policy, driven by the
/// <see cref="Catalog"/>. A direct port of the Java and Python reference
/// compilers. Discovery statements parse but are not translated.
/// </summary>
public sealed class Compiler
{
    private static readonly HashSet<string> SensitivityLevels = new(StringComparer.Ordinal)
        { "auto", "off", "low", "medium", "high" };

    private static readonly Dictionary<string, string> ConfigBlocks = new(StringComparer.Ordinal)
    {
        ["SPLITTING"] = "splitting",
        ["PDF"] = "pdf",
        ["POSTFILTERS"] = "postFilters",
        ["ANALYSIS"] = "analysis",
    };

    private readonly Catalog _catalog;

    public Compiler() : this(Catalog.LoadDefault()) { }

    public Compiler(Catalog catalog) => _catalog = catalog;

    // --- Public entry points -------------------------------------------------

    /// <summary>Compiles PhiSQL from a string.</summary>
    public CompileResult Compile(string source, string? expectedName = null) =>
        CompileDocument(Parser.Parse(source), expectedName);

    /// <summary>
    /// Compiles PhiSQL from a file. The policy name is the file's basename; a
    /// POLICY declaration, if present, must match it after hyphen/underscore
    /// normalization.
    /// </summary>
    public CompileResult CompileFile(string path)
    {
        string source = File.ReadAllText(path);
        return CompileDocument(Parser.Parse(source), BasenameWithoutExtension(path));
    }

    public CompileResult CompileDocument(Document document, string? expectedName = null)
    {
        var policyJson = new JsonObject();
        var identifiers = new JsonObject();
        policyJson["identifiers"] = identifiers;

        string? declaredName = null;
        string? description = null;

        foreach (IStatement stmt in document.Statements)
        {
            switch (stmt)
            {
                case PolicyDecl p:
                    declaredName = p.PolicyName;
                    if (p.DescriptionRaw is not null) description = Unquote(p.DescriptionRaw);
                    break;
                case RedactStmt r: CompileRedact(r, identifiers); break;
                case DeidentifyStmt d: CompileDeidentify(d, identifiers); break;
                case IgnoreStmt ig: CompileIgnore(ig, identifiers, policyJson); break;
                case DefineIdentifierStmt di: CompileDefineIdentifier(di, identifiers); break;
                case DefineDictionaryStmt dd: CompileDefineDictionary(dd, identifiers); break;
                case DefineSectionStmt ds: CompileDefineSection(ds, identifiers); break;
                case DetectStmt det: CompileDetect(det, identifiers); break;
                case ConfigureStmt c: CompileConfigure(c, policyJson); break;
                case DiscoveryStmt: break; // not compiled to Phileas JSON
            }
        }

        string? policyName = ResolvePolicyName(expectedName, declaredName);
        EnforceDateOnlyStrategies(policyJson);
        return new CompileResult(policyName, description, policyJson);
    }

    /// <summary>
    /// Date-only strategies (SHIFT, TRUNCATE_TO_YEAR, RELATIVE) may target only the
    /// DATE entity. The catalog marks them dateFilterStrategy; reject them on any
    /// other target (another entity, a custom identifier, a dictionary, a section,
    /// or PhEye), which the Phileas runtime would not apply meaningfully.
    /// </summary>
    private void EnforceDateOnlyStrategies(JsonObject policyJson)
    {
        IReadOnlySet<string> dateOnly = _catalog.DateOnlyStrategyEnums();
        if (dateOnly.Count == 0) return;
        string dateField = _catalog.GetEntity("DATE")?.PhileasField ?? "date";

        if (policyJson["identifiers"] is not JsonObject identifiers) return;
        foreach (KeyValuePair<string, JsonNode?> kv in identifiers)
        {
            if (kv.Key == dateField || kv.Value is null) continue;
            IEnumerable<JsonNode> filters = kv.Value is JsonArray arr
                ? arr.OfType<JsonNode>()
                : new JsonNode[] { kv.Value! };

            foreach (JsonNode filt in filters)
            {
                if (filt is not JsonObject fobj) continue;
                foreach (KeyValuePair<string, JsonNode?> fkv in fobj)
                {
                    if (!fkv.Key.EndsWith("FilterStrategies", StringComparison.Ordinal)
                        || fkv.Value is not JsonArray strategies) continue;
                    foreach (JsonNode? strat in strategies)
                    {
                        string? enumVal = (strat as JsonObject)?["strategy"]?.GetValue<string>();
                        if (enumVal is not null && dateOnly.Contains(enumVal))
                        {
                            string target = _catalog.EntityNameForField(kv.Key) ?? kv.Key;
                            throw new CompileException(
                                $"{enumVal} is a date-only strategy and cannot be applied to {target}");
                        }
                    }
                }
            }
        }
    }

    // --- CONFIGURE -----------------------------------------------------------

    private void CompileConfigure(ConfigureStmt ctx, JsonObject policyJson)
    {
        if (ctx.CryptoKeyEnvRaw is not null)
        {
            policyJson["crypto"] = new JsonObject { ["key"] = "env:" + Unquote(ctx.CryptoKeyEnvRaw) };
        }
        else if (ctx.FpeKeyEnvRaw is not null)
        {
            policyJson["fpe"] = new JsonObject
            {
                ["key"] = "env:" + Unquote(ctx.FpeKeyEnvRaw),
                ["tweak"] = "env:" + Unquote(ctx.FpeTweakEnvRaw!),
            };
        }
        else if (ctx.ConfigBlock is not null)
        {
            string block = ConfigBlocks[ctx.ConfigBlock];
            JsonObject config = GetOrCreateObject(policyJson, "config");
            ApplySettings(GetOrCreateObject(config, block), ctx.Settings!);
        }
        else
        {
            // GRAPHICAL BOX ( ... ) — append a fixed bounding box.
            JsonObject graphical = GetOrCreateObject(policyJson, "graphical");
            JsonArray boxes = GetOrCreateArray(graphical, "boundingBoxes");
            var box = new JsonObject();
            boxes.Add(box);
            ApplySettings(box, ctx.Settings!);
        }
    }

    // --- OPTIONS / settings --------------------------------------------------

    private void ApplyOptions(JsonObject target, List<Setting>? options)
    {
        if (options is not null) ApplySettings(target, options);
    }

    private void ApplySettings(JsonObject target, List<Setting> settings)
    {
        foreach (Setting s in settings)
            SetOrMerge(target, SettingKeyText(s.Key), BuildValue(s.Value));
    }

    private JsonNode BuildValue(SettingValue value)
    {
        if (value.ObjectSettings is not null)
        {
            var obj = new JsonObject();
            ApplySettings(obj, value.ObjectSettings);
            return obj;
        }
        if (value.ArrayElements is not null)
        {
            var arr = new JsonArray();
            foreach (SettingValue el in value.ArrayElements) arr.Add(BuildValue(el));
            return arr;
        }
        Literal literal = value.Literal!;
        return literal.Kind switch
        {
            LiteralKind.Boolean => JsonValue.Create(string.Equals(literal.Text, "true", StringComparison.OrdinalIgnoreCase)),
            LiteralKind.Numeric => NumberNode(literal.Text),
            LiteralKind.String => JsonValue.Create(Unquote(literal.Text)),
            _ => JsonValue.Create(literal.Text), // bare identifier — string value
        };
    }

    // --- REDACT --------------------------------------------------------------

    private void CompileRedact(RedactStmt ctx, JsonObject identifiers)
    {
        JsonObject? strategyJson = null;
        if (ctx.Strategy is not null)
        {
            strategyJson = BuildStrategyObject(ctx.Strategy);
            if (ctx.Predicate is not null) strategyJson["conditions"] = CompilePredicate(ctx.Predicate);
        }
        foreach (IEntityType entity in ctx.Entities)
        {
            if (strategyJson is not null)
                AppendStrategy(identifiers, entity, (JsonObject)strategyJson.DeepClone());
            if (ctx.Options is not null)
                ApplyOptions(ResolveFilterNode(identifiers, entity), ctx.Options);
        }
    }

    // --- DEIDENTIFY ----------------------------------------------------------

    private void CompileDeidentify(DeidentifyStmt ctx, JsonObject identifiers)
    {
        foreach (EntityAssignment assignment in ctx.Assignments)
        {
            JsonObject strategyJson = BuildStrategyObject(assignment.Strategy);
            AppendStrategy(identifiers, assignment.Entity, strategyJson);
            if (assignment.Options is not null)
                ApplyOptions(ResolveFilterNode(identifiers, assignment.Entity), assignment.Options);
        }
    }

    // --- IGNORE --------------------------------------------------------------

    private void CompileIgnore(IgnoreStmt ctx, JsonObject identifiers, JsonObject policyJson)
    {
        bool isTerms = ctx.Kind == "TERMS";
        bool scoped = ctx.Entities is not null;

        if (scoped && ctx.Options is not null)
        {
            throw new CompileException(
                "OPTIONS is not supported on a scoped IGNORE ... FOR; set per-filter " +
                "options on the entity's REDACT/DEIDENTIFY statement instead.");
        }

        if (isTerms)
        {
            List<string> terms = ctx.Terms!.Select(Unquote).ToList();
            if (scoped)
            {
                foreach (IEntityType entity in ctx.Entities!)
                {
                    JsonObject entityNode = GetOrCreateEntityNode(identifiers, entity);
                    JsonArray ignored = GetOrCreateArray(entityNode, "ignored");
                    foreach (string term in terms) ignored.Add(term);
                }
            }
            else
            {
                JsonArray topLevel = GetOrCreateArray(policyJson, "ignored");
                var termsObject = new JsonObject();
                topLevel.Add(termsObject);
                termsObject["terms"] = StringArray(terms);
                ApplyOptions(termsObject, ctx.Options);
            }
            return;
        }

        // PATTERN
        string pattern = Unquote(ctx.PatternRaw!);
        if (scoped)
        {
            foreach (IEntityType entity in ctx.Entities!)
            {
                JsonObject entityNode = GetOrCreateEntityNode(identifiers, entity);
                JsonArray ignoredPatterns = GetOrCreateArray(entityNode, "ignoredPatterns");
                ignoredPatterns.Add(new JsonObject { ["pattern"] = pattern });
            }
        }
        else
        {
            JsonArray topLevel = GetOrCreateArray(policyJson, "ignoredPatterns");
            var patternObject = new JsonObject { ["pattern"] = pattern };
            topLevel.Add(patternObject);
            ApplyOptions(patternObject, ctx.Options);
        }
    }

    // --- DEFINE IDENTIFIER ---------------------------------------------------

    private void CompileDefineIdentifier(DefineIdentifierStmt ctx, JsonObject identifiers)
    {
        string classification = Unquote(ctx.ClassificationRaw);
        string pattern = Unquote(ctx.PatternRaw);

        JsonObject strategyJson = BuildStrategyObject(ctx.Strategy);
        if (ctx.Predicate is not null) strategyJson["conditions"] = CompilePredicate(ctx.Predicate);

        JsonArray identifierList = GetOrCreateArray(identifiers, "identifiers");
        JsonObject? entry = FindByClassification(identifierList, classification);
        if (entry is null)
        {
            entry = new JsonObject { ["classification"] = classification };
            identifierList.Add(entry);
        }
        entry["pattern"] = pattern;
        if (ctx.GroupNumber is not null)
            entry["groupNumber"] = long.Parse(ctx.GroupNumber, CultureInfo.InvariantCulture);
        if (ctx.Sensitivity is not null)
            entry["caseSensitive"] = ctx.Sensitivity == "SENSITIVE";

        JsonArray strategies = GetOrCreateArray(entry, "identifierFilterStrategies");
        strategies.Add(strategyJson);
        ApplyOptions(entry, ctx.Options);
    }

    // --- DEFINE DICTIONARY ---------------------------------------------------

    private void CompileDefineDictionary(DefineDictionaryStmt ctx, JsonObject identifiers)
    {
        JsonArray dictionaries = GetOrCreateArray(identifiers, "dictionaries");
        var entry = new JsonObject { ["classification"] = Unquote(ctx.ClassificationRaw) };
        dictionaries.Add(entry);

        entry["terms"] = StringArray(ctx.Terms.Select(Unquote));

        if (ctx.Fuzzy)
        {
            entry["fuzzy"] = true;
            if (ctx.Sensitivity is not null)
            {
                string level = ctx.Sensitivity.ToLowerInvariant();
                if (!SensitivityLevels.Contains(level))
                {
                    throw new CompileException(
                        "SENSITIVITY must be one of [" +
                        string.Join(", ", SensitivityLevels.OrderBy(x => x)) + $"]; got '{level}'");
                }
                entry["sensitivity"] = level;
            }
        }
        if (ctx.Capitalized) entry["capitalized"] = true;

        entry["customFilterStrategies"] = new JsonArray(BuildStrategyObject(ctx.Strategy));
        ApplyOptions(entry, ctx.Options);
    }

    // --- DEFINE SECTION ------------------------------------------------------

    private void CompileDefineSection(DefineSectionStmt ctx, JsonObject identifiers)
    {
        JsonArray sections = GetOrCreateArray(identifiers, "sections");
        var entry = new JsonObject
        {
            ["startPattern"] = Unquote(ctx.StartRaw),
            ["endPattern"] = Unquote(ctx.EndRaw),
            ["sectionFilterStrategies"] = new JsonArray(BuildStrategyObject(ctx.Strategy)),
        };
        sections.Add(entry);
        ApplyOptions(entry, ctx.Options);
    }

    // --- DETECT PHEYE --------------------------------------------------------

    private void CompileDetect(DetectStmt ctx, JsonObject identifiers)
    {
        JsonObject strategyJson = BuildStrategyObject(ctx.Strategy);
        if (ctx.Predicate is not null) strategyJson["conditions"] = CompilePredicate(ctx.Predicate);

        JsonArray pheyes = GetOrCreateArray(identifiers, "pheyes");
        var pheye = new JsonObject { ["phEyeFilterStrategies"] = new JsonArray(strategyJson) };
        pheyes.Add(pheye);

        bool hasLabels = ctx.Labels is not null;
        bool hasEndpoint = ctx.EndpointRaw is not null;
        bool hasModel = ctx.ModelRaw is not null;
        if (hasLabels || hasEndpoint || hasModel)
        {
            var config = new JsonObject();
            pheye["phEyeConfiguration"] = config;
            if (hasEndpoint) config["endpoint"] = Unquote(ctx.EndpointRaw!);
            if (hasLabels) config["labels"] = StringArray(ctx.Labels!.Select(Unquote));
            if (hasModel) config["modelPath"] = Unquote(ctx.ModelRaw!);
        }
        ApplyOptions(pheye, ctx.Options);
    }

    // --- Strategy translation ------------------------------------------------

    private JsonObject BuildStrategyObject(StrategyExpr ctx)
    {
        Strategy? strategy = _catalog.GetStrategy(ctx.Name);
        if (strategy is null) throw new CompileException("Unknown strategy: " + ctx.Name);

        var output = new JsonObject { ["strategy"] = strategy.PhileasEnum };

        foreach (NamedArg arg in ctx.Args)
        {
            StrategyArg? catArg = strategy.FindArg(arg.ArgName);
            if (catArg is not null && arg.Value.Literal is not null)
                PlaceArgValue(output, catArg, arg.Value.Literal);
            else
                SetOrMerge(output, arg.ArgName, BuildValue(arg.Value));
        }

        // STATIC_REPLACE has nothing to substitute without a value; the catalog
        // marks the argument required (strategies.yaml). Reject the omission
        // rather than emitting a malformed strategy.
        if (strategy.PhileasEnum == "STATIC_REPLACE" && !output.ContainsKey("staticReplacement"))
            throw new CompileException("STATIC_REPLACE requires argument 'value'");
        return output;
    }

    private void PlaceArgValue(JsonObject strategyObj, StrategyArg arg, Literal literal)
    {
        string text = literal.Text;
        string type = arg.Type ?? "string";
        switch (type)
        {
            case "string":
                strategyObj[arg.PhileasField!] = ParseStringLiteral(text);
                break;
            case "integer":
                strategyObj[arg.PhileasField!] = long.Parse(text, CultureInfo.InvariantCulture);
                break;
            case "boolean":
                strategyObj[arg.PhileasField!] = string.Equals(text, "true", StringComparison.OrdinalIgnoreCase);
                break;
            case "enum":
                string val = StripQuotesIfPresent(text).ToUpperInvariant();
                if (!arg.EnumValues.Contains(val))
                {
                    throw new CompileException(
                        $"Argument '{arg.Name}' must be one of [" +
                        string.Join(", ", arg.EnumValues) + $"]; got '{val}'");
                }
                strategyObj[arg.PhileasField!] = val;
                break;
            default:
                throw new CompileException("Unsupported argument type: " + type);
        }
    }

    // --- Entity placement ----------------------------------------------------

    private void AppendStrategy(JsonObject identifiers, IEntityType entity, JsonObject strategyObj)
    {
        if (entity is SimpleEntityType simple)
        {
            EntityType entityType = RequireEntity(simple.Name);
            JsonObject entityNode = GetOrCreateObject(identifiers, entityType.PhileasField);
            JsonArray strategies = GetOrCreateArray(entityNode, entityType.PhileasStrategiesField);
            strategies.Add(strategyObj);
            return;
        }
        if (entity is CustomIdentifier custom)
        {
            string classification = Unquote(custom.ClassificationRaw);
            JsonArray identifierList = GetOrCreateArray(identifiers, "identifiers");
            JsonObject? entry = FindByClassification(identifierList, classification);
            if (entry is null)
            {
                entry = new JsonObject { ["classification"] = classification };
                identifierList.Add(entry);
            }
            JsonArray strategies = GetOrCreateArray(entry, "identifierFilterStrategies");
            strategies.Add(strategyObj);
            return;
        }
        throw new CompileException("Unsupported entity type form");
    }

    private JsonObject ResolveFilterNode(JsonObject identifiers, IEntityType entity)
    {
        if (entity is SimpleEntityType simple)
            return GetOrCreateObject(identifiers, RequireEntity(simple.Name).PhileasField);
        if (entity is CustomIdentifier custom)
        {
            string classification = Unquote(custom.ClassificationRaw);
            JsonArray identifierList = GetOrCreateArray(identifiers, "identifiers");
            JsonObject? entry = FindByClassification(identifierList, classification);
            if (entry is null)
            {
                entry = new JsonObject { ["classification"] = classification };
                identifierList.Add(entry);
            }
            return entry;
        }
        throw new CompileException("Unsupported entity type form");
    }

    private JsonObject GetOrCreateEntityNode(JsonObject identifiers, IEntityType entity)
    {
        if (entity is SimpleEntityType simple)
            return GetOrCreateObject(identifiers, RequireEntity(simple.Name).PhileasField);
        throw new CompileException(
            "IGNORE clauses scoped to custom identifiers are not supported in v1.0.");
    }

    private EntityType RequireEntity(string name)
    {
        EntityType? entity = _catalog.GetEntity(name);
        if (entity is null) throw new CompileException("Unknown entity type: " + name);
        return entity;
    }

    // --- Predicate translation -----------------------------------------------

    private string CompilePredicate(IPredicate ctx) => ctx switch
    {
        ConfidencePredicate c => $"confidence {c.Op} {c.Number}",
        ParenPredicate p => "( " + CompilePredicate(p.Inner) + " )",
        LogicalPredicate l => CompilePredicate(l.Left) + " " + (l.Op == "AND" ? "and" : "or") + " " + CompilePredicate(l.Right),
        _ => throw new CompileException("Unsupported predicate form"),
    };

    // --- JSON helpers --------------------------------------------------------

    private static JsonObject GetOrCreateObject(JsonObject parent, string field)
    {
        if (parent[field] is JsonObject existing) return existing;
        var obj = new JsonObject();
        parent[field] = obj;
        return obj;
    }

    private static JsonArray GetOrCreateArray(JsonObject parent, string field)
    {
        if (parent[field] is JsonArray existing) return existing;
        var arr = new JsonArray();
        parent[field] = arr;
        return arr;
    }

    private static JsonObject? FindByClassification(JsonArray entries, string classification)
    {
        foreach (JsonNode? candidate in entries)
        {
            if (candidate is JsonObject obj
                && obj["classification"] is JsonValue v
                && v.TryGetValue(out string? s) && s == classification)
            {
                return obj;
            }
        }
        return null;
    }

    private static void SetOrMerge(JsonObject target, string key, JsonNode value)
    {
        if (value is JsonObject vObj && target[key] is JsonObject eObj)
        {
            foreach (KeyValuePair<string, JsonNode?> kv in vObj)
                eObj[kv.Key] = kv.Value?.DeepClone();
        }
        else
        {
            target[key] = value;
        }
    }

    private static JsonArray StringArray(IEnumerable<string> values)
    {
        var arr = new JsonArray();
        foreach (string v in values) arr.Add(v);
        return arr;
    }

    private static JsonNode NumberNode(string text) =>
        text.Contains('.')
            ? JsonValue.Create(double.Parse(text, CultureInfo.InvariantCulture))
            : JsonValue.Create(long.Parse(text, CultureInfo.InvariantCulture));

    private static string SettingKeyText(SettingKey key) =>
        key.Kind == SettingKeyKind.Id ? key.Text : Unquote(key.Text);

    // --- Policy naming + string helpers --------------------------------------

    private static string? ResolvePolicyName(string? expected, string? declared)
    {
        if (expected is not null && declared is not null)
        {
            if (NormalizePolicyName(expected) != NormalizePolicyName(declared))
            {
                throw new CompileException(
                    $"POLICY declaration name '{declared}' does not match the expected " +
                    $"name '{expected}'. Either omit the POLICY statement or change it to match.");
            }
            return expected;
        }
        return expected ?? declared;
    }

    private static string NormalizePolicyName(string name) => name.Replace('-', '_');

    private static string BasenameWithoutExtension(string path)
    {
        string name = Path.GetFileName(path);
        int dot = name.LastIndexOf('.');
        return dot > 0 ? name[..dot] : name;
    }

    private static string Unquote(string text)
    {
        if (text.Length >= 2 && text[0] == '\'' && text[^1] == '\'')
        {
            string inner = text[1..^1];
            return inner.Replace("\\'", "'").Replace("\\n", "\n").Replace("\\\\", "\\");
        }
        return text;
    }

    private static string ParseStringLiteral(string text) =>
        text.Length >= 2 && text.StartsWith('\'') && text.EndsWith('\'') ? Unquote(text) : text;

    private static string StripQuotesIfPresent(string text) =>
        text.Length >= 2 && text[0] == '\'' && text[^1] == '\'' ? text[1..^1] : text;
}
