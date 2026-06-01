#!/usr/bin/env python3
"""
Validate the PhiSQL v1.0 spec artifacts against each other and against the
canonical Phileas policy schema.

Four checks run, in order:

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

SCHEMA_VERSION = "1.0.0"

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

    return errors


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
