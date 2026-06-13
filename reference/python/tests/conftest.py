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
"""Shared pytest fixtures and path setup for the PhiSQL Python reference tests."""

import sys
from pathlib import Path

# Make `import phisql` work when running the tests from a source checkout
# without installing the package.
_PACKAGE_DIR = Path(__file__).resolve().parents[1]
if str(_PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_DIR))

import pytest  # noqa: E402

#: spec/v1.0/examples, resolved relative to this file (reference/python/tests).
EXAMPLES_DIR = (_PACKAGE_DIR / ".." / ".." / "spec" / "v1.0" / "examples").resolve()
EXAMPLES_V11_DIR = (_PACKAGE_DIR / ".." / ".." / "spec" / "v1.1.0" / "examples").resolve()
EXAMPLES_DIRS = [d for d in (EXAMPLES_DIR, EXAMPLES_V11_DIR) if d.is_dir()]


@pytest.fixture(scope="session")
def examples_dir():
    if not EXAMPLES_DIR.is_dir():
        raise AssertionError(f"No examples directory at {EXAMPLES_DIR}")
    return EXAMPLES_DIR


#: Discovery examples parse but do not compile to a Phileas redaction policy
#: (they target a separate discovery-query schema). Compilation/schema tests
#: skip them; they are still covered by parse and discovery-specific tests.
DISCOVERY_EXAMPLES = {
    "15-find-pii-s3.phisql",
    "16-discover-entities-gcs.phisql",
    "17-scan-azure-blob.phisql",
    "18-find-pii-local-filesystem.phisql",
    "19-select-findings-groupby.phisql",
}


def example_phisql_files():
    """Returns the sorted list of example .phisql paths (for parametrization)."""
    files = sorted(p for d in EXAMPLES_DIRS for p in d.glob("*.phisql"))
    if not files:
        raise AssertionError(f"No example files found in {EXAMPLES_DIRS}")
    return files


def example_json_files():
    """Returns the sorted list of example .json paths (for parametrization)."""
    files = sorted(p for d in EXAMPLES_DIRS for p in d.glob("*.json"))
    if not files:
        raise AssertionError(f"No example .json files found in {EXAMPLES_DIRS}")
    return files


def redaction_example_files():
    """Example .phisql files that compile to a Phileas redaction policy."""
    return [p for p in example_phisql_files() if p.name not in DISCOVERY_EXAMPLES]


def discovery_example_files():
    """Example .phisql files for the discovery verbs (parse-only)."""
    return [p for p in example_phisql_files() if p.name in DISCOVERY_EXAMPLES]
