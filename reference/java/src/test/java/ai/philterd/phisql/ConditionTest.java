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

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Verifies how WHERE predicates compile to Phileas conditions (RFC #58): {@code =}
 * is emitted as {@code ==}, and OR and parentheses produce a compile warning.
 */
class ConditionTest {

    private static String condition(CompileResult result) {
        return result.policyJson().path("identifiers").path("ssn")
                .path("ssnFilterStrategies").get(0).path("condition").asText();
    }

    @Test
    void equalsCompilesToDoubleEquals() {
        CompileResult r = new Compiler().compile("REDACT SSN WITH MASK WHERE CONFIDENCE = 0.75;");
        assertEquals("confidence == 0.75", condition(r));
        assertEquals(List.of(), r.warnings());
    }

    @Test
    void otherOperatorsAreUnchanged() {
        for (String op : List.of(">", ">=", "<", "<=")) {
            CompileResult r = new Compiler().compile("REDACT SSN WITH MASK WHERE CONFIDENCE " + op + " 0.5;");
            assertEquals("confidence " + op + " 0.5", condition(r));
        }
    }

    @Test
    void andDoesNotWarn() {
        CompileResult r = new Compiler().compile(
                "REDACT SSN WITH MASK WHERE CONFIDENCE > 0.5 AND CONFIDENCE < 0.9;");
        assertEquals("confidence > 0.5 and confidence < 0.9", condition(r));
        assertEquals(List.of(), r.warnings());
    }

    @Test
    void orWarns() {
        CompileResult r = new Compiler().compile(
                "REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        assertEquals(List.of(Compiler.OR_WARNING), r.warnings());
    }

    @Test
    void parenthesesAndOrWarnOnceEachPerDocument() {
        CompileResult r = new Compiler().compile(
                "REDACT SSN WITH MASK WHERE (CONFIDENCE > 0.5 AND CONFIDENCE < 0.9) OR CONFIDENCE = 1.0;\n"
                        + "REDACT EIN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        assertEquals(List.of(Compiler.OR_WARNING, Compiler.PAREN_WARNING), r.warnings());
    }

    @Test
    void detectAndDefineIdentifierPredicatesAreScanned() {
        CompileResult detect = new Compiler().compile(
                "DETECT PHEYE WITH REDACT WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        assertEquals(List.of(Compiler.OR_WARNING), detect.warnings());
        CompileResult identifier = new Compiler().compile(
                "DEFINE IDENTIFIER 'acct' MATCHING '\\d{6}' WITH REDACT WHERE (CONFIDENCE > 0.5);");
        assertEquals(List.of(Compiler.PAREN_WARNING), identifier.warnings());
    }
}
