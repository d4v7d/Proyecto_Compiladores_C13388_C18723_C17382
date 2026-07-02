"""AST-to-C++ code emitter for the Fangless transpiler."""

from __future__ import annotations

from parser.ast_nodes import ASTNode

from .scope import ScopeManager, sanitize_identifier


class TranspileError(Exception):
    """Raised when the AST contains a construct that cannot be transpiled."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())

    def format_message(self) -> str:
        location = ""
        if self.line is not None:
            location = f" at line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
        return f"Transpile error{location}: {self.message}"

    def __str__(self) -> str:
        return self.format_message()


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

STRING_METHODS = {
    "lower": "py_str_lower",
    "upper": "py_str_upper",
    "strip": "py_str_strip",
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
        self._class_names: set[str] = set()
        self._function_name_stack: list[str] = []
        self._local_function_aliases: dict[str, str] = {}
        self._method_aliases: dict[str, str] = {}

    def _node_location(self, node: ASTNode | None) -> tuple[int | None, int | None]:
        if node is None:
            return None, None
        if node.lineno is not None:
            return node.lineno, node.column
        for child in node.children:
            if isinstance(child, ASTNode):
                line, column = self._node_location(child)
                if line is not None:
                    return line, column
        return None, None

    def _transpile_error(self, node: ASTNode | None, message: str) -> TranspileError:
        line, column = self._node_location(node)
        return TranspileError(message, line=line, column=column)

    def _qualified_function_name(self, name: str) -> str:
        if not self._function_name_stack:
            return sanitize_identifier(name)
        return sanitize_identifier(f"{self._function_name_stack[-1]}_{name}")

    def emit_program(self, program: ASTNode) -> list[str]:
        """Emit class definitions, functions, and a main function."""
        if program.node_type != "program":
            raise self._transpile_error(program, f"Expected program node, got {program.node_type!r}")

        class_defs: list[ASTNode] = []
        function_defs: list[ASTNode] = []
        main_statements: list[ASTNode] = []

        for statement in program.children:
            if statement.node_type == "class_def":
                class_defs.append(statement)
            elif statement.node_type == "function_def":
                function_defs.append(statement)
            else:
                main_statements.append(statement)

        for class_def in class_defs:
            self._emit_class_def(class_def)

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
            "function_def": self._emit_nested_function_def,
            "try_statement": self._emit_try_statement,
        }
        handler = handlers.get(node.node_type)
        if handler is None:
            raise self._transpile_error(node, f"Unsupported statement: {node.node_type}")
        handler(node)

    def _emit_nested_function_def(self, node: ASTNode) -> None:
        qualified_name = self._qualified_function_name(node.value)
        self._local_function_aliases[node.value] = qualified_name
        self._emit_function_def(node, qualified_name=qualified_name)

    def _emit_assignment(self, node: ASTNode) -> None:
        target = node.children[0]
        if target.node_type != "identifier":
            raise self._transpile_error(node, "Only simple identifier assignments are supported")

        name = target.value
        cpp_name = sanitize_identifier(name)
        rhs = self._emit_expression(node.children[1])
        operator = node.value

        if operator not in ASSIGNMENT_OPERATORS:
            raise self._transpile_error(node, f"Unsupported assignment operator: {operator}")

        if operator == "=":
            if self.scope.is_declared(name):
                self._write(f"{cpp_name} = {rhs};")
            else:
                self.scope.declare(name)
                self._write(f"PyValue {cpp_name} = {rhs};")
            return

        if not self.scope.is_declared(name):
            raise self._transpile_error(node, f"Variable '{name}' must be declared before {operator}")

        self._write(f"{ASSIGNMENT_OPERATORS[operator](cpp_name, rhs)};")

    def _emit_attribute_assignment(self, node: ASTNode) -> None:
        object_expr = self._emit_expression(node.children[0])
        attribute = node.children[1].value
        value = self._emit_expression(node.children[2])
        operator = node.value

        if operator != "=":
            raise self._transpile_error(node, "Only simple attribute assignment (=) is supported")

        self._write(
            f"py_set_attr({object_expr}, {escape_cpp_string(attribute)}, {value});"
        )

    def _emit_subscript_assignment(self, node: ASTNode) -> None:
        collection = self._emit_expression(node.children[0])
        index = self._emit_expression(node.children[1])
        value = self._emit_expression(node.children[2])
        operator = node.value

        if operator == "=":
            self._write(f"py_set_item({collection}, {index}, {value});")
            return

        if operator not in ASSIGNMENT_OPERATORS:
            raise self._transpile_error(node, f"Unsupported subscript assignment operator: {operator}")

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
                raise self._transpile_error(branch, f"Unexpected if branch: {branch.node_type}")
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

    def _emit_try_statement(self, node: ASTNode) -> None:
        self._write("try {")
        self._indent += 1
        self._emit_block(node.children[0].children)
        self._indent -= 1

        finally_block = None
        for index in range(1, len(node.children)):
            clause = node.children[index]
            if clause.node_type == "except_clause":
                self._emit_except_clause(clause)
            elif clause.node_type == "finally_clause":
                finally_block = clause.children[0]
            else:
                raise self._transpile_error(clause, f"Unexpected try clause: {clause.node_type}")

        if finally_block is None:
            self._write("}")
        else:
            self._write("} {")
            self._indent += 1
            self._emit_block(finally_block.children)
            self._indent -= 1
            self._write("}")

    def _emit_except_clause(self, node: ASTNode) -> None:
        self._write("} catch (const PyRuntimeError& __py_exc) {")
        self._indent += 1

        block = node.children[-1]
        for child in node.children:
            if child.node_type == "exception_var":
                var_name = sanitize_identifier(child.value)
                self.scope.declare(child.value)
                self._write(
                    f"PyValue {var_name} = PyValue(std::string(__py_exc.what()));"
                )

        self._emit_block(block.children)
        self._indent -= 1

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

    def _emit_class_def(self, node: ASTNode) -> None:
        class_name = node.value
        cpp_class = sanitize_identifier(class_name)
        self._class_names.add(class_name)

        block = node.children[1] if node.children[0].node_type == "base_class" else node.children[0]
        methods = [stmt for stmt in block.children if stmt.node_type == "function_def"]

        for method in methods:
            qualified = f"{cpp_class}_{sanitize_identifier(method.value)}"
            self._emit_function_def(method, qualified_name=qualified, implicit_self=True)
            self._method_aliases[f"{class_name}.{method.value}"] = qualified

        init_method = next((method for method in methods if method.value == "__init__"), None)
        init_params = init_method.children[0].children[1:] if init_method else []

        signature_parts: list[str] = []
        for parameter in init_params:
            if parameter.node_type != "parameter":
                raise self._transpile_error(parameter, "Only simple parameters are supported in __init__")
            param_name = sanitize_identifier(parameter.value)
            if parameter.children:
                default_value = self._emit_expression(parameter.children[0])
                signature_parts.append(f"PyValue {param_name} = {default_value}")
            else:
                signature_parts.append(f"PyValue {param_name}")

        self._write(f"PyValue {cpp_class}({', '.join(signature_parts)}) {{")
        self._indent += 1
        self._write(f"PyValue self = py_make_instance({escape_cpp_string(class_name)});")
        if init_method:
            call_args = ["self"] + [sanitize_identifier(param.value) for param in init_params]
            self._write(f"{cpp_class}___init__({', '.join(call_args)});")
        self._write("return self;")
        self._indent -= 1
        self._write("}")

    def _emit_function_def(
        self,
        node: ASTNode,
        qualified_name: str | None = None,
        implicit_self: bool = False,
    ) -> None:
        function_name = qualified_name or sanitize_identifier(node.value)
        parameters = node.children[0].children
        body = node.children[1].children

        saved_aliases = self._local_function_aliases.copy()
        self._local_function_aliases = {}
        self._function_name_stack.append(function_name)

        nested_functions = [stmt for stmt in body if stmt.node_type == "function_def"]
        regular_body = [stmt for stmt in body if stmt.node_type != "function_def"]

        for nested in nested_functions:
            self._emit_nested_function_def(nested)

        parameter_parts: list[str] = []
        for index, parameter in enumerate(parameters):
            if parameter.node_type == "var_args" or parameter.node_type == "var_kwargs":
                raise self._transpile_error(parameter, "Variadic parameters are not supported")
            if parameter.node_type != "parameter":
                raise self._transpile_error(parameter, "Only simple parameters are supported")

            param_name = sanitize_identifier(parameter.value)
            param_type = "PyValue&" if implicit_self and index == 0 else "PyValue"
            if parameter.children:
                if implicit_self and index == 0:
                    raise self._transpile_error(parameter, "self cannot have a default value")
                default_value = self._emit_expression(parameter.children[0])
                parameter_parts.append(f"{param_type} {param_name} = {default_value}")
            else:
                parameter_parts.append(f"{param_type} {param_name}")

        signature = ", ".join(parameter_parts)
        self._write(f"PyValue {function_name}({signature}) {{")
        self._indent += 1
        self.scope.push()

        if implicit_self and parameters:
            self.scope.declare(parameters[0].value)

        for parameter in parameters:
            if parameter.node_type == "parameter":
                self.scope.declare(parameter.value)

        for statement in regular_body:
            self._emit_statement(statement)

        self._write("return PyValue();")

        self.scope.pop()
        self._indent -= 1
        self._write("}")

        self._function_name_stack.pop()
        self._local_function_aliases = saved_aliases

    def _emit_expression(self, node: ASTNode) -> str:
        if node.node_type == "identifier":
            name = node.value
            if name in self._local_function_aliases:
                return self._local_function_aliases[name]
            if not self.scope.is_declared(name):
                if name in self._class_names:
                    return sanitize_identifier(name)
                raise self._transpile_error(node, f"Undeclared variable: {name}")
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

        if node.node_type == "tuple_literal":
            items = ", ".join(self._emit_expression(item) for item in node.children)
            if items:
                return f"py_tuple_from_list(PyValue::List{{{items}}})"
            return "py_tuple_from_list(PyValue::List{})"

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

        if node.node_type == "attribute_access":
            return self._emit_attribute_access(node)

        if node.node_type == "subscript":
            collection = self._emit_expression(node.children[0])
            index = self._emit_expression(node.children[1])
            return f"py_get_item({collection}, {index})"

        if node.node_type == "slice":
            return self._emit_slice(node)

        raise self._transpile_error(node, f"Unsupported expression: {node.node_type}")

    def _emit_slice(self, node: ASTNode) -> str:
        collection = self._emit_expression(node.children[0])
        slice_range = node.children[1]
        parts = slice_range.children

        def slice_part(index: int) -> str:
            if index >= len(parts) or parts[index] is None:
                return "PyValue()"
            return self._emit_expression(parts[index])

        start = slice_part(0)
        stop = slice_part(1)
        step = slice_part(2)
        return f"py_slice_sequence({collection}, {start}, {stop}, {step})"

    def _emit_attribute_access(self, node: ASTNode) -> str:
        object_expr = self._emit_expression(node.children[0])
        attribute = node.value
        return f"py_get_attr({object_expr}, {escape_cpp_string(attribute)})"

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

        raise self._transpile_error(node, f"Unsupported binary operator: {operator}")

    def _emit_unary_operation(self, node: ASTNode) -> str:
        operator = node.value
        operand = self._emit_expression(node.children[0])

        if operator == "not":
            return f"py_not({operand})"

        if operator == "-":
            return f"py_sub(PyValue(0LL), {operand})"

        if operator == "+":
            return operand

        raise self._transpile_error(node, f"Unsupported unary operator: {operator}")

    def _emit_function_call(self, node: ASTNode) -> str:
        name = node.value
        args = [self._emit_expression(arg) for arg in node.children]

        if name in BUILTIN_FUNCTIONS:
            return self._emit_builtin_call(name, args, node)

        if name in self._class_names:
            cpp_name = sanitize_identifier(name)
            joined_args = ", ".join(args)
            return f"{cpp_name}({joined_args})"

        cpp_name = sanitize_identifier(name)
        if name in self._local_function_aliases:
            cpp_name = self._local_function_aliases[name]

        joined_args = ", ".join(args)
        return f"{cpp_name}({joined_args})"

    def _emit_builtin_call(self, name: str, args: list[str], node: ASTNode) -> str:
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
            raise self._transpile_error(node, "range() accepts 1 to 3 arguments")

        if name == "input":
            if not args:
                return "py_input()"
            raise self._transpile_error(node, "input() with a prompt argument is not supported")

        if len(args) != 1:
            raise self._transpile_error(node, f"{name}() expects exactly one argument")

        mapping = {
            "len": "py_len",
            "int": "py_int",
            "float": "py_float",
            "str": "py_str",
            "bool": "py_bool",
        }
        return f"{mapping[name]}({args[0]})"

    def _emit_method_call(self, node: ASTNode) -> str:
        method_name = node.value
        object_expr = self._emit_expression(node.children[0])
        args = [self._emit_expression(arg) for arg in node.children[1:]]

        if method_name == "append" and len(args) == 1:
            return (
                f"([&]() -> PyValue {{ py_append({object_expr}, {args[0]}); "
                f"return PyValue(); }})()"
            )

        if method_name in STRING_METHODS and not args:
            return f"{STRING_METHODS[method_name]}({object_expr})"

        resolved = self._resolve_instance_method(object_expr, method_name, node)
        if resolved is not None:
            return resolved

        raise self._transpile_error(node, f"Unsupported method call: .{method_name}()")

    def _resolve_instance_method(self, object_expr: str, method_name: str, node: ASTNode) -> str | None:
        for alias_key, qualified in self._method_aliases.items():
            _, aliased_method = alias_key.split(".", 1)
            if aliased_method != method_name:
                continue
            args = [self._emit_expression(arg) for arg in node.children[1:]]
            joined = ", ".join([object_expr] + args)
            return f"{qualified}({joined})"
        return None
