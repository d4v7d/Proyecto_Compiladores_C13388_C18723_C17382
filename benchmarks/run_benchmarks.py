"""Performance benchmark harness for the Fangless transpiler.

For each algorithm and input size, this script times three implementations:

  1. original Python  - the Fangless source run under CPython
  2. generated C++    - the Fangless source transpiled to C++ and compiled
  3. hand-written C++ - a native C++ reference implementation

It verifies that all three produce the same checksum, then writes the timings
to a CSV file for plotting.

For usage: python benchmarks/run_benchmarks.py [--quick] [--samples N] [--timeout SECONDS] [--algorithms a,b]
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
REPO_ROOT = BENCH_DIR.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from parser.parser_builder import FanglessParser
from codegen.transpiler import transpile_source, TranspileError
from codegen.compiler import compile_cpp, CompilerNotFoundError, CompilationError

FANGLESS_DIR = BENCH_DIR / "fangless"
HANDWRITTEN_DIR = BENCH_DIR / "handwritten_cpp"
RESULTS_DIR = BENCH_DIR / "results"
BUILD_DIR = RESULTS_DIR / "build"

# Input sizes per algorithm (assignment: measure n = 1..50 where feasible).
# Naive recursive Fibonacci is exponential; sizes 35-50 are omitted because
# fib(50) alone requires ~40 billion calls and would take hours in Python.
DEFAULT_SIZES = {
    "fib_recursive": list(range(1, 35)),
    "fib_iterative": list(range(1, 51)),
    "bubble_sort": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
}

# Per-algorithm timeout overrides (seconds). Recursive Fib grows very fast.
DEFAULT_TIMEOUTS = {
    "fib_recursive": 300.0,
    "fib_iterative": 120.0,
    "bubble_sort": 120.0,
}

QUICK_SIZES = {
    "fib_recursive": [5, 10, 15, 20],
    "fib_iterative": [5, 10, 20, 30],
    "bubble_sort": [50, 100, 150],
}


def build_generated(algorithm: str) -> Path:
    """Transpile the Fangless program to C++ and compile it with -O2."""
    source = (FANGLESS_DIR / f"{algorithm}.py").read_text(encoding="utf-8")
    parser = FanglessParser()
    cpp_source = transpile_source(source, parser)

    cpp_path = BUILD_DIR / f"{algorithm}_generated.cpp"
    cpp_path.write_text(cpp_source, encoding="utf-8")
    exe_path = BUILD_DIR / f"{algorithm}_generated.exe"
    compile_cpp(cpp_path, exe_path, extra_flags=["-O2"])
    return exe_path


def build_handwritten(algorithm: str) -> Path:
    """Compile the hand-written C++ reference with -O2."""
    cpp_path = HANDWRITTEN_DIR / f"{algorithm}.cpp"
    exe_path = BUILD_DIR / f"{algorithm}_handwritten.exe"
    compile_cpp(cpp_path, exe_path, extra_flags=["-O2"])
    return exe_path


def time_run(command: list[str], stdin_text: str, samples: int, timeout: float):
    """Run a command `samples` times; return (best_seconds, stdout, timed_out)."""
    best: float | None = None
    output = ""
    for _ in range(samples):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                input=stdin_text,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return None, "", True
        elapsed = time.perf_counter() - start
        output = result.stdout.strip()
        if best is None or elapsed < best:
            best = elapsed
    return best, output, False


def main() -> None:
    parser = argparse.ArgumentParser(description="Run transpiler performance benchmarks.")
    parser.add_argument("--quick", action="store_true", help="use small sizes for a fast smoke run")
    parser.add_argument("--samples", type=int, default=3, help="timing runs per data point (min is kept)")
    parser.add_argument("--timeout", type=float, default=120.0, help="per-run timeout in seconds")
    parser.add_argument("--algorithms", type=str, default="", help="comma-separated subset to run")
    args = parser.parse_args()

    sizes_table = QUICK_SIZES if args.quick else DEFAULT_SIZES
    selected = [a.strip() for a in args.algorithms.split(",") if a.strip()] or list(sizes_table)

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    print("Running benchmarks (this can take a while)\n")

    for algorithm in selected:
        if algorithm not in sizes_table:
            print(f"[skip] unknown algorithm: {algorithm}")
            continue

        print(f"=== {algorithm} ===")
        try:
            generated_exe = build_generated(algorithm)
            handwritten_exe = build_handwritten(algorithm)
        except (TranspileError, CompilerNotFoundError, CompilationError) as error:
            print(f"[build error] {algorithm}: {error}")
            continue

        implementations = {
            "python": [sys.executable, str(FANGLESS_DIR / f"{algorithm}.py")],
            "generated_cpp": [str(generated_exe)],
            "handwritten_cpp": [str(handwritten_exe)],
        }

        algorithm_timeout = DEFAULT_TIMEOUTS.get(algorithm, args.timeout)

        for size in sizes_table[algorithm]:
            stdin_text = f"{size}\n"
            checksums: dict[str, str] = {}
            for impl_name, command in implementations.items():
                seconds, output, timed_out = time_run(
                    command, stdin_text, args.samples, algorithm_timeout
                )
                checksums[impl_name] = "TIMEOUT" if timed_out else output
                rows.append(
                    {
                        "algorithm": algorithm,
                        "size": size,
                        "implementation": impl_name,
                        "checksum": checksums[impl_name],
                        "seconds": "" if seconds is None else f"{seconds:.6f}",
                    }
                )
                shown = "timeout" if timed_out else f"{seconds:.4f}s"
                print(f"  n={size:<5} {impl_name:<16} {shown}")

            distinct = {c for c in checksums.values() if c != "TIMEOUT"}
            if len(distinct) > 1:
                print(f"  [WARNING] checksum mismatch at n={size}: {checksums}")
        print()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["algorithm", "size", "implementation", "checksum", "seconds"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {csv_path}")


if __name__ == "__main__":
    main()
