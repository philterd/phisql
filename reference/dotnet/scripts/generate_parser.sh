#!/usr/bin/env bash
#
# Copyright 2026 Philterd, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See ../../../LICENSE.
#
# Regenerates the ANTLR parser for the .NET reference implementation from the
# canonical grammar at spec/v1.0/grammar/PhiSQL.g4.
#
# The grammar is the single source of truth. The generated lexer/parser/visitor
# are committed under PhiSql/Generated/ so that `dotnet build`/`dotnet test`
# stay self-contained (no Java needed to build or test the package). CI
# regenerates with this script and runs `git diff --exit-code` over
# PhiSql/Generated/, so any drift between the grammar and the committed parser
# fails the build. That is the same "the parser cannot drift from the grammar"
# guarantee the Java reference gets from generating at build time; here it is
# enforced in CI.
#
# Requirements: a JDK (java on PATH). The pinned ANTLR tool jar is downloaded to
# a gitignored cache on first run, or supplied via the ANTLR_JAR environment
# variable. The Antlr4.Runtime.Standard package version in PhiSql/PhiSql.csproj
# must be compatible with ANTLR_VERSION below; generated code only loads on a
# compatible runtime.

set -euo pipefail

ANTLR_VERSION="4.13.2"
NAMESPACE="Philterd.PhiSql.Generated"

# reference/dotnet (this script lives in reference/dotnet/scripts).
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/../.." && pwd)"

# ANTLR records the grammar path exactly as passed on the command line in the
# generated file headers. Invoke it from REPO_ROOT with this relative path so
# the headers are identical on every machine (otherwise an absolute path leaks
# in and the CI drift-check diffs against a developer's local path).
GRAMMAR_REL="spec/v1.0/grammar/PhiSQL.g4"
GRAMMAR="${REPO_ROOT}/${GRAMMAR_REL}"
OUT_DIR="${PROJECT_DIR}/PhiSql/Generated"
CACHE_DIR="${PROJECT_DIR}/.antlr"
JAR="${ANTLR_JAR:-${CACHE_DIR}/antlr-${ANTLR_VERSION}-complete.jar}"

if [[ ! -f "${GRAMMAR}" ]]; then
    echo "error: grammar not found at ${GRAMMAR}" >&2
    exit 1
fi

if ! command -v java >/dev/null 2>&1; then
    echo "error: java is required to regenerate the parser (it runs the ANTLR tool)." >&2
    exit 1
fi

# Fetch the pinned ANTLR complete jar into the cache if it is not present and
# the caller did not point ANTLR_JAR at one already.
if [[ ! -f "${JAR}" ]]; then
    mkdir -p "${CACHE_DIR}"
    url="https://www.antlr.org/download/antlr-${ANTLR_VERSION}-complete.jar"
    echo "Downloading ANTLR ${ANTLR_VERSION} tool to ${JAR}"
    curl -fsSL -o "${JAR}" "${url}"
fi

# Generate into a clean temp dir, then copy only the C# sources we keep.
# (-Xexact-output-dir writes directly into TMP_OUT rather than a grammar-named
# subdirectory; the .interp/.tokens byproducts are not copied.)
TMP_OUT="$(mktemp -d)"
trap 'rm -rf "${TMP_OUT}"' EXIT

( cd "${REPO_ROOT}" && java -jar "${JAR}" \
    -Dlanguage=CSharp \
    -visitor \
    -package "${NAMESPACE}" \
    -o "${TMP_OUT}" \
    -Xexact-output-dir \
    "${GRAMMAR_REL}" )

mkdir -p "${OUT_DIR}"
for f in PhiSQLLexer.cs PhiSQLParser.cs PhiSQLBaseListener.cs PhiSQLListener.cs \
         PhiSQLBaseVisitor.cs PhiSQLVisitor.cs; do
    cp "${TMP_OUT}/${f}" "${OUT_DIR}/${f}"
done

echo "Regenerated parser in ${OUT_DIR} from ${GRAMMAR_REL}"
