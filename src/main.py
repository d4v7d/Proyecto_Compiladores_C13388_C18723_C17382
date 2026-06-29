"""
Main entry point for running the lexer, parser, and optional code generation.
Reads a source file passed as a command-line argument, prints the tokens
recognized by the lexer, and then runs the parser over the same source.
Use --codegen to emit C++ instead of printing the AST.
"""

import sys
from pathlib import Path

from lexer.lexer_builder import FanglessLexer
from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_ast, TranspileError


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = sys.argv[1:]
    emit_cpp = False
    output_file = None

    if "--codegen" in args:
        emit_cpp = True
        args.remove("--codegen")

    if "--output" in args:
        output_index = args.index("--output")
        if output_index + 1 >= len(args):
            print("Usage: python src/main.py [--codegen] [--output file.cpp] <input_file>")
            sys.exit(1)
        output_file = args[output_index + 1]
        del args[output_index : output_index + 2]

    if len(args) != 1:
        print("Usage: python src/main.py [--codegen] [--output file.cpp] <input_file>")
        sys.exit(1)

    input_file = args[0]

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: file '{input_file}' was not found.")
        sys.exit(1)

    if emit_cpp:
        parser = FanglessParser()
        ast = parser.parse(source_code)
        if parser.errors:
            print("Syntax errors found:")
            for error in parser.errors:
                print(error)
            sys.exit(1)
        try:
            cpp_source = transpile_ast(ast)
        except TranspileError as error:
            print(f"Transpile error: {error}")
            sys.exit(1)

        if output_file:
            Path(output_file).write_text(cpp_source, encoding="utf-8")
            print(f"Generated C++: {output_file}")
        else:
            print(cpp_source)
        return

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
