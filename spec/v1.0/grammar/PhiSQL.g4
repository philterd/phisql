/*
 * PhiSQL v1.0 grammar.
 *
 * Normative reference. Implementations may generate a parser directly from this file.
 * Reference parser: https://github.com/philterd/phisql.
 *
 * Status: Stable (v1.0). The v1.0 grammar is frozen; changes follow the
 * versioning policy in CONTRIBUTING.md (additive features in a minor version,
 * breaking changes in a major version).
 *
 * Discovery query verbs (FIND PII, DISCOVER ENTITIES, SCAN) and a SELECT
 * projection over a findings store are supported alongside the redaction
 * statements. See spec/v1.0/catalog/findings.yaml for the findings table
 * schema and spec/v1.0/catalog/sources.yaml for the supported URI schemes
 * on the IN clause.
 *
 * Keywords and entity-type identifiers are case-insensitive. User-defined
 * names (policy names, dictionary names, custom-identifier classifications)
 * are case-sensitive.
 */

grammar PhiSQL;

options {
    caseInsensitive = true;
}

// ============================================================================
// Parser rules
// ============================================================================

document
    : (statement ';')* EOF
    ;

statement
    : policyDecl
    | configureStmt
    | redactStmt
    | deidentifyStmt
    | ignoreStmt
    | defineIdentifierStmt
    | defineDictionaryStmt
    | defineSectionStmt
    | defineGeneratorStmt
    | detectStmt
    | discoveryStmt
    ;

policyDecl
    : POLICY policyName=ID (DESCRIPTION description=STRING_LITERAL)?
    ;

// Configures the policy-level secrets used by the encryption strategies. Secrets are always read
// from an environment variable at runtime (never stored inline in the policy).
configureStmt
    : CONFIGURE
      ( CRYPTO KEY FROM ENV cryptoKeyEnv=STRING_LITERAL
      | FPE KEY FROM ENV fpeKeyEnv=STRING_LITERAL TWEAK FROM ENV fpeTweakEnv=STRING_LITERAL
      | configBlock=(SPLITTING | PDF | POSTFILTERS | ANALYSIS) '(' settingList ')'
      | GRAPHICAL BOX '(' settingList ')'
      )
    ;

// A comma-separated list of key = value settings. Keys are the Phileas schema
// property names (e.g. threshold, redactionColor, priority); the JSON type is
// inferred from the value (TRUE -> boolean, 300 -> integer, 0.25 -> number,
// 'x' -> string, ('a','b') -> array of strings). Used by the CONFIGURE
// config/graphical forms and by the OPTIONS clause on filter statements.
settingList
    : setting (',' setting)*
    ;

setting
    : settingKey '=' settingValue
    ;

// Setting keys are Phileas schema property names. A key may be quoted when it
// collides with a reserved keyword (e.g. 'pattern') or is an arbitrary map key.
settingKey
    : ID
    | STRING_LITERAL
    ;

// A setting value is a scalar, a nested object ( k = v, ... ), or an array
// [ v, ... ]. The recursion lets OPTIONS/CONFIGURE express any schema structure,
// including arrays of objects (e.g. ignoredPatterns) and nested config objects.
settingValue
    : literal
    | objectValue
    | arrayValue
    ;

objectValue
    : '(' settingList ')'
    ;

arrayValue
    : '[' (settingValue (',' settingValue)*)? ']'
    ;

// Optional trailing clause that sets arbitrary leaf properties on the filter
// object a statement produces (priority, windowSize, enabled, entity-specific
// validation flags, etc.). Keys are Phileas schema property names.
optionsClause
    : OPTIONS '(' settingList ')'
    ;

redactStmt
    : REDACT entityList (WITH strategyExpr)? (WHERE predicate)? optionsClause?
    ;

deidentifyStmt
    : DEIDENTIFY entityAssignment (',' entityAssignment)*
    ;

entityAssignment
    : entityType AS strategyExpr optionsClause?
    ;

ignoreStmt
    : IGNORE
      ( TERMS stringList
      | PATTERN STRING_LITERAL
      )
      (FOR entityList)?
      optionsClause?
    ;

// Defines a custom identifier from a regex pattern and applies a strategy to it.
defineIdentifierStmt
    : DEFINE IDENTIFIER_KW classification=STRING_LITERAL
      MATCHING pattern=STRING_LITERAL
      (GROUP groupNumber=NUMERIC_LITERAL)?
      (CASE sensitivity=(SENSITIVE | INSENSITIVE))?
      WITH strategyExpr
      (WHERE predicate)?
      optionsClause?
    ;

// Defines a custom dictionary of terms and applies a strategy to matches.
defineDictionaryStmt
    : DEFINE DICTIONARY classification=STRING_LITERAL
      TERMS stringList
      (FUZZY (SENSITIVITY sensitivity=ID)?)?
      capitalized=CAPITALIZED?
      WITH strategyExpr
      optionsClause?
    ;

// Defines a section bounded by start/end regex patterns and redacts it.
defineSectionStmt
    : DEFINE SECTION
      START startPattern=STRING_LITERAL
      END endPattern=STRING_LITERAL
      WITH strategyExpr
      optionsClause?
    ;

