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
Verifies how WHERE predicates compile to Phileas conditions (RFC #58): ``=`` is
emitted as ``==``, and OR and parentheses produce a compile warning.
"""

import pytest

from phisql import Compiler
from phisql.compiler import OR_WARNING, PAREN_WARNING


def _condition(result):
    return result.policy_json()["identifiers"]["ssn"]["ssnFilterStrategies"][0]["condition"]


def test_equals_compiles_to_double_equals():
    r = Compiler().compile("REDACT SSN WITH MASK WHERE CONFIDENCE = 0.75;")
    assert _condition(r) == "confidence == 0.75"
    assert r.warnings() == []


@pytest.mark.parametrize("op", [">", ">=", "<", "<="])
def test_other_operators_are_unchanged(op):
    r = Compiler().compile(f"REDACT SSN WITH MASK WHERE CONFIDENCE {op} 0.5;")
    assert _condition(r) == f"confidence {op} 0.5"


def test_and_does_not_warn():
    r = Compiler().compile("REDACT SSN WITH MASK WHERE CONFIDENCE > 0.5 AND CONFIDENCE < 0.9;")
    assert _condition(r) == "confidence > 0.5 and confidence < 0.9"
    assert r.warnings() == []


def test_or_warns():
    r = Compiler().compile("REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;")
    assert r.warnings() == [OR_WARNING]


def test_parentheses_and_or_warn_once_each_per_document():
    r = Compiler().compile(
        "REDACT SSN WITH MASK WHERE (CONFIDENCE > 0.5 AND CONFIDENCE < 0.9) OR CONFIDENCE = 1.0;\n"
        "REDACT EIN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;")
    assert r.warnings() == [OR_WARNING, PAREN_WARNING]


def test_detect_and_define_identifier_predicates_are_scanned():
    detect = Compiler().compile("DETECT PHEYE WITH REDACT WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;")
    assert detect.warnings() == [OR_WARNING]
    identifier = Compiler().compile(
        "DEFINE IDENTIFIER 'acct' MATCHING '\\d{6}' WITH REDACT WHERE (CONFIDENCE > 0.5);")
    assert identifier.warnings() == [PAREN_WARNING]
