# Fangless Python Compiler

## Project Overview

Fangless Python is a simplified Python compiler front end built with PLY
(Python Lex-Yacc). It reads a source file, converts it into tokens, parses those
tokens, and prints either a visual hierarchical AST or clear errors.

## Requirements

- Python 3.8 or newer
- PLY

Install dependencies with:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python src/main.py <source_file>
```

Example:

```bash
python src/main.py "Casos de prueba/Parser/parser_part1.fpy"
```

## Project Structure

```text
src/
  main.py
  lexer/
    token_definitions.py
    lexer_rules.py
    lexer_builder.py
  parser/
    grammar_rules.py
    grammar_extensions.py
    parser_builder.py
    parser_errors.py
    ast_nodes.py
    precedence.py
Casos de prueba/
Casos de prueba extra/
Casos de prueba incorrectos/
```

## Compiler Flow

```text
source file -> lexer -> tokens -> parser -> AST or errors
```

`src/main.py` prints the token stream first. If the lexer reports errors, those
errors are printed and parser execution stops. If tokenization succeeds, the
parser runs and prints either syntax errors or the generated AST.

## Lexer Features

The lexer supports:

- Identifiers
- Integers
- Floats
- Strings
- Booleans: `True`, `False`
- Keywords
- Operators
- Comments beginning with `#`
- `NEWLINE`
- `INDENT`
- `DENT`

`DENT` is the project's equivalent of the `DEDENT` token mentioned in the
assignment. It is emitted when indentation decreases.

String literals may use single or double quotes. The accepted escape sequences
are:

```text
\n, \t, \\, \", \'
```

The lexer detects:

- Unknown characters
- Invalid indentation
- Invalid string escape sequences

For example:

```python
x = "bad\q"
```

reports:

```text
Lexical error: invalid escape sequence '\q' at line 1, column 9
```

## Parser Features

The parser supports:

- Assignments
- Compound assignments
- Arithmetic expressions
- Relational expressions
- Logical expressions
- Grouped expressions
- Operator precedence
- `if` / `elif` / `else`
- Nested conditionals
- `while`
- `for`
- `break` / `continue` / `pass`
- Function definitions
- Function calls
- `return`
- Class definitions
- Simple inheritance
- Attribute access
- Method calls
- Indexing
- Lists
- Tuples
- Dictionaries
- Sets
- String methods as method-call syntax
- List methods as method-call syntax
- Dictionary methods as method-call syntax
- Set methods as method-call syntax
- `print()`
- `input()`
- Type conversion calls such as `int()`, `float()`, `str()`, `bool()`
- Basic `try-except`

Method calls are parsed syntactically. For example, `text.lower()`,
`items.append(4)`, `data.get("a")`, and `numbers.union({5})` are accepted as
method-call expressions.

## AST Output

The parser generates an AST and `main.py` prints it as a visual hierarchical
tree when parsing succeeds.

Input:

```python
x = 5 + 3
```

Output:

```text
Program
└── Assignment (=)
    ├── Identifier (x)
    └── BinaryOperation (+)
        ├── IntegerLiteral (5)
        └── IntegerLiteral (3)
```

## Error Handling

Lexical errors stop parser execution. This avoids reporting syntax errors that
are only side effects of invalid tokens.

Syntax errors include line, column, and token information when available. If the
parser reaches the end of the input while expecting more syntax, it reports an
unexpected end of input.

Examples:

```python
x =
```

```python
x = * 5
```

```python
x = "bad\q"
```

## Test Commands

```bash
python src/main.py "Casos de prueba/Parser/parser_part1.fpy"
python src/main.py "Casos de prueba/Parser/try_except_basic.fpy"
python src/main.py "Casos de prueba/Parser/method_calls_required.fpy"
python src/main.py "Casos de prueba/Parser/invalid/missing_expression.fpy"
python src/main.py "Casos de prueba/Parser/invalid/invalid_string_escape.fpy"
python src/main.py "Casos de prueba extra/indent_if_elif_else.py"
```

## Supported Subset

The supported subset focuses on a Python-like syntax for lexical analysis and
AST generation. It includes basic statements, expressions, control flow,
functions, classes with simple inheritance, common data structures, indexing,
method-call syntax, built-in style calls, and basic `try-except`.

The current implementation is a front end: it tokenizes and parses the supported
subset and prints an AST. It does not document code generation or runtime
semantics for these constructs.

## Unsupported Features / Limitations

The following features are not implemented:

- Nested functions
- Comprehensions
- Lambdas
- Functions as arguments
- Decorators
- Generators / `yield`
- `async` / `await`
- Metaclasses
- Multiple inheritance
- Context managers / `with`
- Imports
- F-strings
- `try-finally`
- `try-except-else`

