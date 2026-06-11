// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

namespace Philterd.PhiSql;

/// <summary>
/// Command-line front end for the reference compiler. A language-neutral
/// conformance runner drives it the same way it drives any implementation:
/// invoke with a <c>.phisql</c> file, read the compiled Phileas JSON from
/// stdout, and read the exit code to learn whether the input was accepted or
/// rejected, and why.
///
/// Exit codes form the adapter contract:
/// <list type="bullet">
///   <item><c>0</c>  — compiled successfully; the Phileas JSON is on stdout.</item>
///   <item><c>2</c>  — the input failed to parse (a grammar/syntax error).</item>
///   <item><c>3</c>  — the input parsed but failed to compile (a semantic/catalog error).</item>
///   <item><c>64</c> — usage error (wrong arguments).</item>
///   <item><c>1</c>  — an I/O or otherwise unexpected error.</item>
/// </list>
/// </summary>
public static class Cli
{
    public const int ExitOk = 0;
    public const int ExitError = 1;
    public const int ExitParseError = 2;
    public const int ExitCompileError = 3;
    public const int ExitUsage = 64;

    private static bool IsHelp(string arg) => arg is "-h" or "--help";

    /// <summary>
    /// Runs the CLI against explicit streams and returns the exit code.
    /// <paramref name="args"/> excludes the program name.
    /// </summary>
    public static int Run(string[] args, TextWriter outw, TextWriter errw)
    {
        if (args.Length != 1 || IsHelp(args[0]))
        {
            errw.WriteLine("usage: phisql <file.phisql>");
            errw.WriteLine("  compiles a PhiSQL file to a Phileas JSON policy on stdout");
            return args.Length == 1 && IsHelp(args[0]) ? ExitOk : ExitUsage;
        }

        string file = args[0];
        if (!File.Exists(file))
        {
            errw.WriteLine($"error: no such file: {file}");
            return ExitUsage;
        }

        try
        {
            CompileResult result = new Compiler().CompileFile(file);
            outw.WriteLine(result.ToJsonString());
            return ExitOk;
        }
        catch (ParseException e)
        {
            errw.WriteLine($"parse error: {e.Message}");
            return ExitParseError;
        }
        catch (CompileException e)
        {
            errw.WriteLine($"compile error: {e.Message}");
            return ExitCompileError;
        }
        catch (IOException e)
        {
            errw.WriteLine($"error: {e.Message}");
            return ExitError;
        }
    }
}
