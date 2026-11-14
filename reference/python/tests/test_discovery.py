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
Verifies how the compiler reports discovery statements, which it does not
compile yet (#71): each one is skipped with a warning naming it and its line,
and a script with nothing else is a compile error rather than an empty policy.
"""

import pytest

from phisql import Compiler
from phisql.compiler import DISCOVERY_WARNING, OR_WARNING
from phisql.errors import CompileException


def test_discovery_only_script_is_a_compile_error():
    with pytest.raises(CompileException) as e:
        Compiler().compile(
            "FIND PII IN 's3://prod-data/customers/'\n"
            "  WHERE entity_type IN ('SSN', 'CREDIT_CARD');\n"
            "SCAN IN 'file:///mnt/exports/';\n")
    assert str(e.value) == (
        "The script has only discovery statements (FIND PII at line 1, SCAN at line 3), "
        "and discovery statements are not compiled to a redaction policy yet.")


def test_policy_declaration_alone_does_not_make_a_discovery_script_compile():
    with pytest.raises(CompileException) as e:
        Compiler().compile(
            "POLICY findings_report;\n"
            "SELECT path, entity_type, COUNT(*) FROM phinder.findings GROUP BY path, entity_type;\n")
    assert str(e.value) == (
        "The script has only discovery statements (SELECT ... FROM findings at line 2), "
        "and discovery statements are not compiled to a redaction policy yet.")


def test_mixed_script_compiles_the_redaction_statements_and_warns_for_each_discovery_statement():
    r = Compiler().compile(
        "FIND PII IN 's3://prod-data/customers/';\n"
        "REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;\n"
        "\n"
        "DISCOVER ENTITIES IN 'gs://archive/';\n")
    assert r.policy_json()["identifiers"]["ssn"]["ssnFilterStrategies"][0]["strategy"] == "MASK"
    assert r.warnings() == [
        f"FIND PII at line 1 was skipped: {DISCOVERY_WARNING}",
        f"DISCOVER ENTITIES at line 4 was skipped: {DISCOVERY_WARNING}",
        OR_WARNING,
    ]
