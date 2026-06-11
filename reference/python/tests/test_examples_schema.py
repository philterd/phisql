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
Validates that the compiler's output conforms to the canonical redaction policy
JSON Schema — not merely that it equals the example fixtures.

test_compiler.py asserts the compiled output equals the sibling .json file;
this asserts that what the compiler emits actually validates against the schema
the package bundles (``PolicySchema.get_schema()``). Together they pin the
output to both the fixtures and the schema contract.

Both the .phisql-compiled output and the checked-in .json fixture are validated,
so a regression in either the compiler or a fixture is caught.
"""

import json

import pytest

jsonschema = pytest.importorskip("jsonschema")

from phisql import Compiler, PolicySchema
from conftest import redaction_example_files


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(PolicySchema.get_schema())
    return jsonschema.Draft202012Validator(schema)


def _assert_valid(validator, policy, label):
    errors = sorted(validator.iter_errors(policy), key=lambda e: list(e.path))
    if errors:
        detail = "\n".join(
            f"  at /{'/'.join(map(str, e.path))}: {e.message}" for e in errors
        )
        raise AssertionError(f"{label} is not schema-valid:\n{detail}")


@pytest.mark.parametrize("source_path", redaction_example_files(), ids=lambda p: p.name)
def test_compiled_example_validates_against_schema(validator, source_path):
    policy = Compiler().compile(source_path.read_text(encoding="utf-8")).policy_json()
    _assert_valid(validator, policy, f"Compiled {source_path.name}")


@pytest.mark.parametrize("source_path", redaction_example_files(), ids=lambda p: p.name)
def test_example_json_fixture_validates_against_schema(validator, source_path):
    fixture = json.loads(source_path.with_suffix(".json").read_text(encoding="utf-8"))
    _assert_valid(validator, fixture, f"Fixture {source_path.with_suffix('.json').name}")
