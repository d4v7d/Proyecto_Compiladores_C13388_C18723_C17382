"""
Main entry point for running the lexer.
Reads a source file passed as a command-line argument, runs it through
the FanglessLexer, and prints each recognized token with its type,
value, and line number.
"""

import sys
from lexer.lexer_builder import FanglessLexer


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/main.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: file '{input_file}' was not found.")
        sys.exit(1)

    lexer = FanglessLexer()
    tokens = lexer.tokenize(source_code)

    for token in tokens:
        print(
            f"Type: {token.type:<22} Value: {str(token.value):<10} Line: {token.lineno}"
        )


if __name__ == "__main__":
    main()