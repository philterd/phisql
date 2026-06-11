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

using Philterd.PhiSql.Ast;

namespace Philterd.PhiSql;

/// <summary>
/// Recursive-descent parser for PhiSQL v1.0. Each method corresponds to a parser
/// rule in <c>spec/v1.0/grammar/PhiSQL.g4</c>. Syntax errors throw
/// <see cref="ParseException"/> with a <c>line L:C</c> prefix.
/// </summary>
public sealed class Parser
{
    private static readonly HashSet<string> StrategyNames = new(StringComparer.Ordinal)
    {
        "MASK", "REDACT", "ENCRYPT", "FPE_ENCRYPT", "HASH_SHA256", "RANDOM_REPLACE",
        "STATIC_REPLACE", "LAST_4", "TRUNCATE", "TRUNCATE_TO_YEAR", "SHIFT",
        "RELATIVE", "ABBREVIATE",
    };

    private static readonly HashSet<string> CompareOps = new(StringComparer.Ordinal)
        { ">", ">=", "<", "<=", "=" };

    private static readonly HashSet<string> AggFns = new(StringComparer.Ordinal)
        { "COUNT", "AVG", "SUM", "MIN", "MAX" };

    private readonly List<Token> _tokens;
    private int _pos;

    private Parser(List<Token> tokens) => _tokens = tokens;

    /// <summary>Lexes and parses <paramref name="source"/> into a document AST.</summary>
    public static Document Parse(string source) => new Parser(Lexer.Tokenize(source)).ParseDocument();

    // --- Token cursor helpers ------------------------------------------------

    private Token Peek() => _tokens[_pos];

    private Token Advance()
    {
        Token tok = _tokens[_pos];
        if (tok.Type != "EOF") _pos++;
        return tok;
    }

    private bool Check(params string[] types) => Array.IndexOf(types, Peek().Type) >= 0;

    private ParseException Error(string message)
    {
        Token tok = Peek();
        return new ParseException($"line {tok.Line}:{tok.Column} {message}");
    }

    private Token Expect(string type, string? label = null)
    {
        Token tok = Peek();
        if (tok.Type != type)
        {
            string want = label ?? $"'{type}'";
            string got = tok.Type == "EOF" ? "<EOF>" : $"'{tok.Text}'";
            throw Error($"expected {want} but found {got}");
        }
        return Advance();
    }

    // --- document ------------------------------------------------------------

    private Document ParseDocument()
    {
        var doc = new Document();
        while (!Check("EOF"))
        {
            doc.Statements.Add(Statement());
            Expect(";", "';'");
        }
        return doc;
    }

    private IStatement Statement() => Peek().Type switch
    {
        "POLICY" => PolicyDecl(),
        "CONFIGURE" => ConfigureStmt(),
        "REDACT" => RedactStmt(),
        "DEIDENTIFY" => DeidentifyStmt(),
        "IGNORE" => IgnoreStmt(),
        "DEFINE" => DefineStmt(),
        "DETECT" => DetectStmt(),
        "FIND" or "DISCOVER" or "SCAN" or "SELECT" => DiscoveryStmt(),
        _ => throw Error("expected a statement keyword"),
    };

    // --- policyDecl ----------------------------------------------------------

    private PolicyDecl PolicyDecl()
    {
        Expect("POLICY");
        string name = Expect("ID", "a policy name").Text;
        string? description = null;
        if (Check("DESCRIPTION"))
        {
            Advance();
            description = Expect("STRING_LITERAL", "a quoted description").Text;
        }
        return new PolicyDecl { PolicyName = name, DescriptionRaw = description };
    }

    // --- configureStmt -------------------------------------------------------

