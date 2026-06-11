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
Compiles every redaction example .phisql file under spec/v1.0/examples/ and
verifies the output matches the corresponding .json file (compared as parsed
JSON, so key order and formatting are ignored). This is the load-bearing
assertion that the compiler stays in sync with the spec examples.

Discovery examples do not compile to Phileas JSON and are listed explicitly so
the test skips them rather than implicitly. When a discovery compiler lands the
set shrinks; new redaction examples are picked up automatically.
"""

import json

import pytest

from phisql import Compiler
from conftest import example_phisql_files

DISCOVERY_EXAMPLES_NOT_YET_COMPILED = {
    "15-find-pii-s3.phisql",
    "16-discover-entities-gcs.phisql",
    "17-scan-azure-blob.phisql",
    "18-find-pii-local-filesystem.phisql",
    "19-select-findings-groupby.phisql",
}

_REDACTION_EXAMPLES = [
    p for p in example_phisql_files()
    if p.name not in DISCOVERY_EXAMPLES_NOT_YET_COMPILED
]


@pytest.mark.parametrize("source_path", _REDACTION_EXAMPLES, ids=lambda p: p.name)
def test_every_example_compiles_to_expected_json(source_path):
    compiler = Compiler()
    result = compiler.compile(source_path.read_text(encoding="utf-8"))

    expected_path = source_path.with_suffix(".json")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    assert result.policy_json() == expected, (
        f"Compiled output for {source_path.name} does not match {expected_path.name}"
    )
    assert result.policy_name() is not None, (
        "Compiler should extract the POLICY name from the document"
    )
