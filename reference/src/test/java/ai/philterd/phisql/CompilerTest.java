/*
 * Licensed under the Apache License, Version 2.0 (the "License");
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
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

/**
 * Compiles every example {@code .phisql} file under {@code spec/v0.1/examples/}
 * and verifies the output matches the corresponding {@code .json} file. This
 * is the load-bearing assertion that the compiler stays in sync with the spec
 * examples: any divergence fails the build.
 */
class CompilerTest {

    private static final Path EXAMPLES_DIR =
            Paths.get("..", "spec", "v0.1", "examples").toAbsolutePath().normalize();

    private static final ObjectMapper MAPPER = new ObjectMapper();

    @TestFactory
    Stream<DynamicTest> everyExampleCompilesToExpectedJson() throws IOException {
        Compiler compiler = new Compiler();
        List<Path> sources;
        try (Stream<Path> entries = Files.list(EXAMPLES_DIR)) {
            sources = entries
                    .filter(p -> p.getFileName().toString().endsWith(".phisql"))
                    .sorted()
                    .toList();
        }
        if (sources.isEmpty()) {
            throw new IllegalStateException("No example files found at " + EXAMPLES_DIR);
        }
        return sources.stream().map(source -> {
            String stem = source.getFileName().toString().replaceFirst("\\.phisql$", "");
            Path expected = EXAMPLES_DIR.resolve(stem + ".json");
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
