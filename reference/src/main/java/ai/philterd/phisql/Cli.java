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
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Command-line front end for the reference compiler.
 *
 * <p>It exists so that a language-neutral conformance runner can drive this
 * implementation the same way it drives any other: invoke a command with a
 * {@code .phisql} file, read the compiled Phileas JSON from stdout, and read
 * the exit code to learn whether the input was accepted or rejected, and why.
 *
 * <p>Usage:
 * <pre>{@code
 *   phisql-cli <file.phisql>
 * }</pre>
 *
 * <p>Exit codes form the adapter contract the conformance runner relies on:
 * <ul>
 *   <li>{@code 0} - compiled successfully; the Phileas JSON is on stdout.</li>
 *   <li>{@code 2} - the input failed to parse (a grammar/syntax error).</li>
 *   <li>{@code 3} - the input parsed but failed to compile (a semantic or
 *       catalog error, e.g. an unknown entity type or an invalid argument).</li>
 *   <li>{@code 64} - usage error (wrong arguments).</li>
 *   <li>{@code 1} - an I/O or otherwise unexpected error.</li>
 * </ul>
 *
 * <p>The two reject codes are kept distinct so the suite can assert not just
 * that an invalid policy is rejected but that it is rejected at the right
 * layer: a malformed token must fail to parse, while a well-formed policy that
 * names an entity the catalog does not define must fail to compile.
 */
public final class Cli {

    static final int EXIT_OK = 0;
    static final int EXIT_ERROR = 1;
    static final int EXIT_PARSE_ERROR = 2;
    static final int EXIT_COMPILE_ERROR = 3;
    static final int EXIT_USAGE = 64;

    private Cli() {}

    public static void main(String[] args) {
        System.exit(run(args, System.out, System.err));
    }

    /**
     * Runs the CLI against explicit streams and returns the exit code instead of
     * calling {@link System#exit}, so it can be unit-tested.
     */
    static int run(String[] args, PrintStream out, PrintStream err) {
        if (args.length != 1 || isHelp(args[0])) {
            err.println("usage: phisql-cli <file.phisql>");
            err.println("  compiles a PhiSQL file to a Phileas JSON policy on stdout");
            return args.length == 1 && isHelp(args[0]) ? EXIT_OK : EXIT_USAGE;
        }

        Path file = Path.of(args[0]);
        if (!Files.isRegularFile(file)) {
            err.println("error: no such file: " + file);
            return EXIT_USAGE;
        }

        try {
            CompileResult result = new Compiler().compile(file);
            byte[] json = (result.toJsonString() + System.lineSeparator())
                    .getBytes(StandardCharsets.UTF_8);
            out.write(json, 0, json.length);
            out.flush();
            return EXIT_OK;
        } catch (PhiSQL.ParseException e) {
            err.println("parse error: " + e.getMessage());
            return EXIT_PARSE_ERROR;
        } catch (Compiler.CompileException e) {
            err.println("compile error: " + e.getMessage());
            return EXIT_COMPILE_ERROR;
        } catch (IOException e) {
            err.println("error: " + e.getMessage());
            return EXIT_ERROR;
        }
    }

    private static boolean isHelp(String arg) {
        return "-h".equals(arg) || "--help".equals(arg);
    }
}
