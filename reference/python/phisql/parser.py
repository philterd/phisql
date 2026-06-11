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
Recursive-descent parser for PhiSQL v1.0.

Each method corresponds to a parser rule in ``spec/v1.0/grammar/PhiSQL.g4``.
The ``everyExampleParses`` test (which parses every ``.phisql`` example in the
spec) is the load-bearing assertion that this parser stays in sync with the
grammar — the same role the generated parser plays in the Java reference.

Syntax errors raise ``ParseException`` with a ``line L:C`` prefix.
"""

from __future__ import annotations

from . import ast
from .errors import ParseException
from .lexer import tokenize

# Strategy-name keyword token types (the strategyName rule).
_STRATEGY_NAMES = frozenset({
    "MASK", "REDACT", "ENCRYPT", "FPE_ENCRYPT", "HASH_SHA256", "RANDOM_REPLACE",
    "STATIC_REPLACE", "LAST_4", "TRUNCATE", "TRUNCATE_TO_YEAR", "SHIFT",
    "RELATIVE", "ABBREVIATE",
})

_COMPARE_OPS = frozenset({">", ">=", "<", "<=", "="})
_AGG_FNS = frozenset({"COUNT", "AVG", "SUM", "MIN", "MAX"})

# Token types that can begin a statement (used for clearer error messages).
_STATEMENT_STARTS = frozenset({
    "POLICY", "CONFIGURE", "REDACT", "DEIDENTIFY", "IGNORE", "DEFINE",
    "DETECT", "FIND", "DISCOVER", "SCAN", "SELECT",
})


class Parser:
    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = 0

    # --- Token cursor helpers ------------------------------------------------

    def _peek(self):
        return self._tokens[self._pos]

    def _advance(self):
        tok = self._tokens[self._pos]
        if tok.type != "EOF":
            self._pos += 1
        return tok

    def _check(self, *types) -> bool:
        return self._peek().type in types

    def _error(self, message: str):
        tok = self._peek()
        raise ParseException(f"line {tok.line}:{tok.column} {message}")

    def _expect(self, type_, label=None):
        tok = self._peek()
        if tok.type != type_:
            want = label or f"'{type_}'"
            got = "<EOF>" if tok.type == "EOF" else f"'{tok.text}'"
            self._error(f"expected {want} but found {got}")
        return self._advance()

    # --- document ------------------------------------------------------------

    def parse_document(self) -> ast.Document:
        doc = ast.Document()
        while not self._check("EOF"):
            doc.statements.append(self._statement())
            self._expect(";", "';'")
        return doc

    def _statement(self):
        t = self._peek().type
        if t == "POLICY":
            return self._policy_decl()
        if t == "CONFIGURE":
            return self._configure_stmt()
        if t == "REDACT":
            return self._redact_stmt()
        if t == "DEIDENTIFY":
            return self._deidentify_stmt()
        if t == "IGNORE":
            return self._ignore_stmt()
        if t == "DEFINE":
            return self._define_stmt()
        if t == "DETECT":
            return self._detect_stmt()
        if t in ("FIND", "DISCOVER", "SCAN", "SELECT"):
            return self._discovery_stmt()
        self._error("expected a statement keyword")

    # --- policyDecl ----------------------------------------------------------

    def _policy_decl(self) -> ast.PolicyDecl:
        self._expect("POLICY")
        name = self._expect("ID", "a policy name").text
        description = None
        if self._check("DESCRIPTION"):
            self._advance()
            description = self._expect("STRING_LITERAL", "a quoted description").text
        return ast.PolicyDecl(policy_name=name, description_raw=description)

    # --- configureStmt -------------------------------------------------------

    def _configure_stmt(self) -> ast.ConfigureStmt:
        self._expect("CONFIGURE")
        stmt = ast.ConfigureStmt()
        if self._check("CRYPTO"):
            self._advance()
            self._expect("KEY"); self._expect("FROM"); self._expect("ENV")
            stmt.crypto_key_env_raw = self._expect("STRING_LITERAL").text
        elif self._check("FPE"):
            self._advance()
            self._expect("KEY"); self._expect("FROM"); self._expect("ENV")
            stmt.fpe_key_env_raw = self._expect("STRING_LITERAL").text
            self._expect("TWEAK"); self._expect("FROM"); self._expect("ENV")
            stmt.fpe_tweak_env_raw = self._expect("STRING_LITERAL").text
        elif self._check("SPLITTING", "PDF", "POSTFILTERS", "ANALYSIS"):
            stmt.config_block = self._advance().type
            self._expect("(", "'('")
            stmt.settings = self._setting_list()
            self._expect(")", "')'")
        elif self._check("GRAPHICAL"):
            self._advance()
            self._expect("BOX")
            stmt.graphical_box = True
            self._expect("(", "'('")
            stmt.settings = self._setting_list()
            self._expect(")", "')'")
        else:
            self._error("expected CRYPTO, FPE, a config block, or GRAPHICAL BOX")
        return stmt

    # --- settingList / setting / settingValue --------------------------------

    def _setting_list(self):
        settings = [self._setting()]
        while self._check(","):
            self._advance()
            settings.append(self._setting())
        return settings

    def _setting(self) -> ast.Setting:
        key = self._setting_key()
        self._expect("=", "'='")
        return ast.Setting(key=key, value=self._setting_value())

    def _setting_key(self) -> ast.SettingKey:
        tok = self._peek()
        if tok.type == "ID":
            return ast.SettingKey(kind="ID", text=self._advance().text)
        if tok.type == "STRING_LITERAL":
            return ast.SettingKey(kind="STRING", text=self._advance().text)
        self._error("expected a setting key (identifier or quoted string)")

    def _setting_value(self) -> ast.SettingValue:
        tok = self._peek()
        if tok.type == "(":
            self._advance()
            settings = self._setting_list()
            self._expect(")", "')'")
            return ast.SettingValue(object_settings=settings)
        if tok.type == "[":
            self._advance()
            elements = []
            if not self._check("]"):
                elements.append(self._setting_value())
                while self._check(","):
                    self._advance()
                    elements.append(self._setting_value())
            self._expect("]", "']'")
            return ast.SettingValue(array_elements=elements)
        return ast.SettingValue(literal=self._literal())

    def _literal(self) -> ast.Literal:
        tok = self._peek()
        if tok.type == "STRING_LITERAL":
            return ast.Literal("STRING", self._advance().text)
        if tok.type == "NUMERIC_LITERAL":
            return ast.Literal("NUMERIC", self._advance().text)
        if tok.type == "BOOLEAN_LITERAL":
            return ast.Literal("BOOLEAN", self._advance().text)
        if tok.type == "ID":
            return ast.Literal("ID", self._advance().text)
        self._error("expected a literal value")

    def _options_clause(self):
        """Returns the OPTIONS setting list, or None when absent."""
        if not self._check("OPTIONS"):
            return None
        self._advance()
        self._expect("(", "'('")
        settings = self._setting_list()
        self._expect(")", "')'")
        return settings

    # --- redactStmt ----------------------------------------------------------

    def _redact_stmt(self) -> ast.RedactStmt:
        self._expect("REDACT")
        entities = self._entity_list()
        strategy = None
        if self._check("WITH"):
            self._advance()
            strategy = self._strategy_expr()
        predicate = None
        if self._check("WHERE"):
            self._advance()
            predicate = self._predicate()
        options = self._options_clause()
        return ast.RedactStmt(entities=entities, strategy=strategy,
                              predicate=predicate, options=options)

    # --- deidentifyStmt ------------------------------------------------------

    def _deidentify_stmt(self) -> ast.DeidentifyStmt:
        self._expect("DEIDENTIFY")
        assignments = [self._entity_assignment()]
        while self._check(","):
            self._advance()
            assignments.append(self._entity_assignment())
        return ast.DeidentifyStmt(assignments=assignments)

    def _entity_assignment(self) -> ast.EntityAssignment:
        entity = self._entity_type()
        self._expect("AS", "'AS'")
        strategy = self._strategy_expr()
        options = self._options_clause()
        return ast.EntityAssignment(entity=entity, strategy=strategy, options=options)

    # --- ignoreStmt ----------------------------------------------------------

    def _ignore_stmt(self) -> ast.IgnoreStmt:
        self._expect("IGNORE")
        if self._check("TERMS"):
            self._advance()
            terms = self._string_list()
            stmt = ast.IgnoreStmt(kind="TERMS", terms=terms)
        elif self._check("PATTERN"):
            self._advance()
            stmt = ast.IgnoreStmt(kind="PATTERN",
                                  pattern_raw=self._expect("STRING_LITERAL").text)
        else:
            self._error("expected TERMS or PATTERN")
        if self._check("FOR"):
            self._advance()
            stmt.entities = self._entity_list()
        stmt.options = self._options_clause()
        return stmt

    # --- defineStmt (identifier / dictionary / section) ----------------------

    def _define_stmt(self):
        self._expect("DEFINE")
        if self._check("IDENTIFIER"):
            return self._define_identifier_stmt()
        if self._check("DICTIONARY"):
            return self._define_dictionary_stmt()
        if self._check("SECTION"):
            return self._define_section_stmt()
        self._error("expected IDENTIFIER, DICTIONARY, or SECTION after DEFINE")

    def _define_identifier_stmt(self) -> ast.DefineIdentifierStmt:
        self._expect("IDENTIFIER")
        classification = self._expect("STRING_LITERAL").text
        self._expect("MATCHING")
        pattern = self._expect("STRING_LITERAL").text
        group_number = None
        if self._check("GROUP"):
            self._advance()
            group_number = self._expect("NUMERIC_LITERAL").text
        sensitivity = None
        if self._check("CASE"):
            self._advance()
            if self._check("SENSITIVE", "INSENSITIVE"):
                sensitivity = self._advance().type
            else:
                self._error("expected SENSITIVE or INSENSITIVE")
        self._expect("WITH")
        strategy = self._strategy_expr()
        predicate = None
        if self._check("WHERE"):
            self._advance()
            predicate = self._predicate()
        options = self._options_clause()
        return ast.DefineIdentifierStmt(
            classification_raw=classification, pattern_raw=pattern,
            group_number=group_number, sensitivity=sensitivity,
            strategy=strategy, predicate=predicate, options=options)

    def _define_dictionary_stmt(self) -> ast.DefineDictionaryStmt:
        self._expect("DICTIONARY")
        classification = self._expect("STRING_LITERAL").text
        self._expect("TERMS")
        terms = self._string_list()
        fuzzy = False
        sensitivity = None
        if self._check("FUZZY"):
            self._advance()
            fuzzy = True
            if self._check("SENSITIVITY"):
                self._advance()
                sensitivity = self._expect("ID", "a sensitivity level").text
        capitalized = False
        if self._check("CAPITALIZED"):
            self._advance()
            capitalized = True
        self._expect("WITH")
        strategy = self._strategy_expr()
        options = self._options_clause()
        return ast.DefineDictionaryStmt(
            classification_raw=classification, terms=terms, fuzzy=fuzzy,
            sensitivity=sensitivity, capitalized=capitalized,
            strategy=strategy, options=options)

    def _define_section_stmt(self) -> ast.DefineSectionStmt:
        self._expect("SECTION")
        self._expect("START")
        start = self._expect("STRING_LITERAL").text
        self._expect("END")
        end = self._expect("STRING_LITERAL").text
        self._expect("WITH")
        strategy = self._strategy_expr()
        options = self._options_clause()
        return ast.DefineSectionStmt(start_raw=start, end_raw=end,
                                     strategy=strategy, options=options)

    # --- detectStmt ----------------------------------------------------------

    def _detect_stmt(self) -> ast.DetectStmt:
        self._expect("DETECT")
        self._expect("PHEYE")
        labels = None
        if self._check("LABELS"):
            self._advance()
            labels = self._string_list()
        endpoint = None
        if self._check("ENDPOINT"):
            self._advance()
            endpoint = self._expect("STRING_LITERAL").text
        self._expect("WITH")
        strategy = self._strategy_expr()
        predicate = None
        if self._check("WHERE"):
            self._advance()
            predicate = self._predicate()
        options = self._options_clause()
        return ast.DetectStmt(labels=labels, endpoint_raw=endpoint,
                              strategy=strategy, predicate=predicate, options=options)

    # --- entityList / entityType ---------------------------------------------

    def _entity_list(self):
        entities = [self._entity_type()]
        while self._check(","):
            self._advance()
            entities.append(self._entity_type())
        return entities

    def _entity_type(self):
        tok = self._peek()
        if tok.type == "ID":
            return ast.SimpleEntityType(name=self._advance().text)
        if tok.type == "IDENTIFIER":
            self._advance()
            self._expect("(", "'('")
            classification = self._expect("STRING_LITERAL").text
            self._expect(")", "')'")
            return ast.CustomIdentifier(classification_raw=classification)
        self._error("expected an entity type or IDENTIFIER('<classification>')")

    # --- strategyExpr --------------------------------------------------------

    def _strategy_expr(self) -> ast.StrategyExpr:
        tok = self._peek()
        if tok.type not in _STRATEGY_NAMES:
            self._error("expected a strategy name")
        name = self._advance().text
        args = []
        if self._check("("):
            self._advance()
            args = self._strategy_args()
            self._expect(")", "')'")
        return ast.StrategyExpr(name=name, args=args)

    def _strategy_args(self):
        args = [self._named_arg()]
        while self._check(","):
            self._advance()
            args.append(self._named_arg())
        return args

    def _named_arg(self) -> ast.NamedArg:
        name = self._expect("ID", "an argument name").text
        self._expect("=", "'='")
        return ast.NamedArg(arg_name=name, value=self._setting_value())

    # --- predicate (redaction WHERE) -----------------------------------------

    def _predicate(self):
        left = self._predicate_primary()
        while self._check("AND", "OR"):
            op = self._advance().type
            right = self._predicate_primary()
            left = ast.LogicalPredicate(op=op, left=left, right=right)
        return left

    def _predicate_primary(self):
        if self._check("("):
            self._advance()
            inner = self._predicate()
            self._expect(")", "')'")
            return ast.ParenPredicate(inner=inner)
        if self._check("CONFIDENCE"):
            self._advance()
            op = self._compare_op()
            number = self._expect("NUMERIC_LITERAL", "a number").text
            return ast.ConfidencePredicate(op=op, number=number)
        self._error("expected CONFIDENCE or '(' in WHERE predicate")

    def _compare_op(self) -> str:
        tok = self._peek()
        if tok.type not in _COMPARE_OPS:
            self._error("expected a comparison operator")
        return self._advance().type

    # --- stringList ----------------------------------------------------------

    def _string_list(self):
        self._expect("(", "'('")
        terms = [self._expect("STRING_LITERAL").text]
        while self._check(","):
            self._advance()
            terms.append(self._expect("STRING_LITERAL").text)
        self._expect(")", "')'")
        return terms

    # --- discoveryStmt -------------------------------------------------------
    #
    # Parsed for syntactic validation only; the compiler does not translate
    # discovery statements (they target a separate discovery-query schema).

    def _discovery_stmt(self) -> ast.DiscoveryStmt:
        if self._check("FIND"):
            self._advance()
            self._expect("PII")
            self._in_clause()
            self._where_discovery_opt()
            return ast.DiscoveryStmt(verb="FIND_PII")
        if self._check("DISCOVER"):
            self._advance()
            self._expect("ENTITIES")
            self._in_clause()
            self._where_discovery_opt()
            return ast.DiscoveryStmt(verb="DISCOVER_ENTITIES")
        if self._check("SCAN"):
            self._advance()
            self._in_clause()
            self._where_discovery_opt()
            return ast.DiscoveryStmt(verb="SCAN")
        # SELECT projectionList FROM findingsRef whereDiscovery? groupBy? limit?
        self._expect("SELECT")
        self._projection_list()
        self._expect("FROM")
        self._findings_ref()
        self._where_discovery_opt()
        if self._check("GROUP"):
            self._advance()
            self._expect("BY")
            self._column_ref()
            while self._check(","):
                self._advance()
                self._column_ref()
        if self._check("LIMIT"):
            self._advance()
            self._expect("NUMERIC_LITERAL")
        return ast.DiscoveryStmt(verb="SELECT_FINDINGS")

    def _in_clause(self):
        self._expect("IN")
        self._expect("STRING_LITERAL", "a quoted URI")

    def _where_discovery_opt(self):
        if self._check("WHERE"):
            self._advance()
            self._discovery_predicate()

    def _discovery_predicate(self):
        self._discovery_predicate_primary()
        while self._check("AND", "OR"):
            self._advance()
            self._discovery_predicate_primary()

    def _discovery_predicate_primary(self):
        if self._check("("):
            self._advance()
            self._discovery_predicate()
            self._expect(")", "')'")
            return
        self._column_ref()
        if self._check("IN"):
            self._advance()
            self._string_list()
        elif self._peek().type in _COMPARE_OPS:
            self._advance()
            if not self._check("STRING_LITERAL", "NUMERIC_LITERAL", "BOOLEAN_LITERAL"):
                self._error("expected a literal on the right of the comparison")
            self._advance()
        else:
            self._error("expected IN or a comparison operator")

    def _projection_list(self):
        self._projection()
        while self._check(","):
            self._advance()
            self._projection()

    def _projection(self):
        if self._check("*"):
            self._advance()
            return
        if self._peek().type in _AGG_FNS:
            self._advance()
            self._expect("(", "'('")
            if self._check("*"):
                self._advance()
            else:
                self._column_ref()
            self._expect(")", "')'")
            return
        self._column_ref()

    def _column_ref(self):
        if self._check("ID", "CONFIDENCE"):
            return self._advance()
        self._error("expected a column name")

    def _findings_ref(self):
        first = self._expect("ID", "a findings table name")
        if self._check("."):
            self._advance()
            self._expect("ID", "a table name")
        return first


def parse(source: str) -> ast.Document:
    """Lexes and parses ``source`` into a :class:`ast.Document`."""
    return Parser(tokenize(source)).parse_document()
