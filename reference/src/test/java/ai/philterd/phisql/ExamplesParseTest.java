/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 */
package ai.philterd.phisql;

import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Parses every example file under spec/v0.1/examples/ to verify the generated
 * parser stays in sync with the spec. New examples added to the spec are
 * automatically covered.
 */
class ExamplesParseTest {

    private static final Path EXAMPLES_DIR =
            Paths.get("..", "spec", "v0.1", "examples").toAbsolutePath().normalize();

    @TestFactory
    Stream<DynamicTest> everyExampleParses() throws IOException {
        List<Path> files;
        try (Stream<Path> entries = Files.list(EXAMPLES_DIR)) {
            files = entries
                    .filter(p -> p.getFileName().toString().endsWith(".phisql"))
                    .sorted()
                    .toList();
        }
        if (files.isEmpty()) {
            throw new IllegalStateException("No example files found at " + EXAMPLES_DIR);
        }
        return files.stream().map(p -> DynamicTest.dynamicTest(p.getFileName().toString(), () -> {
            String source = Files.readString(p);
            assertDoesNotThrow(() -> PhiSQL.parse(source),
                    "Failed to parse " + p.getFileName());
        }));
    }
}
