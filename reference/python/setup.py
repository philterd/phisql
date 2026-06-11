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
Build-time packaging of the PhiSQL spec data.

This is the Python equivalent of the two ``maven-resources-plugin``
``copy-resources`` executions in ``reference/java/pom.xml``: it copies the spec
catalog YAML files and the canonical redaction policy schema JSON into the
package as data, so the built wheel is self-contained and does not depend on
the repository being checked out at runtime.

- catalog: ``../../spec/v1.0/catalog/*.yaml``  ->  ``phisql/_data/spec/v1.0/catalog/``
- schema:  ``../../schema/<version>/schema.json`` -> ``phisql/_data/schema/<version>/``

The schema version is the single value ``SUPPORTED_SCHEMA_VERSION`` in
``phisql/policy_schema.py`` (the analogue of the Maven
``redaction.policy.schema.version`` property). The repository remains the
single source of truth; ``phisql/_data`` is a gitignored build artifact, like
the Java ``target/`` resources.

All other project metadata lives in ``pyproject.toml``.
"""

import re
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

_HERE = Path(__file__).parent.resolve()
_REPO_ROOT = _HERE.parent.parent  # reference/python -> reference -> repo root
_PACKAGE_DIR = _HERE / "phisql"
_DATA_DIR = _PACKAGE_DIR / "_data"


def _schema_version() -> str:
    """Reads SUPPORTED_SCHEMA_VERSION from policy_schema.py without importing it."""
    text = (_PACKAGE_DIR / "policy_schema.py").read_text(encoding="utf-8")
    match = re.search(r'SUPPORTED_SCHEMA_VERSION\s*=\s*"([^"]+)"', text)
    if not match:
        raise RuntimeError("Could not find SUPPORTED_SCHEMA_VERSION in policy_schema.py")
    return match.group(1)


def _copy_license() -> None:
    """Copies the repo-root LICENSE into this project so it ships in the dist.

    The Apache LICENSE lives at the repository root, outside this project
    directory, which packaging tools cannot reach. Copying it here (and
    declaring license-files = ["LICENSE"] in pyproject.toml) includes it in the
    sdist and wheel. No-op when the repo tree is absent (building from an sdist
    that already contains LICENSE).
    """
    license_src = _REPO_ROOT / "LICENSE"
    if license_src.is_file():
        shutil.copy2(license_src, _HERE / "LICENSE")


def _copy_spec_data() -> None:
    """Copies the catalog and schema from the repo into phisql/_data.

    No-op when the repository tree is not present (e.g. building from an sdist
    that already contains phisql/_data).
    """
    catalog_src = _REPO_ROOT / "spec" / "v1.0" / "catalog"
    schema_version = _schema_version()
    schema_src = _REPO_ROOT / "schema" / schema_version / "schema.json"

    if not catalog_src.is_dir():
        # Building from a distribution without the repo tree; the data should
        # already be bundled under phisql/_data. Nothing to copy.
        return

    # catalog/*.yaml -> _data/spec/v1.0/catalog/ (verbatim copy)
    catalog_dst = _DATA_DIR / "spec" / "v1.0" / "catalog"
    catalog_dst.mkdir(parents=True, exist_ok=True)
    for yaml_file in sorted(catalog_src.glob("*.yaml")):
        shutil.copy2(yaml_file, catalog_dst / yaml_file.name)

    # schema/<version>/schema.json -> _data/schema/<version>/ (byte-identical)
    schema_dst = _DATA_DIR / "schema" / schema_version
    schema_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(schema_src, schema_dst / "schema.json")


class BuildPyWithSpecData(build_py):
    """Runs the spec-data copy before the normal build, so it lands in the wheel."""

    def run(self):
        _copy_spec_data()
        super().run()


# Also copy at setup.py load time so that any command (sdist, egg_info, develop)
# packages the data and license, not just bdist_wheel.
_copy_license()
_copy_spec_data()

setup(cmdclass={"build_py": BuildPyWithSpecData})
