"""
Transpile a Fangless Python source file to C++.

Usage:
    py src/transpile.py <input_file> [output_file.cpp]
"""

from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_source, TranspileError


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: py src/transpile.py <input_file> [output_file.cpp]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = (
        Path(sys.argv[2])
        if len(sys.argv) == 3
        else input_path.with_suffix(".cpp")
    )

    try:
        source_code = input_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: file '{input_path}' was not found.")
        sys.exit(1)

    parser = FanglessParser()
    try:
        cpp_source = transpile_source(source_code, parser)
    except TranspileError as error:
        print(f"Transpile error: {error}")
        sys.exit(1)

    output_path.write_text(cpp_source, encoding="utf-8")
    print(f"Generated C++: {output_path}")


if __name__ == "__main__":
    main()
