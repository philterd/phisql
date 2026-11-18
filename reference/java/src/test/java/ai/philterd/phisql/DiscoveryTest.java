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
import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Verifies how the compiler reports discovery statements, which it does not
 * compile yet (#71): each one is skipped with a warning naming it and its line,
 * and a script with nothing else is a compile error rather than an empty policy.
 */
class DiscoveryTest {

    @Test
    void discoveryOnlyScriptIsACompileError() {
        Compiler.CompileException e = assertThrows(Compiler.CompileException.class,
                () -> new Compiler().compile(
                        "FIND PII IN 's3://prod-data/customers/'\n"
                                + "  WHERE entity_type IN ('SSN', 'CREDIT_CARD');\n"
                                + "SCAN IN 'file:///mnt/exports/';\n"));
        assertEquals("The script has only discovery statements (FIND PII at line 1, SCAN at line 3), "
                + "and discovery statements are not compiled to a redaction policy yet.", e.getMessage());
    }

    @Test
    void policyDeclarationAloneDoesNotMakeADiscoveryScriptCompile() {
        Compiler.CompileException e = assertThrows(Compiler.CompileException.class,
                () -> new Compiler().compile(
                        "POLICY findings_report;\n"
                                + "SELECT path, entity_type, COUNT(*) FROM phinder.findings GROUP BY path, entity_type;\n"));
        assertEquals("The script has only discovery statements (SELECT ... FROM findings at line 2), "
                + "and discovery statements are not compiled to a redaction policy yet.", e.getMessage());
    }

    @Test
    void mixedScriptCompilesTheRedactionStatementsAndWarnsForEachDiscoveryStatement() {
        CompileResult r = new Compiler().compile(
                "FIND PII IN 's3://prod-data/customers/';\n"
                        + "REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;\n"
                        + "\n"
                        + "DISCOVER ENTITIES IN 'gs://archive/';\n");
        assertEquals("MASK", r.policyJson().path("identifiers").path("ssn")
                .path("ssnFilterStrategies").get(0).path("strategy").asText());
        assertEquals(List.of(
                "FIND PII at line 1 was skipped: " + Compiler.DISCOVERY_WARNING,
                "DISCOVER ENTITIES at line 4 was skipped: " + Compiler.DISCOVERY_WARNING,
                Compiler.OR_WARNING), r.warnings());
    }
}
