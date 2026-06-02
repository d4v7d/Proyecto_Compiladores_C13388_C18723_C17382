"""
Grammar extensions: classes, OOP, data structures, and general subscript/attribute.

These rules are loaded AFTER grammar_rules.py by parser_builder.py.
Functions with the same name as grammar_rules.py override the old limited versions:

  - p_expression_attribute  : was IDENTIFIER.IDENTIFIER only
                               now   expression.IDENTIFIER  (supports chaining)
  - p_expression_subscript  : was IDENTIFIER[expr] only
                               now   expression[expr]       (any subscriptable expr)
"""

from .ast_nodes import ASTNode

# ============================================================================
# CLASS DEFINITION
# ============================================================================

def p_statement_class_def(parser):
    "statement : class_def"
    parser[0] = parser[1]


def p_class_def_simple(parser):
    "class_def : CLASS IDENTIFIER COLON NEWLINE indented_block"
    # class Foo:\n    ...
    parser[0] = ASTNode(
        "class_def",
        value=parser[2],
        children=[ASTNode("block", children=parser[5])],
    )


def p_class_def_empty_parens(parser):
    "class_def : CLASS IDENTIFIER LPAREN RPAREN COLON NEWLINE indented_block"
    # class Foo():\n    ...  (explicit empty base list)
    parser[0] = ASTNode(
        "class_def",
        value=parser[2],
        children=[ASTNode("block", children=parser[7])],
    )


def p_class_def_with_base(parser):
    "class_def : CLASS IDENTIFIER LPAREN IDENTIFIER RPAREN COLON NEWLINE indented_block"
    # class Child(Parent):\n    ...  (single inheritance)
    parser[0] = ASTNode(
        "class_def",
        value=parser[2],
        children=[
            ASTNode("base_class", value=parser[4]),
            ASTNode("block", children=parser[8]),
        ],
    )


# ============================================================================
# ATTRIBUTE ACCESS  (overrides the IDENTIFIER.IDENTIFIER-only rule)
# ============================================================================

def p_expression_attribute(parser):
    "expression : expression DOT IDENTIFIER"
    # Handles: obj.attr, self.x, obj.a.b (chained via left recursion)
    parser[0] = ASTNode(
        "attribute_access",
        value=parser[3],          # attribute name
        children=[parser[1]],     # object expression
    )


# ============================================================================
# METHOD CALLS
# ============================================================================

def p_expression_method_call(parser):
    """expression : expression DOT IDENTIFIER LPAREN RPAREN
                  | expression DOT IDENTIFIER LPAREN argument_list RPAREN"""
    # obj.method()  or  obj.method(a, b, ...)
    if len(parser) == 6:
        args = []
    else:
        # argument_list is already a list (from grammar_rules.py p_argument_list_*)
        args = parser[5] if isinstance(parser[5], list) else [parser[5]]

    parser[0] = ASTNode(
        "method_call",
        value=parser[3],          # method name
        children=[parser[1]] + args,  # object + arguments
    )


# ============================================================================
# SUBSCRIPT  (overrides the IDENTIFIER[expr]-only rule)
# ============================================================================

def p_expression_subscript(parser):
    "expression : expression LBRACKET expression RBRACKET"
    # lista[0], dict["key"], s[i], obj.items[j], etc.
    parser[0] = ASTNode(
        "subscript",
        children=[parser[1], parser[3]],  # object, index
    )


# ============================================================================
# SLICING
# ============================================================================

def p_expression_slice_full(parser):
    "expression : expression LBRACKET expression COLON expression RBRACKET"
    # expr[start:stop]
    parser[0] = ASTNode(
        "slice",
        children=[
            parser[1],
            ASTNode("slice_range", children=[parser[3], parser[5], None]),
        ],
    )


def p_expression_slice_start_only(parser):
    "expression : expression LBRACKET expression COLON RBRACKET"
    # expr[start:]
    parser[0] = ASTNode(
        "slice",
        children=[
            parser[1],
            ASTNode("slice_range", children=[parser[3], None, None]),
        ],
    )


def p_expression_slice_stop_only(parser):
    "expression : expression LBRACKET COLON expression RBRACKET"
    # expr[:stop]
    parser[0] = ASTNode(
        "slice",
        children=[
            parser[1],
            ASTNode("slice_range", children=[None, parser[4], None]),
        ],
    )


def p_expression_slice_all(parser):
    "expression : expression LBRACKET COLON RBRACKET"
    # expr[:]  — full copy
    parser[0] = ASTNode(
        "slice",
        children=[
            parser[1],
            ASTNode("slice_range", children=[None, None, None]),
        ],
    )


