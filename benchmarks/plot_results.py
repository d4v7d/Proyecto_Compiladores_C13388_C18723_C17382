"""Generate performance charts from benchmark_results.csv.

Produces one PNG per algorithm plotting execution time against input size,
with one line per implementation (python, generated_cpp, handwritten_cpp).
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Write files without a display
import matplotlib.pyplot as plt

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"
CSV_PATH = RESULTS_DIR / "benchmark_results.csv"

# Algorithms whose growth is best viewed on a logarithmic time axis.
LOG_Y_AXIS = {"fib_recursive"}


def load_rows() -> list[dict]:
    with CSV_PATH.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(
            f"No results found at {CSV_PATH}. Run run_benchmarks.py first."
        )

    rows = load_rows()

    # algorithm - implementation - list of (size, seconds)
    data: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if not row["seconds"]:  # skip timeouts and missing measurements
            continue
        data[row["algorithm"]][row["implementation"]].append(
            (int(row["size"]), float(row["seconds"]))
        )

    for algorithm, implementations in data.items():
        plt.figure(figsize=(8, 5))
        for impl_name, points in sorted(implementations.items()):
            points.sort()
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            plt.plot(xs, ys, marker="o", label=impl_name)

        plt.title(f"{algorithm}: execution time vs input size")
        plt.xlabel("input size (n)")
        plt.ylabel("time (seconds, best of samples)")
        if algorithm in LOG_Y_AXIS:
            plt.yscale("log")
            plt.ylabel("time (seconds, log scale)")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        output_path = RESULTS_DIR / f"{algorithm}.png"
        plt.savefig(output_path, dpi=120, bbox_inches="tight")
        plt.close()
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
