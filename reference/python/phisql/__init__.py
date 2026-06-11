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
PhiSQL reference implementation (Python).

The parser mirrors ``spec/v1.0/grammar/PhiSQL.g4`` and the compiler is driven
by the catalog files under ``spec/v1.0/catalog/``. This package is a sibling of
the Java reference implementation and produces the same Phileas JSON output.

Quick start::

    from phisql import Compiler

    result = Compiler().compile("POLICY ssn_only; REDACT SSN WITH MASK;")
    print(result.policy_name())      # "ssn_only"
    print(result.to_json_string())   # Phileas JSON policy
"""

from .catalog import Catalog
from .compiler import Compiler, CompileResult
from .errors import CompileException, ParseException
from .phisql import parse
from .policy_schema import (
    SUPPORTED_SCHEMA_VERSION,
    get_schema,
    get_supported_schema_version,
)

__version__ = "1.0.0"

__all__ = [
    "Catalog",
    "Compiler",
    "CompileResult",
    "CompileException",
    "ParseException",
    "parse",
    "get_schema",
    "get_supported_schema_version",
    "SUPPORTED_SCHEMA_VERSION",
    "__version__",
]
