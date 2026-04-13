from pathlib import Path
from src.lexer.lexer_builder import FanglessLexer

TESTS_DIR = Path("Casos de prueba")


def collect_test_files(base_path: Path):
    return sorted(base_path.rglob("*.py")) + sorted(base_path.rglob("*.fp"))


def run_tests():
    lexer = FanglessLexer()

    passed = []
    failed = []

    for file_path in collect_test_files(TESTS_DIR):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                source_code = file.read()

            tokens = lexer.tokenize(source_code)

            if lexer.errors:
                failed.append((file_path, lexer.errors.copy()))
            elif len(tokens) == 0 and source_code.strip():
                failed.append((file_path, ["No tokens generated"]))
            else:
                passed.append((file_path, len(tokens)))

        except Exception as error:
            failed.append((file_path, [str(error)]))

    total = len(passed) + len(failed)

    print("=== TEST SUMMARY ===")
    print(f"Total: {total}")
    print(f"Passed: {len(passed)}")
    print(f"Failed: {len(failed)}")

    if total > 0:
        print(f"Success rate: {(len(passed) / total) * 100:.2f}%")

    print("\n=== FIRST 10 PASSED FILES ===")
    for file_path, token_count in passed[:10]:
        print(f"[PASS] {file_path} -> {token_count} tokens")

    print("\n=== FAILED FILES ===")
    for file_path, reasons in failed:
        print(f"[FAIL] {file_path}")
        for reason in reasons[:5]:
            print(f"   - {reason}")


if __name__ == "__main__":
    run_tests()