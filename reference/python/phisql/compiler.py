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
Compiles a parsed PhiSQL document into a Phileas JSON policy.

The compiler is driven by :class:`~phisql.catalog.Catalog`, which loads the
``spec/v1.0/catalog/*.yaml`` files. Translation rules are defined by those
files; this module implements the traversal — a direct port of the Java
reference ``Compiler``.

**Scope.** This compiler targets the redaction subset of PhiSQL (REDACT,
DEIDENTIFY, IGNORE, DEFINE IDENTIFIER, DEFINE DICTIONARY, DEFINE SECTION,
DETECT PHEYE, and the CONFIGURE forms) and emits Phileas JSON. Discovery
statements (FIND PII, DISCOVER ENTITIES, SCAN, SELECT FROM findings) parse
successfully but are silently ignored by this compiler; they target a separate
discovery-query JSON schema.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Optional

from . import ast
from .catalog import Catalog
from .errors import CompileException
from .phisql import parse

# Allowed values for the dictionary FUZZY SENSITIVITY clause.
_SENSITIVITY_LEVELS = frozenset({"auto", "off", "low", "medium", "high"})

# CONFIGURE config-block keyword -> Phileas `config` sub-object name.
_CONFIG_BLOCKS = {
    "SPLITTING": "splitting",
    "PDF": "pdf",
    "POSTFILTERS": "postFilters",
    "ANALYSIS": "analysis",
}


class CompileResult:
    """Result of compiling a PhiSQL document.

    ``policy_name`` is the name from the ``POLICY`` declaration (or the
    filename basename), which callers should use as the output filename
    (``<name>.json``). ``description`` is the ``DESCRIPTION '...'`` text, which
    the spec places in a sibling ``<name>.md`` file. ``policy_json`` is the
    compiled Phileas JSON policy as a Python ``dict``.
    """

    def __init__(self, policy_name, description, policy_json):
        self._policy_name = policy_name
        self._description = description
        self._policy_json = policy_json

    def policy_name(self) -> Optional[str]:
        return self._policy_name

    def description(self) -> Optional[str]:
        return self._description

    def policy_json(self) -> dict:
        return self._policy_json

    def to_json_string(self) -> str:
        """Returns the policy JSON as a pretty-printed string."""
        return json.dumps(self._policy_json, indent=2, ensure_ascii=False)


class Compiler:
    def __init__(self, catalog: Optional[Catalog] = None):
        self._catalog = catalog if catalog is not None else Catalog.load_default()

    # --- Public entry points -------------------------------------------------

    def compile(self, source: str, expected_name: Optional[str] = None) -> CompileResult:
        """Compiles PhiSQL from a string.

        The policy name comes from the ``POLICY`` declaration if present, or
        from ``expected_name`` when supplied; if both are present they must
        match after hyphen/underscore normalization.
        """
        return self.compile_document(parse(source), expected_name)

    def compile_file(self, file) -> CompileResult:
        """Compiles PhiSQL from a file.

        The policy name is the file's basename (with the extension stripped).
        A ``POLICY`` declaration, if present, must match the basename after
        normalization (hyphens and underscores are equivalent).
        """
        path = Path(file)
        source = path.read_text(encoding="utf-8")
        return self.compile_document(parse(source), _basename_without_extension(path))

    def compile_document(self, document: ast.Document,
                         expected_name: Optional[str] = None) -> CompileResult:
        policy_json = {}
        identifiers = {}
        policy_json["identifiers"] = identifiers

        declared_name = None
        description = None

        for stmt in document.statements:
            if isinstance(stmt, ast.PolicyDecl):
                declared_name = stmt.policy_name
                if stmt.description_raw is not None:
                    description = _unquote_string(stmt.description_raw)
            elif isinstance(stmt, ast.RedactStmt):
                self._compile_redact(stmt, identifiers)
            elif isinstance(stmt, ast.DeidentifyStmt):
                self._compile_deidentify(stmt, identifiers)
            elif isinstance(stmt, ast.IgnoreStmt):
                self._compile_ignore(stmt, identifiers, policy_json)
            elif isinstance(stmt, ast.DefineIdentifierStmt):
                self._compile_define_identifier(stmt, identifiers)
            elif isinstance(stmt, ast.DefineDictionaryStmt):
                self._compile_define_dictionary(stmt, identifiers)
            elif isinstance(stmt, ast.DefineSectionStmt):
                self._compile_define_section(stmt, identifiers)
            elif isinstance(stmt, ast.DetectStmt):
                self._compile_detect(stmt, identifiers)
            elif isinstance(stmt, ast.ConfigureStmt):
                self._compile_configure(stmt, policy_json)
            elif isinstance(stmt, ast.DiscoveryStmt):
                pass  # discovery statements are not compiled to Phileas JSON

        policy_name = _resolve_policy_name(expected_name, declared_name)
        return CompileResult(policy_name, description, policy_json)

    # --- CONFIGURE -----------------------------------------------------------

    def _compile_configure(self, ctx: ast.ConfigureStmt, policy_json: dict):
        if ctx.crypto_key_env_raw is not None:
            policy_json["crypto"] = {"key": "env:" + _unquote_string(ctx.crypto_key_env_raw)}
        elif ctx.fpe_key_env_raw is not None:
            policy_json["fpe"] = {
                "key": "env:" + _unquote_string(ctx.fpe_key_env_raw),
                "tweak": "env:" + _unquote_string(ctx.fpe_tweak_env_raw),
            }
        elif ctx.config_block is not None:
            block = _CONFIG_BLOCKS[ctx.config_block]
            config = _get_or_create_object(policy_json, "config")
            self._apply_settings(_get_or_create_object(config, block), ctx.settings)
        else:
            # GRAPHICAL BOX ( ... ) — append a fixed bounding box.
            graphical = _get_or_create_object(policy_json, "graphical")
            boxes = _get_or_create_array(graphical, "boundingBoxes")
            box = {}
            boxes.append(box)
            self._apply_settings(box, ctx.settings)

    # --- OPTIONS / settings --------------------------------------------------

    def _apply_options(self, target: dict, options):
        """Applies an OPTIONS setting list to ``target``; no-op when None."""
        if options is not None:
            self._apply_settings(target, options)

    def _apply_settings(self, target: dict, settings):
        for s in settings:
            _set_or_merge(target, _setting_key_text(s.key), self._build_value(s.value))

    def _build_value(self, value: ast.SettingValue):
        """Builds the JSON value for a setting: scalar, nested object, or array."""
        if value.object_settings is not None:
            obj = {}
            self._apply_settings(obj, value.object_settings)
            return obj
        if value.array_elements is not None:
            return [self._build_value(el) for el in value.array_elements]
        literal = value.literal
        if literal.kind == "BOOLEAN":
            return literal.text.lower() == "true"
        if literal.kind == "NUMERIC":
            text = literal.text
            return float(text) if "." in text else int(text)
        if literal.kind == "STRING":
            return _unquote_string(literal.text)
        # Bare identifier — treated as a string value.
        return literal.text

    # --- REDACT --------------------------------------------------------------

    def _compile_redact(self, ctx: ast.RedactStmt, identifiers: dict):
        strategy_json = None
        if ctx.strategy is not None:
            strategy_json = self._build_strategy_object(ctx.strategy)
            if ctx.predicate is not None:
                strategy_json["conditions"] = self._compile_predicate(ctx.predicate)
        for entity in ctx.entities:
            if strategy_json is not None:
                self._append_strategy(identifiers, entity, copy.deepcopy(strategy_json))
            if ctx.options is not None:
                self._apply_options(self._resolve_filter_node(identifiers, entity), ctx.options)

    # --- DEIDENTIFY ----------------------------------------------------------

    def _compile_deidentify(self, ctx: ast.DeidentifyStmt, identifiers: dict):
        for assignment in ctx.assignments:
            strategy_json = self._build_strategy_object(assignment.strategy)
            self._append_strategy(identifiers, assignment.entity, strategy_json)
            if assignment.options is not None:
                self._apply_options(
                    self._resolve_filter_node(identifiers, assignment.entity),
                    assignment.options)

    # --- IGNORE --------------------------------------------------------------

    def _compile_ignore(self, ctx: ast.IgnoreStmt, identifiers: dict, policy_json: dict):
        is_terms = ctx.kind == "TERMS"
        scoped = ctx.entities is not None

        if scoped and ctx.options is not None:
            raise CompileException(
                "OPTIONS is not supported on a scoped IGNORE ... FOR; set per-filter "
                "options on the entity's REDACT/DEIDENTIFY statement instead.")

        if is_terms:
            terms = [_unquote_string(t) for t in ctx.terms]
            if scoped:
                for entity in ctx.entities:
                    entity_node = self._get_or_create_entity_node(identifiers, entity)
                    ignored = _get_or_create_array(entity_node, "ignored")
                    ignored.extend(terms)
            else:
                # Scope-less IGNORE TERMS compiles to the top-level `ignored`
                # array of named term-list objects.
                top_level = _get_or_create_array(policy_json, "ignored")
                terms_object = {}
                top_level.append(terms_object)
                terms_object["terms"] = list(terms)
                self._apply_options(terms_object, ctx.options)
            return

        # PATTERN
        pattern = _unquote_string(ctx.pattern_raw)
        if scoped:
            for entity in ctx.entities:
                entity_node = self._get_or_create_entity_node(identifiers, entity)
                ignored_patterns = _get_or_create_array(entity_node, "ignoredPatterns")
                ignored_patterns.append({"pattern": pattern})
        else:
            top_level = _get_or_create_array(policy_json, "ignoredPatterns")
            pattern_object = {"pattern": pattern}
            top_level.append(pattern_object)
            self._apply_options(pattern_object, ctx.options)

    # --- DEFINE IDENTIFIER ---------------------------------------------------

    def _compile_define_identifier(self, ctx: ast.DefineIdentifierStmt, identifiers: dict):
        classification = _unquote_string(ctx.classification_raw)
        pattern = _unquote_string(ctx.pattern_raw)

        strategy_json = self._build_strategy_object(ctx.strategy)
        if ctx.predicate is not None:
            strategy_json["conditions"] = self._compile_predicate(ctx.predicate)

        identifier_list = _get_or_create_array(identifiers, "identifiers")
        entry = _find_by_classification(identifier_list, classification)
        if entry is None:
            entry = {"classification": classification}
            identifier_list.append(entry)
        entry["pattern"] = pattern
        if ctx.group_number is not None:
            entry["groupNumber"] = int(ctx.group_number)
        if ctx.sensitivity is not None:
            entry["caseSensitive"] = ctx.sensitivity == "SENSITIVE"

        strategies = _get_or_create_array(entry, "identifierFilterStrategies")
        strategies.append(strategy_json)
        self._apply_options(entry, ctx.options)

    # --- DEFINE DICTIONARY ---------------------------------------------------

    def _compile_define_dictionary(self, ctx: ast.DefineDictionaryStmt, identifiers: dict):
        dictionaries = _get_or_create_array(identifiers, "dictionaries")
        entry = {"classification": _unquote_string(ctx.classification_raw)}
        dictionaries.append(entry)

        entry["terms"] = [_unquote_string(t) for t in ctx.terms]

        if ctx.fuzzy:
            entry["fuzzy"] = True
            if ctx.sensitivity is not None:
                level = ctx.sensitivity.lower()
                if level not in _SENSITIVITY_LEVELS:
                    raise CompileException(
                        "SENSITIVITY must be one of "
                        f"{sorted(_SENSITIVITY_LEVELS)}; got '{level}'")
                entry["sensitivity"] = level
        if ctx.capitalized:
            entry["capitalized"] = True

        entry["customFilterStrategies"] = [self._build_strategy_object(ctx.strategy)]
        self._apply_options(entry, ctx.options)

    # --- DEFINE SECTION ------------------------------------------------------

    def _compile_define_section(self, ctx: ast.DefineSectionStmt, identifiers: dict):
        sections = _get_or_create_array(identifiers, "sections")
        entry = {
            "startPattern": _unquote_string(ctx.start_raw),
            "endPattern": _unquote_string(ctx.end_raw),
            "sectionFilterStrategies": [self._build_strategy_object(ctx.strategy)],
        }
        sections.append(entry)
        self._apply_options(entry, ctx.options)

    # --- DETECT PHEYE --------------------------------------------------------

    def _compile_detect(self, ctx: ast.DetectStmt, identifiers: dict):
        strategy_json = self._build_strategy_object(ctx.strategy)
        if ctx.predicate is not None:
            strategy_json["conditions"] = self._compile_predicate(ctx.predicate)

        pheyes = _get_or_create_array(identifiers, "pheyes")
        pheye = {"phEyeFilterStrategies": [strategy_json]}
        pheyes.append(pheye)

        has_labels = ctx.labels is not None
        has_endpoint = ctx.endpoint_raw is not None
        has_model = ctx.model_raw is not None
        if has_labels or has_endpoint or has_model:
            config = {}
            pheye["phEyeConfiguration"] = config
            if has_endpoint:
                config["endpoint"] = _unquote_string(ctx.endpoint_raw)
            if has_labels:
                config["labels"] = [_unquote_string(t) for t in ctx.labels]
            if has_model:
                config["modelPath"] = _unquote_string(ctx.model_raw)
        self._apply_options(pheye, ctx.options)

    # --- Strategy translation ------------------------------------------------

    def _build_strategy_object(self, ctx: ast.StrategyExpr) -> dict:
        strategy = self._catalog.get_strategy(ctx.name)
        if strategy is None:
            raise CompileException("Unknown strategy: " + ctx.name)

        out = {"strategy": strategy.phileas_enum}

        for arg in ctx.args:
            cat_arg = strategy.find_arg(arg.arg_name)
            if cat_arg is not None and arg.value.literal is not None:
                # Catalogued argument with a scalar value: validate and map it
                # (handles aliases like days -> shiftDays and enum checks).
                self._place_arg_value(out, cat_arg, arg.value.literal)
            else:
                # Any other strategy property passes through by its schema name.
                _set_or_merge(out, arg.arg_name, self._build_value(arg.value))
        return out

    def _place_arg_value(self, strategy_obj: dict, arg, literal: ast.Literal):
        text = literal.text
        arg_type = arg.type or "string"

        if arg_type == "string":
            strategy_obj[arg.phileas_field] = _parse_string_literal(text)
        elif arg_type == "integer":
            strategy_obj[arg.phileas_field] = int(text)
        elif arg_type == "boolean":
            strategy_obj[arg.phileas_field] = text.lower() == "true"
        elif arg_type == "enum":
            value = _strip_quotes_if_present(text).upper()
            if value not in arg.enum_values:
                raise CompileException(
                    f"Argument '{arg.name}' must be one of "
                    f"{list(arg.enum_values)}; got '{value}'")
            strategy_obj[arg.phileas_field] = value
        else:
            raise CompileException("Unsupported argument type: " + arg_type)

    # --- Entity placement ----------------------------------------------------

    def _append_strategy(self, identifiers: dict, entity, strategy_obj: dict):
        if isinstance(entity, ast.SimpleEntityType):
            entity_type = self._catalog.get_entity(entity.name)
            if entity_type is None:
                raise CompileException("Unknown entity type: " + entity.name)
            entity_node = _get_or_create_object(identifiers, entity_type.phileas_field)
            strategies = _get_or_create_array(entity_node,
                                              entity_type.phileas_strategies_field)
            strategies.append(strategy_obj)
            return
        if isinstance(entity, ast.CustomIdentifier):
            classification = _unquote_string(entity.classification_raw)
            identifier_list = _get_or_create_array(identifiers, "identifiers")
            entry = _find_by_classification(identifier_list, classification)
            if entry is None:
                entry = {"classification": classification}
                identifier_list.append(entry)
            strategies = _get_or_create_array(entry, "identifierFilterStrategies")
            strategies.append(strategy_obj)
            return
        raise CompileException("Unsupported entity type form")

    def _resolve_filter_node(self, identifiers: dict, entity) -> dict:
        if isinstance(entity, ast.SimpleEntityType):
            entity_type = self._catalog.get_entity(entity.name)
            if entity_type is None:
                raise CompileException("Unknown entity type: " + entity.name)
            return _get_or_create_object(identifiers, entity_type.phileas_field)
        if isinstance(entity, ast.CustomIdentifier):
            classification = _unquote_string(entity.classification_raw)
            identifier_list = _get_or_create_array(identifiers, "identifiers")
            entry = _find_by_classification(identifier_list, classification)
            if entry is None:
                entry = {"classification": classification}
                identifier_list.append(entry)
            return entry
        raise CompileException("Unsupported entity type form")

    def _get_or_create_entity_node(self, identifiers: dict, entity) -> dict:
        if isinstance(entity, ast.SimpleEntityType):
            entity_type = self._catalog.get_entity(entity.name)
            if entity_type is None:
                raise CompileException("Unknown entity type: " + entity.name)
            return _get_or_create_object(identifiers, entity_type.phileas_field)
        raise CompileException(
            "IGNORE clauses scoped to custom identifiers are not supported in v1.0.")

    # --- Predicate translation -----------------------------------------------

    def _compile_predicate(self, ctx) -> str:
        if isinstance(ctx, ast.ConfidencePredicate):
            return f"confidence {ctx.op} {ctx.number}"
        if isinstance(ctx, ast.ParenPredicate):
            return "( " + self._compile_predicate(ctx.inner) + " )"
        if isinstance(ctx, ast.LogicalPredicate):
            op = "and" if ctx.op == "AND" else "or"
            return (self._compile_predicate(ctx.left) + " " + op + " "
                    + self._compile_predicate(ctx.right))
        raise CompileException("Unsupported predicate form")


# --- Module-level helpers ----------------------------------------------------


def _get_or_create_object(parent: dict, field: str) -> dict:
    existing = parent.get(field)
    if isinstance(existing, dict):
        return existing
    obj = {}
    parent[field] = obj
    return obj


def _get_or_create_array(parent: dict, field: str) -> list:
    existing = parent.get(field)
    if isinstance(existing, list):
        return existing
    arr = []
    parent[field] = arr
    return arr


def _find_by_classification(entries: list, classification: str):
    for candidate in entries:
        if candidate.get("classification") == classification:
            return candidate
    return None


def _set_or_merge(target: dict, key: str, value):
    """Sets key=value, merging into an existing object value."""
    existing = target.get(key)
    if isinstance(value, dict) and isinstance(existing, dict):
        existing.update(value)
    else:
        target[key] = value


def _setting_key_text(key: ast.SettingKey) -> str:
    return key.text if key.kind == "ID" else _unquote_string(key.text)


def _resolve_policy_name(expected: Optional[str], declared: Optional[str]) -> Optional[str]:
    if expected is not None and declared is not None:
        if _normalize_policy_name(expected) != _normalize_policy_name(declared):
            raise CompileException(
                f"POLICY declaration name '{declared}' does not match the expected "
                f"name '{expected}'. Either omit the POLICY statement or change it "
                "to match.")
        return expected
    if expected is not None:
        return expected
    return declared


def _normalize_policy_name(name: str) -> str:
    return name.replace("-", "_")


def _basename_without_extension(path: Path) -> str:
    name = path.name
    dot = name.rfind(".")
    return name[:dot] if dot > 0 else name


def _unquote_string(text: str) -> str:
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        inner = text[1:-1]
        return inner.replace("\\'", "'").replace("\\n", "\n").replace("\\\\", "\\")
    return text


def _parse_string_literal(text: str) -> str:
    if len(text) >= 2 and text.startswith("'") and text.endswith("'"):
        return _unquote_string(text)
    return text


def _strip_quotes_if_present(text: str) -> str:
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1]
    return text
