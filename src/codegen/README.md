# Code Generation (`src/codegen`)

This package implements **Phase 3** of the Fangless Python compiler project: translating the parser AST into self-contained, compilable C++ that uses a dynamic typing runtime (`PyValue`).

The assignment specification is defined in `Tarea Programada 3 compiladores.pdf` at the repository root.

---

## Package Structure

| File | Responsibility |
|------|----------------|
| `cpp_runtime.py` | Embeds the C++ runtime (`PyValue`, operators, builtins) as a string returned by `get_cpp_runtime()` |
| `scope.py` | Lexical scope tracking and C++-safe identifier sanitization |
| `cpp_emitter.py` | AST visitor that emits C++ statements and expressions |
| `transpiler.py` | High-level API: combines runtime + generated code into one translation unit |
| `__init__.py` | Public entry point for `get_cpp_runtime()` |

Related files outside this folder:

| File | Responsibility |
|------|----------------|
| `src/transpile.py` | CLI to transpile a source file to `.cpp` |
| `src/main.py` | Supports `--codegen` and `--output` flags |
| `tests/runtime/run_runtime_smoke_test.py` | Validates the C++ runtime in isolation |
| `tests/codegen/run_codegen_tests.py` | End-to-end transpiler tests (parse → C++ → compile → run) |

---

## Recent Changes

### 1. Dynamic C++ Runtime (`cpp_runtime.py`)

- `PyValue` class using `std::variant` for `None`, `int`, `float`, `bool`, `str`, and `list`
- Runtime type checks and arithmetic, comparison, and logical operations
- Builtins: `len`, `int`, `float`, `str`, `bool`, `range`, `print`, `input`
- List helpers: indexing, mutation, iteration
- Added `py_floor_div` (`//`) and `py_pow` (`**`) for expression support

### 2. AST-to-C++ Emitter (`cpp_emitter.py`)

- Global statements are emitted inside `int main()`
- Top-level `def` functions are emitted as `PyValue name(PyValue ...)` before `main`
- Variable scopes are managed with a stack (`ScopeManager`)
- First assignment declares `PyValue x = ...`; later assignments allow dynamic type changes
- Conditions use `py_truthy()` as required by the assignment

### 3. Transpiler API (`transpiler.py`)

- `transpile_ast(ast)` → full `.cpp` source (runtime + generated code)
- `transpile_source(source, parser)` → parse then transpile
- Raises `TranspileError` for unsupported constructs

### 4. Tooling and Tests

- `src/transpile.py` CLI
- `src/main.py --codegen [--output file.cpp] <input>`
- `tests/codegen/run_codegen_tests.py` with 10 passing end-to-end cases

---

## How It Works

```
Fangless source (.py / .fpy)
        │
        ▼
   FanglessParser  ──► AST
        │
        ▼
    CppEmitter.emit_program()
        │
        ├── function definitions  →  PyValue foo(PyValue a, ...) { ... }
        └── global statements     →  int main() { ... }
        │
        ▼
   transpile_ast()
        │
        ├── get_cpp_runtime()     →  embedded C++ runtime
        └── generated lines       →  main + user functions
        │
        ▼
   output.cpp (self-contained)
        │
        ▼
   g++ -std=c++17 output.cpp -o program
```

### Design Decisions

1. **All user values are `PyValue`** — dynamic typing is handled at runtime, not with C++ static types.
2. **Functions return `PyValue`** — parameters and return values can change type across calls.
3. **Scopes are lexical** — each block, function body, and `for` loop pushes a new scope frame.
4. **Builtins map to runtime helpers** — e.g. `print(x)` → `py_print(x)`, `a + b` → `py_add(a, b)`.
5. **Output is self-contained** — every generated file includes the full runtime so it compiles without external headers beyond the C++ standard library.

---

## How to Test

### Prerequisites

- Python 3 with `ply` installed: `pip install ply`
- A C++17 compiler (`g++` recommended)

### 1. Runtime Smoke Test (validates `PyValue` only)

From the repository root:

```bash
python tests/runtime/run_runtime_smoke_test.py
```

