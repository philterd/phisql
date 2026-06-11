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
Verifies the CLI adapter contract the conformance runner depends on: stdout
carries the compiled JSON, and the exit code distinguishes success, parse
failure, and compile failure.
"""

import io
import json

from phisql import cli


def _invoke(*args):
    out, err = io.StringIO(), io.StringIO()
    code = cli.run(list(args), out, err)
    return code, out.getvalue(), err.getvalue()


def _write(tmp_path, name, body):
    file = tmp_path / name
    file.write_text(body, encoding="utf-8")
    return file


def test_compiles_valid_policy_to_json_on_stdout(tmp_path):
    file = _write(tmp_path, "ssn.phisql", "REDACT SSN WITH MASK;\n")
    code, out, err = _invoke(str(file))
    assert code == cli.EXIT_OK, err
    payload = json.loads(out)
    strategy = payload["identifiers"]["ssn"]["ssnFilterStrategies"][0]
    assert strategy["strategy"] == "MASK"


def test_parse_error_exits_with_parse_code(tmp_path):
    # Missing the semicolon after the POLICY declaration is a grammar error.
    file = _write(tmp_path, "bad.phisql", "POLICY x\nREDACT SSN WITH MASK;\n")
    code, out, err = _invoke(str(file))
    assert code == cli.EXIT_PARSE_ERROR
    assert "parse error" in err


def test_unknown_entity_exits_with_compile_code(tmp_path):
    file = _write(tmp_path, "sem.phisql", "REDACT NOT_AN_ENTITY WITH MASK;\n")
    code, out, err = _invoke(str(file))
    assert code == cli.EXIT_COMPILE_ERROR
    assert "compile error" in err


def test_policy_name_mismatch_exits_with_compile_code(tmp_path):
    file = _write(tmp_path, "mismatch.phisql",
                  "POLICY something_else;\nREDACT SSN WITH MASK;\n")
    code, out, err = _invoke(str(file))
    assert code == cli.EXIT_COMPILE_ERROR


def test_missing_argument_is_usage_error():
    code, out, err = _invoke()
    assert code == cli.EXIT_USAGE
    assert "usage" in err


def test_missing_file_is_usage_error(tmp_path):
    code, out, err = _invoke(str(tmp_path / "does-not-exist.phisql"))
    assert code == cli.EXIT_USAGE
