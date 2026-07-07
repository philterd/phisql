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
Verifies that PhiSQL that parses successfully but cannot be compiled raises a
CompileException with a useful message.
"""

import pytest

from phisql import CompileException, Compiler


def test_rejects_unknown_entity_type():
    with pytest.raises(CompileException) as exc:
        Compiler().compile("REDACT NOT_AN_ENTITY WITH MASK;")
    assert "NOT_AN_ENTITY" in str(exc.value)


def test_passes_through_uncatalogued_strategy_argument():
    # An argument the strategy catalog does not list passes through to the
    # Phileas JSON by its schema property name, so any strategy field is settable.
    strategy = (
        Compiler().compile("REDACT SSN WITH MASK(salt=TRUE);")
        .policy_json()["identifiers"]["ssn"]["ssnFilterStrategies"][0]
    )
    assert strategy.get("salt") is True


def test_rejects_invalid_enum_value():
    with pytest.raises(CompileException) as exc:
        Compiler().compile("REDACT SSN WITH STATIC_REPLACE(value='X', scope=invalid);")
    message = str(exc.value).lower()
    assert "scope" in message or "invalid" in message


@pytest.mark.parametrize(
    "source,strategy",
    [
        # Each date-only strategy, on the entity (object-valued) path...
        ("REDACT SSN WITH SHIFT(days=30);", "SHIFT"),
        ("REDACT EMAIL_ADDRESS WITH TRUNCATE_TO_YEAR;", "TRUNCATE_TO_YEAR"),
        # ...and on the array-container path (a custom identifier).
        ("DEFINE IDENTIFIER 'X' MATCHING '\\d+' WITH RELATIVE;", "RELATIVE"),
    ],
)
def test_rejects_date_only_strategy_on_non_date_target(source, strategy):
    with pytest.raises(CompileException) as exc:
        Compiler().compile("POLICY t;\n" + source)
    message = str(exc.value)
    assert strategy in message and "date-only" in message


def test_allows_date_only_strategy_on_date():
    # Positive control: a date-only strategy on DATE compiles.
    strategy = (
        Compiler().compile("REDACT DATE WITH SHIFT(days=30);")
        .policy_json()["identifiers"]["date"]["dateFilterStrategies"][0]
    )
    assert strategy["strategy"] == "SHIFT"


def test_rejects_static_replace_without_value():
    # The catalog marks STATIC_REPLACE's `value` required; omitting it is a
    # semantic error rather than a malformed strategy.
    with pytest.raises(CompileException) as exc:
        Compiler().compile("REDACT SURNAME WITH STATIC_REPLACE(scope=document);")
    assert "STATIC_REPLACE requires argument 'value'" in str(exc.value)


def test_allows_static_replace_with_value():
    # Positive control: STATIC_REPLACE with a value compiles.
    strategy = (
        Compiler().compile("REDACT SURNAME WITH STATIC_REPLACE(value='Customer');")
        .policy_json()["identifiers"]["surname"]["surnameFilterStrategies"][0]
    )
    assert strategy["staticReplacement"] == "Customer"
