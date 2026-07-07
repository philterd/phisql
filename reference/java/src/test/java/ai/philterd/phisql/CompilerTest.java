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
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Compiles every redaction example {@code .phisql} file under
 * {@code spec/v1.0/examples/} and verifies the output matches the
 * corresponding {@code .json} file. This is the load-bearing assertion that
 * the compiler stays in sync with the spec examples: any divergence fails
 * the build.
 *
 * <p>Discovery examples do not compile to Phileas JSON and are not yet
 * handled by this compiler. They are listed in
 * {@link #DISCOVERY_EXAMPLES_NOT_YET_COMPILED} so the test skips them
 * explicitly rather than implicitly. When the discovery compiler lands, the
 * set shrinks; new redaction examples are automatically picked up.
 */
class CompilerTest {

    private static final List<Path> EXAMPLES_DIRS = List.of(
            Paths.get("..", "..", "spec", "v1.0", "examples").toAbsolutePath().normalize(),
            Paths.get("..", "..", "spec", "v1.1.0", "examples").toAbsolutePath().normalize(),
            Paths.get("..", "..", "spec", "v1.2.0", "examples").toAbsolutePath().normalize());

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static final Set<String> DISCOVERY_EXAMPLES_NOT_YET_COMPILED = Set.of(
            "15-find-pii-s3.phisql",
            "16-discover-entities-gcs.phisql",
            "17-scan-azure-blob.phisql",
            "18-find-pii-local-filesystem.phisql",
            "19-select-findings-groupby.phisql"
    );

    @TestFactory
    Stream<DynamicTest> everyExampleCompilesToExpectedJson() throws IOException {
        Compiler compiler = new Compiler();
        List<Path> sources = new ArrayList<>();
        for (Path dir : EXAMPLES_DIRS) {
            if (!Files.isDirectory(dir)) continue;
            try (Stream<Path> entries = Files.list(dir)) {
                entries.filter(p -> p.getFileName().toString().endsWith(".phisql"))
                       .filter(p -> !DISCOVERY_EXAMPLES_NOT_YET_COMPILED.contains(p.getFileName().toString()))
                       .forEach(sources::add);
            }
        }
        sources.sort(null);
        if (sources.isEmpty()) {
            throw new IllegalStateException("No example files found in " + EXAMPLES_DIRS);
        }
        return sources.stream().map(source -> {
            String stem = source.getFileName().toString().replaceFirst("\\.phisql$", "");
            Path expected = source.getParent().resolve(stem + ".json");
            return DynamicTest.dynamicTest(source.getFileName().toString(), () -> {
                String phisql = Files.readString(source);
                CompileResult result = compiler.compile(phisql);

                JsonNode actualJson = result.policyJson();
                JsonNode expectedJson = MAPPER.readTree(expected.toFile());

                assertEquals(
                        expectedJson,
                        actualJson,
                        "Compiled output for " + source.getFileName()
                                + " does not match expected JSON at " + expected.getFileName()
                                + ".\nExpected:\n" + expectedJson.toPrettyString()
                                + "\nActual:\n" + actualJson.toPrettyString()
                );

                assertNotNull(result.policyName(),
                        "Compiler should extract the POLICY name from the document");
            });
        });
    }
}
