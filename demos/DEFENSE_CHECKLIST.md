# Defense Demo Checklist

Use this guide during the project defense. Each demo exercises a core
requirement from Phase 3 of the assignment.

## Prerequisites

```bash
pip install -r requirements.txt
```

You need Python 3, PLY, and a C++17 compiler (`g++`) on PATH.

## Quick validation (run before the defense)

```bash
python demos/run_demos.py --full
python tests/transpile/run_transpile_error_tests.py
```

This runs:

1. Runtime smoke test (`PyValue` C++ runtime)
2. Codegen test suite (14 end-to-end cases)
3. All five defense demos below

## Live demo commands

Each demo can be shown live with one command:

```bash
python src/main.py --codegen --compile --run --output demos/build/demo.cpp demos/demo_functions.py
```

Replace `demo_functions.py` with any file from the table below.

## Demo program reference

| # | File | What it shows | Expected output |
|---|------|---------------|-----------------|
| 1 | `demo_dynamic_typing.py` | Dynamic typing via `PyValue` | `True` |
| 2 | `demo_functions.py` | `def`, parameters, `return`, calls | `16` |
| 3 | `demo_control_flow.py` | `if`/`elif`/`else`, `while`, `for`, `break`/`continue` | `large` then `22` |
| 4 | `demo_lists.py` | Lists, `.append()`, indexing, `len()` | `10 30 3` |
| 5 | `demo_fibonacci.py` | Recursive functions (benchmark-style) | `55` |

## Suggested defense flow (5–7 minutes)

1. **Overview** — Show the pipeline: Fangless source → AST → C++ → executable.
2. **Dynamic typing (Demo 1)** — Explain `PyValue` and runtime type checks.
3. **Functions (Demo 2)** — Show generated `PyValue foo(PyValue a, ...)`.
4. **Control flow (Demo 3)** — Highlight `py_truthy()` for conditions.
5. **Lists (Demo 4)** — Show list operations through the runtime.
6. **Fibonacci (Demo 5)** — Connect to performance benchmarks.
7. **Benchmarks** — Open `benchmarks/results/PERFORMANCE_ANALYSIS.md` and charts.

## One-liner for any demo

```bash
python demos/run_demos.py --demo demo_functions
```

## Known limitations (mention proactively)

- Classes, tuples, dicts, slicing, and `try/except` are parsed but not transpiled.
- Recursive Fibonacci benchmark stops at n=34 (exponential cost).
- Generated code uses the `PyValue` runtime; hand-written C++ is faster.

## Full test commands

```bash
python tests/runtime/run_runtime_smoke_test.py
python tests/codegen/run_codegen_tests.py
python demos/run_demos.py
python benchmarks/run_benchmarks.py --quick --samples 1
```