    private ConfigureStmt ConfigureStmt()
    {
        Expect("CONFIGURE");
        var stmt = new ConfigureStmt();
        if (Check("CRYPTO"))
        {
            Advance();
            Expect("KEY"); Expect("FROM"); Expect("ENV");
            stmt.CryptoKeyEnvRaw = Expect("STRING_LITERAL").Text;
        }
        else if (Check("FPE"))
        {
            Advance();
            Expect("KEY"); Expect("FROM"); Expect("ENV");
            stmt.FpeKeyEnvRaw = Expect("STRING_LITERAL").Text;
            Expect("TWEAK"); Expect("FROM"); Expect("ENV");
            stmt.FpeTweakEnvRaw = Expect("STRING_LITERAL").Text;
        }
        else if (Check("SPLITTING", "PDF", "POSTFILTERS", "ANALYSIS"))
        {
            stmt.ConfigBlock = Advance().Type;
            Expect("(", "'('");
            stmt.Settings = SettingList();
            Expect(")", "')'");
        }
        else if (Check("GRAPHICAL"))
        {
            Advance();
            Expect("BOX");
            stmt.GraphicalBox = true;
            Expect("(", "'('");
            stmt.Settings = SettingList();
            Expect(")", "')'");
        }
        else
        {
            throw Error("expected CRYPTO, FPE, a config block, or GRAPHICAL BOX");
        }
        return stmt;
    }

    // --- settingList / setting / settingValue --------------------------------

    private List<Setting> SettingList()
    {
        var settings = new List<Setting> { Setting() };
        while (Check(",")) { Advance(); settings.Add(Setting()); }
        return settings;
    }

    private Setting Setting()
    {
        SettingKey key = SettingKey();
        Expect("=", "'='");
        return new Setting { Key = key, Value = SettingValue() };
    }

    private SettingKey SettingKey()
    {
        Token tok = Peek();
        if (tok.Type == "ID")
            return new SettingKey { Kind = SettingKeyKind.Id, Text = Advance().Text };
        if (tok.Type == "STRING_LITERAL")
            return new SettingKey { Kind = SettingKeyKind.String, Text = Advance().Text };
        throw Error("expected a setting key (identifier or quoted string)");
    }

    private SettingValue SettingValue()
    {
        Token tok = Peek();
        if (tok.Type == "(")
        {
            Advance();
            List<Setting> settings = SettingList();
            Expect(")", "')'");
            return new SettingValue { ObjectSettings = settings };
        }
        if (tok.Type == "[")
        {
            Advance();
            var elements = new List<SettingValue>();
            if (!Check("]"))
            {
                elements.Add(SettingValue());
                while (Check(",")) { Advance(); elements.Add(SettingValue()); }
            }
            Expect("]", "']'");
            return new SettingValue { ArrayElements = elements };
        }
        return new SettingValue { Literal = Literal() };
    }

    private Literal Literal()
    {
        Token tok = Peek();
        switch (tok.Type)
        {
            case "STRING_LITERAL": return new Literal { Kind = LiteralKind.String, Text = Advance().Text };
            case "NUMERIC_LITERAL": return new Literal { Kind = LiteralKind.Numeric, Text = Advance().Text };
            case "BOOLEAN_LITERAL": return new Literal { Kind = LiteralKind.Boolean, Text = Advance().Text };
            case "ID": return new Literal { Kind = LiteralKind.Id, Text = Advance().Text };
            default: throw Error("expected a literal value");
        }
    }

    private List<Setting>? OptionsClause()
    {
        if (!Check("OPTIONS")) return null;
        Advance();
        Expect("(", "'('");
        List<Setting> settings = SettingList();
        Expect(")", "')'");
        return settings;
    }

    // --- redactStmt ----------------------------------------------------------

    private RedactStmt RedactStmt()
    {
        Expect("REDACT");
        List<IEntityType> entities = EntityList();
        StrategyExpr? strategy = null;
        if (Check("WITH")) { Advance(); strategy = StrategyExpr(); }
        IPredicate? predicate = null;
        if (Check("WHERE")) { Advance(); predicate = Predicate(); }
        List<Setting>? options = OptionsClause();
        return new RedactStmt { Entities = entities, Strategy = strategy, Predicate = predicate, Options = options };
    }

