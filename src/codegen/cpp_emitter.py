"""AST-to-C++ code emitter for the Fangless transpiler."""

from __future__ import annotations

from parser.ast_nodes import ASTNode

from .scope import ScopeManager, sanitize_identifier


class TranspileError(Exception):
    """Raised when the AST contains a construct that cannot be transpiled."""


BUILTIN_FUNCTIONS = {
    "print",
    "len",
    "int",
    "float",
    "str",
    "bool",
    "range",
    "input",
}

ASSIGNMENT_OPERATORS = {
    "=": lambda target, rhs: f"{target} = {rhs}",
    "+=": lambda target, rhs: f"{target} = py_add({target}, {rhs})",
    "-=": lambda target, rhs: f"{target} = py_sub({target}, {rhs})",
    "*=": lambda target, rhs: f"{target} = py_mul({target}, {rhs})",
    "/=": lambda target, rhs: f"{target} = py_div({target}, {rhs})",
    "%=": lambda target, rhs: f"{target} = py_mod({target}, {rhs})",
}

BINARY_OPERATORS = {
    "+": "py_add",
    "-": "py_sub",
    "*": "py_mul",
    "/": "py_div",
    "%": "py_mod",
    "==": "py_eq",
    "!=": "py_ne",
    "<": "py_lt",
    "<=": "py_le",
    ">": "py_gt",
    ">=": "py_ge",
    "and": "py_and",
    "or": "py_or",
}


def decode_python_string(raw: str) -> str:
    """Decode Fangless string escape sequences from the lexer."""
    result: list[str] = []
    index = 0
    while index < len(raw):
        if raw[index] == "\\" and index + 1 < len(raw):
            escape = raw[index + 1]
            if escape == "n":
                result.append("\n")
            elif escape == "t":
                result.append("\t")
            elif escape in {'"', "'", "\\"}:
                result.append(escape)
            else:
                result.append("\\")
                result.append(escape)
                index += 1
                continue
            index += 2
            continue
        result.append(raw[index])
        index += 1
    return "".join(result)


def escape_cpp_string(value: str) -> str:
    """Escape a Python string for use inside a C++ string literal."""
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


