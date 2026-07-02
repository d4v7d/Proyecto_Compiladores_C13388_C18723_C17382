# Performance Benchmarks

This tests measure the performance of the Fangless-to-C++ compiler by
comparing three implementations of the same algorithms.

## The three implementations compared

| Implementation | How it is produced |
|----------------|--------------------|
| **Original Python** | The Fangless source in `fangless/` run directly under CPython |
| **Generated C++** | The same Fangless source transpiled to C++ and compiled with `g++ -O2` |
| **Hand-written C++** | A native C++ reference in `handwritten_cpp/`, compiled with `g++ -O2` |

The hand-written version is the performance ceiling; the gap between it and the
generated version is the cost of the dynamic-typing runtime.

## Algorithms

| Algorithm | File | What it stresses |
|-----------|------|------------------|
| Recursive Fibonacci | `fib_recursive.py` | Function-call overhead, exponential growth |
| Iterative Fibonacci | `fib_iterative.py` | Tight arithmetic loops (repeated 100 000×) |
| Bubble sort | `bubble_sort.py` | Nested loops, list indexing and mutation |

Every program reads the input size `n` from stdin and prints a checksum so
the harness can verify all three implementations agree.

## Requirements

- Python 3 with `ply` and `matplotlib` (`pip install ply matplotlib`)
- A C++17 compiler on `PATH` (`g++`)

## How to run

```bash
python benchmarks/run_benchmarks.py --quick --samples 1
```

Full run (the numbers for the report):

```bash
python benchmarks/run_benchmarks.py --samples 5
python benchmarks/plot_results.py
```

Added flags:

- `--samples N` — timing runs per data point; the fastest (min) is kept to
  reduce noise from OS scheduling.
- `--timeout SECONDS` — per-run timeout; a run that exceeds it is recorded as a
  timeout instead of hanging the suite.
- `--algorithms fib_iterative,bubble_sort` — run only an algo.

## Methodology notes

- **Wall-clock timing** of the whole process (`time.perf_counter`) is used, so
  each implementation pays its own startup cost. Process
  startup is part of the real cost of running a program.
- **Best-of-N**: the minimum of `--samples` runs is reported, which is the
  standard way to filter out scheduling noise.
- **`-O2`** is applied to both C++ builds for a fair comparison.
- **Checksum verification**: if the three implementations disagree for any size,
  the harness prints a `[WARNING] checksum mismatch`.

## The `fib(50)` recursive caveat

The assignment asks for recursive Fibonacci "for values 1 to 50". Naive
recursion is exponential: `fib(50)` performs on the order of 40 billion calls,
which is infeasible for the Python and generated-C++ versions (hours to
compute). The default recursive sizes therefore stop at `n = 34`, which already
shows the exponential curve clearly. The **iterative** version runs all the way
to `n = 50` because it is linear. For running the complete test modify `DEFAULT_SIZES` in `run_benchmarks.py`.

## Output

- `results/benchmark_results.csv` — one row per (algorithm, size, implementation)
  with the checksum and best time in seconds.
- `results/<algorithm>.png` — time-vs-size chart, one line per implementation.
  Recursive Fibonacci uses a logarithmic time axis because of its exponential
  growth.
