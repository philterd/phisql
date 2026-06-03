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
# Conformance adapter for the PhiSQL Java reference implementation.
#
# The runner invokes this script with a single argument, the path to a .phisql
# file. It must print the compiled Phileas JSON to stdout and exit 0, or exit 2
# (parse error) / 3 (semantic error). All of that behavior lives in the CLI; this
# wrapper just locates the runnable jar and forwards the argument and exit code.
#
# Build the jar first:
#   (cd reference && mvn -Pcli -DskipTests package)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"

jar="$(ls "$repo"/reference/target/phisql-*-cli.jar 2>/dev/null | head -n 1 || true)"
if [[ -z "$jar" ]]; then
  echo "reference CLI jar not found under reference/target/" >&2
  echo "build it with: (cd reference && mvn -Pcli -DskipTests package)" >&2
  exit 70
fi

exec java -jar "$jar" "$1"
