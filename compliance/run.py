#!/usr/bin/env python3
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
PhiSQL conformance test runner.

This runner is implementation-neutral. It drives an *adapter* command that
wraps the implementation under test, and judges the implementation purely by
what that command writes to stdout and the exit code it returns. Nothing here
is specific to the Java reference implementation; pointing --adapter at any
conforming command tests that implementation instead.

The adapter contract
--------------------
The adapter is invoked as:

    <adapter> <path-to-.phisql-file>

and MUST:

  * on success, write the compiled Phileas JSON policy to stdout and exit 0;
  * on a parse/grammar error, exit 2;
  * on a semantic/catalog error (parsed, but not a valid policy), exit 3.

The two distinct reject codes let the suite assert that an invalid input is
rejected at the correct layer, not merely that it is rejected.

How a case is classified (by its location under cases/)
-------------------------------------------------------
  accept/...          compile must succeed (exit 0) and the produced JSON must
                      equal the sibling <name>.json (compared as parsed JSON,
                      so key order and formatting are ignored).
  parse-only/...      must be accepted (exit 0); output is not compared. Used
                      for statements the reference compiler parses but does not
                      yet translate (the discovery verbs).
  reject/parse/...    must fail to parse (exit 2).
  reject/semantic/... must parse but fail to compile (exit 3).

An optional sibling <name>.reject (JSON: {"messageContains": "..."}) adds an
assertion that the adapter's stderr contains a substring.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ADAPTER = HERE / "adapters" / "reference.sh"
DEFAULT_CASES = HERE / "cases"

EXIT_OK = 0
EXIT_PARSE = 2
EXIT_SEMANTIC = 3