class CppEmitter:
    """Walks the AST and emits equivalent C++ source lines."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._indent = 0
        self.scope = ScopeManager()

    def emit_program(self, program: ASTNode) -> list[str]:
        """Emit function definitions and a main function for top-level statements."""
        if program.node_type != "program":
            raise TranspileError(f"Expected program node, got {program.node_type!r}")

        function_defs: list[ASTNode] = []
        main_statements: list[ASTNode] = []

        for statement in program.children:
            if statement.node_type == "function_def":
                function_defs.append(statement)
            else:
                main_statements.append(statement)

        for function_def in function_defs:
            self._emit_function_def(function_def)

        self._write("int main() {")
        self._indent += 1
        self.scope.push()
        for statement in main_statements:
            self._emit_statement(statement)
        self._write("return 0;")
        self._indent -= 1
        self.scope.pop()
        self._write("}")

        return self._lines

    def _write(self, line: str) -> None:
        self._lines.append("    " * self._indent + line)

    def _emit_block(self, statements: list[ASTNode]) -> None:
        self.scope.push()
        for statement in statements:
            self._emit_statement(statement)
        self.scope.pop()

    def _emit_statement(self, node: ASTNode) -> None:
        handlers = {
            "assignment": self._emit_assignment,
            "attribute_assignment": self._emit_attribute_assignment,
            "subscript_assignment": self._emit_subscript_assignment,
            "expression_statement": self._emit_expression_statement,
            "if_statement": self._emit_if_statement,
            "while_statement": self._emit_while_statement,
            "for_statement": self._emit_for_statement,
            "return_statement": self._emit_return_statement,
            "break_statement": self._emit_break_statement,
            "continue_statement": self._emit_continue_statement,
            "pass_statement": self._emit_pass_statement,
            "function_def": self._emit_nested_function_error,
        }
        handler = handlers.get(node.node_type)
        if handler is None:
            raise TranspileError(f"Unsupported statement: {node.node_type}")
        handler(node)

    def _emit_nested_function_error(self, _node: ASTNode) -> None:
        raise TranspileError("Nested function definitions are not supported")

    def _emit_assignment(self, node: ASTNode) -> None:
        target = node.children[0]
        if target.node_type != "identifier":
            raise TranspileError("Only simple identifier assignments are supported")

        name = target.value
        cpp_name = sanitize_identifier(name)
        rhs = self._emit_expression(node.children[1])
        operator = node.value

        if operator not in ASSIGNMENT_OPERATORS:
            raise TranspileError(f"Unsupported assignment operator: {operator}")

        if operator == "=":
            if self.scope.is_declared(name):
                self._write(f"{cpp_name} = {rhs};")
            else:
                self.scope.declare(name)
                self._write(f"PyValue {cpp_name} = {rhs};")
            return

        if not self.scope.is_declared(name):
            raise TranspileError(f"Variable '{name}' must be declared before {operator}")

        self._write(f"{ASSIGNMENT_OPERATORS[operator](cpp_name, rhs)};")

    def _emit_attribute_assignment(self, node: ASTNode) -> None:
        raise TranspileError("Attribute assignment is not supported yet")

    def _emit_subscript_assignment(self, node: ASTNode) -> None:
        collection = self._emit_expression(node.children[0])
        index = self._emit_expression(node.children[1])
        value = self._emit_expression(node.children[2])
        operator = node.value

        if operator == "=":
            self._write(f"py_set_item({collection}, {index}, {value});")
            return

        if operator not in ASSIGNMENT_OPERATORS:
            raise TranspileError(f"Unsupported subscript assignment operator: {operator}")

        temp_name = f"__subscript_tmp_{len(self._lines)}"
        self._write(
            f"{{ PyValue {temp_name} = py_get_item({collection}, {index}); "
            f"py_set_item({collection}, {index}, "
            f"{ASSIGNMENT_OPERATORS[operator](temp_name, value).split(' = ', 1)[1]}); }}"
        )

    def _emit_expression_statement(self, node: ASTNode) -> None:
        expression = self._emit_expression(node.children[0])
        if expression:
            self._write(f"{expression};")

    def _emit_if_statement(self, node: ASTNode) -> None:
        condition = self._emit_expression(node.children[0])
        self._write(f"if (py_truthy({condition})) {{")
        self._indent += 1
        self._emit_block(node.children[1].children)
        self._indent -= 1

        index = 2
        while index < len(node.children):
            branch = node.children[index]
            if branch.node_type == "elif_statement":
                elif_condition = self._emit_expression(branch.children[0])
                self._write(f"}} else if (py_truthy({elif_condition})) {{")
                self._indent += 1
                self._emit_block(branch.children[1].children)
                self._indent -= 1
            elif branch.node_type == "else_statement":
                self._write("} else {")
                self._indent += 1
                self._emit_block(branch.children[0].children)
                self._indent -= 1
            else:
                raise TranspileError(f"Unexpected if branch: {branch.node_type}")
            index += 1

        self._write("}")

    def _emit_while_statement(self, node: ASTNode) -> None:
        condition = self._emit_expression(node.children[0])
        self._write(f"while (py_truthy({condition})) {{")
        self._indent += 1
        self._emit_block(node.children[1].children)
        self._indent -= 1
        self._write("}")

    def _emit_for_statement(self, node: ASTNode) -> None:
        loop_var = node.children[0].value
        cpp_loop_var = sanitize_identifier(loop_var)
        iterable = self._emit_expression(node.children[1])
        iterator_name = f"__iter_{cpp_loop_var}"

        self._write(f"{{ PyValue::List {iterator_name} = py_iter({iterable});")
        self._indent += 1
        self._write(f"for (const PyValue& __item_{cpp_loop_var} : {iterator_name}) {{")
        self._indent += 1
        self.scope.push()

        if self.scope.is_declared(loop_var):
            self._write(f"{cpp_loop_var} = __item_{cpp_loop_var};")
        else:
            self.scope.declare(loop_var)
            self._write(f"PyValue {cpp_loop_var} = __item_{cpp_loop_var};")

        for statement in node.children[2].children:
            self._emit_statement(statement)

        self.scope.pop()
        self._indent -= 1
        self._write("}")
        self._indent -= 1
        self._write("}")

    def _emit_return_statement(self, node: ASTNode) -> None:
        if node.children:
            self._write(f"return {self._emit_expression(node.children[0])};")
        else:
            self._write("return PyValue();")

    def _emit_break_statement(self, _node: ASTNode) -> None:
        self._write("break;")

    def _emit_continue_statement(self, _node: ASTNode) -> None:
        self._write("continue;")

    def _emit_pass_statement(self, _node: ASTNode) -> None:
        pass

    def _emit_function_def(self, node: ASTNode) -> None:
        function_name = sanitize_identifier(node.value)
        parameters = node.children[0].children
        body = node.children[1].children

        parameter_names: list[str] = []
        for parameter in parameters:
            if parameter.node_type != "parameter" or parameter.children:
                raise TranspileError("Only simple parameters are supported")
            parameter_names.append(sanitize_identifier(parameter.value))

        signature = ", ".join(f"PyValue {name}" for name in parameter_names)
        self._write(f"PyValue {function_name}({signature}) {{")
        self._indent += 1
        self.scope.push()

        for parameter in parameters:
            self.scope.declare(parameter.value)

        for statement in body:
            self._emit_statement(statement)

        self.scope.pop()
        self._indent -= 1
        self._write("}")

    def _emit_expression(self, node: ASTNode) -> str:
        if node.node_type == "identifier":
            name = node.value
            if not self.scope.is_declared(name):
                raise TranspileError(f"Undeclared variable: {name}")
            return sanitize_identifier(name)

        if node.node_type == "integer_literal":
            return f"PyValue({node.value}LL)"

        if node.node_type == "float_literal":
            return f"PyValue({node.value})"

        if node.node_type == "string_literal":
            decoded = decode_python_string(node.value)
            return f"PyValue({escape_cpp_string(decoded)})"

        if node.node_type == "boolean_literal":
            return f"PyValue({'true' if node.value else 'false'})"

        if node.node_type == "list_literal":
            items = ", ".join(self._emit_expression(item) for item in node.children)
            if items:
                return f"py_list(PyValue::List{{{items}}})"
            return "py_list(PyValue::List{})"

        if node.node_type == "grouped_expression":
            return self._emit_expression(node.children[0])

        if node.node_type == "binary_operation":
            return self._emit_binary_operation(node)

        if node.node_type == "unary_operation":
            return self._emit_unary_operation(node)

        if node.node_type == "function_call":
            return self._emit_function_call(node)

        if node.node_type == "method_call":
            return self._emit_method_call(node)

        if node.node_type == "subscript":
            collection = self._emit_expression(node.children[0])
            index = self._emit_expression(node.children[1])
            return f"py_get_item({collection}, {index})"

        raise TranspileError(f"Unsupported expression: {node.node_type}")

    def _emit_binary_operation(self, node: ASTNode) -> str:
        operator = node.value
        left = self._emit_expression(node.children[0])
        right = self._emit_expression(node.children[1])

        if operator in BINARY_OPERATORS:
            function_name = BINARY_OPERATORS[operator]
            return f"{function_name}({left}, {right})"

        if operator == "//":
            return f"py_floor_div({left}, {right})"

        if operator == "**":
            return f"py_pow({left}, {right})"

        raise TranspileError(f"Unsupported binary operator: {operator}")

    def _emit_unary_operation(self, node: ASTNode) -> str:
        operator = node.value
        operand = self._emit_expression(node.children[0])

        if operator == "not":
            return f"py_not({operand})"

        if operator == "-":
            return f"py_sub(PyValue(0LL), {operand})"

        if operator == "+":
            return operand

        raise TranspileError(f"Unsupported unary operator: {operator}")

    def _emit_function_call(self, node: ASTNode) -> str:
        name = node.value
        args = [self._emit_expression(arg) for arg in node.children]

        if name in BUILTIN_FUNCTIONS:
            return self._emit_builtin_call(name, args)

        cpp_name = sanitize_identifier(name)
        joined_args = ", ".join(args)
        return f"{cpp_name}({joined_args})"

    def _emit_builtin_call(self, name: str, args: list[str]) -> str:
        if name == "print":
            if not args:
                return "py_print()"
            if len(args) == 1:
                return f"py_print({args[0]})"
            return f"py_print({', '.join(args)})"

        if name == "range":
            if len(args) == 1:
                return f"py_range({args[0]})"
            if len(args) == 2:
                return f"py_range({args[0]}, {args[1]})"
            if len(args) == 3:
                return f"py_range({args[0]}, {args[1]}, {args[2]})"
            raise TranspileError("range() accepts 1 to 3 arguments")

        if len(args) != 1:
            raise TranspileError(f"{name}() expects exactly one argument")

        mapping = {
            "len": "py_len",
            "int": "py_int",
            "float": "py_float",
            "str": "py_str",
            "bool": "py_bool",
            "input": "py_input",
        }
        return f"{mapping[name]}({args[0]})"

    def _emit_method_call(self, node: ASTNode) -> str:
        method_name = node.value
        object_expr = self._emit_expression(node.children[0])
        args = [self._emit_expression(arg) for arg in node.children[1:]]

        if method_name == "append" and len(args) == 1:
            return f"([&]() -> PyValue {{ py_append({object_expr}, {args[0]}); return PyValue(); }})()"

        raise TranspileError(f"Unsupported method call: .{method_name}()")
