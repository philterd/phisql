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

import tools.jackson.core.JacksonException;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.ObjectWriter;
import tools.jackson.databind.node.ObjectNode;

import java.util.List;

/**
 * Result of compiling a PhiSQL document.
 *
 * <p>{@link #policyName()} is the name from the {@code POLICY} declaration, which
 * implementations should use as the output filename ({@code <name>.json}).
 *
 * <p>{@link #description()} is the {@code DESCRIPTION '...'} text. As of schema
 * 1.3.0 it is also compiled into the policy itself as {@code metadata.description},
 * so it travels with the policy; it is returned here as well for callers that keep
 * a description elsewhere (such as a sibling {@code <name>.md} file). The compiler
 * does not write files; that is the caller's choice.
 *
 * <p>{@link #toJsonString()} is the compiled Phileas JSON policy. The JSON library
 * the compiler uses to build it is an internal detail and is not part of this API.
 *
 * <p>{@link #warnings()} lists problems that do not stop compilation, such as a
 * {@code WHERE} clause that not every Phileas runtime can evaluate yet.
 */
public final class CompileResult {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final ObjectWriter PRETTY = MAPPER.writerWithDefaultPrettyPrinter();

    private final String policyName;
    private final String description;
    private final ObjectNode policyJson;
    private final List<String> warnings;

    CompileResult(String policyName, String description, ObjectNode policyJson) {
        this(policyName, description, policyJson, List.of());
    }

    CompileResult(String policyName, String description, ObjectNode policyJson, List<String> warnings) {
        this.policyName = policyName;
        this.description = description;
        this.policyJson = policyJson;
        this.warnings = List.copyOf(warnings);
    }

    public String policyName() {
        return policyName;
    }

    public String description() {
        return description;
    }

    /** Returns the compile warnings, in the order found; empty when there are none. */
    public List<String> warnings() {
        return warnings;
    }

    /** Returns the policy JSON as a pretty-printed string. */
    public String toJsonString() {
        try {
            return PRETTY.writeValueAsString(policyJson);
        } catch (JacksonException e) {
            throw new IllegalStateException("Failed to serialize compiled policy", e);
        }
    }
}
