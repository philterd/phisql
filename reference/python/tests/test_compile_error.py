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
