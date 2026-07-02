"""Run defense demos: transpile -> compile -> run, verifying expected output.

Also runs the runtime smoke test and codegen test suite when invoked with
--full.

Usage:
    python demos/run_demos.py
    python demos/run_demos.py --full
    python demos/run_demos.py --demo demo_functions
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMOS_DIR = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_source, TranspileError


@dataclass
class DemoCase:
    name: str
    source_file: str
    expected_output: str
    description: str


DEMO_CASES = [
    DemoCase(
        name="demo_dynamic_typing",
        source_file="demo_dynamic_typing.py",
        expected_output="True",
        description="Variable reassigned across int, str, and bool (PyValue runtime)",
    ),
    DemoCase(
        name="demo_functions",
        source_file="demo_functions.py",
        expected_output="16",
        description="Functions with parameters, return values, and nested calls",
    ),
    DemoCase(
        name="demo_control_flow",
        source_file="demo_control_flow.py",
        expected_output="large\n22",
        description="if/elif/else, while, for, break, and continue",
    ),
    DemoCase(
        name="demo_lists",
        source_file="demo_lists.py",
        expected_output="10 30 3",
        description="List literals, append, indexing, and len()",
    ),
    DemoCase(
        name="demo_fibonacci",
        source_file="demo_fibonacci.py",
        expected_output="55",
        description="Recursive Fibonacci (benchmark-style algorithm)",
    ),
]


def find_gpp() -> str:
    compiler = shutil.which("g++")
    if compiler:
        return compiler

    winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_root.exists():
        for candidate in winget_root.glob("**/mingw64/bin/g++.exe"):
            return candidate

    raise RuntimeError("g++ was not found. Install a C++17 compiler and add it to PATH.")


def compile_and_run(cpp_source: str) -> str:
    compiler = find_gpp()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        source_file = temp_path / "demo.cpp"
        binary_file = temp_path / "demo.exe"
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


def run_subprocess_script(relative_path: str) -> int:
    script = REPO_ROOT / relative_path
    result = subprocess.run([sys.executable, str(script)], cwd=str(REPO_ROOT))
    return result.returncode


def run_demo(case: DemoCase, parser: FanglessParser) -> tuple[bool, str]:
    source_path = DEMOS_DIR / case.source_file
    source = source_path.read_text(encoding="utf-8")

    try:
        cpp_source = transpile_source(source, parser)
        actual = compile_and_run(cpp_source)
    except (TranspileError, RuntimeError) as error:
        return False, str(error)

    if actual == case.expected_output:
        return True, actual
    return False, f"expected {case.expected_output!r}, got {actual!r}"


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Run Fangless defense demos.")
    arg_parser.add_argument(
        "--full",
        action="store_true",
        help="also run runtime smoke test and codegen test suite",
    )
    arg_parser.add_argument(
        "--demo",
        type=str,
        default="",
        help="run a single demo by name (e.g. demo_functions)",
    )
    args = arg_parser.parse_args()

    if args.full:
        print("=== Runtime smoke test ===")
        if run_subprocess_script("tests/runtime/run_runtime_smoke_test.py") != 0:
            raise SystemExit(1)
        print()

        print("=== Codegen test suite ===")
        if run_subprocess_script("tests/codegen/run_codegen_tests.py") != 0:
            raise SystemExit(1)
        print()

    selected = DEMO_CASES
    if args.demo:
        selected = [case for case in DEMO_CASES if case.name == args.demo]
        if not selected:
            names = ", ".join(case.name for case in DEMO_CASES)
            raise SystemExit(f"Unknown demo {args.demo!r}. Choose from: {names}")

    parser = FanglessParser()
    passed = 0
    failed = 0

    print("=== Defense demos (transpile -> compile -> run) ===\n")

    for case in selected:
        ok, detail = run_demo(case, parser)
        if ok:
            print(f"[PASS] {case.name}")
            print(f"       {case.description}")
            print(f"       output: {detail}")
            passed += 1
        else:
            print(f"[FAIL] {case.name}")
            print(f"       {case.description}")
            print(f"       {detail}")
            failed += 1
        print()

    print(f"Demos: {passed} passed, {failed} failed, {len(selected)} total")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
