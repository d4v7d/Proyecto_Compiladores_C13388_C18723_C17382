from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "tests" / "runtime" / "generate_runtime_smoke_test.py"
CPP_FILE = REPO_ROOT / "tests" / "runtime" / "runtime_smoke_test.cpp"
BINARY_FILE = REPO_ROOT / "tests" / "runtime" / "runtime_smoke_test"


def run_checked(command: list[str], step: str) -> None:
    try:
        subprocess.run(
            command,
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as error:
        print(f"{step} failed", file=sys.stderr)
        if error.stdout:
            print(error.stdout, file=sys.stdout)
        if error.stderr:
            print(error.stderr, file=sys.stderr)
        raise SystemExit(error.returncode) from error


def main() -> None:
    print("generating")
    run_checked([sys.executable, str(GENERATOR)], "generating")

    if shutil.which("g++") is None:
        print("g++ was not found. A C++17-compatible compiler is required.", file=sys.stderr)
        raise SystemExit(1)

    print("compiling")
    run_checked(
        [
            "g++",
            "-std=c++17",
            str(CPP_FILE.relative_to(REPO_ROOT)),
            "-o",
            str(BINARY_FILE.relative_to(REPO_ROOT)),
        ],
        "compiling",
    )

    print("running")
    run_checked([str(BINARY_FILE)], "running")

    print("success")


if __name__ == "__main__":
    main()
