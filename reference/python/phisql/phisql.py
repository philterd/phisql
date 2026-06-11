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
Entry point for parsing PhiSQL source into an AST.

Behavior is defined by the grammar at ``spec/v1.0/grammar/PhiSQL.g4`` and by
the catalog files under ``spec/v1.0/catalog/`` (consumed by the compiler).
"""

from __future__ import annotations

from . import ast, parser
from .errors import ParseException

__all__ = ["parse", "ParseException"]


def parse(source: str) -> ast.Document:
    """Parses PhiSQL source into a document AST.

    :raises ParseException: on any syntax error, with a ``line L:C`` prefix.
    """
    return parser.parse(source)
