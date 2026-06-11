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
Unit tests for the hand-written lexer.

The Java reference generates its lexer from the grammar, so its tests do not
exercise tokenization directly. This Python reference transcribes the lexer
rules by hand, so these tests cover the lexer's contract directly: keyword
case-insensitivity, maximal munch, comments, string/number forms, operators,
and lexical error reporting.
"""

import re

import pytest

from phisql import ParseException
from phisql.lexer import tokenize


def _types(source):
    return [t.type for t in tokenize(source) if t.type != "EOF"]


def _texts(source):
    return [t.text for t in tokenize(source) if t.type != "EOF"]


# --- keywords, case-insensitivity, maximal munch ----------------------------


def test_keywords_are_case_insensitive():
    # caseInsensitive = true in the grammar: keywords match in any case.
    assert _types("REDACT redact ReDaCt") == ["REDACT", "REDACT", "REDACT"]
    assert _types("mask MASK Mask") == ["MASK", "MASK", "MASK"]


def test_identifiers_preserve_original_case():
    # User-defined names keep their case even though keywords are folded.
    toks = [t for t in tokenize("SSN email_Address") if t.type != "EOF"]
    assert [(t.type, t.text) for t in toks] == [
        ("ID", "SSN"),
        ("ID", "email_Address"),
    ]


def test_maximal_munch_distinguishes_keyword_from_identifier():
    # MASK is the keyword; MASKED reads as a longer word and is an ID.
    assert _types("MASK MASKED") == ["MASK", "ID"]
    # TRUNCATE_TO_YEAR must not be split into TRUNCATE + ...
    assert _types("TRUNCATE_TO_YEAR TRUNCATE") == ["TRUNCATE_TO_YEAR", "TRUNCATE"]


def test_boolean_literals():
    assert _types("TRUE false True") == [
        "BOOLEAN_LITERAL", "BOOLEAN_LITERAL", "BOOLEAN_LITERAL",
    ]


def test_custom_identifier_keyword_token():
    # IDENTIFIER is a keyword (IDENTIFIER_KW in the grammar), not a generic ID.
    assert _types("IDENTIFIER") == ["IDENTIFIER"]


# --- comments ---------------------------------------------------------------


def test_line_comment_is_skipped():
    assert _types("REDACT -- a comment\nSSN") == ["REDACT", "ID"]


def test_block_comment_is_skipped():
    assert _types("REDACT /* multi\nline */ SSN") == ["REDACT", "ID"]


def test_block_comment_between_tokens():
    assert _types("MASK/* x */(") == ["MASK", "("]


# --- string literals and escapes --------------------------------------------


def test_string_literal_is_one_token_with_quotes():
    assert _texts("'hello'") == ["'hello'"]


def test_string_literal_keeps_escapes_raw():
    # The lexer keeps the raw text (including escapes); unquoting happens later.
    assert _texts(r"'O\'Brien'") == [r"'O\'Brien'"]


def test_two_string_literals():
    assert _types("'a', 'b'") == ["STRING_LITERAL", ",", "STRING_LITERAL"]


# --- numeric literals -------------------------------------------------------


def test_integer_and_decimal_literals():
    assert _texts("30 0.85") == ["30", "0.85"]
    assert _types("30 0.85") == ["NUMERIC_LITERAL", "NUMERIC_LITERAL"]


def test_negative_numeric_literal():
    assert _texts("=-30") == ["=", "-30"]


# --- operators --------------------------------------------------------------


def test_two_char_operators_beat_single_char():
    assert _types(">= <= > < =") == [">=", "<=", ">", "<", "="]


def test_punctuation_tokens():
    assert _types("( ) , ; [ ] . *") == [
        "(", ")", ",", ";", "[", "]", ".", "*",
    ]


# --- lexical errors ---------------------------------------------------------


def _assert_line_col(exc_info):
    assert re.match(r"line \d+:\d+", str(exc_info.value)), str(exc_info.value)


def test_unterminated_string_is_an_error():
    with pytest.raises(ParseException) as exc:
        tokenize("'oops")
    _assert_line_col(exc)


def test_raw_newline_in_string_is_an_error():
    # The grammar forbids an unescaped newline inside a string literal.
    with pytest.raises(ParseException) as exc:
        tokenize("'a\nb'")
    _assert_line_col(exc)


def test_unterminated_block_comment_is_an_error():
    with pytest.raises(ParseException) as exc:
        tokenize("/* never closed")
    _assert_line_col(exc)


def test_unrecognized_character_is_an_error():
    with pytest.raises(ParseException) as exc:
        tokenize("REDACT SSN @ MASK;")
    _assert_line_col(exc)


def test_error_reports_correct_line_and_column():
    with pytest.raises(ParseException) as exc:
        tokenize("REDACT\nSSN @")
    # '@' is on line 2 at column 4.
    assert "line 2:4" in str(exc.value), str(exc.value)
