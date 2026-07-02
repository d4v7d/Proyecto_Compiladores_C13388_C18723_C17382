"""End-to-end tests for AST-to-C++ code generation."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_source, TranspileError


@dataclass
class CodegenCase:
    name: str
    source: str
    expected_output: str


TEST_CASES = [
    CodegenCase(
        name="literals_and_assignments",
        source=(
            "x = 5\n"
            "x += 3\n"
            "y = 2 + 3 * 4\n"
            "z = (2 + 3) * 4\n"
            "flag = True and not False\n"
            "print(x, y, z, flag)\n"
        ),
        expected_output="8 14 20 True",
    ),
    CodegenCase(
        name="dynamic_reassignment",
        source=(
            "value = 10\n"
            "value = \"hello\"\n"
            "print(value)\n"
        ),
        expected_output="hello",
    ),
    CodegenCase(
        name="function_definition",
        source=(
            "def add(a, b):\n"
            "    return a + b\n"
            "result = add(2, 3)\n"
            "print(result)\n"
        ),
        expected_output="5",
    ),
    CodegenCase(
        name="if_else",
        source=(
            "x = 10\n"
            "if x > 5:\n"
            "    print(\"big\")\n"
            "else:\n"
            "    print(\"small\")\n"
        ),
        expected_output="big",
    ),
    CodegenCase(
        name="while_loop",
        source=(
            "count = 0\n"
            "while count < 3:\n"
            "    count += 1\n"
            "print(count)\n"
        ),
        expected_output="3",
    ),
    CodegenCase(
        name="for_loop_list",
        source=(
            "total = 0\n"
            "for item in [1, 2, 3]:\n"
            "    total += item\n"
            "print(total)\n"
        ),
        expected_output="6",
    ),
    CodegenCase(
        name="for_loop_range",
        source=(
            "total = 0\n"
            "for i in range(5):\n"
            "    total += i\n"
            "print(total)\n"
        ),
        expected_output="10",
    ),
    CodegenCase(
        name="list_operations",
        source=(
            "items = [1, 2]\n"
            "items.append(3)\n"
            "print(items[1], len(items))\n"
        ),
        expected_output="2 3",
    ),
    CodegenCase(
        name="comparisons_and_strings",
        source=(
            "name = \"hello \" + \"world\"\n"
            "check = name == \"hello world\"\n"
            "print(name, check)\n"
        ),
        expected_output="hello world True",
    ),
    CodegenCase(
        name="nested_function_scope",
        source=(
            "def square(n):\n"
            "    result = n * n\n"
            "    return result\n"
            "print(square(4))\n"
        ),
        expected_output="16",
    ),
    CodegenCase(
        name="elif_chain",
        source=(
            "x = 2\n"
            "if x == 1:\n"
            "    print(\"one\")\n"
            "elif x == 2:\n"
            "    print(\"two\")\n"
            "elif x == 3:\n"
            "    print(\"three\")\n"
            "else:\n"
            "    print(\"other\")\n"
        ),
        expected_output="two",
    ),
    CodegenCase(
        name="nested_loops",
        source=(
            "total = 0\n"
            "for i in range(3):\n"
            "    for j in range(3):\n"
            "        total += i * j\n"
            "print(total)\n"
        ),
        expected_output="9",
    ),
    CodegenCase(
        name="break_and_continue",
        source=(
            "total = 0\n"
            "for i in range(10):\n"
            "    if i == 5:\n"
            "        break\n"
            "    if i % 2 == 0:\n"
            "        continue\n"
            "    total += i\n"
            "print(total)\n"
        ),
        expected_output="4",
    ),
    CodegenCase(
        name="pass_statement",
        source=(
            "x = 0\n"
            "if x == 0:\n"
            "    pass\n"
            "else:\n"
            "    x = 99\n"
            "print(x)\n"
        ),
        expected_output="0",
    ),
    CodegenCase(
        name="tuple_literal",
        source="pair = (1, 2)\nprint(pair[0], len(pair))\n",
        expected_output="1 2",
    ),
    CodegenCase(
        name="string_slicing",
        source=(
            'text = "Hello World"\n'
            "print(text[:5])\n"
            "print(text[6:])\n"
        ),
        expected_output="Hello\nWorld",
    ),
    CodegenCase(
        name="default_parameters",
        source=(
            "def greet(name=\"world\"):\n"
            "    return name\n"
            "print(greet())\n"
            "print(greet(\"Fangless\"))\n"
        ),
        expected_output="world\nFangless",
    ),
    CodegenCase(
        name="string_methods",
        source=(
            'text = " Hello "\n'
            "print(text.strip().lower())\n"
        ),
        expected_output="hello",
    ),
    CodegenCase(
        name="nested_function",
        source=(
            "def outer():\n"
            "    def inner():\n"
            "        return 7\n"
            "    return inner()\n"
            "print(outer())\n"
        ),
        expected_output="7",
    ),
    CodegenCase(
        name="try_except",
        source=(
            "value = 0\n"
            "try:\n"
            "    value = 10\n"
            "except:\n"
            "    value = 99\n"
            "print(value)\n"
        ),
        expected_output="10",
    ),
    CodegenCase(
        name="basic_class",
        source=(
            "class Dog:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def describe(self):\n"
            "        return self.name\n"
            "pet = Dog(\"Rex\")\n"
            "print(pet.describe())\n"
        ),
        expected_output="Rex",
    ),
]


def find_gpp() -> str:
    compiler = shutil.which("g++")
    if compiler:
        return compiler

    winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_root.exists():
        for candidate in winget_root.glob("**/mingw64/bin/g++.exe"):
            return str(candidate)

    raise RuntimeError("g++ was not found. A C++17-compatible compiler is required.")


def compile_and_run(cpp_source: str) -> str:
    compiler = find_gpp()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "generated.cpp"
        binary_file = temp_path / "generated.exe"
        source_file.write_text(cpp_source, encoding="utf-8")

        compile_result = subprocess.run(
            [compiler, "-std=c++17", str(source_file), "-o", str(binary_file)],
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            raise RuntimeError(
                "Compilation failed:\n"
                f"{compile_result.stdout}\n{compile_result.stderr}"
            )

        run_result = subprocess.run(
            [str(binary_file)],
            capture_output=True,
            text=True,
        )
        if run_result.returncode != 0:
            raise RuntimeError(
                "Execution failed:\n"
                f"{run_result.stdout}\n{run_result.stderr}"
            )

        return run_result.stdout.strip()


def main() -> None:
    parser = FanglessParser()
    passed = 0
    failed = 0

    print("Running codegen end-to-end tests\n")

    for case in TEST_CASES:
        try:
            cpp_source = transpile_source(case.source, parser)
            actual_output = compile_and_run(cpp_source)
            if actual_output == case.expected_output:
                print(f"[PASS] {case.name}")
                passed += 1
            else:
                print(f"[FAIL] {case.name}")
                print(f"  expected: {case.expected_output!r}")
                print(f"  actual:   {actual_output!r}")
                failed += 1
        except (TranspileError, RuntimeError) as error:
            print(f"[FAIL] {case.name}")
            print(f"  error: {error}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {len(TEST_CASES)} total")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
