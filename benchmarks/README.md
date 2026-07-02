# Performance Benchmarks

These tests measure the performance of the Fangless-to-C++ compiler by
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

| Algorithm | File | Input sizes | What it stresses |
|-----------|------|-------------|------------------|
| Recursive Fibonacci | `fib_recursive.py` | n = 1..34 | Function-call overhead, exponential growth |
| Iterative Fibonacci | `fib_iterative.py` | n = 1..50 | Tight arithmetic loops (repeated 100 000×) |
| Bubble sort | `bubble_sort.py` | n = 100..1000 (10 sizes) | Nested loops, list indexing and mutation |

Every program reads the input size `n` from stdin and prints a checksum so
the harness can verify all three implementations agree.

## Requirements

- Python 3 with dependencies from `requirements.txt` (`ply`, `matplotlib`)
- A C++17 compiler on `PATH` (`g++`)

```bash
pip install -r requirements.txt
```

## How to run

Quick smoke test:

```bash
python benchmarks/run_benchmarks.py --quick --samples 1
```

Full run (numbers for the assignment report):

```bash
python benchmarks/run_benchmarks.py --samples 5
python benchmarks/plot_results.py
python benchmarks/generate_report.py
```

Additional flags:

- `--samples N` — timing runs per data point; the fastest (min) is kept to
  reduce noise from OS scheduling.
- `--timeout SECONDS` — default per-run timeout; recursive Fibonacci uses 300 s.
- `--algorithms fib_iterative,bubble_sort` — run only a subset.

## Methodology notes

- **Wall-clock timing** of the whole process (`time.perf_counter`) is used, so
  each implementation pays its own startup cost.
- **Best-of-N**: the minimum of `--samples` runs is reported.
- **`-O2`** is applied to both C++ builds for a fair comparison.
- **Checksum verification**: if the three implementations disagree for any size,
  the harness prints a `[WARNING] checksum mismatch`.

## The `fib(50)` recursive caveat

The assignment asks for recursive Fibonacci "for values 1 to 50". Naive
recursion is exponential: `fib(50)` performs on the order of 40 billion calls,
which is infeasible for the Python and generated-C++ versions (hours to
compute). The default recursive sizes therefore cover **n = 1..34**, which
already shows the exponential curve clearly. The **iterative** version runs
**n = 1..50** because it is linear.

## Output

| File | Description |
|------|-------------|
| `results/benchmark_results.csv` | Raw timings and checksums |
| `results/fib_recursive.png` | Chart: recursive Fibonacci |
| `results/fib_iterative.png` | Chart: iterative Fibonacci |
| `results/bubble_sort.png` | Chart: bubble sort |
| `results/PERFORMANCE_ANALYSIS.md` | Tables, chart references, and written analysis |

Recursive Fibonacci charts use a logarithmic time axis because of exponential
growth.
