#include <iostream>
#include <string>
#include <vector>
#include <variant>
#include <stdexcept>
#include <sstream>
#include <cstddef>
#include <cmath>

// Runtime errors
// Used for invalid operations, failed conversions, and out-of-range access.
class PyRuntimeError : public std::runtime_error {
public:
    explicit PyRuntimeError(const std::string& message)
        : std::runtime_error(message) {}
};

// Dynamic value representation
// Represents dynamic Fangless Python values in C++.
class PyValue {
public:
    using List = std::vector<PyValue>;
    using Value = std::variant<std::monostate, long long, double, bool, std::string, List>;

    Value data;

    PyValue()
        : data(std::monostate{}) {}

    PyValue(std::nullptr_t)
        : data(std::monostate{}) {}

    PyValue(int value)
        : data(static_cast<long long>(value)) {}

    PyValue(long long value)
        : data(value) {}

    PyValue(double value)
        : data(value) {}

    PyValue(bool value)
        : data(value) {}

    PyValue(const char* value)
        : data(std::string(value)) {}

    PyValue(const std::string& value)
        : data(value) {}

    PyValue(const List& value)
        : data(value) {}

    std::string type_name() const {
        if (std::holds_alternative<std::monostate>(data)) {
            return "NoneType";
        }
        if (std::holds_alternative<long long>(data)) {
            return "int";
        }
        if (std::holds_alternative<double>(data)) {
            return "float";
        }
        if (std::holds_alternative<bool>(data)) {
            return "bool";
        }
        if (std::holds_alternative<std::string>(data)) {
            return "str";
        }
        if (std::holds_alternative<List>(data)) {
            return "list";
        }
        throw PyRuntimeError("Unknown PyValue type");
    }

    std::string to_string() const {
        if (std::holds_alternative<std::monostate>(data)) {
            return "None";
        }
        if (std::holds_alternative<long long>(data)) {
            return std::to_string(std::get<long long>(data));
        }
        if (std::holds_alternative<double>(data)) {
            std::ostringstream stream;
            stream << std::get<double>(data);
            return stream.str();
        }
        if (std::holds_alternative<bool>(data)) {
            return std::get<bool>(data) ? "True" : "False";
        }
        if (std::holds_alternative<std::string>(data)) {
            return std::get<std::string>(data);
        }
        if (std::holds_alternative<List>(data)) {
            const List& values = std::get<List>(data);
            std::ostringstream stream;
            stream << "[";
            for (std::size_t index = 0; index < values.size(); ++index) {
                if (index > 0) {
                    stream << ", ";
                }
                stream << values[index].to_string();
            }
            stream << "]";
            return stream.str();
        }
        throw PyRuntimeError("Unknown PyValue type");
    }
};

// Type helpers
bool py_is_int(const PyValue& value) {
    return std::holds_alternative<long long>(value.data);
}

bool py_is_float(const PyValue& value) {
    return std::holds_alternative<double>(value.data);
}

bool py_is_number(const PyValue& value) {
    return py_is_int(value) || py_is_float(value);
}

double py_as_double(const PyValue& value) {
    if (py_is_int(value)) {
        return static_cast<double>(std::get<long long>(value.data));
    }
    if (py_is_float(value)) {
        return std::get<double>(value.data);
    }
    throw PyRuntimeError("Expected number, got " + value.type_name());
}

long long py_as_int(const PyValue& value) {
    if (py_is_int(value)) {
        return std::get<long long>(value.data);
    }
    throw PyRuntimeError("Expected int, got " + value.type_name());
}

std::string py_unsupported_operand_types(
    const std::string& op,
    const PyValue& left,
    const PyValue& right
) {
    return "Unsupported operand types for " + op + ": "
        + left.type_name() + " and " + right.type_name();
}

// Arithmetic operations
PyValue py_add(const PyValue& left, const PyValue& right) {
    if (py_is_int(left) && py_is_int(right)) {
        return PyValue(py_as_int(left) + py_as_int(right));
    }
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) + py_as_double(right));
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return PyValue(std::get<std::string>(left.data) + std::get<std::string>(right.data));
    }
    throw PyRuntimeError(py_unsupported_operand_types("+", left, right));
}

