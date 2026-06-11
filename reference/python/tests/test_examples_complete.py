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
Completeness checks over the spec example pairs under spec/v1.0/examples/.

Every example is a (.phisql, .json) pair. These tests assert the pairing is
complete (no orphan files), every .json is well-formed, and the discovery
examples — which the compiler does not translate — are still covered: their
.phisql parses to a discovery statement and their .json carries an
``operation``. This guarantees no example file is silently uncovered by the
suite.
"""

import json

import pytest

from phisql import parse
from phisql.ast import DiscoveryStmt
from conftest import (
    discovery_example_files,
    example_json_files,
    example_phisql_files,
)


@pytest.mark.parametrize("phisql_path", example_phisql_files(), ids=lambda p: p.name)
def test_every_phisql_has_a_json_sibling(phisql_path):
    assert phisql_path.with_suffix(".json").is_file(), (
        f"{phisql_path.name} has no sibling .json"
    )


@pytest.mark.parametrize("json_path", example_json_files(), ids=lambda p: p.name)
def test_every_json_has_a_phisql_sibling(json_path):
    assert json_path.with_suffix(".phisql").is_file(), (
        f"{json_path.name} has no sibling .phisql"
    )


@pytest.mark.parametrize("json_path", example_json_files(), ids=lambda p: p.name)
def test_every_json_example_is_well_formed(json_path):
    json.loads(json_path.read_text(encoding="utf-8"))  # raises on malformed JSON


@pytest.mark.parametrize("source_path", discovery_example_files(), ids=lambda p: p.name)
def test_discovery_example_parses_to_discovery_statement(source_path):
    # The compiler does not translate discovery verbs, but they must still parse,
    # and their statements are discovery statements.
    document = parse(source_path.read_text(encoding="utf-8"))
    assert document.statements, f"{source_path.name} produced no statements"
    assert any(isinstance(s, DiscoveryStmt) for s in document.statements), (
        f"{source_path.name} parsed without a discovery statement"
    )


@pytest.mark.parametrize("source_path", discovery_example_files(), ids=lambda p: p.name)
def test_discovery_json_declares_an_operation(source_path):
    fixture = json.loads(source_path.with_suffix(".json").read_text(encoding="utf-8"))
    assert "operation" in fixture, (
        f"{source_path.with_suffix('.json').name} has no 'operation' field"
    )
