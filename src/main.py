"""
Main entry point for running the lexer and parser.
Reads a source file passed as a command-line argument, prints the tokens
recognized by the lexer, and then runs the parser over the same source.
"""

import sys
from lexer.lexer_builder import FanglessLexer
from parser.parser_builder import FanglessParser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

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

    if lexer.errors:
        print("\n--- Lexical Errors ---")
        for error in lexer.errors:
            print(error)
        return

    parser = FanglessParser()
    ast = parser.parse(source_code)

    print("\n--- Parser ---")
    if parser.errors:
        print("Syntax errors found:")
        for error in parser.errors:
            print(error)
    else:
        print("Parse successful")
        if ast is not None:
            print(ast.pretty_print())


if __name__ == "__main__":
    main()
