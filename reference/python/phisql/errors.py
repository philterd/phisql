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
"""Exceptions raised by the PhiSQL reference implementation."""


class ParseException(Exception):
    """Raised when PhiSQL source fails to lex or parse.

    The message is prefixed with ``line L:C`` (1-based line, 0-based column,
    matching the reference parser) so callers can surface diagnostics.
    """


class CompileException(Exception):
    """Raised when a parsed PhiSQL document cannot be compiled."""
