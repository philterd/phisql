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
Parses every example file under spec/v1.0/examples/ to verify the parser stays
in sync with the spec. New examples added to the spec are automatically
covered.
"""

import pytest

from phisql import parse
from conftest import example_phisql_files


@pytest.mark.parametrize("source_path", example_phisql_files(), ids=lambda p: p.name)
def test_every_example_parses(source_path):
    parse(source_path.read_text(encoding="utf-8"))
