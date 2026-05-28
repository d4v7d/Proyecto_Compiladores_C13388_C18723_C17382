"""Basic AST node structures for the Fangless parser."""


class ASTNode:
    """Simple tree node used by the initial parser grammar."""

    DISPLAY_NAMES = {
        "program": "Program",
        "assignment": "Assignment",
        "expression_statement": "ExpressionStatement",
        "identifier": "Identifier",
        "integer_literal": "IntegerLiteral",
        "float_literal": "FloatLiteral",
        "string_literal": "StringLiteral",
        "boolean_literal": "BooleanLiteral",
        "binary_operation": "BinaryOperation",
        "unary_operation": "UnaryOperation",
        "grouped_expression": "GroupedExpression",
    }

    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return (
            f"ASTNode(node_type={self.node_type!r}, "
            f"value={self.value!r}, children={self.children!r})"
        )

    def pretty_print(self):
        """Return a readable tree representation of this AST node."""
        lines = [self._display_label()]

        for index, child in enumerate(self.children):
            is_last = index == len(self.children) - 1
            lines.extend(self._format_child(child, "", is_last))

        return "\n".join(lines)

    def _format_child(self, child, prefix, is_last):
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        if isinstance(child, ASTNode):
            lines = [prefix + connector + child._display_label()]
            for index, grandchild in enumerate(child.children):
                grandchild_is_last = index == len(child.children) - 1
                lines.extend(
                    child._format_child(grandchild, child_prefix, grandchild_is_last)
                )
            return lines

        return [prefix + connector + repr(child)]

    def _display_label(self):
        label = self.DISPLAY_NAMES.get(self.node_type, self._to_pascal_case())
        if self.value is not None:
            return f"{label} ({self.value})"
        return label

    def _to_pascal_case(self):
        return "".join(part.capitalize() for part in self.node_type.split("_"))
