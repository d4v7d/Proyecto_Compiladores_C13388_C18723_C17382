from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.codegen.cpp_runtime import get_cpp_runtime


OUTPUT_PATH = Path(__file__).resolve().parent / "runtime_smoke_test.cpp"


def main() -> None:
    cpp_code = get_cpp_runtime()
    smoke_test = r"""

void assert_truthy(const PyValue& value, const std::string& message) {
    if (!py_truthy(value)) {
        throw std::runtime_error(message);
    }
}

void assert_equal_string(
    const PyValue& actual,
    const std::string& expected,
    const std::string& message
) {
    if (actual.to_string() != expected) {
        throw std::runtime_error(
            message + ": expected '" + expected + "', got '" + actual.to_string() + "'"
        );
    }
}

void assert_equal_int(
    const PyValue& actual,
    long long expected,
    const std::string& message
) {
    if (py_as_int(actual) != expected) {
        throw std::runtime_error(
            message + ": expected '" + std::to_string(expected)
            + "', got '" + actual.to_string() + "'"
        );
    }
}

int main() {
    PyValue value = PyValue(10);
    value = PyValue("hello");
    assert_equal_string(value, "hello", "Dynamic reassignment failed");

    assert_equal_string(py_add(PyValue(2), PyValue(3)), "5", "Integer addition failed");

    assert_equal_string(
        py_add(PyValue("hello "), PyValue("world")),
        "hello world",
        "String concatenation failed"
    );

    assert_truthy(py_eq(PyValue(5), PyValue(5)), "Equality comparison failed");
    assert_truthy(py_not(PyValue(false)), "Logical not failed");

    PyValue list_value = py_list(PyValue::List{PyValue(1), PyValue(2)});
    py_append(list_value, PyValue(3));
    assert_equal_int(py_len(list_value), 3, "List append or len failed");

    assert_equal_string(py_get_item(list_value, PyValue(1)), "2", "List indexing failed");

    PyValue range_value = py_range(PyValue(5));
    assert_equal_int(py_len(range_value), 5, "Range length failed");

    PyValue::List iterated_values = py_iter(range_value);
    if (iterated_values.size() != 5) {
        throw std::runtime_error("Range iteration failed");
    }
    assert_equal_string(iterated_values[4], "4", "Range iteration value failed");

    assert_equal_int(py_int(PyValue("123")), 123, "String to int conversion failed");
    assert_equal_string(py_float(PyValue("3.5")), "3.5", "String to float conversion failed");
    assert_equal_string(py_str(PyValue(42)), "42", "Int to string conversion failed");
    assert_truthy(py_bool(PyValue(1)), "Int to bool conversion failed");

    py_print();
    py_print(PyValue("x ="), PyValue(10));

    return 0;
}
"""
    OUTPUT_PATH.write_text(cpp_code + smoke_test, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(
        "Compile manually with: "
        "g++ -std=c++17 tests/runtime/runtime_smoke_test.cpp "
        "-o tests/runtime/runtime_smoke_test"
    )


if __name__ == "__main__":
    main()
