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
Verifies that malformed PhiSQL raises ParseException with messages that include
line and column. This is the error-reporting surface implementations rely on
for IDE integration and CLI diagnostics.
"""

import re

import pytest

from phisql import ParseException, parse

LINE_COL = re.compile(r"line \d+:\d+")


def _assert_has_line_and_column(exc_info):
    assert LINE_COL.match(str(exc_info.value)), (
        f"Expected 'line N:M' format, got: {exc_info.value}"
    )


def test_rejects_unknown_statement_keyword():
    with pytest.raises(ParseException) as exc:
        parse("REDAKT SSN WITH MASK;")
    _assert_has_line_and_column(exc)


def test_rejects_unknown_strategy_name():
    with pytest.raises(ParseException) as exc:
        parse("REDACT SSN WITH NOTASTRATEGY;")
    _assert_has_line_and_column(exc)


def test_rejects_missing_semicolon():
    with pytest.raises(ParseException) as exc:
        parse("REDACT SSN WITH MASK")
    _assert_has_line_and_column(exc)


def test_rejects_malformed_named_arg():
    with pytest.raises(ParseException) as exc:
        parse("REDACT SSN WITH MASK(=value);")
    _assert_has_line_and_column(exc)


def test_rejects_custom_identifier_without_classification():
    # IDENTIFIER must be followed by ('<classification>').
    with pytest.raises(ParseException) as exc:
        parse("REDACT IDENTIFIER WITH MASK;")
    _assert_has_line_and_column(exc)


def test_error_message_reports_correct_line_number():
    # Three statements; the typo is on line 3.
    source = (
        "POLICY support_tickets;\n"
        "REDACT SSN WITH MASK;\n"
        "REDAKT EMAIL_ADDRESS WITH MASK;\n"
    )
    with pytest.raises(ParseException) as exc:
        parse(source)
    assert "line 3:" in str(exc.value), f"Expected error on line 3, got: {exc.value}"