PyValue py_sub(const PyValue& left, const PyValue& right) {
    if (py_is_int(left) && py_is_int(right)) {
        return PyValue(py_as_int(left) - py_as_int(right));
    }
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) - py_as_double(right));
    }
    throw PyRuntimeError(py_unsupported_operand_types("-", left, right));
}

PyValue py_mul(const PyValue& left, const PyValue& right) {
    if (py_is_int(left) && py_is_int(right)) {
        return PyValue(py_as_int(left) * py_as_int(right));
    }
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) * py_as_double(right));
    }
    throw PyRuntimeError(py_unsupported_operand_types("*", left, right));
}

PyValue py_div(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        double divisor = py_as_double(right);
        if (divisor == 0.0) {
            throw PyRuntimeError("Division by zero");
        }
        return PyValue(py_as_double(left) / divisor);
    }
    throw PyRuntimeError(py_unsupported_operand_types("/", left, right));
}

PyValue py_mod(const PyValue& left, const PyValue& right) {
    if (py_is_int(left) && py_is_int(right)) {
        long long divisor = py_as_int(right);
        if (divisor == 0) {
            throw PyRuntimeError("Modulo by zero");
        }
        return PyValue(py_as_int(left) % divisor);
    }
    throw PyRuntimeError(py_unsupported_operand_types("%", left, right));
}

PyValue py_floor_div(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        double divisor = py_as_double(right);
        if (divisor == 0.0) {
            throw PyRuntimeError("Division by zero");
        }
        double quotient = std::floor(py_as_double(left) / divisor);
        if (py_is_int(left) && py_is_int(right)) {
            return PyValue(static_cast<long long>(quotient));
        }
        return PyValue(quotient);
    }
    throw PyRuntimeError(py_unsupported_operand_types("//", left, right));
}

PyValue py_pow(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(std::pow(py_as_double(left), py_as_double(right)));
    }
    throw PyRuntimeError(py_unsupported_operand_types("**", left, right));
}

// Comparison operations
bool py_values_equal(const PyValue& left, const PyValue& right) {
    if (
        std::holds_alternative<std::monostate>(left.data)
        && std::holds_alternative<std::monostate>(right.data)
    ) {
        return true;
    }
    if (py_is_number(left) && py_is_number(right)) {
        return py_as_double(left) == py_as_double(right);
    }
    if (
        std::holds_alternative<bool>(left.data)
        && std::holds_alternative<bool>(right.data)
    ) {
        return std::get<bool>(left.data) == std::get<bool>(right.data);
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return std::get<std::string>(left.data) == std::get<std::string>(right.data);
    }
    return false;
}

PyValue py_eq(const PyValue& left, const PyValue& right) {
    return PyValue(py_values_equal(left, right));
}

PyValue py_ne(const PyValue& left, const PyValue& right) {
    return PyValue(!py_values_equal(left, right));
}

PyValue py_lt(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) < py_as_double(right));
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return PyValue(std::get<std::string>(left.data) < std::get<std::string>(right.data));
    }
    throw PyRuntimeError(py_unsupported_operand_types("<", left, right));
}

PyValue py_le(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) <= py_as_double(right));
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return PyValue(std::get<std::string>(left.data) <= std::get<std::string>(right.data));
    }
    throw PyRuntimeError(py_unsupported_operand_types("<=", left, right));
}

PyValue py_gt(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) > py_as_double(right));
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return PyValue(std::get<std::string>(left.data) > std::get<std::string>(right.data));
    }
    throw PyRuntimeError(py_unsupported_operand_types(">", left, right));
}

PyValue py_ge(const PyValue& left, const PyValue& right) {
    if (py_is_number(left) && py_is_number(right)) {
        return PyValue(py_as_double(left) >= py_as_double(right));
    }
    if (
        std::holds_alternative<std::string>(left.data)
        && std::holds_alternative<std::string>(right.data)
    ) {
        return PyValue(std::get<std::string>(left.data) >= std::get<std::string>(right.data));
    }
    throw PyRuntimeError(py_unsupported_operand_types(">=", left, right));
}