Expected output:

```
generating
compiling
running
success
```

### 2. Codegen End-to-End Tests (validates AST → C++ → execution)

```bash
python tests/codegen/run_codegen_tests.py
```

Expected output:

```
Running codegen end-to-end tests

[PASS] literals_and_assignments
[PASS] dynamic_reassignment
[PASS] function_definition
[PASS] if_else
[PASS] while_loop
[PASS] for_loop_list
[PASS] for_loop_range
[PASS] list_operations
[PASS] comparisons_and_strings
[PASS] nested_function_scope

Results: 10 passed, 0 failed, 10 total
```

### 3. Transpile a Single File

```bash
python src/transpile.py "Test Files/test_function.py" "Test Files/test_function.cpp"
g++ -std=c++17 "Test Files/test_function.cpp" -o "Test Files/test_function"
./Test Files/test_function        # Linux/macOS
Test Files\test_function.exe      # Windows
```

Expected output: `5`

### 4. Transpile via `main.py`

```bash
python src/main.py --codegen --output out.cpp "Test Files/test_function.py"
g++ -std=c++17 out.cpp -o out
./out
```

---

## Feature Coverage vs. Assignment PDF

Legend: ✅ Implemented · ⚠️ Partial · ❌ Not implemented

### Core Transpiler Requirements (PDF Section: Mapeo de Características)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Global code wrapped in `main()` | ✅ | `CppEmitter.emit_program()` |
| `def` → C++ functions with dynamic params/returns | ✅ | `PyValue name(PyValue ...)` |
| Dynamic typing (`PyValue`) | ✅ | Runtime + all generated variables |
| `if` / `elif` / `else` with `py_truthy()` | ✅ | Emitted as `if` / `else if` / `else` |
| `while` loops | ✅ | Direct `while (py_truthy(...))` |
| `for NAME in expression` | ✅ | Uses `py_iter()` + C++ range-for |
| Arithmetic operators (`+`, `-`, `*`, `/`, `%`, `//`, `**`) | ✅ | Via `py_add`, `py_sub`, etc. |
| Relational operators (`==`, `!=`, `<`, `<=`, `>`, `>=`) | ✅ | Via `py_eq`, `py_lt`, etc. |
| Logical operators (`and`, `or`, `not`) | ✅ | Via `py_and`, `py_or`, `py_not` |
| Function calls with `PyValue` arguments | ✅ | User functions + builtins |
| Self-contained compilable `.cpp` output | ✅ | Runtime embedded in every file |

### Statements

| Construct | Status | Notes |
|-----------|--------|-------|
| Assignment (`=`, `+=`, `-=`, `*=`, `/=`, `%=` ) | ✅ | |
| Expression statements | ✅ | |
| `return` / `return expr` | ✅ | |
| `break` / `continue` | ✅ | |
| `pass` | ✅ | No-op |
| `try` / `except` / `finally` | ❌ | Parser supports it; emitter does not |
| `raise` | ❌ | |
| Nested `def` inside functions | ❌ | Explicit `TranspileError` |
| Class definitions | ❌ | Parser supports it; emitter does not |

### Expressions and Literals

| Construct | Status | Notes |
|-----------|--------|-------|
| `int`, `float`, `str`, `bool` literals | ✅ | |
| List literals `[a, b, ...]` | ✅ | |
| Identifier references | ✅ | Scope-checked |
| Grouped expressions `( ... )` | ✅ | |
| Unary `-`, `+`, `not` | ✅ | |
| Subscript read `obj[index]` | ✅ | `py_get_item` |
| Subscript write `obj[i] = v` | ✅ | `py_set_item` |
| Tuple literals | ❌ | |
| Dict / set literals | ❌ | |
| Slicing `a[start:stop]` | ❌ | |
| Attribute access `obj.attr` | ❌ | |
| Attribute assignment `obj.x = v` | ❌ | |
| Method calls (general) | ⚠️ | Only `.append()` on lists |
| `**=` / `//=` compound assignment | ❌ | Parser supports; emitter does not |

