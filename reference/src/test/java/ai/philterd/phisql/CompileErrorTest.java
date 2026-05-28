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
    void rejectsUnknownStrategyArgument() {
        Compiler compiler = new Compiler();
        Compiler.CompileException ex = assertThrows(
                Compiler.CompileException.class,
                () -> compiler.compile("REDACT SSN WITH MASK(unknown_arg='x');")
        );
        assertTrue(ex.getMessage().contains("unknown_arg"),
                "Expected error to name the bad arg: " + ex.getMessage());
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
}