// Logical operations
bool py_truthy(const PyValue& value) {
    if (std::holds_alternative<std::monostate>(value.data)) {
        return false;
    }
    if (std::holds_alternative<long long>(value.data)) {
        return std::get<long long>(value.data) != 0;
    }
    if (std::holds_alternative<double>(value.data)) {
        return std::get<double>(value.data) != 0.0;
    }
    if (std::holds_alternative<bool>(value.data)) {
        return std::get<bool>(value.data);
    }
    if (std::holds_alternative<std::string>(value.data)) {
        return !std::get<std::string>(value.data).empty();
    }
    if (std::holds_alternative<PyValue::List>(value.data)) {
        return !std::get<PyValue::List>(value.data).empty();
    }
    throw PyRuntimeError("Unknown PyValue type");
}

// Built-in conversions
PyValue py_str(const PyValue& value) {
    return PyValue(value.to_string());
}

PyValue py_bool(const PyValue& value) {
    return PyValue(py_truthy(value));
}

PyValue py_int(const PyValue& value) {
    if (py_is_int(value)) {
        return PyValue(py_as_int(value));
    }
    if (py_is_float(value)) {
        return PyValue(static_cast<long long>(std::get<double>(value.data)));
    }
    if (std::holds_alternative<bool>(value.data)) {
        return PyValue(std::get<bool>(value.data) ? 1LL : 0LL);
    }
    if (std::holds_alternative<std::string>(value.data)) {
        const std::string& text = std::get<std::string>(value.data);
        try {
            std::size_t parsed_chars = 0;
            long long result = std::stoll(text, &parsed_chars);
            if (parsed_chars != text.size()) {
                throw PyRuntimeError("Invalid literal for int: " + text);
            }
            return PyValue(result);
        } catch (const PyRuntimeError&) {
            throw;
        } catch (const std::exception&) {
            throw PyRuntimeError("Invalid literal for int: " + text);
        }
    }
    throw PyRuntimeError("Cannot convert " + value.type_name() + " to int");
}

PyValue py_float(const PyValue& value) {
    if (py_is_int(value)) {
        return PyValue(static_cast<double>(py_as_int(value)));
    }
    if (py_is_float(value)) {
        return PyValue(std::get<double>(value.data));
    }
    if (std::holds_alternative<bool>(value.data)) {
        return PyValue(std::get<bool>(value.data) ? 1.0 : 0.0);
    }
    if (std::holds_alternative<std::string>(value.data)) {
        const std::string& text = std::get<std::string>(value.data);
        try {
            std::size_t parsed_chars = 0;
            double result = std::stod(text, &parsed_chars);
            if (parsed_chars != text.size()) {
                throw PyRuntimeError("Invalid literal for float: " + text);
            }
            return PyValue(result);
        } catch (const PyRuntimeError&) {
            throw;
        } catch (const std::exception&) {
            throw PyRuntimeError("Invalid literal for float: " + text);
        }
    }
    throw PyRuntimeError("Cannot convert " + value.type_name() + " to float");
}

// List and iteration helpers
bool py_is_list(const PyValue& value) {
    return std::holds_alternative<PyValue::List>(value.data);
}

const PyValue::List& py_as_list(const PyValue& value) {
    if (py_is_list(value)) {
        return std::get<PyValue::List>(value.data);
    }
    throw PyRuntimeError("Expected list, got " + value.type_name());
}

PyValue::List& py_as_list_mut(PyValue& value) {
    if (py_is_list(value)) {
        return std::get<PyValue::List>(value.data);
    }
    throw PyRuntimeError("Expected list, got " + value.type_name());
}

PyValue py_list(const PyValue::List& values) {
    return PyValue(values);
}

long long py_normalize_index(long long index, std::size_t size) {
    long long length = static_cast<long long>(size);
    if (index < 0) {
        index += length;
    }
    if (index < 0 || index >= length) {
        throw PyRuntimeError("Index out of range");
    }
    return index;
}

PyValue py_len(const PyValue& value) {
    if (std::holds_alternative<std::string>(value.data)) {
        return PyValue(static_cast<long long>(std::get<std::string>(value.data).size()));
    }
    if (py_is_list(value)) {
        return PyValue(static_cast<long long>(py_as_list(value).size()));
    }
    throw PyRuntimeError("Object of type " + value.type_name() + " has no len()");
}

