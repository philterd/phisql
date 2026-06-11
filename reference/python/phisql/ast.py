# Copyright 2026 Philterd, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
AST node types for PhiSQL v1.0.

These mirror the parser rules in ``spec/v1.0/grammar/PhiSQL.g4`` one-for-one.
The compiler walks this tree the way the Java reference walks the ANTLR parse
tree. String and numeric literals are stored as their raw source text (quotes
included for strings); the compiler unquotes and coerces them, matching the
Java reference's use of ``getText()`` plus ``unquoteString``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Document:
    statements: List = field(default_factory=list)


# --- Entity references -------------------------------------------------------


@dataclass
class SimpleEntityType:
    name: str  # the ID text, e.g. "SSN"


@dataclass
class CustomIdentifier:
    classification_raw: str  # the quoted STRING_LITERAL text


# --- Literals and setting values ---------------------------------------------


@dataclass
class Literal:
    # kind is one of: "STRING", "NUMERIC", "BOOLEAN", "ID"
    kind: str
    text: str  # raw source text (quotes included for STRING)


@dataclass
class SettingValue:
    """A setting/argument value: a scalar literal, a nested object, or an array."""

    literal: Optional[Literal] = None
    object_settings: Optional[List] = None      # list[Setting] when an object value
    array_elements: Optional[List] = None        # list[SettingValue] when an array


@dataclass
class SettingKey:
    # kind is "ID" or "STRING"
    kind: str
    text: str  # ID text, or raw quoted text for STRING


@dataclass
class Setting:
    key: SettingKey
    value: SettingValue


@dataclass
class NamedArg:
    arg_name: str  # ID text
    value: SettingValue


@dataclass
class StrategyExpr:
    name: str          # strategy keyword text, e.g. "MASK"
    args: List = field(default_factory=list)  # list[NamedArg]


# --- Redaction predicates ----------------------------------------------------


@dataclass
class ConfidencePredicate:
    op: str       # one of > >= < <= =
    number: str   # raw NUMERIC_LITERAL text


@dataclass
class ParenPredicate:
    inner: object


@dataclass
class LogicalPredicate:
    op: str  # "AND" or "OR"
    left: object
    right: object


# --- Statements --------------------------------------------------------------


@dataclass
class PolicyDecl:
    policy_name: str
    description_raw: Optional[str] = None  # quoted STRING_LITERAL text or None


@dataclass
class RedactStmt:
    entities: List                       # list[entity type node]
    strategy: Optional[StrategyExpr] = None
    predicate: object = None
    options: Optional[List] = None       # list[Setting] or None


@dataclass
class EntityAssignment:
    entity: object
    strategy: StrategyExpr
    options: Optional[List] = None


@dataclass
class DeidentifyStmt:
    assignments: List  # list[EntityAssignment]


@dataclass
class IgnoreStmt:
    kind: str                              # "TERMS" or "PATTERN"
    terms: Optional[List] = None           # list[raw STRING_LITERAL] for TERMS
    pattern_raw: Optional[str] = None      # raw STRING_LITERAL for PATTERN
    entities: Optional[List] = None        # FOR entityList, or None
    options: Optional[List] = None


@dataclass
class DefineIdentifierStmt:
    classification_raw: str
    pattern_raw: str
    group_number: Optional[str] = None     # raw NUMERIC_LITERAL text or None
    sensitivity: Optional[str] = None      # "SENSITIVE" / "INSENSITIVE" / None
    strategy: StrategyExpr = None
    predicate: object = None
    options: Optional[List] = None


@dataclass
class DefineDictionaryStmt:
    classification_raw: str
    terms: List                            # list[raw STRING_LITERAL]
    fuzzy: bool = False
    sensitivity: Optional[str] = None      # the ID text after SENSITIVITY, or None
    capitalized: bool = False
    strategy: StrategyExpr = None
    options: Optional[List] = None


@dataclass
class DefineSectionStmt:
    start_raw: str
    end_raw: str
    strategy: StrategyExpr
    options: Optional[List] = None


@dataclass
class DetectStmt:
    labels: Optional[List] = None          # list[raw STRING_LITERAL] or None
    endpoint_raw: Optional[str] = None     # raw STRING_LITERAL or None
    strategy: StrategyExpr = None
    predicate: object = None
    options: Optional[List] = None


@dataclass
class ConfigureStmt:
    # Exactly one of these shapes is populated.
    crypto_key_env_raw: Optional[str] = None
    fpe_key_env_raw: Optional[str] = None
    fpe_tweak_env_raw: Optional[str] = None
    config_block: Optional[str] = None     # SPLITTING/PDF/POSTFILTERS/ANALYSIS
    graphical_box: bool = False
    settings: Optional[List] = None        # list[Setting] for config/graphical forms


@dataclass
class DiscoveryStmt:
    """A parsed discovery statement.

    Discovery verbs (FIND PII, DISCOVER ENTITIES, SCAN, SELECT ... FROM
    findings) parse successfully but are not compiled to Phileas JSON by this
    compiler — they target a separate discovery-query schema. The parsed shape
    is retained for completeness but the compiler ignores it, matching the Java
    reference's scope.
    """

    verb: str  # "FIND_PII" | "DISCOVER_ENTITIES" | "SCAN" | "SELECT_FINDINGS"
