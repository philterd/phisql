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

import java.lang.reflect.Constructor;
import java.lang.reflect.Executable;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.lang.reflect.Type;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

/**
 * Verifies that the JSON library is an internal detail (#77): no Jackson type
 * appears in the public API, and {@link CompileResult#toJsonString()} keeps its format.
 */
class CompileResultTest {

    @Test
    void noJacksonTypeInThePublicApi() throws Exception {
        Path packageDir = Path.of(CompileResult.class.getProtectionDomain().getCodeSource().getLocation().toURI())
                .resolve("ai/philterd/phisql");
        List<String> classNames = new ArrayList<>();
        try (Stream<Path> files = Files.list(packageDir)) {
            files.map(p -> p.getFileName().toString())
                    .filter(name -> name.endsWith(".class"))
                    .forEach(name -> classNames.add("ai.philterd.phisql." + name.replaceFirst("\\.class$", "")));
        }
        assertFalse(classNames.isEmpty(), "No classes found in " + packageDir);

        List<String> leaks = new ArrayList<>();
        for (String className : classNames) {
            Class<?> type = Class.forName(className, false, CompileResultTest.class.getClassLoader());
            if (!isPublicApi(type)) continue;

            check(leaks, type.getName() + " superclass", type.getGenericSuperclass());
            for (Type i : type.getGenericInterfaces()) {
                check(leaks, type.getName() + " interface", i);
            }
            for (Constructor<?> c : type.getDeclaredConstructors()) {
                if (isVisible(c.getModifiers()) && !c.isSynthetic()) {
                    checkExecutable(leaks, type.getName() + " constructor", c);
                }
            }
            for (Method m : type.getDeclaredMethods()) {
                if (isVisible(m.getModifiers()) && !m.isSynthetic() && !m.isBridge()) {
                    checkExecutable(leaks, type.getName() + "." + m.getName(), m);
                    check(leaks, type.getName() + "." + m.getName() + " return type", m.getGenericReturnType());
                }
            }
            for (Field f : type.getDeclaredFields()) {
                if (isVisible(f.getModifiers()) && !f.isSynthetic()) {
                    check(leaks, type.getName() + "." + f.getName(), f.getGenericType());
                }
            }
        }

        assertEquals(List.of(), leaks, "Jackson types in public or protected signatures");
    }

    @Test
    void toJsonStringKeepsItsFormat() {
        CompileResult result = new Compiler().compile(
                "REDACT SSN WITH MASK(salt=TRUE);\n"
                        + "DETECT PHEYE LABELS ('PER') WITH REDACT\n"
                        + "  OPTIONS (thresholds = (PER = 0.8), phEyeConfiguration = (timeout = 30));\n");

        String expected = String.join(System.lineSeparator(),
                "{",
                "  \"identifiers\" : {",
                "    \"ssn\" : {",
                "      \"ssnFilterStrategies\" : [ {",
                "        \"strategy\" : \"MASK\",",
                "        \"salt\" : true",
                "      } ]",
                "    },",
                "    \"pheyes\" : [ {",
                "      \"phEyeFilterStrategies\" : [ {",
                "        \"strategy\" : \"REDACT\"",
                "      } ],",
                "      \"phEyeConfiguration\" : {",
                "        \"labels\" : [ \"PER\" ],",
                "        \"timeout\" : 30",
                "      },",
                "      \"thresholds\" : {",
                "        \"PER\" : 0.8",
                "      }",
                "    } ]",
                "  }",
                "}");

        assertEquals(expected, result.toJsonString());
    }

    private static boolean isPublicApi(Class<?> type) {
        for (Class<?> c = type; c != null; c = c.getEnclosingClass()) {
            if (!Modifier.isPublic(c.getModifiers()) || c.isAnonymousClass() || c.isSynthetic()) {
                return false;
            }
        }
        return true;
    }

    private static boolean isVisible(int modifiers) {
        return Modifier.isPublic(modifiers) || Modifier.isProtected(modifiers);
    }

    private static void checkExecutable(List<String> leaks, String where, Executable e) {
        for (Type p : e.getGenericParameterTypes()) {
            check(leaks, where + " parameter", p);
        }
        for (Type x : e.getGenericExceptionTypes()) {
            check(leaks, where + " exception", x);
        }
    }

    private static void check(List<String> leaks, String where, Type type) {
        if (type != null && type.getTypeName().contains("jackson.")) {
            leaks.add(where + ": " + type.getTypeName());
        }
    }
}