PyValue::List py_iter(const PyValue& value) {
    if (py_is_list(value)) {
        return py_as_list(value);
    }
    if (std::holds_alternative<std::string>(value.data)) {
        const std::string& text = std::get<std::string>(value.data);
        PyValue::List values;
        for (char character : text) {
            values.push_back(PyValue(std::string(1, character)));
        }
        return values;
    }
    throw PyRuntimeError("Object of type " + value.type_name() + " is not iterable");
}

PyValue py_get_item(const PyValue& collection, const PyValue& index) {
    long long raw_index = py_as_int(index);
    if (py_is_list(collection)) {
        const PyValue::List& values = py_as_list(collection);
        long long normalized_index = py_normalize_index(raw_index, values.size());
        return values[static_cast<std::size_t>(normalized_index)];
    }
    if (std::holds_alternative<std::string>(collection.data)) {
        const std::string& text = std::get<std::string>(collection.data);
        long long normalized_index = py_normalize_index(raw_index, text.size());
        return PyValue(std::string(1, text[static_cast<std::size_t>(normalized_index)]));
    }
    throw PyRuntimeError("Object of type " + collection.type_name() + " is not subscriptable");
}

void py_set_item(PyValue& collection, const PyValue& index, const PyValue& new_value) {
    PyValue::List& values = py_as_list_mut(collection);
    long long normalized_index = py_normalize_index(py_as_int(index), values.size());
    values[static_cast<std::size_t>(normalized_index)] = new_value;
}

void py_append(PyValue& collection, const PyValue& new_value) {
    py_as_list_mut(collection).push_back(new_value);
}

PyValue py_range(const PyValue& start, const PyValue& stop, const PyValue& step) {
    long long start_value = py_as_int(py_int(start));
    long long stop_value = py_as_int(py_int(stop));
    long long step_value = py_as_int(py_int(step));

    if (step_value == 0) {
        throw PyRuntimeError("range() step argument must not be zero");
    }

    PyValue::List values;
    if (step_value > 0) {
        for (long long value = start_value; value < stop_value; value += step_value) {
            values.push_back(PyValue(value));
        }
    } else {
        for (long long value = start_value; value > stop_value; value += step_value) {
            values.push_back(PyValue(value));
        }
    }
    return PyValue(values);
}

PyValue py_range(const PyValue& start, const PyValue& stop) {
    return py_range(start, stop, PyValue(1LL));
}

PyValue py_range(const PyValue& stop) {
    return py_range(PyValue(0LL), stop, PyValue(1LL));
}

PyValue py_and(const PyValue& left, const PyValue& right) {
    return PyValue(py_truthy(left) && py_truthy(right));
}

PyValue py_or(const PyValue& left, const PyValue& right) {
    return PyValue(py_truthy(left) || py_truthy(right));
}

PyValue py_not(const PyValue& value) {
    return PyValue(!py_truthy(value));
}

// Input/output helpers
void py_print() {
    std::cout << std::endl;
}

void py_print(const PyValue& value) {
    std::cout << value.to_string() << std::endl;
}

template <typename... Args>
void py_print_remaining(const PyValue& value, const Args&... args) {
    std::cout << " " << value.to_string();
    if constexpr (sizeof...(args) > 0) {
        py_print_remaining(args...);
    }
}

template <typename... Args>
void py_print(const PyValue& first, const PyValue& second, const Args&... args) {
    std::cout << first.to_string();
    py_print_remaining(second, args...);
    std::cout << std::endl;
}

PyValue py_input() {
    std::string line;
    std::getline(std::cin, line);
    return PyValue(line);
}

int main() {
    PyValue x = PyValue(5LL);
    x = py_add(x, PyValue(3LL));
    PyValue y = py_add(PyValue(2LL), py_mul(PyValue(3LL), PyValue(4LL)));
    PyValue z = py_mul(py_add(PyValue(2LL), PyValue(3LL)), PyValue(4LL));
    PyValue flag = py_and(PyValue(true), py_not(PyValue(false)));
    PyValue result = py_ge(x, PyValue(10LL));
    return 0;
}
