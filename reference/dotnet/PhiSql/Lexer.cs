// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

namespace Philterd.PhiSql;

/// <summary>A lexical token. <see cref="Column"/> is 0-based, matching ANTLR.</summary>
public readonly record struct Token(string Type, string Text, int Line, int Column);

/// <summary>
/// Hand-written lexer for PhiSQL v1.0 — a direct transcription of the lexer
/// rules in <c>spec/v1.0/grammar/PhiSQL.g4</c>. Keywords and the boolean
/// literals are case-insensitive; identifiers preserve their original case. As
/// in ANTLR, a word is lexed with maximal munch and only becomes a keyword when
/// it matches one exactly, so <c>MASK</c> is a keyword while <c>MASKED</c> is an ID.
/// </summary>
public static class Lexer
{
    private static readonly HashSet<string> Keywords = new(StringComparer.Ordinal)
    {
        // Redaction statement keywords.
        "POLICY", "DESCRIPTION", "CONFIGURE", "CRYPTO", "FPE", "KEY", "TWEAK",
        "FROM", "ENV", "SPLITTING", "PDF", "POSTFILTERS", "ANALYSIS",
        "GRAPHICAL", "BOX", "REDACT", "DEIDENTIFY", "IGNORE", "TERMS",
        "PATTERN", "FOR", "WITH", "WHERE", "AS", "AND", "OR", "CONFIDENCE",
        // Custom-identifier / dictionary / section keywords.
        "DEFINE", "MATCHING", "GROUP", "CASE", "SENSITIVE", "INSENSITIVE",
        "DICTIONARY", "SECTION", "START", "END", "FUZZY", "SENSITIVITY",
        "CAPITALIZED", "OPTIONS",
        // PhEye detection keywords.
        "DETECT", "PHEYE", "LABELS", "ENDPOINT",
        // Discovery keywords.
        "FIND", "PII", "DISCOVER", "ENTITIES", "SCAN", "IN", "SELECT", "BY",
        "LIMIT", "COUNT", "AVG", "SUM", "MIN", "MAX",
        // Custom-identifier reference keyword.
        "IDENTIFIER",
        // Strategy keywords.
        "MASK", "ENCRYPT", "FPE_ENCRYPT", "HASH_SHA256", "RANDOM_REPLACE",
        "STATIC_REPLACE", "LAST_4", "TRUNCATE_TO_YEAR", "TRUNCATE", "SHIFT",
        "RELATIVE", "ABBREVIATE",
    };

    private static readonly HashSet<char> OneCharOps = new(">=<;(),[].*");

    private static bool IsIdStart(char ch) => char.IsAsciiLetter(ch) || ch == '_';

    private static bool IsIdPart(char ch) => char.IsAsciiLetterOrDigit(ch) || ch == '_';

    /// <summary>
    /// Lexes <paramref name="source"/> into a list of tokens terminated by an
    /// <c>EOF</c> token. Throws <see cref="ParseException"/> (with a
    /// <c>line L:C</c> prefix) on a lexical error.
    /// </summary>
    public static List<Token> Tokenize(string source)
    {
        var tokens = new List<Token>();
        int i = 0, n = source.Length, line = 1, col = 0;

        static ParseException Err(string message, int atLine, int atCol) =>
            new($"line {atLine}:{atCol} {message}");

        while (i < n)
        {
            char ch = source[i];

            // Whitespace.
            if (ch is ' ' or '\t' or '\r') { i++; col++; continue; }
            if (ch == '\n') { i++; line++; col = 0; continue; }

            // Line comment: '--' to end of line.
            if (ch == '-' && i + 1 < n && source[i + 1] == '-')
            {
                while (i < n && source[i] != '\n') { i++; col++; }
                continue;
            }

            // Block comment: '/* ... */'.
            if (ch == '/' && i + 1 < n && source[i + 1] == '*')
            {
                int startLine = line, startCol = col;
                i += 2; col += 2;
                bool closed = false;
                while (i < n)
                {
                    if (source[i] == '*' && i + 1 < n && source[i + 1] == '/')
                    {
                        i += 2; col += 2; closed = true; break;
                    }
                    if (source[i] == '\n') { line++; col = 0; } else { col++; }
                    i++;
                }
                if (!closed) throw Err("unterminated block comment", startLine, startCol);
                continue;
            }

            // Identifiers and keywords.
            if (IsIdStart(ch))
            {
                int startCol = col, start = i;
                while (i < n && IsIdPart(source[i])) { i++; col++; }
                string word = source[start..i];
                string upper = word.ToUpperInvariant();
                if (upper is "TRUE" or "FALSE")
                    tokens.Add(new Token("BOOLEAN_LITERAL", word, line, startCol));
                else if (Keywords.Contains(upper))
                    tokens.Add(new Token(upper, word, line, startCol));
                else
                    tokens.Add(new Token("ID", word, line, startCol));
                continue;
            }

            // String literal: single-quoted with backslash escapes.
            if (ch == '\'')
            {
                int startLine = line, startCol = col, start = i;
                i++; col++;
                bool terminated = false;
                while (i < n)
                {
                    char c = source[i];
                    if (c == '\\')
                    {
                        if (i + 1 >= n) break;
                        i += 2; col += 2; continue;
                    }
                    if (c == '\'') { i++; col++; terminated = true; break; }
                    if (c is '\r' or '\n') break;
                    i++; col++;
                }
                if (!terminated) throw Err("unterminated string literal", startLine, startCol);
                tokens.Add(new Token("STRING_LITERAL", source[start..i], line, startCol));
                continue;
            }

            // Numeric literal: optional leading minus, digits, optional fraction.
            if (char.IsAsciiDigit(ch) || (ch == '-' && i + 1 < n && char.IsAsciiDigit(source[i + 1])))
            {
                int startCol = col, start = i;
                if (source[i] == '-') { i++; col++; }
                while (i < n && char.IsAsciiDigit(source[i])) { i++; col++; }
                if (i < n && source[i] == '.' && i + 1 < n && char.IsAsciiDigit(source[i + 1]))
                {
                    i++; col++;
                    while (i < n && char.IsAsciiDigit(source[i])) { i++; col++; }
                }
                tokens.Add(new Token("NUMERIC_LITERAL", source[start..i], line, startCol));
                continue;
            }

            // Operators and punctuation.
            if (i + 1 < n && (source[i..(i + 2)] is ">=" or "<="))
            {
                tokens.Add(new Token(source[i..(i + 2)], source[i..(i + 2)], line, col));
                i += 2; col += 2; continue;
            }
            if (OneCharOps.Contains(ch))
            {
                tokens.Add(new Token(ch.ToString(), ch.ToString(), line, col));
                i++; col++; continue;
            }

            throw Err($"token recognition error at: '{ch}'", line, col);
        }

        tokens.Add(new Token("EOF", "<EOF>", line, col));
        return tokens;
    }
}
