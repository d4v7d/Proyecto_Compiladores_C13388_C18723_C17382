"""Basic AST node structures for the Fangless parser."""

_parse_source = ""


def set_parse_source(source: str) -> None:
    """Store source text so token positions can be mapped to columns."""
    global _parse_source
    _parse_source = source


def token_location(parser, index: int) -> tuple[int | None, int | None]:
    """Return (line, column) for a PLY production slice index."""
    try:
        token = parser.slice[index]
    except (IndexError, AttributeError, TypeError):
        return None, None

    if token is None:
        return None, None

    lineno = getattr(token, "lineno", None)
    column = None
    lexpos = getattr(token, "lexpos", None)
    if _parse_source and lexpos is not None:
        line_start = _parse_source.rfind("\n", 0, lexpos) + 1
        column = (lexpos - line_start) + 1

    return lineno, column


def make_node(parser, slice_index, node_type, value=None, children=None):
    """Create an AST node with source location from a grammar production token."""
    lineno, column = token_location(parser, slice_index)
    return ASTNode(
        node_type,
        value=value,
        children=children,
        lineno=lineno,
        column=column,
    )


def propagate_locations(node: "ASTNode") -> None:
    """Fill missing parent locations from the first located child."""
    for child in node.children:
        if isinstance(child, ASTNode):
            propagate_locations(child)

    if node.lineno is not None:
        return

    for child in node.children:
        if isinstance(child, ASTNode) and child.lineno is not None:
            node.lineno = child.lineno
            node.column = child.column
            return


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

    def __init__(self, node_type, value=None, children=None, lineno=None, column=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []
        self.lineno = lineno
        self.column = column

    def __repr__(self):
        return (
            f"ASTNode(node_type={self.node_type!r}, "
            f"value={self.value!r}, children={self.children!r}, "
            f"lineno={self.lineno!r}, column={self.column!r})"
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
