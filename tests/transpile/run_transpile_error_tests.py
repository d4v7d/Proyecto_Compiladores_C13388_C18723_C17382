"""Tests for transpiler error messages with source locations."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_source, TranspileError


@dataclass
class TranspileErrorCase:
    name: str
    source: str
    message_fragment: str
    expected_line: int


ERROR_CASES = [
    TranspileErrorCase(
        name="unsupported_var_args",
        source=(
            "def collect(*items):\n"
            "    return items\n"
        ),
        message_fragment="Variadic parameters are not supported",
        expected_line=1,
    ),
    TranspileErrorCase(
        name="undeclared_variable",
        source="print(missing_name)\n",
        message_fragment="Undeclared variable: missing_name",
        expected_line=1,
    ),
    TranspileErrorCase(
        name="unsupported_dict_literal",
        source="data = {\"a\": 1}\n",
        message_fragment="Unsupported expression: dict_literal",
        expected_line=1,
    ),
    TranspileErrorCase(
        name="unsupported_raise",
        source="raise ValueError\n",
        message_fragment="Unsupported statement: raise_statement",
        expected_line=1,
    ),
]


PARSER_ERROR_CASES = [
    (
        "missing_expression",
        "x =\n",
        "unexpected end of input",
    ),
    (
        "invalid_escape",
        'x = "bad\\q"\n',
        "Lexical error:",
    ),
]


def main() -> None:
    passed = 0
    failed = 0

    print("Running transpiler error-location tests\n")

    for case in ERROR_CASES:
        try:
            transpile_source(case.source, FanglessParser())
            print(f"[FAIL] {case.name}")
            print("  expected TranspileError, but transpile succeeded")
            failed += 1
            continue
        except TranspileError as error:
            message = str(error)
            line_ok = error.line == case.expected_line
            fragment_ok = case.message_fragment in message
            location_ok = "at line" in message

            if line_ok and fragment_ok and location_ok:
                print(f"[PASS] {case.name}")
                print(f"       {message}")
                passed += 1
            else:
                print(f"[FAIL] {case.name}")
                print(f"  message:  {message!r}")
                print(f"  expected line: {case.expected_line}, got: {error.line}")
                print(f"  expected fragment: {case.message_fragment!r}")
                failed += 1
        except Exception as error:
            print(f"[FAIL] {case.name}")
            print(f"  unexpected error: {error}")
            failed += 1

    print("\nRunning parser/lexer error smoke checks\n")

    for name, source, fragment in PARSER_ERROR_CASES:
        local_parser = FanglessParser()
        local_parser.parse(source)
        messages = [str(error) for error in local_parser.errors]
        if local_parser.errors and any(fragment in message for message in messages):
            matched = next(message for message in messages if fragment in message)
            print(f"[PASS] {name}")
            print(f"       {matched}")
            passed += 1
        else:
            print(f"[FAIL] {name}")
            print(f"  errors: {local_parser.errors}")
            failed += 1

    total = len(ERROR_CASES) + len(PARSER_ERROR_CASES)
    print(f"\nResults: {passed} passed, {failed} failed, {total} total")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