# ============================================================================
# ATTRIBUTE ASSIGNMENT
# ============================================================================

def p_assignment_attribute(parser):
    """assignment : expression DOT IDENTIFIER ASSIGN expression
                  | expression DOT IDENTIFIER PLUS_ASSIGN expression
                  | expression DOT IDENTIFIER MINUS_ASSIGN expression
                  | expression DOT IDENTIFIER TIMES_ASSIGN expression
                  | expression DOT IDENTIFIER DIVIDE_ASSIGN expression
                  | expression DOT IDENTIFIER MOD_ASSIGN expression
                  | expression DOT IDENTIFIER FLOOR_DIVIDE_ASSIGN expression
                  | expression DOT IDENTIFIER POWER_ASSIGN expression"""
    # self.x = value  /  obj.counter += 1  /  etc.
    parser[0] = ASTNode(
        "attribute_assignment",
        value=parser[4],                        # operator (=, +=, …)
        children=[
            parser[1],                          # object expression
            ASTNode("identifier", value=parser[3]),  # attribute name
            parser[5],                          # right-hand side value
        ],
    )


# ============================================================================
# SUBSCRIPT ASSIGNMENT
# ============================================================================

def p_assignment_subscript(parser):
    """assignment : expression LBRACKET expression RBRACKET ASSIGN expression
                  | expression LBRACKET expression RBRACKET PLUS_ASSIGN expression
                  | expression LBRACKET expression RBRACKET MINUS_ASSIGN expression
                  | expression LBRACKET expression RBRACKET TIMES_ASSIGN expression
                  | expression LBRACKET expression RBRACKET DIVIDE_ASSIGN expression"""
    # lista[0] = val  /  d["key"] += 1  /  etc.
    parser[0] = ASTNode(
        "subscript_assignment",
        value=parser[5],   # operator
        children=[
            parser[1],     # object
            parser[3],     # index/key
            parser[6],     # value
        ],
    )


# ============================================================================
# TUPLE LITERAL
# ============================================================================

def p_expression_tuple_multi(parser):
    "expression : LPAREN tuple_items RPAREN"
    # (a, b)  /  (a, b, c)  /  (1 + 2, x * y)
    parser[0] = ASTNode("tuple_literal", children=parser[2])


def p_expression_tuple_single(parser):
    "expression : LPAREN expression COMMA RPAREN"
    # (a,)  — single-element tuple (the trailing comma distinguishes it from grouping)
    parser[0] = ASTNode("tuple_literal", children=[parser[2]])


def p_tuple_items_base(parser):
    "tuple_items : expression COMMA expression"
    # First two elements: a, b
    parser[0] = [parser[1], parser[3]]


def p_tuple_items_extend(parser):
    "tuple_items : tuple_items COMMA expression"
    # Additional elements: a, b, c, ...
    parser[0] = parser[1] + [parser[3]]


# ============================================================================
# DICTIONARY LITERAL
# ============================================================================

def p_expression_dict_empty(parser):
    "expression : LBRACE RBRACE"
    # {}  — empty dict (empty set uses set())
    parser[0] = ASTNode("dict_literal", children=[])


def p_expression_dict(parser):
    "expression : LBRACE dict_items RBRACE"
    # {"key": value, ...}
    parser[0] = ASTNode("dict_literal", children=parser[2])


def p_dict_items_single(parser):
    "dict_items : dict_pair"
    parser[0] = [parser[1]]


def p_dict_items_extend(parser):
    "dict_items : dict_items COMMA dict_pair"
    parser[0] = parser[1] + [parser[3]]


def p_dict_pair(parser):
    "dict_pair : expression COLON expression"
    # key: value  — note: COLON lookahead prevents conflict with set_items
    parser[0] = ASTNode("dict_pair", children=[parser[1], parser[3]])


# ============================================================================
# SET LITERAL
# ============================================================================

def p_expression_set(parser):
    "expression : LBRACE set_items RBRACE"
    # {1, 2, 3}  — non-empty only; empty set = set()
    parser[0] = ASTNode("set_literal", children=parser[2])


def p_set_items_single(parser):
    "set_items : expression"
    # After {expression, lookahead `,` or `}` → set (not `:` → dict)
    parser[0] = [parser[1]]


def p_set_items_extend(parser):
    "set_items : set_items COMMA expression"
    parser[0] = parser[1] + [parser[3]]
