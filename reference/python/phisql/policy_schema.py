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
Access to the canonical redaction policy JSON Schema.

The schema is authored in this repository at ``schema/<version>/schema.json``
and is the contract PhiSQL compiles to and Phileas executes against. This
module selects a single version (see :data:`SUPPORTED_SCHEMA_VERSION`) and
reads it from the repository, mirroring the Java reference's ``PolicySchema``.
"""

from __future__ import annotations

from . import _paths

#: Version of the canonical redaction policy schema this implementation targets.
#: The Java reference selects this via the ``redaction.policy.schema.version``
#: Maven property; here it is a module constant. Keep the two in sync.
SUPPORTED_SCHEMA_VERSION = "1.0.0"


def get_supported_schema_version() -> str:
    """Returns the version of the supported schema, e.g. ``"1.0.0"``."""
    return SUPPORTED_SCHEMA_VERSION


def get_schema() -> str:
    """Returns the full schema JSON as a string."""
    path = _paths.schema_file(SUPPORTED_SCHEMA_VERSION)
    return path.read_text(encoding="utf-8")