### Built-in Functions (Runtime + Emitter)

| Builtin | Runtime | Emitter |
|---------|---------|---------|
| `print` | ✅ | ✅ |
| `len` | ✅ | ✅ |
| `int` | ✅ | ✅ |
| `float` | ✅ | ✅ |
| `str` | ✅ | ✅ |
| `bool` | ✅ | ✅ |
| `range` | ✅ | ✅ (1–3 arguments) |
| `input` | ✅ | ✅ |
| `list()` constructor | ✅ | ⚠️ Use `[...]` literal instead |
| `dict`, `set`, `tuple` | ❌ | ❌ |

### Function Parameters

| Feature | Status |
|---------|--------|
| Simple parameters `def f(a, b)` | ✅ |
| Default values `def f(a=1)` | ❌ |
| `*args` | ❌ |
| `**kwargs` | ❌ |

### C++ Runtime Helpers (`cpp_runtime.py`)

| Category | Functions |
|----------|-----------|
| Type checks | `py_is_int`, `py_is_float`, `py_is_number`, `py_is_list` |
| Conversions | `py_as_int`, `py_as_double`, `py_int`, `py_float`, `py_str`, `py_bool` |
| Arithmetic | `py_add`, `py_sub`, `py_mul`, `py_div`, `py_mod`, `py_floor_div`, `py_pow` |
| Comparison | `py_eq`, `py_ne`, `py_lt`, `py_le`, `py_gt`, `py_ge`, `py_values_equal` |
| Logic | `py_and`, `py_or`, `py_not`, `py_truthy` |
| Lists | `py_list`, `py_len`, `py_get_item`, `py_set_item`, `py_append`, `py_iter` |
| Iteration | `py_range` (1/2/3 args) |
| I/O | `py_print`, `py_input` |

---

## What Is Still Missing for Full Assignment Compliance

### Transpiler (correctness — 40 pts rubric)

High priority to reach full parser coverage:

1. **Classes and OOP** — `class_def`, `attribute_access`, general `method_call`
2. **Data structures** — tuples, dicts, sets, slicing
3. **Exception handling** — `try` / `except` / `finally`, `raise`
4. **Advanced functions** — default parameters, `*args`, `**kwargs`
5. **Compound assignments** — `//=`, `**=`
6. **Semantic errors** — undeclared variables are caught; broader semantic analysis is not implemented

### Performance Analysis (rubric — not in `codegen` yet)

The PDF requires benchmarking and documentation:

| Benchmark | Status |
|-----------|--------|
| Recursive Fibonacci (n = 1..50) | ❌ Not implemented |
| Iterative Fibonacci (n = 1..50) | ❌ Not implemented |
| Custom algorithm (≥10 input sizes) | ❌ Not implemented |
| Tables, graphs, and written analysis | ❌ Not implemented |

These require separate benchmark scripts and a results document outside this package.

### Error Handling (rubric — 15 pts)

| Layer | Status |
|-------|--------|
| Lexical errors (unknown chars, bad escapes, indentation) | ✅ In lexer |
| Syntax errors (invalid grammar, malformed expressions) | ✅ In parser |
| Transpile errors (unsupported AST nodes) | ⚠️ `TranspileError` with message; no line/column yet |
| Runtime errors (`PyRuntimeError`) | ✅ In C++ runtime |

---

## Suggested Next Steps

1. Extend `cpp_emitter.py` for classes, dicts, and exception nodes already parsed by the grammar.
2. Add runtime support for dict/set/tuple in `cpp_runtime.py` before emitting those constructs.
3. Create `tests/benchmarks/` for Fibonacci and the custom algorithm required by the PDF.
4. Add line/column information to `TranspileError` for easier debugging.

---

## Quick Reference

```python
from codegen.transpiler import transpile_ast, transpile_source, TranspileError
from parser.parser_builder import FanglessParser

parser = FanglessParser()
cpp = transpile_source(open("program.py").read(), parser)
```

```bash
# Full validation pipeline
python tests/runtime/run_runtime_smoke_test.py
python tests/codegen/run_codegen_tests.py
```
