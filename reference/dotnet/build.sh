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
# Builds and tests the PhiSQL .NET reference implementation inside the official
# .NET 10 SDK Docker image, so the only requirement on the host is Docker — no
# .NET SDK needed.
#
# Usage: ./build.sh [Release|Debug]   (default: Release)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
config="${1:-Release}"
image="mcr.microsoft.com/dotnet/sdk:10.0"

if ! command -v docker >/dev/null 2>&1; then
  echo "error: docker is not installed or not on PATH." >&2
  exit 1
fi

# The build embeds spec/ and schema/ from the repository root, and the tests
# read spec/v1.0/examples, so the whole repo is mounted (not just
# reference/dotnet). The container runs as the host user so build output
# (bin/obj) is not left root-owned; HOME=/tmp gives the SDK a writable cache.
exec docker run --rm \
  -u "$(id -u):$(id -g)" \
  -e HOME=/tmp \
  -e DOTNET_CLI_TELEMETRY_OPTOUT=1 \
  -e DOTNET_NOLOGO=1 \
  -e BUILD_CONFIG="$config" \
  -v "$repo":/src \
  -w /src/reference/dotnet \
  "$image" \
  bash -ec '
    echo "==> Building the library (Philterd.PhiSql) [$BUILD_CONFIG]"
    dotnet build PhiSql/PhiSql.csproj -c "$BUILD_CONFIG"
    echo "==> Building the CLI (phisql) [$BUILD_CONFIG]"
    dotnet build PhiSql.Cli/PhiSql.Cli.csproj -c "$BUILD_CONFIG"
    echo "==> Running the tests [$BUILD_CONFIG]"
    dotnet test PhiSql.Tests/PhiSql.Tests.csproj -c "$BUILD_CONFIG"
    echo "==> Done."
  '
