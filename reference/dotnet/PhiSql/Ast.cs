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

namespace Philterd.PhiSql.Ast;

// AST node types for PhiSQL v1.0, mirroring the parser rules in
// spec/v1.0/grammar/PhiSQL.g4 one-for-one. String and numeric literals are
// stored as their raw source text (quotes included for strings); the compiler
// unquotes and coerces them, matching the Java reference's getText() usage.

public interface IStatement { }
public interface IEntityType { }
public interface IPredicate { }

public sealed class Document
{
    public List<IStatement> Statements { get; } = new();
}

// --- Entity references -------------------------------------------------------

/// <summary>A plain entity type, e.g. <c>SSN</c> (the ID text).</summary>
public sealed class SimpleEntityType : IEntityType
{
    public required string Name { get; init; }
}

/// <summary>A custom-identifier reference, <c>IDENTIFIER('classification')</c>.</summary>
public sealed class CustomIdentifier : IEntityType
{
    public required string ClassificationRaw { get; init; } // quoted STRING_LITERAL
}

// --- Literals and setting values ---------------------------------------------

public enum LiteralKind { String, Numeric, Boolean, Id }

public sealed class Literal
{
    public required LiteralKind Kind { get; init; }
    public required string Text { get; init; } // raw source text (quotes included for String)
}

/// <summary>A setting/argument value: a scalar literal, a nested object, or an array.</summary>
public sealed class SettingValue
{
    public Literal? Literal { get; init; }
    public List<Setting>? ObjectSettings { get; init; }
    public List<SettingValue>? ArrayElements { get; init; }
}

public enum SettingKeyKind { Id, String }

public sealed class SettingKey
{
    public required SettingKeyKind Kind { get; init; }
    public required string Text { get; init; } // ID text, or raw quoted text for String
}

public sealed class Setting
{
    public required SettingKey Key { get; init; }
    public required SettingValue Value { get; init; }
}

public sealed class NamedArg
{
    public required string ArgName { get; init; }
    public required SettingValue Value { get; init; }
}

public sealed class StrategyExpr
{
    public required string Name { get; init; } // strategy keyword text, e.g. "MASK"
    public List<NamedArg> Args { get; init; } = new();
}

// --- Redaction predicates ----------------------------------------------------

public sealed class ConfidencePredicate : IPredicate
{
    public required string Op { get; init; }     // one of > >= < <= =
    public required string Number { get; init; } // raw NUMERIC_LITERAL text
}

public sealed class ParenPredicate : IPredicate
{
    public required IPredicate Inner { get; init; }
}

public sealed class LogicalPredicate : IPredicate
{
    public required string Op { get; init; } // "AND" or "OR"
    public required IPredicate Left { get; init; }
    public required IPredicate Right { get; init; }
}

// --- Statements --------------------------------------------------------------

public sealed class PolicyDecl : IStatement
{
    public required string PolicyName { get; init; }
    public string? DescriptionRaw { get; init; } // quoted STRING_LITERAL or null
}

public sealed class RedactStmt : IStatement
{
    public required List<IEntityType> Entities { get; init; }
    public StrategyExpr? Strategy { get; init; }
    public IPredicate? Predicate { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class EntityAssignment
{
    public required IEntityType Entity { get; init; }
    public required StrategyExpr Strategy { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class DeidentifyStmt : IStatement
{
    public required List<EntityAssignment> Assignments { get; init; }
}

public sealed class IgnoreStmt : IStatement
{
    public required string Kind { get; init; }     // "TERMS" or "PATTERN"
    public List<string>? Terms { get; init; }      // raw STRING_LITERALs for TERMS
    public string? PatternRaw { get; init; }       // raw STRING_LITERAL for PATTERN
    public List<IEntityType>? Entities { get; set; } // FOR entityList, or null
    public List<Setting>? Options { get; set; }
}

public sealed class DefineIdentifierStmt : IStatement
{
    public required string ClassificationRaw { get; init; }
    public required string PatternRaw { get; init; }
    public string? GroupNumber { get; init; }   // raw NUMERIC_LITERAL or null
    public string? Sensitivity { get; init; }   // "SENSITIVE" / "INSENSITIVE" / null
    public required StrategyExpr Strategy { get; init; }
    public IPredicate? Predicate { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class DefineDictionaryStmt : IStatement
{
    public required string ClassificationRaw { get; init; }
    public required List<string> Terms { get; init; }
    public bool Fuzzy { get; init; }
    public string? Sensitivity { get; init; }   // ID text after SENSITIVITY, or null
    public bool Capitalized { get; init; }
    public required StrategyExpr Strategy { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class DefineSectionStmt : IStatement
{
    public required string StartRaw { get; init; }
    public required string EndRaw { get; init; }
    public required StrategyExpr Strategy { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class DetectStmt : IStatement
{
    public List<string>? Labels { get; init; }   // raw STRING_LITERALs or null
    public string? EndpointRaw { get; init; }    // raw STRING_LITERAL or null
    public string? ModelRaw { get; init; }       // raw STRING_LITERAL (local model path) or null
    public required StrategyExpr Strategy { get; init; }
    public IPredicate? Predicate { get; init; }
    public List<Setting>? Options { get; init; }
}

public sealed class ConfigureStmt : IStatement
{
    public string? CryptoKeyEnvRaw { get; set; }
    public string? FpeKeyEnvRaw { get; set; }
    public string? FpeTweakEnvRaw { get; set; }
    public string? ConfigBlock { get; set; }   // SPLITTING/PDF/POSTFILTERS/ANALYSIS
    public bool GraphicalBox { get; set; }
    public List<Setting>? Settings { get; set; }
}

/// <summary>
/// A parsed discovery statement. Discovery verbs parse successfully but are not
/// compiled to Phileas JSON — they target a separate discovery-query schema.
/// </summary>
public sealed class DiscoveryStmt : IStatement
{
    public required string Verb { get; init; } // FIND_PII | DISCOVER_ENTITIES | SCAN | SELECT_FINDINGS
}
