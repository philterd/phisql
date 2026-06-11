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

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.Properties;

/**
 * Access to the canonical redaction policy JSON Schema bundled in this JAR.
 *
 * <p>The schema is authored in this repository at {@code schema/<version>/schema.json}
 * and is the contract PhiSQL compiles to and Phileas executes against. The build
 * packages a single version of it into the JAR, selected by the
 * {@code redaction.policy.schema.version} Maven property, so projects that depend
 * on {@code ai.philterd:phisql} can read the schema without checking out this repo
 * or fetching it over the network.
 *
 * @see <a href="https://www.philterd.ai/schemas/redaction-policy/">Published schema</a>
 */
public final class PolicySchema {

    private static final String VERSION_RESOURCE = "/ai/philterd/phisql/policy-schema.properties";

    private static final String VERSION = loadVersion();
    private static final String SCHEMA_RESOURCE = "/schema/" + VERSION + "/schema.json";

    private PolicySchema() {
    }

    /** Returns the version of the bundled schema, e.g. {@code "1.0.0"}. */
    public static String getSupportedSchemaVersion() {
        return VERSION;
    }

    /** Returns the full bundled schema JSON as a string. */
    public static String getSchema() {
        try (InputStream in = open(SCHEMA_RESOURCE)) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read policy schema resource " + SCHEMA_RESOURCE, e);
        }
    }

    private static String loadVersion() {
        Properties props = new Properties();
        try (InputStream in = open(VERSION_RESOURCE)) {
            props.load(in);
        } catch (IOException e) {
            throw new UncheckedIOException("Failed to read policy schema version resource " + VERSION_RESOURCE, e);
        }
        String version = props.getProperty("schema.version");
        if (version == null || version.isBlank() || version.startsWith("${")) {
            throw new IllegalStateException(
                    "Policy schema version was not filtered into " + VERSION_RESOURCE
                            + "; check the build's resource filtering configuration");
        }
        return version;
    }

    private static InputStream open(String resource) {
        InputStream in = PolicySchema.class.getResourceAsStream(resource);
        if (in == null) {
            throw new IllegalStateException("Policy schema resource not found: " + resource);
        }
        return in;
    }
}
