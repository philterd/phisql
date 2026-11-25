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


def test_rejects_duplicate_generator_name():
    # Two DEFINE GENERATOR statements with the same name would collide in the
    # single name-keyed generators object; that is a semantic error.
    src = (
        "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'A: {{token}}', timeoutMs = 1000);\n"
        "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'B: {{token}}', timeoutMs = 1000);"
    )
    with pytest.raises(CompileException) as exc:
        Compiler().compile(src)
    assert "Duplicate generator name" in str(exc.value)


def test_allows_two_distinct_generators():
    # Positive control: distinct names both land in the generators block.
    generators = (
        Compiler().compile(
            "DEFINE GENERATOR 'a' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);\n"
            "DEFINE GENERATOR 'b' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);"
        )
        .policy_json()["generators"]
    )
    assert set(generators) == {"a", "b"}


def test_compiles_review_sampling_rate():
    review = (
        Compiler().compile("REDACT SSN WITH MASK;\nCONFIGURE review (samplingRate = 0.10);")
        .policy_json()["config"]["review"]
    )
    assert review == {"samplingRate": 0.1}


def test_review_is_not_reserved():
    # REVIEW is matched contextually, so it stays usable as an identifier.
    policy = Compiler().compile("POLICY review;\nREDACT SSN WITH MASK;").policy_json()
    assert "ssn" in policy["identifiers"]


@pytest.mark.parametrize("rate", ["1.5", "-0.1", "'half'", "TRUE"])
def test_rejects_sampling_rate_out_of_range(rate):
    with pytest.raises(CompileException) as exc:
        Compiler().compile(f"REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = {rate});")
    assert "samplingRate must be a number from 0.0 to 1.0" in str(exc.value)


def test_rejects_unknown_config_block():
    with pytest.raises(CompileException) as exc:
        Compiler().compile("REDACT SSN WITH MASK;\nCONFIGURE AUDIT (samplingRate = 0.1);")
    assert "Unknown config block: AUDIT" in str(exc.value)


def test_compiles_email_config():
    email = (
        Compiler().compile(
            "REDACT SSN WITH MASK;\nCONFIGURE email (headers = (removeDate = TRUE, removeSubject = FALSE),"
            " attachments = 'redact', inlineImages = 'remove');"
        )
        .policy_json()["config"]["email"]
    )
    assert email == {
        "headers": {"removeDate": True, "removeSubject": False},
        "attachments": "redact",
        "inlineImages": "remove",
    }


def test_email_is_not_reserved():
    policy = Compiler().compile("POLICY email;\nREDACT SSN WITH MASK;").policy_json()
    assert "ssn" in policy["identifiers"]


@pytest.mark.parametrize(
    "settings,message",
    [
        ("attachment = 'remove'", "Unknown email setting: attachment"),
        ("headers = (removeBcc = TRUE)", "Unknown email header setting: removeBcc"),
        ("headers = (removeDate = 'yes')", "email header setting removeDate must be TRUE or FALSE"),
        ("headers = TRUE", "email headers must be a setting list"),
        ("attachments = 'strip'", "attachments must be one of keep, remove, redact"),
        ("attachments = TRUE", "attachments must be one of keep, remove, redact"),
        ("inlineImages = 'redact'", "inlineImages must be one of keep, remove"),
    ],
)
def test_rejects_invalid_email_config(settings, message):
    with pytest.raises(CompileException) as exc:
        Compiler().compile(f"REDACT SSN WITH MASK;\nCONFIGURE EMAIL ({settings});")
    assert message in str(exc.value)


def test_compiles_leftover_check():
    review = (
        Compiler().compile(
            "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = 0.1,"
            " leftoverCheck = (mode = 'always', using = 'samePolicy'));"
        )
        .policy_json()["config"]["review"]
    )
    assert review == {"samplingRate": 0.1, "leftoverCheck": {"mode": "always", "using": "samePolicy"}}


@pytest.mark.parametrize(
    "settings,message",
    [
        ("leftoverCheck = TRUE", "leftoverCheck must be a setting list"),
        ("leftoverCheck = (depth = 'broad')", "Unknown leftoverCheck setting: depth"),
        ("leftoverCheck = (mode = 'sometimes')", "leftoverCheck mode must be one of off, onRequest, always"),
        ("leftoverCheck = (mode = 'onrequest')", "leftoverCheck mode must be one of off, onRequest, always"),
        ("leftoverCheck = (using = 'everything')", "leftoverCheck using must be one of broad, samePolicy"),
        ("leftoverCheck = (using = TRUE)", "leftoverCheck using must be one of broad, samePolicy"),
    ],
)
def test_rejects_invalid_leftover_check(settings, message):
    with pytest.raises(CompileException) as exc:
        Compiler().compile(f"REDACT SSN WITH MASK;\nCONFIGURE REVIEW ({settings});")
    assert message in str(exc.value)


def test_compiles_word_and_excel_config():
    config = (
        Compiler().compile(
            "REDACT SSN WITH MASK;\nCONFIGURE word (comments = 'redact', trackedChanges = 'redact',"
            " removeDocumentProperties = FALSE, highlight = TRUE);\n"
            "CONFIGURE Excel (formulaCaches = 'keep', uninspectableObjects = 'keep');"
        )
        .policy_json()["config"]
    )
    assert config["word"] == {
        "comments": "redact",
        "trackedChanges": "redact",
        "removeDocumentProperties": False,
        "highlight": True,
    }
    assert config["excel"] == {"formulaCaches": "keep", "uninspectableObjects": "keep"}


@pytest.mark.parametrize("name", ["word", "excel"])
def test_word_and_excel_are_not_reserved(name):
    policy = Compiler().compile(f"POLICY {name};\nREDACT SSN WITH MASK;").policy_json()
    assert "ssn" in policy["identifiers"]


@pytest.mark.parametrize(
    "block,settings,message",
    [
        ("WORD", "comment = 'remove'", "Unknown word setting: comment"),
        ("WORD", "comments = 'strip'", "word setting comments must be one of remove, redact"),
        ("WORD", "trackedChanges = 'reject'", "word setting trackedChanges must be one of accept, redact"),
        ("WORD", "headersFooters = TRUE", "word setting headersFooters must be one of redact, keep"),
        ("WORD", "highlight = 'yes'", "word setting highlight must be TRUE or FALSE"),
        ("EXCEL", "comments = 'remove'", "Unknown excel setting: comments"),
        ("EXCEL", "formulaCaches = 'remove'", "excel setting formulaCaches must be one of redact, keep"),
        ("EXCEL", "removeDocumentProperties = 1", "excel setting removeDocumentProperties must be TRUE or FALSE"),
    ],
)
def test_rejects_invalid_word_and_excel_config(block, settings, message):
    with pytest.raises(CompileException) as exc:
        Compiler().compile(f"REDACT SSN WITH MASK;\nCONFIGURE {block} ({settings});")
    assert message in str(exc.value)
