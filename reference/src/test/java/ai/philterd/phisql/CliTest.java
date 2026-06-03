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
import org.junit.jupiter.api.io.TempDir;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies the {@link Cli} adapter contract the conformance runner depends on:
 * stdout carries the compiled JSON, and the exit code distinguishes success,
 * parse failure, and compile failure.
 */
class CliTest {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    @TempDir
    Path dir;

    private record Run(int code, String out, String err) {}

    private Run invoke(String... args) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        int code = Cli.run(args,
                new PrintStream(out, true, StandardCharsets.UTF_8),
                new PrintStream(err, true, StandardCharsets.UTF_8));
        return new Run(code, out.toString(StandardCharsets.UTF_8), err.toString(StandardCharsets.UTF_8));
    }

    private Path write(String name, String body) throws IOException {
        Path f = dir.resolve(name);
        Files.writeString(f, body);
        return f;
    }

    @Test
    void compilesValidPolicyToJsonOnStdout() throws IOException {
        Path f = write("ssn.phisql", "REDACT SSN WITH MASK;\n");
        Run r = invoke(f.toString());
        assertEquals(Cli.EXIT_OK, r.code(), r.err());
        JsonNode json = MAPPER.readTree(r.out());
        assertEquals("MASK",
                json.path("identifiers").path("ssn").path("ssnFilterStrategies").get(0).path("strategy").asText());
    }

    @Test
    void parseErrorExitsWithParseCode() throws IOException {
        // Missing the semicolon after the POLICY declaration is a grammar error.
        Path f = write("bad.phisql", "POLICY x\nREDACT SSN WITH MASK;\n");
        Run r = invoke(f.toString());
        assertEquals(Cli.EXIT_PARSE_ERROR, r.code());
        assertTrue(r.err().contains("parse error"), r.err());
    }

    @Test
    void unknownEntityExitsWithCompileCode() throws IOException {
        // Well-formed syntax, but NOT_AN_ENTITY is not in the catalog.
        Path f = write("sem.phisql", "REDACT NOT_AN_ENTITY WITH MASK;\n");
        Run r = invoke(f.toString());
        assertEquals(Cli.EXIT_COMPILE_ERROR, r.code());
        assertTrue(r.err().contains("compile error"), r.err());
    }

    @Test
    void policyNameMismatchExitsWithCompileCode() throws IOException {
        // The basename (mismatch) does not match the POLICY name (something_else).
        Path f = write("mismatch.phisql", "POLICY something_else;\nREDACT SSN WITH MASK;\n");
        Run r = invoke(f.toString());
        assertEquals(Cli.EXIT_COMPILE_ERROR, r.code());
    }

    @Test
    void missingArgumentIsUsageError() {
        Run r = invoke();
        assertEquals(Cli.EXIT_USAGE, r.code());
        assertTrue(r.err().contains("usage"), r.err());
    }

    @Test
    void missingFileIsUsageError() {
        Run r = invoke(dir.resolve("does-not-exist.phisql").toString());
        assertEquals(Cli.EXIT_USAGE, r.code());
    }
}
