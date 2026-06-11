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
Compiler/parser coverage for grammar features the spec examples do not exercise.

The example round-trip tests (test_compiler.py) are the primary correctness
assertion, but the bundled examples happen not to use string escapes, negative
numbers, the ``=`` comparison operator, boolean/parenthesised redaction
predicates, the ``DETECT ... ENDPOINT`` clause, or several catalogued strategy
arguments. These tests cover those paths directly so a regression in the
hand-written parser or in the compiler's translation is caught.
"""

import pytest

from phisql import CompileException, Compiler


@pytest.fixture
def compiler():
    return Compiler()


def _strategy(compiler, source, field, strategies_field, index=0):
    """Compiles a single REDACT/DEIDENTIFY and returns the index-th strategy object."""
    identifiers = compiler.compile(source).policy_json()["identifiers"]
    return identifiers[field][strategies_field][index]


# --- case-insensitive keywords compile correctly ----------------------------


def test_lowercase_keywords_compile(compiler):
    strategy = _strategy(compiler, "redact ssn with mask;", "ssn", "ssnFilterStrategies")
    assert strategy == {"strategy": "MASK"}


# --- string escapes through the compiler ------------------------------------


def test_escaped_single_quote_is_unquoted(compiler):
    strategy = _strategy(
        compiler, r"REDACT SSN WITH STATIC_REPLACE(value='O\'Brien');",
        "ssn", "ssnFilterStrategies")
    assert strategy["staticReplacement"] == "O'Brien"


def test_escaped_newline_is_unquoted(compiler):
    strategy = _strategy(
        compiler, r"REDACT SSN WITH STATIC_REPLACE(value='a\nb');",
        "ssn", "ssnFilterStrategies")
    assert strategy["staticReplacement"] == "a\nb"


def test_escaped_backslash_is_collapsed(compiler):
    strategy = _strategy(
        compiler, r"REDACT SSN WITH STATIC_REPLACE(value='a\\b');",
        "ssn", "ssnFilterStrategies")
    assert strategy["staticReplacement"] == "a\\b"  # the two-char source \\ -> one backslash


# --- numeric forms ----------------------------------------------------------


def test_negative_integer_argument(compiler):
    strategy = _strategy(compiler, "REDACT DATE WITH SHIFT(days=-30);",
                         "date", "dateFilterStrategies")
    assert strategy["shiftDays"] == -30


def test_decimal_passthrough_argument(compiler):
    # An uncatalogued numeric arg with a fraction infers a float.
    strategy = _strategy(compiler, "REDACT SSN WITH MASK(weight=0.25);",
                         "ssn", "ssnFilterStrategies")
    assert strategy["weight"] == 0.25


# --- redaction WHERE predicates ---------------------------------------------


def test_equals_comparison_operator(compiler):
    strategy = _strategy(compiler, "REDACT SSN WITH MASK WHERE CONFIDENCE = 0.5;",
                         "ssn", "ssnFilterStrategies")
    assert strategy["conditions"] == "confidence = 0.5"


def test_parenthesised_and_predicate(compiler):
    strategy = _strategy(
        compiler,
        "REDACT SSN WITH MASK WHERE (CONFIDENCE > 0.5) AND CONFIDENCE < 0.9;",
        "ssn", "ssnFilterStrategies")
    assert strategy["conditions"] == "( confidence > 0.5 ) and confidence < 0.9"


def test_or_predicate(compiler):
    strategy = _strategy(
        compiler,
        "REDACT SSN WITH MASK WHERE CONFIDENCE > 0.9 OR CONFIDENCE < 0.1;",
        "ssn", "ssnFilterStrategies")
    assert strategy["conditions"] == "confidence > 0.9 or confidence < 0.1"


# --- DETECT PHEYE ENDPOINT ---------------------------------------------------


def test_detect_endpoint_and_labels(compiler):
    pheye = compiler.compile(
        "DETECT PHEYE LABELS ('PER') ENDPOINT 'http://pheye:8080' WITH REDACT;"
    ).policy_json()["identifiers"]["pheyes"][0]
    assert pheye["phEyeConfiguration"] == {
        "endpoint": "http://pheye:8080",
        "labels": ["PER"],
    }


def test_detect_with_confidence_predicate(compiler):
    pheye = compiler.compile(
        "DETECT PHEYE LABELS ('PER') WITH REDACT WHERE CONFIDENCE > 0.7;"
    ).policy_json()["identifiers"]["pheyes"][0]
    assert pheye["phEyeFilterStrategies"][0]["conditions"] == "confidence > 0.7"


# --- multi-statement accumulation -------------------------------------------


def test_strategies_accumulate_across_statements(compiler):
    strategies = compiler.compile(
        "REDACT EMAIL_ADDRESS WITH HASH_SHA256;\n"
        "REDACT EMAIL_ADDRESS WITH MASK;"
    ).policy_json()["identifiers"]["emailAddress"]["emailAddressFilterStrategies"]
    assert [s["strategy"] for s in strategies] == ["HASH_SHA256_REPLACE", "MASK"]


def test_custom_identifier_reuses_entry_by_classification(compiler):
    identifiers = compiler.compile(
        "REDACT IDENTIFIER('acct') WITH LAST_4;\n"
        "REDACT IDENTIFIER('acct') WITH MASK;"
    ).policy_json()["identifiers"]["identifiers"]
    assert len(identifiers) == 1
    assert identifiers[0]["classification"] == "acct"
    assert len(identifiers[0]["identifierFilterStrategies"]) == 2


# --- scoped-IGNORE error paths ----------------------------------------------


def test_scoped_ignore_with_options_is_rejected(compiler):
    with pytest.raises(CompileException) as exc:
        compiler.compile("IGNORE TERMS ('x') FOR SSN OPTIONS (name='n');")
    assert "OPTIONS is not supported on a scoped IGNORE" in str(exc.value)


def test_ignore_scoped_to_custom_identifier_is_rejected(compiler):
    # IGNORE ... FOR a custom identifier is not supported in v1.0.
    with pytest.raises(CompileException):
        compiler.compile(
            "DEFINE IDENTIFIER 'acct' MATCHING '[0-9]+' WITH MASK;\n"
            "IGNORE TERMS ('x') FOR IDENTIFIER('acct');"
        )


# --- scope-less IGNORE TERMS and PATTERN top-level placement -----------------


def test_scopeless_ignore_terms_goes_to_top_level(compiler):
    policy = compiler.compile("IGNORE TERMS ('a', 'b');").policy_json()
    assert policy["ignored"] == [{"terms": ["a", "b"]}]


def test_scopeless_ignore_pattern_goes_to_top_level(compiler):
    policy = compiler.compile("IGNORE PATTERN '[0-9]+';").policy_json()
    assert policy["ignoredPatterns"] == [{"pattern": "[0-9]+"}]
