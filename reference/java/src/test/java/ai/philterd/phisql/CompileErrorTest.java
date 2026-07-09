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

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies that PhiSQL that parses successfully but cannot be compiled produces
 * a {@link Compiler.CompileException} with a useful message.
 */
class CompileErrorTest {

    @Test
    void rejectsUnknownEntityType() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT NOT_AN_ENTITY WITH MASK;")
        );
        assertTrue(ex.getMessage().contains("NOT_AN_ENTITY"),
                "Expected error to name the unknown entity: " + ex.getMessage());
    }

    @Test
    void passesThroughUncataloguedStrategyArgument() {
        // An argument the strategy catalog does not list is no longer an error:
        // it passes through to the Phileas JSON by its schema property name, so
        // any strategy field (salt, condition, truncateDirection, ...) is settable.
        Compiler compiler = new Compiler();
        JsonNode strategy = compiler.compile("REDACT SSN WITH MASK(salt=TRUE);")
                .policyJson().path("identifiers").path("ssn")
                .path("ssnFilterStrategies").path(0);
        assertTrue(strategy.path("salt").asBoolean(),
                "Uncatalogued strategy arg should pass through to JSON: " + strategy);
    }

    @Test
    void rejectsInvalidEnumValue() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SSN WITH STATIC_REPLACE(value='X', scope=invalid);")
        );
        assertTrue(ex.getMessage().toLowerCase().contains("scope")
                        || ex.getMessage().toLowerCase().contains("invalid"),
                "Expected error to identify the invalid enum value: " + ex.getMessage());
    }

    @Test
    void rejectsDateOnlyStrategyOnNonDateEntity() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SSN WITH SHIFT(days=30);")
        );
        assertTrue(ex.getMessage().contains("SHIFT") && ex.getMessage().contains("date-only"),
                "Expected a date-only strategy error: " + ex.getMessage());
    }

    @Test
    void allowsDateOnlyStrategyOnDate() {
        // Positive control: a date-only strategy on DATE compiles.
        JsonNode strategy = new Compiler().compile("REDACT DATE WITH SHIFT(days=30);")
                .policyJson().path("identifiers").path("date")
                .path("dateFilterStrategies").path(0);
        assertTrue(strategy.path("strategy").asText().equals("SHIFT"),
                "DATE + SHIFT should compile: " + strategy);
    }

    @Test
    void rejectsStaticReplaceWithoutValue() {
        // The catalog marks STATIC_REPLACE's `value` required; omitting it is a
        // semantic error rather than a malformed strategy.
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SURNAME WITH STATIC_REPLACE(scope=document);")
        );
        assertTrue(ex.getMessage().contains("STATIC_REPLACE requires argument 'value'"),
                "Expected a required-argument error: " + ex.getMessage());
    }

    @Test
    void allowsStaticReplaceWithValue() {
        // Positive control: STATIC_REPLACE with a value compiles.
        JsonNode strategy = new Compiler().compile("REDACT SURNAME WITH STATIC_REPLACE(value='Customer');")
                .policyJson().path("identifiers").path("surname")
                .path("surnameFilterStrategies").path(0);
        assertTrue(strategy.path("staticReplacement").asText().equals("Customer"),
                "STATIC_REPLACE with value should compile: " + strategy);
    }

    @Test
    void rejectsDuplicateGeneratorName() {
        // Two DEFINE GENERATOR statements with the same name would collide in the
        // single name-keyed generators object; that is a semantic error.
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile(
                        "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'A: {{token}}', timeoutMs = 1000);\n"
                        + "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'B: {{token}}', timeoutMs = 1000);")
        );
        assertTrue(ex.getMessage().contains("Duplicate generator name"),
                "Expected a duplicate-generator error: " + ex.getMessage());
    }

    @Test
    void allowsTwoDistinctGenerators() {
        // Positive control: distinct names both land in the generators block.
        JsonNode generators = new Compiler().compile(
                "DEFINE GENERATOR 'a' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);\n"
                + "DEFINE GENERATOR 'b' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);")
                .policyJson().path("generators");
        assertTrue(generators.has("a") && generators.has("b"),
                "Both generators should be present: " + generators);
    }
}
