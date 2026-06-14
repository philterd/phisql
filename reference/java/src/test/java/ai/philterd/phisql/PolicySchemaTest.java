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
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies that the canonical redaction policy schema is bundled in the JAR and
 * that the bundled version, the version reported at runtime, and the schema's own
 * {@code version}/{@code $id} agree. This is the assertion that
 * PolicySchema.getSupportedSchemaVersion() and the packaged file cannot drift.
 */
class PolicySchemaTest {

    @Test
    void versionIsFilteredAndNonEmpty() {
        String version = PolicySchema.getSupportedSchemaVersion();
        assertFalse(version.isBlank(), "schema version should be filtered in at build time");
        assertFalse(version.startsWith("${"), "schema version property was not filtered");
    }

    @Test
    void schemaIsBundledAndMatchesReportedVersion() throws IOException {
        String schema = PolicySchema.getSchema();
        assertFalse(schema.isBlank(), "bundled schema should not be empty");

        JsonNode root = new ObjectMapper().readTree(schema);

        // The schema's own version field must match what PolicySchema reports.
        assertEquals(PolicySchema.getSupportedSchemaVersion(), root.path("version").asText(),
                "schema 'version' must match the bundled/reported version");

        // The $id encodes the same version in its path.
        assertTrue(root.path("$id").asText().contains("/" + PolicySchema.getSupportedSchemaVersion() + "/"),
                "schema '$id' should embed the version: " + root.path("$id").asText());
    }

    @Test
    void schemaExposesIdentifierValidator() throws IOException {
        JsonNode root = new ObjectMapper().readTree(PolicySchema.getSchema());

        assertTrue(root.path("$defs").path("filterIdentifier").path("properties").has("validator"),
                "filterIdentifier should expose the 'validator' property");

        JsonNode enumNode = root.path("$defs").path("validatorName").path("enum");
        assertTrue(enumNode.isArray(), "validatorName should define an enum");
        java.util.Set<String> names = new java.util.HashSet<>();
        enumNode.forEach(n -> names.add(n.asText()));
        assertEquals(java.util.Set.of(
                        "luhn", "mod11", "mod97", "mod23-letter", "aba", "verhoeff", "damm",
                        "es-cif", "de-steuerid", "de-personalausweis", "bic-structural"),
                names, "validatorName enum must match the validators catalog");
    }
}
