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
Access to the canonical redaction policy JSON Schema bundled in this package.

The schema is authored in this repository at ``schema/<version>/schema.json``
and is the contract PhiSQL compiles to and Phileas executes against. The build
copies a single version of it into the package (``phisql/_data/schema/...``),
selected by :data:`SUPPORTED_SCHEMA_VERSION`, so an application that depends on
``phisql`` can read the schema without checking out this repository or fetching
it over the network.

This mirrors the Java reference's ``ai.philterd.phisql.PolicySchema``::

    Java                                   Python
    ----                                   ------
    PolicySchema.getSupportedSchemaVersion()   PolicySchema.get_supported_schema_version()
    PolicySchema.getSchema()                   PolicySchema.get_schema()
"""

from __future__ import annotations

import json

from . import _paths

#: Version of the canonical redaction policy schema this implementation targets.
#: The Java reference selects this via the ``redaction.policy.schema.version``
#: Maven property; here it is a module constant. Keep the two in sync.
SUPPORTED_SCHEMA_VERSION = "1.0.0"


class PolicySchema:
    """The canonical redaction policy JSON Schema bundled with this library.

    The Java reference exposes the same surface as a class with static methods;
    this mirrors it so an application can retrieve the schema from the library:

        >>> from phisql import PolicySchema
        >>> PolicySchema.get_supported_schema_version()
        '1.0.0'
        >>> schema_text = PolicySchema.get_schema()        # raw JSON string
        >>> schema_obj = PolicySchema.get_schema_dict()    # parsed dict
    """

    @staticmethod
    def get_supported_schema_version() -> str:
        """Returns the version of the bundled schema, e.g. ``"1.0.0"``."""
        return SUPPORTED_SCHEMA_VERSION

    @staticmethod
    def get_schema() -> str:
        """Returns the full bundled schema as a JSON string (as Java does)."""
        return _paths.schema_file(SUPPORTED_SCHEMA_VERSION).read_text(encoding="utf-8")

    @staticmethod
    def get_schema_dict() -> dict:
        """Returns the bundled schema parsed into a ``dict`` (Python convenience)."""
        return json.loads(PolicySchema.get_schema())


# Module-level aliases, for callers that prefer functions over the class.
def get_supported_schema_version() -> str:
    """Returns the version of the bundled schema, e.g. ``"1.0.0"``."""
    return PolicySchema.get_supported_schema_version()


def get_schema() -> str:
    """Returns the full bundled schema as a JSON string."""
    return PolicySchema.get_schema()


def get_schema_dict() -> dict:
    """Returns the bundled schema parsed into a ``dict``."""
    return PolicySchema.get_schema_dict()