# The canonical redaction policy schema. Accept-case output must validate
# against it, not merely match the expected fixture, so a schema-invalid fixture
# (or a compiler emitting malformed policy JSON) is caught rather than passing by
# faithful reproduction. jsonschema is listed in scripts/requirements.txt; if it
# is not installed the schema checks are skipped so the runner still drives any
# adapter.
REPO_ROOT = HERE.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "1.0.0" / "schema.json"
try:
    from jsonschema import Draft202012Validator as _Draft202012Validator
    _SCHEMA_VALIDATOR = _Draft202012Validator(
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
except ImportError:
    _SCHEMA_VALIDATOR = None

# ANSI colors, disabled when stdout is not a TTY or NO_COLOR is set.
if sys.stdout.isatty() and not os.environ.get("NO_COLOR"):
    GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
else:
    GREEN = RED = YELLOW = DIM = RESET = ""


class Case:
    def __init__(self, phisql_path, kind, expected_exit, expected_json,
                 message_contains, schema_exempt=None):
        self.phisql_path = phisql_path
        self.kind = kind                      # "accept" | "parse-only" | "reject-parse" | "reject-semantic"
        self.expected_exit = expected_exit
        self.expected_json = expected_json    # parsed JSON for accept cases, else None
        self.message_contains = message_contains
        # When set (from a sibling <name>.schema-exempt sidecar), the accept
        # case is still checked for exit code and fixture match but is skipped
        # by the schema check. Used for cases whose expected output is known to
        # diverge from the schema pending an RFC (the dict carries the reason).
        self.schema_exempt = schema_exempt


def classify(phisql_path, cases_root):
    """Determine a case's expectations from its path and sibling files."""
    rel_parts = phisql_path.relative_to(cases_root).parts
    sidecar = phisql_path.with_suffix(".reject")
    message_contains = None
    if sidecar.exists():
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        message_contains = meta.get("messageContains")

    if "accept" in rel_parts:
        expected = phisql_path.with_suffix(".json")
        if not expected.exists():
            raise CaseConfigError(
                f"accept case has no expected output: {expected.name} "
                f"(generate it with: python3 compliance/run.py --bless)")
        exempt_path = phisql_path.with_suffix(".schema-exempt")
        schema_exempt = (json.loads(exempt_path.read_text(encoding="utf-8"))
                         if exempt_path.exists() else None)
        return Case(phisql_path, "accept", EXIT_OK,
                    json.loads(expected.read_text(encoding="utf-8")),
                    message_contains, schema_exempt)
    if "parse-only" in rel_parts:
        return Case(phisql_path, "parse-only", EXIT_OK, None, message_contains)
    if "reject" in rel_parts and "parse" in rel_parts:
        return Case(phisql_path, "reject-parse", EXIT_PARSE, None, message_contains)
    if "reject" in rel_parts and "semantic" in rel_parts:
        return Case(phisql_path, "reject-semantic", EXIT_SEMANTIC, None, message_contains)
    raise CaseConfigError(
        f"cannot classify case (not under accept/, parse-only/, reject/parse/, "
        f"or reject/semantic/): {phisql_path}")


class CaseConfigError(Exception):
    pass


def run_adapter(adapter, phisql_path):
    proc = subprocess.run(
        [str(adapter), str(phisql_path)],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def check(case, code, stdout, stderr):
    """Return None if the case passes, else a human-readable failure reason."""
    if code != case.expected_exit:
        return (f"expected exit {case.expected_exit}, got {code}"
                + (f"\n      stderr: {stderr.strip().splitlines()[0]}" if stderr.strip() else ""))
    if case.message_contains and case.message_contains not in stderr:
        return f"stderr did not contain {case.message_contains!r}"
    if case.kind == "accept":
        try:
            actual = json.loads(stdout)
        except json.JSONDecodeError as e:
            return f"stdout was not valid JSON: {e}"
        if actual != case.expected_json:
            return ("compiled JSON did not match expected\n"
                    + _json_diff(case.expected_json, actual))
        # The accepted output must also be a valid Phileas policy, not merely
        # match the fixture — this catches a schema-invalid fixture or a
        # compiler emitting malformed policy JSON. Cases with a .schema-exempt
        # sidecar are skipped here (a known, documented divergence pending an RFC).
        if _SCHEMA_VALIDATOR is not None and case.schema_exempt is None:
            errors = sorted(_SCHEMA_VALIDATOR.iter_errors(actual),
                            key=lambda e: list(e.path))
            if errors:
                e0 = errors[0]
                loc = "/" + "/".join(map(str, e0.path))
                return f"compiled JSON is not schema-valid: at {loc}: {e0.message}"
    return None


def _json_diff(expected, actual):
    exp = json.dumps(expected, indent=2, sort_keys=True).splitlines()
    act = json.dumps(actual, indent=2, sort_keys=True).splitlines()
    import difflib
    lines = list(difflib.unified_diff(exp, act, "expected", "actual", lineterm=""))
    return "      " + "\n      ".join(lines[:40])


def discover_cases(cases_root):
    return sorted(p for p in cases_root.rglob("*.phisql"))


def bless(adapter, cases_root):
    """(Re)generate expected JSON for every accept case using the adapter."""
    written = 0
    for phisql_path in discover_cases(cases_root):
        if "accept" not in phisql_path.relative_to(cases_root).parts:
            continue
        code, stdout, stderr = run_adapter(adapter, phisql_path)
        if code != 0:
            print(f"{RED}cannot bless{RESET} {phisql_path.name}: exit {code}: {stderr.strip()}")
            return 1
        out = phisql_path.with_suffix(".json")
        normalized = json.dumps(json.loads(stdout), indent=2) + "\n"
        out.write_text(normalized, encoding="utf-8")
        written += 1
    print(f"blessed {written} accept case(s)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="PhiSQL conformance test runner")
    ap.add_argument("--adapter", default=str(DEFAULT_ADAPTER),
                    help="command that compiles a .phisql file to JSON (default: the reference adapter)")
    ap.add_argument("--cases", default=str(DEFAULT_CASES),
                    help="root directory of conformance cases")
    ap.add_argument("--filter", default="",
                    help="only run cases whose path contains this substring")
    ap.add_argument("--bless", action="store_true",
                    help="regenerate expected JSON for accept cases from the adapter (maintainers only)")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every case, not just failures")
    args = ap.parse_args()

    adapter = Path(args.adapter).resolve()
    cases_root = Path(args.cases).resolve()
    if not adapter.exists():
        print(f"adapter not found: {adapter}", file=sys.stderr)
        return 70
    if not cases_root.is_dir():
        print(f"cases directory not found: {cases_root}", file=sys.stderr)
        return 70

    if args.bless:
        return bless(adapter, cases_root)

    cases = [p for p in discover_cases(cases_root) if args.filter in str(p)]
    if not cases:
        print("no cases found", file=sys.stderr)
        return 70

    passed = failed = errored = schema_exempt_ct = 0
    by_kind = {}
    failures = []
    for phisql_path in cases:
        rel = phisql_path.relative_to(cases_root)
        try:
            case = classify(phisql_path, cases_root)
        except CaseConfigError as e:
            errored += 1
            print(f"{YELLOW}ERROR{RESET} {rel}: {e}")
            continue
        if case.kind == "accept" and case.schema_exempt is not None:
            schema_exempt_ct += 1
        code, stdout, stderr = run_adapter(adapter, phisql_path)
        reason = check(case, code, stdout, stderr)
        by_kind.setdefault(case.kind, [0, 0])
        if reason is None:
            passed += 1
            by_kind[case.kind][0] += 1
            if args.verbose:
                print(f"{GREEN}PASS{RESET} {DIM}{case.kind}{RESET} {rel}")
        else:
            failed += 1
            by_kind[case.kind][1] += 1
            failures.append((rel, case.kind, reason))
            print(f"{RED}FAIL{RESET} {DIM}{case.kind}{RESET} {rel}\n      {reason}")

    print()
    print("conformance summary")
    for kind in sorted(by_kind):
        ok, bad = by_kind[kind]
        print(f"  {kind:16} {ok:3} passed  {bad:3} failed")
    total = passed + failed
    color = GREEN if failed == 0 and errored == 0 else RED
    print(f"  {'total':16} {color}{passed}/{total}{RESET} passed"
          + (f", {errored} config error(s)" if errored else ""))
    if schema_exempt_ct:
        print(f"  {DIM}{schema_exempt_ct} accept case(s) schema-exempt "
              f"(see .schema-exempt sidecars){RESET}")
    if _SCHEMA_VALIDATOR is None:
        print(f"  {YELLOW}note:{RESET} jsonschema not installed; "
              f"accept-case schema checks were skipped")

    return 0 if failed == 0 and errored == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
