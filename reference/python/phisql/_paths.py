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
Locates the spec catalog and schema files that drive this implementation.

The Java reference bundles the spec ``catalog/*.yaml`` files and the canonical
``schema/<version>/schema.json`` into its JAR at build time so it does not
depend on the spec being checked out at runtime. This Python reference, run
from within the repository, instead resolves those files directly from the
single source of truth in ``spec/`` and ``schema/`` — there is no copy of the
catalog or schema inside ``reference/python/``.

The repository root is found by walking up from this file until a directory
containing ``spec/v1.0/catalog`` is found. ``PHISQL_SPEC_ROOT`` overrides the
search (point it at a checkout's root) for installs outside the repo tree.
"""

import os
from pathlib import Path

_CATALOG_REL = Path("spec") / "v1.0" / "catalog"


def repo_root() -> Path:
    """Returns the repository root containing ``spec/`` and ``schema/``."""
    override = os.environ.get("PHISQL_SPEC_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if (root / _CATALOG_REL).is_dir():
            return root
        raise FileNotFoundError(
            f"PHISQL_SPEC_ROOT={root} does not contain {_CATALOG_REL}"
        )
    for parent in Path(__file__).resolve().parents:
        if (parent / _CATALOG_REL).is_dir():
            return parent
    raise FileNotFoundError(
        "Could not locate the PhiSQL spec; no ancestor directory contains "
        f"{_CATALOG_REL}. Set PHISQL_SPEC_ROOT to the repository root."
    )


def catalog_dir() -> Path:
    """Returns the ``spec/v1.0/catalog`` directory."""
    return repo_root() / _CATALOG_REL


def schema_file(version: str) -> Path:
    """Returns the path to ``schema/<version>/schema.json``."""
    return repo_root() / "schema" / version / "schema.json"
