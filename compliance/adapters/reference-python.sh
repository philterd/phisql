#!/usr/bin/env bash
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
#
# Conformance adapter for the PhiSQL Python reference implementation.
#
# The runner invokes this script with a single argument, the path to a .phisql
# file. It must print the compiled Phileas JSON to stdout and exit 0, or exit 2
# (parse error) / 3 (semantic error). All of that behavior lives in the CLI;
# this wrapper just runs `python -m phisql` with the package on PYTHONPATH and
# forwards the argument and exit code.
#
# Requires PyYAML to be importable (pip install -e reference/python, or
# pip install pyyaml).
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"

exec env PYTHONPATH="$repo/reference/python${PYTHONPATH:+:$PYTHONPATH}" \
  "${PYTHON:-python3}" -m phisql "$1"