    // --- deidentifyStmt ------------------------------------------------------

    private DeidentifyStmt DeidentifyStmt()
    {
        Expect("DEIDENTIFY");
        var assignments = new List<EntityAssignment> { EntityAssignment() };
        while (Check(",")) { Advance(); assignments.Add(EntityAssignment()); }
        return new DeidentifyStmt { Assignments = assignments };
    }

    private EntityAssignment EntityAssignment()
    {
        IEntityType entity = EntityType();
        Expect("AS", "'AS'");
        StrategyExpr strategy = StrategyExpr();
        List<Setting>? options = OptionsClause();
        return new EntityAssignment { Entity = entity, Strategy = strategy, Options = options };
    }

    // --- ignoreStmt ----------------------------------------------------------

    private IgnoreStmt IgnoreStmt()
    {
        Expect("IGNORE");
        IgnoreStmt stmt;
        if (Check("TERMS"))
        {
            Advance();
            stmt = new IgnoreStmt { Kind = "TERMS", Terms = StringList() };
        }
        else if (Check("PATTERN"))
        {
            Advance();
            stmt = new IgnoreStmt { Kind = "PATTERN", PatternRaw = Expect("STRING_LITERAL").Text };
        }
        else
        {
            throw Error("expected TERMS or PATTERN");
        }
        if (Check("FOR")) { Advance(); stmt.Entities = EntityList(); }
        stmt.Options = OptionsClause();
        return stmt;
    }

    // --- defineStmt (identifier / dictionary / section) ----------------------

    private IStatement DefineStmt()
    {
        Expect("DEFINE");
        if (Check("IDENTIFIER")) return DefineIdentifierStmt();
        if (Check("DICTIONARY")) return DefineDictionaryStmt();
        if (Check("SECTION")) return DefineSectionStmt();
        throw Error("expected IDENTIFIER, DICTIONARY, or SECTION after DEFINE");
    }

    private DefineIdentifierStmt DefineIdentifierStmt()
    {
        Expect("IDENTIFIER");
        string classification = Expect("STRING_LITERAL").Text;
        Expect("MATCHING");
        string pattern = Expect("STRING_LITERAL").Text;
        string? groupNumber = null;
        if (Check("GROUP")) { Advance(); groupNumber = Expect("NUMERIC_LITERAL").Text; }
        string? sensitivity = null;
        if (Check("CASE"))
        {
            Advance();
            if (Check("SENSITIVE", "INSENSITIVE")) sensitivity = Advance().Type;
            else throw Error("expected SENSITIVE or INSENSITIVE");
        }
        Expect("WITH");
        StrategyExpr strategy = StrategyExpr();
        IPredicate? predicate = null;
        if (Check("WHERE")) { Advance(); predicate = Predicate(); }
        List<Setting>? options = OptionsClause();
        return new DefineIdentifierStmt
        {
            ClassificationRaw = classification, PatternRaw = pattern,
            GroupNumber = groupNumber, Sensitivity = sensitivity,
            Strategy = strategy, Predicate = predicate, Options = options,
        };
    }

    private DefineDictionaryStmt DefineDictionaryStmt()
    {
        Expect("DICTIONARY");
        string classification = Expect("STRING_LITERAL").Text;
        Expect("TERMS");
        List<string> terms = StringList();
        bool fuzzy = false;
        string? sensitivity = null;
        if (Check("FUZZY"))
        {
            Advance();
            fuzzy = true;
            if (Check("SENSITIVITY")) { Advance(); sensitivity = Expect("ID", "a sensitivity level").Text; }
        }
        bool capitalized = false;
        if (Check("CAPITALIZED")) { Advance(); capitalized = true; }
        Expect("WITH");
        StrategyExpr strategy = StrategyExpr();
        List<Setting>? options = OptionsClause();
        return new DefineDictionaryStmt
        {
            ClassificationRaw = classification, Terms = terms, Fuzzy = fuzzy,
            Sensitivity = sensitivity, Capitalized = capitalized,
            Strategy = strategy, Options = options,
        };
    }

