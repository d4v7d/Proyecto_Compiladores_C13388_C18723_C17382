"""Genera un informe PDF en español con los gráficos y explicación de cada benchmark."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

BENCH_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BENCH_DIR / "results"
CSV_PATH = RESULTS_DIR / "benchmark_results.csv"
PDF_PATH = RESULTS_DIR / "Informe_Benchmarks.pdf"

BENCHMARKS = [
    {
        "key": "fib_recursive",
        "title": "Fibonacci Recursivo",
        "sentence": (
            "Este benchmark calcula Fibonacci(n) con recursión y muestra cómo "
            "el tiempo crece muy rápido al aumentar n, comparando Python, C++ "
            "generado por el transpilador y C++ escrito a mano."
        ),
        "log_y": True,
    },
    {
        "key": "fib_iterative",
        "title": "Fibonacci Iterativo",
        "sentence": (
            "Este benchmark repite muchas veces un Fibonacci iterativo para "
            "medir la velocidad de bucles simples en las tres implementaciones."
        ),
        "log_y": False,
    },
    {
        "key": "bubble_sort",
        "title": "Ordenamiento Burbuja (Bubble Sort)",
        "sentence": (
            "Este benchmark ordena un arreglo en el peor caso y sirve para "
            "comparar el rendimiento con bucles anidados y acceso a listas."
        ),
        "log_y": False,
    },
]

IMPL_LABELS = {
    "python": "Python original",
    "generated_cpp": "C++ generado (transpilador)",
    "handwritten_cpp": "C++ escrito a mano",
}


def load_rows() -> list[dict]:
    if not CSV_PATH.exists():
        raise SystemExit(
            f"No se encontró {CSV_PATH}. Ejecuta primero: py benchmarks/run_benchmarks.py --samples 5"
        )
    with CSV_PATH.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_chart_figure(algorithm: str, rows: list[dict], title: str, log_y: bool) -> plt.Figure:
    data: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        if row["algorithm"] != algorithm or not row["seconds"]:
            continue
        data[row["implementation"]].append((int(row["size"]), float(row["seconds"])))

    figure, axis = plt.subplots(figsize=(8.5, 5))
    for impl_name, points in sorted(data.items()):
        points.sort()
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        label = IMPL_LABELS.get(impl_name, impl_name)
        axis.plot(xs, ys, marker="o", label=label)

    axis.set_title(title, fontsize=14, fontweight="bold")
    axis.set_xlabel("Tamaño de entrada (n)")
    axis.set_ylabel("Tiempo (segundos)")
    if log_y:
        axis.set_yscale("log")
        axis.set_ylabel("Tiempo (segundos, escala logarítmica)")
    axis.legend()
    axis.grid(True, linestyle="--", alpha=0.4)
    figure.tight_layout()
    return figure


def add_cover_page(pdf: PdfPages) -> None:
    figure = plt.figure(figsize=(8.5, 11))
    figure.patch.set_facecolor("white")
    axis = figure.add_subplot(111)
    axis.axis("off")
    text = (
        "Informe de Benchmarks\n"
        "Proyecto: Transpilador Fangless Python → C++\n\n"
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        "Se comparan tres versiones de cada programa:\n"
        "  • Python original\n"
        "  • C++ generado por el transpilador\n"
        "  • C++ escrito a mano (referencia)\n\n"
        "Los tres algoritmos probados son:\n"
        "  1. Fibonacci Recursivo (n = 1..34)\n"
        "  2. Fibonacci Iterativo (n = 1..50)\n"
        "  3. Ordenamiento Burbuja (n = 100..1000)\n"
    )
    axis.text(
        0.5,
        0.55,
        text,
        ha="center",
        va="center",
        fontsize=13,
        family="sans-serif",
        linespacing=1.6,
        transform=axis.transAxes,
    )
    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)


def add_benchmark_page(pdf: PdfPages, bench: dict, rows: list[dict]) -> None:
    figure = plt.figure(figsize=(8.5, 10))
    grid = figure.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.35)

    chart_ax = figure.add_subplot(grid[0])
    data: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        if row["algorithm"] != bench["key"] or not row["seconds"]:
            continue
        data[row["implementation"]].append((int(row["size"]), float(row["seconds"])))

    for impl_name, points in sorted(data.items()):
        points.sort()
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        label = IMPL_LABELS.get(impl_name, impl_name)
        chart_ax.plot(xs, ys, marker="o", label=label)

    chart_ax.set_title(bench["title"], fontsize=14, fontweight="bold")
    chart_ax.set_xlabel("Tamaño de entrada (n)")
    if bench["log_y"]:
        chart_ax.set_yscale("log")
        chart_ax.set_ylabel("Tiempo (segundos, escala logarítmica)")
    else:
        chart_ax.set_ylabel("Tiempo (segundos)")
    chart_ax.legend()
    chart_ax.grid(True, linestyle="--", alpha=0.4)

    text_ax = figure.add_subplot(grid[1])
    text_ax.axis("off")
    text_ax.text(
        0.5,
        0.5,
        f"¿Qué mide? {bench['sentence']}",
        ha="center",
        va="center",
        fontsize=11,
        wrap=True,
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#f0f4f8", edgecolor="#c0c8d0"),
    )

    pdf.savefig(figure, bbox_inches="tight")
    plt.close(figure)

    png_path = RESULTS_DIR / f"{bench['key']}.png"
    png_figure = build_chart_figure(bench["key"], rows, bench["title"], bench["log_y"])
    png_figure.savefig(png_path, dpi=120, bbox_inches="tight")
    plt.close(png_figure)


def main() -> None:
    rows = load_rows()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with PdfPages(PDF_PATH) as pdf:
        add_cover_page(pdf)
        for bench in BENCHMARKS:
            add_benchmark_page(pdf, bench, rows)

    print(f"Informe PDF generado: {PDF_PATH}")
    for bench in BENCHMARKS:
        print(f"Gráfico PNG: {RESULTS_DIR / (bench['key'] + '.png')}")


if __name__ == "__main__":
    main()
