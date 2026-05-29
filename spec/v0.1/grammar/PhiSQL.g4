/*
 * PhiSQL v0.1 grammar.
 *
 * Normative reference. Implementations may generate a parser directly from this file.
 * Reference parser: https://github.com/philterd/phisql.
 *
 * Status: DRAFT. Grammar may change before v1.0.
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
    | redactStmt
    | deidentifyStmt
    | ignoreStmt
    | defineIdentifierStmt
    | detectStmt
    ;

policyDecl
    : POLICY policyName=ID (DESCRIPTION description=STRING_LITERAL)?
    ;

redactStmt
    : REDACT entityList (WITH strategyExpr)? (WHERE predicate)?
    ;

deidentifyStmt
    : DEIDENTIFY entityAssignment (',' entityAssignment)*
    ;

entityAssignment
    : entityType AS strategyExpr
    ;

ignoreStmt
    : IGNORE
      ( TERMS stringList
      | PATTERN STRING_LITERAL
      )
      (FOR entityList)?
    ;

// Defines a custom identifier from a regex pattern and applies a strategy to it.
defineIdentifierStmt
    : DEFINE IDENTIFIER_KW classification=STRING_LITERAL
      MATCHING pattern=STRING_LITERAL
      (GROUP groupNumber=NUMERIC_LITERAL)?
      (CASE sensitivity=(SENSITIVE | INSENSITIVE))?
      WITH strategyExpr
      (WHERE predicate)?
    ;

// Detects entities with the PhEye AI/NER model and applies a strategy to them.
detectStmt
    : DETECT PHEYE
      (LABELS stringList)?
      (ENDPOINT endpoint=STRING_LITERAL)?
      WITH strategyExpr
      (WHERE predicate)?
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
    | ABBREVIATE
    ;

strategyArgs
    : namedArg (',' namedArg)*
    ;

namedArg
    : argName=ID '=' literal
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

// Statement keywords
POLICY          : 'POLICY' ;
DESCRIPTION     : 'DESCRIPTION' ;
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

// PhEye (AI/NER) detection keywords.
DETECT          : 'DETECT' ;
PHEYE           : 'PHEYE' ;
LABELS          : 'LABELS' ;
ENDPOINT        : 'ENDPOINT' ;

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
ABBREVIATE      : 'ABBREVIATE' ;

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
