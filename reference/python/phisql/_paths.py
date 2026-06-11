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

The Java reference packs the spec ``catalog/*.yaml`` files and the canonical
``schema/<version>/schema.json`` into its JAR at build time (the Maven
``copy-resources`` executions in ``reference/java/pom.xml``) so it does not
depend on the spec being checked out at runtime. This Python reference does the
same: the build step in ``setup.py`` copies those files into ``phisql/_data/``,
mirroring the JAR's ``spec/...`` and ``schema/...`` layout, so an installed
wheel is self-contained.

Resolution order for the "spec root" (a directory containing ``spec/`` and
``schema/``):

1. ``PHISQL_SPEC_ROOT`` — explicit override, for running against a checkout.
2. The bundled ``phisql/_data`` directory — present in a built/installed wheel.
3. The repository tree — found by walking up from this file. This lets the
   tests and a source checkout work without first running the build step.

The repo stays the single source of truth; ``phisql/_data`` is a gitignored
build artifact, exactly like the Java ``target/`` resources.
"""

import os
from pathlib import Path

_CATALOG_REL = Path("spec") / "v1.0" / "catalog"
_PACKAGE_DIR = Path(__file__).resolve().parent
_BUNDLED_DATA_DIR = _PACKAGE_DIR / "_data"


def spec_root() -> Path:
    """Returns the root directory that contains ``spec/`` and ``schema/``."""
    override = os.environ.get("PHISQL_SPEC_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
        if (root / _CATALOG_REL).is_dir():
            return root
        raise FileNotFoundError(
            f"PHISQL_SPEC_ROOT={root} does not contain {_CATALOG_REL}"
        )

    # Data bundled into the package at build time (the installed-wheel case).
    if (_BUNDLED_DATA_DIR / _CATALOG_REL).is_dir():
        return _BUNDLED_DATA_DIR

    # Fall back to the repository tree (running from a source checkout).
    for parent in _PACKAGE_DIR.parents:
        if (parent / _CATALOG_REL).is_dir():
            return parent

    raise FileNotFoundError(
        "Could not locate the PhiSQL spec data. It is normally bundled into the "
        "package at build time (phisql/_data); when running from a source "
        f"checkout, an ancestor directory must contain {_CATALOG_REL}. Set "
        "PHISQL_SPEC_ROOT to the repository root to override."
    )


def catalog_dir() -> Path:
    """Returns the ``spec/v1.0/catalog`` directory."""
    return spec_root() / _CATALOG_REL


def schema_file(version: str) -> Path:
    """Returns the path to ``schema/<version>/schema.json``."""
    return spec_root() / "schema" / version / "schema.json"