    private DefineSectionStmt DefineSectionStmt()
    {
        Expect("SECTION");
        Expect("START");
        string start = Expect("STRING_LITERAL").Text;
        Expect("END");
        string end = Expect("STRING_LITERAL").Text;
        Expect("WITH");
        StrategyExpr strategy = StrategyExpr();
        List<Setting>? options = OptionsClause();
        return new DefineSectionStmt { StartRaw = start, EndRaw = end, Strategy = strategy, Options = options };
    }

    // --- detectStmt ----------------------------------------------------------

    private DetectStmt DetectStmt()
    {
        Expect("DETECT");
        Expect("PHEYE");
        List<string>? labels = null;
        if (Check("LABELS")) { Advance(); labels = StringList(); }
        string? endpoint = null;
        if (Check("ENDPOINT")) { Advance(); endpoint = Expect("STRING_LITERAL").Text; }
        Expect("WITH");
        StrategyExpr strategy = StrategyExpr();
        IPredicate? predicate = null;
        if (Check("WHERE")) { Advance(); predicate = Predicate(); }
        List<Setting>? options = OptionsClause();
        return new DetectStmt
        {
            Labels = labels, EndpointRaw = endpoint,
            Strategy = strategy, Predicate = predicate, Options = options,
        };
    }

    // --- entityList / entityType ---------------------------------------------

    private List<IEntityType> EntityList()
    {
        var entities = new List<IEntityType> { EntityType() };
        while (Check(",")) { Advance(); entities.Add(EntityType()); }
        return entities;
    }

    private IEntityType EntityType()
    {
        Token tok = Peek();
        if (tok.Type == "ID")
            return new SimpleEntityType { Name = Advance().Text };
        if (tok.Type == "IDENTIFIER")
        {
            Advance();
            Expect("(", "'('");
            string classification = Expect("STRING_LITERAL").Text;
            Expect(")", "')'");
            return new CustomIdentifier { ClassificationRaw = classification };
        }
        throw Error("expected an entity type or IDENTIFIER('<classification>')");
    }

    // --- strategyExpr --------------------------------------------------------

    private StrategyExpr StrategyExpr()
    {
        Token tok = Peek();
        if (!StrategyNames.Contains(tok.Type)) throw Error("expected a strategy name");
        string name = Advance().Text;
        var args = new List<NamedArg>();
        if (Check("("))
        {
            Advance();
            args = StrategyArgs();
            Expect(")", "')'");
        }
        return new StrategyExpr { Name = name, Args = args };
    }

    private List<NamedArg> StrategyArgs()
    {
        var args = new List<NamedArg> { NamedArg() };
        while (Check(",")) { Advance(); args.Add(NamedArg()); }
        return args;
    }

    private NamedArg NamedArg()
    {
        string name = Expect("ID", "an argument name").Text;
        Expect("=", "'='");
        return new NamedArg { ArgName = name, Value = SettingValue() };
    }

    // --- predicate (redaction WHERE) -----------------------------------------

    private IPredicate Predicate()
    {
        IPredicate left = PredicatePrimary();
        while (Check("AND", "OR"))
        {
            string op = Advance().Type;
            IPredicate right = PredicatePrimary();
            left = new LogicalPredicate { Op = op, Left = left, Right = right };
        }
        return left;
    }

    private IPredicate PredicatePrimary()
    {
        if (Check("("))
        {
            Advance();
            IPredicate inner = Predicate();
            Expect(")", "')'");
            return new ParenPredicate { Inner = inner };
        }
        if (Check("CONFIDENCE"))
        {
            Advance();
            string op = CompareOp();
            string number = Expect("NUMERIC_LITERAL", "a number").Text;
            return new ConfidencePredicate { Op = op, Number = number };
        }
        throw Error("expected CONFIDENCE or '(' in WHERE predicate");
    }

