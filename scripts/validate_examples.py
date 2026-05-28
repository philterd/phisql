#!/usr/bin/env python3
"""
Validate every example JSON file under spec/v0.1/examples/ against the
canonical Phileas policy schema fetched from philterd/phileas.

This is the load-bearing assertion that the PhiSQL spec compiles to valid
Phileas JSON. CI runs this on every push; PRs that break the relationship
with the Phileas schema fail here.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_URL = (
    "https://raw.githubusercontent.com/philterd/phileas/main/"
    "policy-schema/redaction-policy-schema.json"
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def fetch_schema() -> dict:
    cached = REPO_ROOT / ".cache" / "phileas-schema.json"
    if cached.exists():
        return json.loads(cached.read_text())
    with urllib.request.urlopen(SCHEMA_URL) as response:
        return json.loads(response.read())


def main() -> int:
    schema = fetch_schema()
    validator = Draft202012Validator(schema)

    examples_dir = REPO_ROOT / "spec" / "v0.1" / "examples"
    files = sorted(examples_dir.glob("*.json"))

    all_valid = True
    for path in files:
        data = json.loads(path.read_text())
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if not errors:
            print(f"PASS  {path.name}")
        else:
            all_valid = False
            print(f"FAIL  {path.name}")
            for error in errors[:5]:
                location = "/".join(str(p) for p in error.absolute_path) or "(root)"
                print(f"        {location}  {error.message}")

    print()
    print("All examples valid." if all_valid else "Validation failed.")
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
