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
Verifies that the canonical redaction policy schema is readable and that the
selected version, the version reported at runtime, and the schema's own
``version``/``$id`` agree.
"""

import json

from phisql import get_schema, get_supported_schema_version


def test_version_is_non_empty():
    version = get_supported_schema_version()
    assert version.strip()


def test_schema_matches_reported_version():
    schema = get_schema()
    assert schema.strip()

    root = json.loads(schema)

    # The schema's own version field must match what the module reports.
    assert root.get("version") == get_supported_schema_version()

    # The $id encodes the same version in its path.
    assert f"/{get_supported_schema_version()}/" in root.get("$id", "")