    private string CompareOp()
    {
        Token tok = Peek();
        if (!CompareOps.Contains(tok.Type)) throw Error("expected a comparison operator");
        return Advance().Type;
    }

    // --- stringList ----------------------------------------------------------

    private List<string> StringList()
    {
        Expect("(", "'('");
        var terms = new List<string> { Expect("STRING_LITERAL").Text };
        while (Check(",")) { Advance(); terms.Add(Expect("STRING_LITERAL").Text); }
        Expect(")", "')'");
        return terms;
    }

    // --- discoveryStmt -------------------------------------------------------
    // Parsed for syntactic validation only; the compiler does not translate
    // discovery statements (they target a separate discovery-query schema).

    private DiscoveryStmt DiscoveryStmt()
    {
        if (Check("FIND"))
        {
            Advance(); Expect("PII"); InClause(); WhereDiscoveryOpt();
            return new DiscoveryStmt { Verb = "FIND_PII" };
        }
        if (Check("DISCOVER"))
        {
            Advance(); Expect("ENTITIES"); InClause(); WhereDiscoveryOpt();
            return new DiscoveryStmt { Verb = "DISCOVER_ENTITIES" };
        }
        if (Check("SCAN"))
        {
            Advance(); InClause(); WhereDiscoveryOpt();
            return new DiscoveryStmt { Verb = "SCAN" };
        }
        // SELECT projectionList FROM findingsRef whereDiscovery? groupBy? limit?
        Expect("SELECT");
        ProjectionList();
        Expect("FROM");
        FindingsRef();
        WhereDiscoveryOpt();
        if (Check("GROUP"))
        {
            Advance(); Expect("BY"); ColumnRef();
            while (Check(",")) { Advance(); ColumnRef(); }
        }
        if (Check("LIMIT")) { Advance(); Expect("NUMERIC_LITERAL"); }
        return new DiscoveryStmt { Verb = "SELECT_FINDINGS" };
    }

    private void InClause()
    {
        Expect("IN");
        Expect("STRING_LITERAL", "a quoted URI");
    }

    private void WhereDiscoveryOpt()
    {
        if (Check("WHERE")) { Advance(); DiscoveryPredicate(); }
    }

    private void DiscoveryPredicate()
    {
        DiscoveryPredicatePrimary();
        while (Check("AND", "OR")) { Advance(); DiscoveryPredicatePrimary(); }
    }

    private void DiscoveryPredicatePrimary()
    {
        if (Check("("))
        {
            Advance(); DiscoveryPredicate(); Expect(")", "')'");
            return;
        }
        ColumnRef();
        if (Check("IN")) { Advance(); StringList(); }
        else if (CompareOps.Contains(Peek().Type))
        {
            Advance();
            if (!Check("STRING_LITERAL", "NUMERIC_LITERAL", "BOOLEAN_LITERAL"))
                throw Error("expected a literal on the right of the comparison");
            Advance();
        }
        else
        {
            throw Error("expected IN or a comparison operator");
        }
    }

    private void ProjectionList()
    {
        Projection();
        while (Check(",")) { Advance(); Projection(); }
    }

    private void Projection()
    {
        if (Check("*")) { Advance(); return; }
        if (AggFns.Contains(Peek().Type))
        {
            Advance();
            Expect("(", "'('");
            if (Check("*")) Advance(); else ColumnRef();
            Expect(")", "')'");
            return;
        }
        ColumnRef();
    }

    private void ColumnRef()
    {
        if (Check("ID", "CONFIDENCE")) { Advance(); return; }
        throw Error("expected a column name");
    }

    private void FindingsRef()
    {
        Expect("ID", "a findings table name");
        if (Check(".")) { Advance(); Expect("ID", "a table name"); }
    }
}
