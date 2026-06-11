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
Verifies the policy-naming rule defined in spec/v1.0/catalog/policy.yaml:

* POLICY declaration is optional.
* When a filename is provided and POLICY is declared, the declared name must
  match the filename basename after hyphen/underscore normalization.
* When POLICY is omitted, the policy name is the filename basename.
* When no filename is provided and POLICY is omitted, policy_name is None.
"""

import pytest

from phisql import CompileException, Compiler


@pytest.fixture
def compiler():
    return Compiler()


def _write_phisql(tmp_path, filename, contents):
    file = tmp_path / filename
    file.write_text(contents, encoding="utf-8")
    return file


def test_filename_provides_name_when_policy_declaration_omitted(compiler, tmp_path):
    file = _write_phisql(tmp_path, "hipaa-safe-harbor.phisql", "REDACT SSN WITH MASK;")
    assert compiler.compile_file(file).policy_name() == "hipaa-safe-harbor"


def test_matching_policy_declaration_compiles_successfully(compiler, tmp_path):
    file = _write_phisql(tmp_path, "ssn_only.phisql",
                         "POLICY ssn_only; REDACT SSN WITH MASK;")
    assert compiler.compile_file(file).policy_name() == "ssn_only"


def test_mismatched_policy_declaration_produces_compile_error(compiler, tmp_path):
    file = _write_phisql(tmp_path, "whatever.phisql",
                         "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;")
    with pytest.raises(CompileException):
        compiler.compile_file(file)


def test_hyphen_underscore_normalization(compiler, tmp_path):
    # A file named hipaa-safe-harbor.phisql may declare POLICY hipaa_safe_harbor.
    file = _write_phisql(tmp_path, "hipaa-safe-harbor.phisql",
                         "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;")
    assert compiler.compile_file(file).policy_name() == "hipaa-safe-harbor"


def test_string_only_compile_without_policy_declaration_is_none(compiler):
    assert compiler.compile("REDACT SSN WITH MASK;").policy_name() is None


def test_string_only_compile_with_policy_declaration_uses_declared_name(compiler):
    assert compiler.compile("POLICY foo; REDACT SSN WITH MASK;").policy_name() == "foo"


def test_explicit_expected_name_overrides_null_declaration(compiler):
    result = compiler.compile("REDACT SSN WITH MASK;", "ssn_only")
    assert result.policy_name() == "ssn_only"


def test_explicit_expected_name_must_match_policy_declaration(compiler):
    with pytest.raises(CompileException) as exc:
        compiler.compile("POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;",
                         "different_name")
    assert "hipaa_safe_harbor" in str(exc.value)


def test_description_text_is_extracted(compiler, tmp_path):
    file = _write_phisql(tmp_path, "test_policy.phisql",
                         "POLICY test_policy DESCRIPTION 'A policy for X.'; "
                         "REDACT SSN WITH MASK;")
    assert compiler.compile_file(file).description() == "A policy for X."
