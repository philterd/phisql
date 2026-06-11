# Copyright 2026 Philterd, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Command-line front end for the reference compiler.

It exists so that a language-neutral conformance runner can drive this
implementation the same way it drives any other: invoke a command with a
``.phisql`` file, read the compiled Phileas JSON from stdout, and read the exit
code to learn whether the input was accepted or rejected, and why.

Usage::

    python -m phisql <file.phisql>

Exit codes form the adapter contract the conformance runner relies on:

* ``0``  — compiled successfully; the Phileas JSON is on stdout.
* ``2``  — the input failed to parse (a grammar/syntax error).
* ``3``  — the input parsed but failed to compile (a semantic/catalog error).
* ``64`` — usage error (wrong arguments).
* ``1``  — an I/O or otherwise unexpected error.

The two reject codes are kept distinct so the suite can assert not just that an
invalid policy is rejected but that it is rejected at the right layer.
"""

from __future__ import annotations

import sys
from pathlib import Path

from .compiler import Compiler
from .errors import CompileException, ParseException

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_PARSE_ERROR = 2
EXIT_COMPILE_ERROR = 3
EXIT_USAGE = 64


def _is_help(arg: str) -> bool:
    return arg in ("-h", "--help")


def run(args, out, err) -> int:
    """Runs the CLI against explicit streams and returns the exit code.

    ``args`` is the argument list (excluding the program name).
    """
    if len(args) != 1 or _is_help(args[0]):
        print("usage: phisql <file.phisql>", file=err)
        print("  compiles a PhiSQL file to a Phileas JSON policy on stdout", file=err)
        return EXIT_OK if (len(args) == 1 and _is_help(args[0])) else EXIT_USAGE

    file = Path(args[0])
    if not file.is_file():
        print(f"error: no such file: {file}", file=err)
        return EXIT_USAGE

    try:
        result = Compiler().compile_file(file)
        print(result.to_json_string(), file=out)
        out.flush()
        return EXIT_OK
    except ParseException as e:
        print(f"parse error: {e}", file=err)
        return EXIT_PARSE_ERROR
    except CompileException as e:
        print(f"compile error: {e}", file=err)
        return EXIT_COMPILE_ERROR
    except OSError as e:
        print(f"error: {e}", file=err)
        return EXIT_ERROR


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    return run(argv, sys.stdout, sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
