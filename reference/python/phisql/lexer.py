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
Hand-written lexer for PhiSQL v1.0.

This is a direct transcription of the lexer rules in
``spec/v1.0/grammar/PhiSQL.g4``. Keywords and the boolean literals are
case-insensitive (the grammar sets ``caseInsensitive = true``); user-defined
identifiers preserve their original case. As in ANTLR, a word is lexed with
maximal munch and only converted to a keyword token when it matches a keyword
exactly, so ``MASK`` is the ``MASK`` keyword while ``MASKED`` is an ``ID``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ParseException

# Keyword spelling -> token type. The token type is the upper-case keyword.
# "IDENTIFIER" is the IDENTIFIER_KW keyword in the grammar; its token text is
# "IDENTIFIER", which is the type used here.
_KEYWORDS = {
    name: name
    for name in (
        # Redaction statement keywords.
        "POLICY", "DESCRIPTION", "CONFIGURE", "CRYPTO", "FPE", "KEY", "TWEAK",
        "FROM", "ENV", "SPLITTING", "PDF", "POSTFILTERS", "ANALYSIS",
        "GRAPHICAL", "BOX", "REDACT", "DEIDENTIFY", "IGNORE", "TERMS",
        "PATTERN", "FOR", "WITH", "WHERE", "AS", "AND", "OR", "CONFIDENCE",
        # Custom-identifier / dictionary / section keywords.
        "DEFINE", "MATCHING", "GROUP", "CASE", "SENSITIVE", "INSENSITIVE",
        "DICTIONARY", "SECTION", "START", "END", "FUZZY", "SENSITIVITY",
        "CAPITALIZED", "OPTIONS",
        # PhEye detection keywords.
        "DETECT", "PHEYE", "LABELS", "ENDPOINT",
        # Discovery keywords.
        "FIND", "PII", "DISCOVER", "ENTITIES", "SCAN", "IN", "SELECT", "BY",
        "LIMIT", "COUNT", "AVG", "SUM", "MIN", "MAX",
        # Custom-identifier reference keyword.
        "IDENTIFIER",
        # Strategy keywords.
        "MASK", "ENCRYPT", "FPE_ENCRYPT", "HASH_SHA256", "RANDOM_REPLACE",
        "STATIC_REPLACE", "LAST_4", "TRUNCATE_TO_YEAR", "TRUNCATE", "SHIFT",
        "RELATIVE", "ABBREVIATE",
    )
}

# Two-character operators must be tried before their single-character prefixes.
_TWO_CHAR_OPS = (">=", "<=")
_ONE_CHAR_OPS = set(">=<;(),[].*")


@dataclass(frozen=True)
class Token:
    type: str
    text: str
    line: int
    column: int  # 0-based, matching ANTLR's charPositionInLine

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Token({self.type!r}, {self.text!r}, {self.line}:{self.column})"


def _is_id_start(ch: str) -> bool:
    return ch.isascii() and (ch.isalpha() or ch == "_")


def _is_id_part(ch: str) -> bool:
    return ch.isascii() and (ch.isalnum() or ch == "_")


def tokenize(source: str) -> list:
    """Lexes ``source`` into a list of tokens, terminated by an ``EOF`` token.

    Raises ``ParseException`` (with ``line L:C`` prefix) on a lexical error,
    matching the reference parser's error-reporting surface.
    """
    tokens = []
    i = 0
    n = len(source)
    line = 1
    col = 0

    def error(message: str, at_line: int, at_col: int):
        raise ParseException(f"line {at_line}:{at_col} {message}")

    while i < n:
        ch = source[i]

        # Whitespace.
        if ch in " \t\r":
            i += 1
            col += 1
            continue
        if ch == "\n":
            i += 1
            line += 1
            col = 0
            continue

        # Comments.
        if ch == "-" and i + 1 < n and source[i + 1] == "-":
            # Line comment: '--' to end of line.
            while i < n and source[i] != "\n":
                i += 1
                col += 1
            continue
        if ch == "/" and i + 1 < n and source[i + 1] == "*":
            # Block comment: '/* ... */'.
            start_line, start_col = line, col
            i += 2
            col += 2
            closed = False
            while i < n:
                if source[i] == "*" and i + 1 < n and source[i + 1] == "/":
                    i += 2
                    col += 2
                    closed = True
                    break
                if source[i] == "\n":
                    line += 1
                    col = 0
                else:
                    col += 1
                i += 1
            if not closed:
                error("unterminated block comment", start_line, start_col)
            continue

        # Identifiers and keywords.
        if _is_id_start(ch):
            start_col = col
            start = i
            while i < n and _is_id_part(source[i]):
                i += 1
                col += 1
            word = source[start:i]
            upper = word.upper()
            if upper in ("TRUE", "FALSE"):
                tokens.append(Token("BOOLEAN_LITERAL", word, line, start_col))
            elif upper in _KEYWORDS:
                tokens.append(Token(_KEYWORDS[upper], word, line, start_col))
            else:
                tokens.append(Token("ID", word, line, start_col))
            continue

        # String literal: single-quoted with backslash escapes.
        if ch == "'":
            start_line, start_col = line, col
            start = i
            i += 1
            col += 1
            terminated = False
            while i < n:
                c = source[i]
                if c == "\\":
                    if i + 1 >= n:
                        break
                    i += 2
                    col += 2
                    continue
                if c == "'":
                    i += 1
                    col += 1
                    terminated = True
                    break
                if c in "\r\n":
                    break
                i += 1
                col += 1
            if not terminated:
                error("unterminated string literal", start_line, start_col)
            tokens.append(Token("STRING_LITERAL", source[start:i], line, start_col))
            continue

        # Numeric literal: optional leading minus, digits, optional fraction.
        if ch.isdigit() or (ch == "-" and i + 1 < n and source[i + 1].isdigit()):
            start_col = col
            start = i
            if source[i] == "-":
                i += 1
                col += 1
            while i < n and source[i].isdigit():
                i += 1
                col += 1
            if i < n and source[i] == "." and i + 1 < n and source[i + 1].isdigit():
                i += 1
                col += 1
                while i < n and source[i].isdigit():
                    i += 1
                    col += 1
            tokens.append(Token("NUMERIC_LITERAL", source[start:i], line, start_col))
            continue

        # Operators and punctuation.
        two = source[i:i + 2]
        if two in _TWO_CHAR_OPS:
            tokens.append(Token(two, two, line, col))
            i += 2
            col += 2
            continue
        if ch in _ONE_CHAR_OPS:
            tokens.append(Token(ch, ch, line, col))
            i += 1
            col += 1
            continue

        error(f"token recognition error at: '{ch}'", line, col)

    tokens.append(Token("EOF", "<EOF>", line, col))
    return tokens
