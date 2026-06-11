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
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Verifies the policy-naming rule defined in spec/v1.0/catalog/policy.yaml:
 *
 * <ul>
 *   <li>POLICY declaration is optional.</li>
 *   <li>When a filename is provided and POLICY is declared, the declared name
 *       must match the filename basename after hyphen/underscore normalization.</li>
 *   <li>When POLICY is omitted, the policy name is the filename basename.</li>
 *   <li>When no filename is provided and POLICY is omitted, policyName is null.</li>
 * </ul>
 */
class PolicyNamingTest {

    private final Compiler compiler = new Compiler();

    @Test
    void filenameProvidesNameWhenPolicyDeclarationOmitted() throws IOException {
        Path file = writePhisql("hipaa-safe-harbor.phisql", "REDACT SSN WITH MASK;");
        CompileResult result = compiler.compile(file);
        assertEquals("hipaa-safe-harbor", result.policyName());
    }

    @Test
    void matchingPolicyDeclarationCompilesSuccessfully() throws IOException {
        Path file = writePhisql("ssn_only.phisql",
                "POLICY ssn_only; REDACT SSN WITH MASK;");
        CompileResult result = compiler.compile(file);
        assertEquals("ssn_only", result.policyName());
    }

    @Test
    void mismatchedPolicyDeclarationProducesCompileError() throws IOException {
        Path file = writePhisql("whatever.phisql",
                "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;");
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile(file)
        );
        assertTrue(ex.getMessage().contains("hipaa_safe_harbor"),
                "Expected error to mention the declared name: " + ex.getMessage());
        assertTrue(ex.getMessage().contains("whatever"),
                "Expected error to mention the expected name: " + ex.getMessage());
    }

    @Test
    void hyphensAndUnderscoresAreEquivalentForMatching() throws IOException {
        // Real-world case: file uses hyphens (philterd/pii-redaction-policies
        // convention), POLICY declaration uses underscores (PhiSQL identifier rule).
        Path file = writePhisql("hipaa-safe-harbor.phisql",
                "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;");
        CompileResult result = compiler.compile(file);
        assertEquals("hipaa-safe-harbor", result.policyName(),
                "Policy name should be the filename basename, not the normalized form");
    }

    @Test
    void stringOnlyCompileWithoutPolicyHasNullName() {
        CompileResult result = compiler.compile("REDACT SSN WITH MASK;");
        assertNull(result.policyName());
    }

    @Test
    void stringOnlyCompileWithPolicyDeclarationUsesDeclaredName() {
        CompileResult result = compiler.compile("POLICY foo; REDACT SSN WITH MASK;");
        assertEquals("foo", result.policyName());
    }

    @Test
    void explicitExpectedNameOverridesNullDeclaration() {
        CompileResult result = compiler.compile("REDACT SSN WITH MASK;", "ssn_only");
        assertEquals("ssn_only", result.policyName());
    }

    @Test
    void explicitExpectedNameMustMatchPolicyDeclaration() {
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;",
                        "different_name")
        );
        assertTrue(ex.getMessage().contains("hipaa_safe_harbor"),
                "Expected error to mention the declared name: " + ex.getMessage());
    }

    @Test
    void descriptionTextIsExtracted() throws IOException {
        Path file = writePhisql("test_policy.phisql",
                "POLICY test_policy DESCRIPTION 'A policy for X.'; REDACT SSN WITH MASK;");
        CompileResult result = compiler.compile(file);
        assertEquals("A policy for X.", result.description());
    }

    @TempDir
    Path tempDir;

    private Path writePhisql(String filename, String contents) throws IOException {
        Path file = tempDir.resolve(filename);
        Files.writeString(file, contents);
        return file;
    }
}
