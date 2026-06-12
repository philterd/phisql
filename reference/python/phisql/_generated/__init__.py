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
ANTLR-generated lexer, parser, and visitor for PhiSQL v1.0.

The modules in this package are generated from the canonical grammar at
``spec/v1.0/grammar/PhiSQL.g4`` by ``scripts/generate_parser.sh``. Do not edit
them by hand: change the grammar and regenerate. They are committed (rather than
built at install time) so that installing and testing this package stays
pure-Python; CI regenerates and diffs them so the grammar stays the single
source of truth.
"""
