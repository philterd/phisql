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


@pytest.fixture(scope="session")
def examples_dir():
    if not EXAMPLES_DIR.is_dir():
        raise AssertionError(f"No examples directory at {EXAMPLES_DIR}")
    return EXAMPLES_DIR


def example_phisql_files():
    """Returns the sorted list of example .phisql paths (for parametrization)."""
    files = sorted(EXAMPLES_DIR.glob("*.phisql"))
    if not files:
        raise AssertionError(f"No example files found at {EXAMPLES_DIR}")
    return files
