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
Regression test for the catalog/schema arg-type guard (RFC #13).

The guard exists because maskLength was catalogued as `integer` while the schema
typed it `string`, so valid PhiSQL compiled to schema-invalid JSON undetected.
These cases prove the helper *fires* on that contradiction and *passes* once the
schema admits the integer form, so the bug class cannot recur silently.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_spec import _arg_type_compatible  # noqa: E402


def test_integer_arg_against_string_schema_is_incompatible():
    # The exact #13 contradiction: maskLength as it stood on frozen schema 1.0.0.
    assert _arg_type_compatible("integer", "string") is False


def test_integer_arg_against_widened_union_is_compatible():
    # The #13 fix: schema 1.1.0 widened maskLength to ["string", "integer"].
    assert _arg_type_compatible("integer", ["string", "integer"]) is True


def test_string_arg_still_fits_the_widened_union():
    # The widening must not break the original string form (maskLength = "SAME").
    assert _arg_type_compatible("string", ["string", "integer"]) is True


def test_matching_scalar_types_are_compatible():
    assert _arg_type_compatible("string", "string") is True
    assert _arg_type_compatible("boolean", "boolean") is True
    assert _arg_type_compatible("enum", "string") is True


def test_integer_arg_accepts_schema_number():
    assert _arg_type_compatible("integer", "number") is True


def test_mismatched_scalar_types_are_incompatible():
    assert _arg_type_compatible("boolean", "string") is False
    assert _arg_type_compatible("string", "integer") is False


def test_unknown_arg_type_is_not_flagged():
    # A new arg kind the table does not know about must not hard-fail the build.
    assert _arg_type_compatible("date", "string") is True