// Defines a named, reusable replacement generator at the top level, referenced
// by name from a MAP_REPLACE strategy's generator argument. TYPE is the backend
// discriminator ('ollama'); the OPTIONS carry the backend settings (endpoint,
// model, prompt, timeoutMs) as passthrough keys on the compiled generator object.
defineGeneratorStmt
    : DEFINE GENERATOR generatorName=STRING_LITERAL
      TYPE generatorType=STRING_LITERAL
      optionsClause
    ;

// Detects entities with the PhEye AI/NER model and applies a strategy to them.
detectStmt
    : DETECT PHEYE
      (LABELS stringList)?
      (ENDPOINT endpoint=STRING_LITERAL)?
      (MODEL model=STRING_LITERAL)?
      WITH strategyExpr
      (WHERE predicate)?
      optionsClause?
    ;

// Discovery query verbs. Unlike the redaction statements above, discovery
// statements do not compile to Phileas JSON. They compile to a discovery-query
// JSON shape that a discovery engine (such as Phinder) executes against a
// storage source or a findings store. The findings schema lives in
// spec/v1.0/catalog/findings.yaml; the column names referenced here must
// resolve against that catalog when the compiler runs.
discoveryStmt
    : FIND PII inClause whereDiscovery?                                       # findPiiStmt
    | DISCOVER ENTITIES inClause whereDiscovery?                              # discoverEntitiesStmt
    | SCAN inClause whereDiscovery?                                           # scanStmt
    | SELECT projectionList FROM findingsRef whereDiscovery? groupByClause? limitClause?  # selectFindingsStmt
    ;

inClause
    : IN uri=STRING_LITERAL
    ;

whereDiscovery
    : WHERE discoveryPredicate
    ;

// Predicates over finding-row columns.
discoveryPredicate
    : columnRef IN stringList                                                 # inDiscoveryPredicate
    | columnRef compareOp (STRING_LITERAL | NUMERIC_LITERAL | BOOLEAN_LITERAL) # compareDiscoveryPredicate
    | '(' discoveryPredicate ')'                                              # parenDiscoveryPredicate
    | discoveryPredicate (AND | OR) discoveryPredicate                        # logicalDiscoveryPredicate
    ;

projectionList
    : projection (',' projection)*
    ;

projection
    : '*'                                       # starProjection
    | aggregate                                 # aggregateProjection
    | columnRef                                 # columnProjection
    ;

aggregate
    : aggFn=(COUNT | AVG | SUM | MIN | MAX) '(' aggArg ')'
    ;

aggArg
    : '*'                                       # starAggArg
    | columnRef                                 # columnAggArg
    ;

// CONFIDENCE is also accepted because it is a reserved keyword (it appears in
// the redaction WHERE predicate) but is a valid findings-table column name.
// Other reserved-word/column overlaps follow the same pattern as they arise.
columnRef
    : ID
    | CONFIDENCE
    ;

findingsRef
    : (namespace=ID '.')? table=ID
    ;

groupByClause
    : GROUP BY columnRef (',' columnRef)*
    ;

limitClause
    : LIMIT NUMERIC_LITERAL
    ;

entityList
    : entityType (',' entityType)*
    ;

entityType
    : ID                                              # simpleEntityType
    | IDENTIFIER_KW '(' STRING_LITERAL ')'            # customIdentifier
    ;

strategyExpr
    : strategyName ('(' strategyArgs ')')?
    ;

strategyName
    : MASK
    | REDACT
    | ENCRYPT
    | FPE_ENCRYPT
    | HASH_SHA256
    | RANDOM_REPLACE
    | STATIC_REPLACE
    | LAST_4
    | TRUNCATE
    | TRUNCATE_TO_YEAR
    | SHIFT
    | RELATIVE
    | ABBREVIATE
    | MAP_REPLACE
    ;

strategyArgs
    : namedArg (',' namedArg)*
    ;

// A strategy argument name is normally an identifier, but a few keyword tokens
// are also valid Phileas strategy property names and must be usable here without
// quoting (e.g. MAP_REPLACE's "generator", "type"). ANTLR still exposes the
// matched token's text through the argName label.
namedArg
    : argName=(ID | GENERATOR | TYPE) '=' settingValue
    ;

predicate
    : CONFIDENCE compareOp NUMERIC_LITERAL            # confidencePredicate
    | '(' predicate ')'                               # parenPredicate
    | predicate (AND | OR) predicate                  # logicalPredicate
    ;

compareOp
    : '>'
    | '>='
    | '<'
    | '<='
    | '='
    ;

stringList
    : '(' STRING_LITERAL (',' STRING_LITERAL)* ')'
    ;

// A literal value on the right-hand side of a named strategy argument.
// Bare identifiers are accepted for enum-typed arguments (e.g., scope=document
// where DOCUMENT and CONTEXT are valid enum values from strategies.yaml).
// The compiler validates that bare identifiers correspond to enum values
// declared in the strategy catalog for the relevant argument.
literal
    : STRING_LITERAL
    | NUMERIC_LITERAL
    | BOOLEAN_LITERAL
    | ID
    ;

