#!/usr/bin/env python3
"""
Validate the PhiSQL v1.0 spec artifacts against each other and against the
canonical Phileas policy schema.

Five checks run, in order:

1. Catalog YAML files are well-formed and internally consistent.
2. Every Phileas field referenced by the catalogs exists in the canonical
   Phileas JSON schema. This is the load-bearing assertion that PhiSQL
   compiles to valid Phileas JSON for the redaction subset.
3. Every redaction-example JSON file under spec/v1.0/examples/ validates
   against the canonical Phileas schema. Examples are routed by their
   top-level `operation` field: a discovery operation skips this check,
   everything else validates as a Phileas redaction policy.
4. Discovery example JSON files are well-formed and reference column names
   that resolve against the findings catalog.
5. PhiSQL covers the schema: every identifier type, strategy, and top-level
   policy block in the schema is either exposed by PhiSQL or recorded as a
   deliberate deferral below. This is the reverse of check 2 — it stops the
   language from silently falling behind the schema when the schema grows.
6. PhiSQL covers every schema leaf field: descends into every policy-bearing
   object and asserts each individual property is expressible (via passthrough,
   a dedicated clause, or an explicit mechanism) or recorded as a deferral.

CI runs this script on every push and pull request. PRs that break the
relationship with the Phileas schema or the findings catalog fail here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA_VERSION = "1.1.0"

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "spec" / "v1.0"

# The canonical redaction policy schema is authored in this repository
# (schema/<version>/schema.json) and published to philterd.ai. Validate against the in-repo
# source of truth rather than the deployed copy.
SCHEMA_PATH = REPO_ROOT / "schema" / SCHEMA_VERSION / "schema.json"

# Discovery examples target a separate JSON shape (a discovery-query AST with
# a top-level `operation` field) and are validated by check_discovery_examples()
# rather than check_examples_validate(). The presence of an operation in this
# set is the routing signal; example filenames are not load-bearing.
DISCOVERY_OPERATIONS = {"FIND_PII", "DISCOVER_ENTITIES", "SCAN", "SELECT_FINDINGS"}

# --- Reverse-coverage accounting (check 5) -------------------------------------
#
# Check 2 proves PhiSQL never references a schema field that does not exist.
# Check 5 proves the opposite direction: every schema feature is either exposed
# by PhiSQL or listed here as a deliberate deferral. When the schema gains a new
# identifier, strategy, or top-level block, check 5 fails until PhiSQL either
# exposes it (catalog/grammar) or someone records the deferral below — so a gap
# is always a conscious choice, never a silent omission. The reasons are part of
# the contract; keep them accurate.

# Schema identifier properties PhiSQL exposes through a dedicated statement
# rather than an entity-types.yaml row.
IDENTIFIERS_EXPOSED_VIA_GRAMMAR = {
    "identifiers": "custom regex identifiers via `DEFINE IDENTIFIER ... MATCHING`",
    "dictionaries": "custom dictionary filters via `DEFINE DICTIONARY ... TERMS`",
    "sections": "section start/end filters via `DEFINE SECTION START ... END`",
    "pheyes": "AI/NER detection via `DETECT PHEYE`",
}

# Schema identifier properties intentionally not yet exposed by PhiSQL.
IDENTIFIERS_DEFERRED = {
    "person": "the schema marks `person` deprecated ('use pheyes instead'); it is a "
              "$ref to filterPhEye, the exact shape PhiSQL already exposes fully via "
              "DETECT PHEYE, so the capability is not lost — only the legacy JSON key",
}

# Strategy enum values intentionally not exposed. Empty: PhiSQL exposes them all.
STRATEGIES_DEFERRED: dict[str, str] = {}

# Top-level policy blocks PhiSQL exposes, and those it does not yet author.
TOPLEVEL_EXPOSED = {
    "crypto": "CONFIGURE CRYPTO KEY FROM ENV",
    "fpe": "CONFIGURE FPE KEY FROM ENV ... TWEAK FROM ENV",
    "identifiers": "entity statements, DEFINE IDENTIFIER/DICTIONARY/SECTION, DETECT PHEYE",
    "ignored": "IGNORE TERMS",
    "ignoredPatterns": "IGNORE PATTERN",
    "config": "CONFIGURE SPLITTING | PDF | POSTFILTERS | ANALYSIS ( ... )",
    "graphical": "CONFIGURE GRAPHICAL BOX ( ... )",
}
TOPLEVEL_DEFERRED: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Field-level coverage (check 6). Check 5 works at the granularity of types,
# strategies, and top-level blocks; this one descends to every individual leaf
# property of every policy-bearing object and asserts PhiSQL can set it.
#
# Filters, strategies, and config objects are reachable by a passthrough
# mechanism — OPTIONS (...), CONFIGURE <block> (...), or strategy args — and the
# setting value is recursive (scalars, nested objects, and arrays), so *every*
# property on them, however deeply nested, is expressible by name. Only objects
# with no passthrough entry point (crypto/fpe, set by dedicated CONFIGURE forms)
# need a field-by-field map.
# ---------------------------------------------------------------------------

# Objects whose every leaf — scalar, array, or nested object — is reachable by
# passthrough. (Entity filter $defs are added dynamically.) phEyeConfiguration is
# reachable as a nested value inside a PhEye/medical-condition filter's OPTIONS.
FIELD_PASSTHROUGH_CONTAINERS = {
    "filterCustomDictionary", "filterSection", "filterIdentifier", "filterPhEye",
    "baseFilterStrategy", "dateFilterStrategy",
    "splitting", "pdf", "postFilters", "analysis", "boundingBox",
    "ignored", "ignoredPattern", "phEyeConfiguration",
}

# Objects with no passthrough: every leaf must be listed here with its mechanism.
FIELD_EXPLICIT_CONTAINERS = {
    "crypto": {"key": "CONFIGURE CRYPTO KEY FROM ENV"},
    "fpe": {"key": "CONFIGURE FPE KEY FROM ENV", "tweak": "CONFIGURE FPE ... TWEAK FROM ENV"},
}

# Nested properties that cannot be expressed and are deliberately deferred.
# Empty: recursive OPTIONS/CONFIGURE settings reach every schema structure.
FIELD_DEFERRED: dict[tuple[str, str], str] = {}


def is_discovery_example(data: Any) -> bool:
    """A discovery example is any JSON whose top-level `operation` names a
    known discovery verb. Anything else (including malformed JSON missing the
    field entirely) is treated as a redaction example."""
    return isinstance(data, dict) and data.get("operation") in DISCOVERY_OPERATIONS


def load_schema() -> dict:
    """Load the canonical redaction policy schema from the in-repo source of truth."""
    with SCHEMA_PATH.open() as f:
        return json.load(f)


def load_yaml(path: Path) -> Any:
    with path.open() as f:
        return yaml.safe_load(f)


def check_catalog_well_formed() -> list[str]:
    """Each catalog file must parse and contain the expected top-level keys."""
    errors = []
    required = {
        "entity-types.yaml": ["version", "entities"],
        "strategies.yaml": ["version", "strategies"],
        "keywords.yaml": ["version", "keywords"],
        "predicates.yaml": ["version", "predicates"],
        "policy.yaml": ["version", "policy_name", "policy_declaration", "consistency_rule"],
        "findings.yaml": ["version", "table", "columns", "filterable_columns", "groupable_columns"],
        "sources.yaml": ["version", "schemes"],
        "validators.yaml": ["version", "validators"],
    }
    for name, keys in required.items():
        path = SPEC_DIR / "catalog" / name
        if not path.exists():
            errors.append(f"catalog/{name}: missing file")
            continue
        data = load_yaml(path)
        for key in keys:
            if key not in data:
                errors.append(f"catalog/{name}: missing top-level key '{key}'")
    return errors


def check_validators_match_schema(schema: dict) -> list[str]:
    """The validators.yaml catalog is the source of truth for the validator
    vocabulary; the schema's validatorName enum must list exactly the same names,
    in the same order, so the two cannot drift."""
    errors = []
    catalog = load_yaml(SPEC_DIR / "catalog" / "validators.yaml")
    catalog_names = [v["name"] for v in catalog.get("validators", [])]
    enum = schema.get("$defs", {}).get("validatorName", {}).get("enum", [])
    if catalog_names != enum:
        errors.append(
            "validators.yaml names do not match schema $defs.validatorName.enum "
            f"(catalog: {catalog_names}; schema: {enum})"
        )
    return errors


def check_catalog_references_phileas_schema(schema: dict) -> list[str]:
    """Every Phileas field referenced by the catalogs must exist in the schema."""
    errors = []
    defs = schema.get("$defs", {})
    identifier_props = defs.get("identifiers", {}).get("properties", {})

    # Entity types
    entities = load_yaml(SPEC_DIR / "catalog" / "entity-types.yaml")["entities"]
    for entry in entities:
        field = entry["phileas_field"]
        if field not in identifier_props:
            errors.append(
                f"entity-types.yaml: phileas_field '{field}' "
                f"(for entity {entry['name']}) not in Phileas identifiers schema"
            )
            continue
        # Resolve the $ref to the filter definition and verify the strategies
        # field name exists on it.
        ref = identifier_props[field].get("$ref")
        if not ref or not ref.startswith("#/$defs/"):
            continue
        filter_def_name = ref.split("/")[-1]
        filter_def = defs.get(filter_def_name, {})
        filter_props = filter_def.get("properties", {})
        strategies_field = entry["phileas_strategies_field"]
        if strategies_field not in filter_props:
            errors.append(
                f"entity-types.yaml: phileas_strategies_field "
                f"'{strategies_field}' (for entity {entry['name']}) not on "
                f"{filter_def_name}"
            )

    # Strategies. Each strategy is validated against its declared Phileas
    # strategy $def (baseFilterStrategy by default; date-only strategies such as
    # SHIFT declare dateFilterStrategy, which extends the base strategy).
    strategies = load_yaml(SPEC_DIR / "catalog" / "strategies.yaml")["strategies"]
    for entry in strategies:
        def_name = entry.get("phileas_strategy_def", "baseFilterStrategy")
        strategy_def = defs.get(def_name, {}).get("properties", {})
        if not strategy_def:
            errors.append(
                f"strategies.yaml: phileas_strategy_def '{def_name}' "
                f"(for strategy {entry['name']}) not found in Phileas schema"
            )
            continue
        strategy_enum = strategy_def.get("strategy", {}).get("enum", [])
        if entry["phileas_enum"] not in strategy_enum:
            errors.append(
                f"strategies.yaml: phileas_enum '{entry['phileas_enum']}' "
                f"(for strategy {entry['name']}) not in {def_name}.strategy enum"
            )
        for arg in entry.get("args") or []:
            field = arg["phileas_field"]
            if field not in strategy_def:
                errors.append(
                    f"strategies.yaml: arg phileas_field '{field}' "
                    f"(for strategy {entry['name']}, arg {arg['name']}) "
                    f"not on {def_name}"
                )
                continue
            # Type compatibility: the catalog arg's declared type must be representable
            # by the schema property's type, so catalog/schema type drift (issue #13,
            # maskLength: catalog integer vs schema string) cannot recur silently.
            arg_type = arg.get("type")
            schema_type = strategy_def[field].get("type")
            if arg_type and schema_type is not None and not _arg_type_compatible(arg_type, schema_type):
                schema_types = set(schema_type) if isinstance(schema_type, list) else {schema_type}
                errors.append(
                    f"strategies.yaml: arg '{arg['name']}' (strategy {entry['name']}) "
                    f"declares type '{arg_type}' but the schema types "
                    f"{def_name}.{field} as {sorted(schema_types)}"
                )

    return errors


# How a catalog arg `type:` maps onto the JSON Schema `type` of the Phileas field it
# sets. An arg is compatible when the schema admits at least one of these. Unknown arg
# types (empty set) are treated as compatible so a new arg kind does not hard-fail the
# build before this table is taught about it.
_ARG_TYPE_TO_SCHEMA_TYPES = {
    "string": {"string"},
    "integer": {"integer", "number"},
    "boolean": {"boolean"},
    "enum": {"string"},
}


def _arg_type_compatible(arg_type: str, schema_type: Any) -> bool:
    """True if a catalog arg of `arg_type` can set a schema field of `schema_type`.

    `schema_type` is a JSON Schema type: a string, or a list of strings for a union
    (e.g. maskLength's ["string", "integer"] after issue #13).
    """
    schema_types = set(schema_type) if isinstance(schema_type, list) else {schema_type}
    acceptable = _ARG_TYPE_TO_SCHEMA_TYPES.get(arg_type, set())
    if not acceptable:
        return True
    return bool(acceptable & schema_types)


def _schema_strategy_enums(schema: dict) -> set[str]:
    """Union of the `strategy` enum across every *FilterStrategy $def."""
    values: set[str] = set()
    for definition in schema.get("$defs", {}).values():
        enum = definition.get("properties", {}).get("strategy", {}).get("enum")
        if enum:
            values.update(enum)
    return values


def _coverage_errors(kind: str, in_schema: set[str], accounted: set[str]) -> list[str]:
    """Bidirectional diff between what the schema has and what PhiSQL accounts
    for. Missing = schema has it, PhiSQL neither exposes nor defers it. Stale =
    PhiSQL accounts for something the schema no longer has."""
    errors = []
    for name in sorted(in_schema - accounted):
        errors.append(
            f"{kind} '{name}': present in the schema but neither exposed by "
            f"PhiSQL nor listed as deferred in validate_spec.py"
        )
    for name in sorted(accounted - in_schema):
        errors.append(
            f"{kind} '{name}': accounted for in validate_spec.py but no longer "
            f"present in the schema — remove the stale entry"
        )
    return errors


def check_phisql_covers_schema(schema: dict) -> list[str]:
    """Every schema identifier, strategy, and top-level block must be exposed by
    PhiSQL or recorded as a deliberate deferral. The reverse of check 2."""
    defs = schema.get("$defs", {})

    # Identifiers: catalog entity rows + statement-exposed + deferred.
    schema_idents = set(defs.get("identifiers", {}).get("properties", {}).keys())
    catalog_fields = {
        e["phileas_field"]
        for e in load_yaml(SPEC_DIR / "catalog" / "entity-types.yaml")["entities"]
    }
    accounted_idents = (
        catalog_fields
        | set(IDENTIFIERS_EXPOSED_VIA_GRAMMAR)
        | set(IDENTIFIERS_DEFERRED)
    )

    # Strategies: catalog enum values + deferred. The catalog cannot reference a
    # strategy the schema lacks (check 2), so only the missing direction matters
    # here, but _coverage_errors flags stale deferrals too.
    schema_strats = _schema_strategy_enums(schema)
    catalog_strats = {
        s["phileas_enum"]
        for s in load_yaml(SPEC_DIR / "catalog" / "strategies.yaml")["strategies"]
    }
    accounted_strats = catalog_strats | set(STRATEGIES_DEFERRED)

    # Top-level policy blocks: exposed + deferred.
    schema_top = set(schema.get("properties", {}).keys())
    accounted_top = set(TOPLEVEL_EXPOSED) | set(TOPLEVEL_DEFERRED)

    return (
        _coverage_errors("identifier", schema_idents, accounted_idents)
        + _coverage_errors("strategy", schema_strats, accounted_strats)
        + _coverage_errors("top-level block", schema_top, accounted_top)
    )


def _resolve(schema: dict, node: dict) -> dict:
    """Resolve a one-level $ref against $defs; otherwise return the node."""
    if "$ref" in node:
        return schema.get("$defs", {}).get(node["$ref"].split("/")[-1], {})
    return node


def _leaf_fields(schema: dict, defname: str) -> dict[str, dict]:
    """All properties of a $def, merging any allOf base (abstractFilterProperties)."""
    node = schema.get("$defs", {}).get(defname, {})
    props = dict(node.get("properties", {}))
    for sub in node.get("allOf", []):
        if "$ref" in sub:
            props.update(_resolve(schema, sub).get("properties", {}))
    return props


def check_phisql_covers_schema_fields(schema: dict) -> tuple[list[str], dict[str, str]]:
    """Every leaf property of every policy-bearing object must be expressible by
    PhiSQL (via passthrough, a dedicated clause, or an explicit mechanism) or
    listed as a deliberate deferral. Returns (errors, deferred-report)."""
    defs = schema.get("$defs", {})
    idents = defs.get("identifiers", {}).get("properties", {})
    special = {"identifiers", "dictionaries", "sections", "pheyes", "person"}

    # Entity filter $defs (e.g. filterSsn) and the set of "strategies array"
    # fields, both derived from the catalog so they cannot drift.
    entity_defs = {
        idents[name]["$ref"].split("/")[-1]
        for name, node in idents.items()
        if name not in special and "$ref" in node
    }
    passthrough = FIELD_PASSTHROUGH_CONTAINERS | entity_defs
    containers = sorted(
        passthrough | set(FIELD_EXPLICIT_CONTAINERS) | {c for c, _ in FIELD_DEFERRED}
    )

    errors: list[str] = []
    deferred_report: dict[str, str] = {}
    seen_deferred: set[tuple[str, str]] = set()

    for container in containers:
        fields = _leaf_fields(schema, container)
        if not fields and container not in defs:
            errors.append(f"container '{container}': not found in schema $defs (stale registry entry)")
            continue
        for field in fields:
            key = (container, field)
            if key in FIELD_DEFERRED:
                deferred_report[f"{container}.{field}"] = FIELD_DEFERRED[key]
                seen_deferred.add(key)
            elif container in FIELD_EXPLICIT_CONTAINERS:
                # No passthrough entry point: every leaf must be mapped.
                if field not in FIELD_EXPLICIT_CONTAINERS[container]:
                    errors.append(
                        f"{container}.{field}: object exposed field-by-field but this "
                        f"leaf is neither mapped nor deferred in validate_spec.py"
                    )
            # else: passthrough container — recursive OPTIONS/CONFIGURE settings
            # (or WITH <strategy> for the strategy arrays) reach every leaf.

    # Flag stale explicit-field mappings the schema no longer has.
    for container, fmap in FIELD_EXPLICIT_CONTAINERS.items():
        schema_fields = set(_leaf_fields(schema, container))
        for field in fmap:
            if field not in schema_fields:
                errors.append(
                    f"{container}.{field}: mapped in validate_spec.py but not present in "
                    f"the schema — remove the stale entry"
                )

    # Flag stale deferrals (registry entries the schema no longer has).
    for key in FIELD_DEFERRED:
        if key not in seen_deferred:
            container, field = key
            errors.append(
                f"{container}.{field}: deferred in validate_spec.py but not present in "
                f"the schema — remove the stale entry"
            )

    return errors, deferred_report


def check_examples_validate(schema: dict) -> list[str]:
    """Redaction example JSONs must validate against the Phileas schema."""
    errors = []
    validator = Draft202012Validator(schema)
    examples_dir = SPEC_DIR / "examples"
    for path in sorted(examples_dir.glob("*.json")):
        data = json.loads(path.read_text())
        if is_discovery_example(data):
            continue
        problems = sorted(validator.iter_errors(data), key=lambda e: e.path)
        for problem in problems[:5]:
            location = "/".join(str(p) for p in problem.absolute_path) or "(root)"
            errors.append(f"examples/{path.name}: {location}  {problem.message}")
    return errors


def check_discovery_examples() -> list[str]:
    """Discovery example JSONs must be well-formed and reference real columns.

    The findings catalog declares the canonical column set. Every column name
    that appears in a projection, predicate, or group_by must resolve against
    that set; an unknown column is a discovery-compiler bug.
    """
    errors = []
    findings = load_yaml(SPEC_DIR / "catalog" / "findings.yaml")
    known_columns = {col["name"] for col in findings["columns"]}

    examples_dir = SPEC_DIR / "examples"
    for path in sorted(examples_dir.glob("*.json")):
        data = json.loads(path.read_text())
        if not is_discovery_example(data):
            continue
        for col in _columns_referenced(data):
            if col not in known_columns and col != "*":
                errors.append(
                    f"examples/{path.name}: column '{col}' not defined in findings.yaml"
                )
    return errors


def _columns_referenced(node: Any) -> list[str]:
    """Walk a discovery-query JSON node and return every column name it touches."""
    out: list[str] = []
    if isinstance(node, dict):
        if node.get("type") == "column" and "name" in node:
            out.append(node["name"])
        if node.get("type") == "aggregate" and "argument" in node:
            out.append(node["argument"])
        if "column" in node and isinstance(node["column"], str):
            out.append(node["column"])
        for key in ("projection", "group_by"):
            if key in node:
                out.extend(_columns_referenced(node[key]))
        for key in ("where", "left", "right"):
            if key in node:
                out.extend(_columns_referenced(node[key]))
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, str):
                out.append(item)
            else:
                out.extend(_columns_referenced(item))
    return out


def section(title: str) -> None:
    print(title)
    print("-" * len(title))


def main() -> int:
    schema = load_schema()
    all_errors: list[tuple[str, list[str]]] = []

    section("1. Catalog YAML well-formedness")
    errors = check_catalog_well_formed()
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("catalog", errors))
    print()

    if not errors:
        section("2. Catalog references resolve in Phileas schema")
        errors = check_catalog_references_phileas_schema(schema)
        print("PASS" if not errors else f"FAIL ({len(errors)})")
        all_errors.append(("references", errors))
        print()

    section("3. Redaction examples validate against Phileas schema")
    errors = check_examples_validate(schema)
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("examples", errors))
    print()

    section("4. Discovery examples reference known findings columns")
    errors = check_discovery_examples()
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("discovery", errors))
    print()

    section("5. PhiSQL covers the schema (no silent drift)")
    errors = check_phisql_covers_schema(schema)
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("coverage", errors))
    if not errors:
        deferred = {
            **IDENTIFIERS_DEFERRED,
            **STRATEGIES_DEFERRED,
            **TOPLEVEL_DEFERRED,
        }
        if deferred:
            print(f"  ({len(deferred)} schema features intentionally deferred:)")
            for name, reason in sorted(deferred.items()):
                print(f"    - {name}: {reason}")
    print()

    section("6. PhiSQL covers every schema leaf field")
    errors, field_deferred = check_phisql_covers_schema_fields(schema)
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("field-coverage", errors))
    if not errors and field_deferred:
        print(f"  ({len(field_deferred)} nested-object fields intentionally deferred:)")
        for name, reason in sorted(field_deferred.items()):
            print(f"    - {name}: {reason}")
    print()

    section("7. Validator catalog matches schema enum")
    errors = check_validators_match_schema(schema)
    print("PASS" if not errors else f"FAIL ({len(errors)})")
    all_errors.append(("validators", errors))
    print()

    has_errors = any(errors for _, errors in all_errors)
    if has_errors:
        section("Errors")
        for stage, errors in all_errors:
            for err in errors:
                print(f"  [{stage}] {err}")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
