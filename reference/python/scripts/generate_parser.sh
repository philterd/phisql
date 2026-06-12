#!/usr/bin/env bash
#
# Copyright 2026 Philterd, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# See ../../../LICENSE.
#
# Regenerates the ANTLR parser for the Python reference implementation from the
# canonical grammar at spec/v1.0/grammar/PhiSQL.g4.
#
# The grammar is the single source of truth. The generated lexer/parser/visitor
# are committed under phisql/_generated/ so that `pip install` and `pytest` stay
# pure-Python (no Java needed to use or test the package). CI regenerates with
# this script and runs `git diff --exit-code` over phisql/_generated/, so any
# drift between the grammar and the committed parser fails the build. That is
# the same "the parser cannot drift from the grammar" guarantee the Java
# reference gets from generating at build time; here it is enforced in CI.
#
# Requirements: a JDK (java on PATH). The pinned ANTLR tool jar is downloaded to
# a gitignored cache on first run, or supplied via the ANTLR_JAR environment
# variable. The ANTLR runtime version in pyproject.toml must match ANTLR_VERSION
# below; ANTLR generates code only the matching runtime can load.

set -euo pipefail

ANTLR_VERSION="4.13.2"

# reference/python (this script lives in reference/python/scripts).
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "${PROJECT_DIR}/../.." && pwd)"

GRAMMAR="${REPO_ROOT}/spec/v1.0/grammar/PhiSQL.g4"
OUT_DIR="${PROJECT_DIR}/phisql/_generated"
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

# Generate into a clean temp dir, then copy only the Python sources we keep.
# (-Xexact-output-dir writes directly into TMP_OUT rather than a grammar-named
# subdirectory; the .interp/.tokens byproducts are not copied.)
TMP_OUT="$(mktemp -d)"
trap 'rm -rf "${TMP_OUT}"' EXIT

java -jar "${JAR}" \
    -Dlanguage=Python3 \
    -visitor \
    -o "${TMP_OUT}" \
    -Xexact-output-dir \
    "${GRAMMAR}"

mkdir -p "${OUT_DIR}"
for f in PhiSQLLexer.py PhiSQLParser.py PhiSQLListener.py PhiSQLVisitor.py; do
    cp "${TMP_OUT}/${f}" "${OUT_DIR}/${f}"
done

echo "Regenerated parser in ${OUT_DIR} from ${GRAMMAR#"${REPO_ROOT}/"}"
