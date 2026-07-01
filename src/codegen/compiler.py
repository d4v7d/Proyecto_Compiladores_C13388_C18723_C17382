"""Locate a C++ compiler and use it to compile and run generated code.

This module isolates all interaction with the external C++ toolchain so that
both the CLI (``main.py``) and the benchmark scripts can share one robust
implementation instead of duplicating compiler-discovery logic.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable


class CompilerNotFoundError(Exception):
    """Raised when no C++ compiler can be located on the system."""


class CompilationError(Exception):
    """Raised when the compiler fails to build the generated C++ source."""


def find_compiler() -> str:
    """Return the path to a ``g++`` executable.

    Searches, in order: the system ``PATH``, packages installed through
    ``winget`` (WinLibs / MSYS2), and the default MSYS2 location. Raises
    :class:`CompilerNotFoundError` with actionable guidance if none is found.
    """
    compiler = shutil.which("g++")
    if compiler:
        return compiler

    # WinLibs / MSYS2 installed via winget land under the user's WinGet folder.
    winget_root = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget_root.exists():
        for candidate in winget_root.glob("**/g++.exe"):
            return str(candidate)

    # Default MSYS2 UCRT location.
    msys2_default = Path("C:/msys64/ucrt64/bin/g++.exe")
    if msys2_default.exists():
        return str(msys2_default)

    raise CompilerNotFoundError(
        "No C++ compiler (g++) was found. Install one, for example:\n"
        "  winget install --id BrechtSanders.WinLibs.POSIX.UCRT.MinGW -e\n"
        "then open a new terminal so g++ is available on your PATH."
    )


def compile_cpp(
    source_path: str | Path,
    output_path: str | Path,
    *,
    std: str = "c++17",
    extra_flags: Iterable[str] | None = None,
) -> Path:
    """Compile a ``.cpp`` file into an executable.

    Returns the path to the produced executable. Raises
    :class:`CompilationError` (never a raw traceback) when the compiler reports
    errors, so callers can present clean diagnostics.
    """
    compiler = find_compiler()
    command = [compiler, f"-std={std}"]
    if extra_flags:
        command.extend(extra_flags)
    command.extend([str(source_path), "-o", str(output_path)])

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise CompilationError(
            f"g++ failed (exit code {result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}".strip()
        )
    return Path(output_path)


def run_executable(
    executable_path: str | Path,
    *,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    """Run a compiled executable.

    With ``capture=False`` (default) the program's stdio is inherited, so its
    output appears live and ``input()`` still works. With ``capture=True`` the
    output is captured and returned for programmatic inspection (used by tests
    and benchmarks).
    """
    if capture:
        return subprocess.run(
            [str(executable_path)], capture_output=True, text=True
        )
    return subprocess.run([str(executable_path)])