// ============================================================================
// Lexer rules
// ============================================================================

// Statement keywords (redaction)
POLICY          : 'POLICY' ;
DESCRIPTION     : 'DESCRIPTION' ;
CONFIGURE       : 'CONFIGURE' ;
CRYPTO          : 'CRYPTO' ;
FPE             : 'FPE' ;
KEY             : 'KEY' ;
TWEAK           : 'TWEAK' ;
FROM            : 'FROM' ;
ENV             : 'ENV' ;
// CONFIGURE config-block and graphical keywords.
SPLITTING       : 'SPLITTING' ;
PDF             : 'PDF' ;
POSTFILTERS     : 'POSTFILTERS' ;
ANALYSIS        : 'ANALYSIS' ;
GRAPHICAL       : 'GRAPHICAL' ;
BOX             : 'BOX' ;
REDACT          : 'REDACT' ;
DEIDENTIFY      : 'DEIDENTIFY' ;
IGNORE          : 'IGNORE' ;
TERMS           : 'TERMS' ;
PATTERN         : 'PATTERN' ;
FOR             : 'FOR' ;
WITH            : 'WITH' ;
WHERE           : 'WHERE' ;
AS              : 'AS' ;
AND             : 'AND' ;
OR              : 'OR' ;
CONFIDENCE      : 'CONFIDENCE' ;

// Custom-identifier definition keywords.
DEFINE          : 'DEFINE' ;
MATCHING        : 'MATCHING' ;
GROUP           : 'GROUP' ;
CASE            : 'CASE' ;
SENSITIVE       : 'SENSITIVE' ;
INSENSITIVE     : 'INSENSITIVE' ;

// Custom-dictionary and section definition keywords.
DICTIONARY      : 'DICTIONARY' ;
SECTION         : 'SECTION' ;
START           : 'START' ;
END             : 'END' ;
FUZZY           : 'FUZZY' ;
SENSITIVITY     : 'SENSITIVITY' ;
CAPITALIZED     : 'CAPITALIZED' ;

// Generator definition keywords.
GENERATOR       : 'GENERATOR' ;
TYPE            : 'TYPE' ;

// Generic per-filter options clause.
OPTIONS         : 'OPTIONS' ;

// PhEye (AI/NER) detection keywords.
DETECT          : 'DETECT' ;
PHEYE           : 'PHEYE' ;
LABELS          : 'LABELS' ;
ENDPOINT        : 'ENDPOINT' ;
MODEL           : 'MODEL' ;

// Discovery keywords.
FIND            : 'FIND' ;
PII             : 'PII' ;
DISCOVER        : 'DISCOVER' ;
ENTITIES        : 'ENTITIES' ;
SCAN            : 'SCAN' ;
IN              : 'IN' ;
SELECT          : 'SELECT' ;
// FROM is defined above (shared with the CONFIGURE ... FROM ENV statement).
BY              : 'BY' ;
LIMIT           : 'LIMIT' ;
COUNT           : 'COUNT' ;
AVG             : 'AVG' ;
SUM             : 'SUM' ;
MIN             : 'MIN' ;
MAX             : 'MAX' ;

// Custom-identifier reference keyword.
// "IDENTIFIER" is a PhiSQL keyword, not a generic identifier token name.
IDENTIFIER_KW   : 'IDENTIFIER' ;

// Strategy keywords (must precede ID for first-match disambiguation).
// TRUNCATE_TO_YEAR is declared before TRUNCATE; ANTLR's longest-match rule
// selects it for the full keyword, but explicit ordering keeps intent clear.
MASK            : 'MASK' ;
ENCRYPT         : 'ENCRYPT' ;
FPE_ENCRYPT     : 'FPE_ENCRYPT' ;
HASH_SHA256     : 'HASH_SHA256' ;
RANDOM_REPLACE  : 'RANDOM_REPLACE' ;
STATIC_REPLACE  : 'STATIC_REPLACE' ;
LAST_4          : 'LAST_4' ;
TRUNCATE_TO_YEAR: 'TRUNCATE_TO_YEAR' ;
TRUNCATE        : 'TRUNCATE' ;
SHIFT           : 'SHIFT' ;
RELATIVE        : 'RELATIVE' ;
ABBREVIATE      : 'ABBREVIATE' ;
MAP_REPLACE     : 'MAP_REPLACE' ;

// Boolean literals (must precede ID)
BOOLEAN_LITERAL : 'TRUE' | 'FALSE' ;

// Generic identifier (entity types, named args, policy names, dictionary names)
ID
    : [A-Za-z_] [A-Za-z0-9_]*
    ;

// String literal: single-quoted, with backslash escapes
STRING_LITERAL
    : '\'' ( '\\' . | ~['\\\r\n] )* '\''
    ;

// Numeric literal: integers and decimals, optional leading minus
NUMERIC_LITERAL
    : '-'? [0-9]+ ('.' [0-9]+)?
    ;

// Comments
LINE_COMMENT
    : '--' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

// Whitespace
WS
    : [ \t\r\n]+ -> skip
    ;
