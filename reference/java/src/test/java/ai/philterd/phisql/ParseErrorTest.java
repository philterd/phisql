/*
 * Copyright 2026 Philterd, LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ai.philterd.phisql;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies that malformed PhiSQL produces a {@link PhiSQL.ParseException} with
 * error messages that include line and column. This is the error-reporting
 * surface implementations rely on for IDE integration and CLI diagnostics.
 */
class ParseErrorTest {

    @Test
    void rejectsUnknownStatementKeyword() {
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse("REDAKT SSN WITH MASK;")
        );
        assertHasLineAndColumn(ex);
    }

    @Test
    void rejectsUnknownStrategyName() {
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse("REDACT SSN WITH NOTASTRATEGY;")
        );
        assertHasLineAndColumn(ex);
    }

    @Test
    void rejectsMissingSemicolon() {
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse("REDACT SSN WITH MASK")
        );
        assertHasLineAndColumn(ex);
    }

    @Test
    void rejectsMalformedNamedArg() {
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse("REDACT SSN WITH MASK(=value);")
        );
        assertHasLineAndColumn(ex);
    }

    @Test
    void rejectsCustomIdentifierWithoutClassification() {
        // IDENTIFIER must be followed by ('<classification>').
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse("REDACT IDENTIFIER WITH MASK;")
        );
        assertHasLineAndColumn(ex);
    }

    @Test
    void errorMessageReportsCorrectLineNumber() {
        // Three statements; the typo is on line 3.
        String source = """
                POLICY support_tickets;
                REDACT SSN WITH MASK;
                REDAKT EMAIL_ADDRESS WITH MASK;
                """;
        PhiSQL.ParseException ex = assertThrows(
                PhiSQL.ParseException.class,
                () -> PhiSQL.parse(source)
        );
        assertTrue(
                ex.getMessage().contains("line 3:"),
                "Expected error on line 3, got: " + ex.getMessage()
        );
    }

    private static void assertHasLineAndColumn(PhiSQL.ParseException ex) {
        assertTrue(
                ex.getMessage().matches("(?s)line \\d+:\\d+.*"),
                "Expected 'line N:M' format, got: " + ex.getMessage()
        );
    }
}
