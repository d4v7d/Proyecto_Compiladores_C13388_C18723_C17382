"""Initial grammar rules for the Fangless parser.

This module intentionally contains only the parser skeleton needed for the
next implementation stage: programs, statement lists, assignments, and basic
expressions.
"""

from .ast_nodes import ASTNode


def p_program(parser):
    "program : optional_newlines statement_list optional_newlines"
    parser[0] = ASTNode("program", children=parser[2])


def p_optional_newlines_empty(parser):
    "optional_newlines : empty"
    parser[0] = []


def p_optional_newlines_multiple(parser):
    "optional_newlines : optional_newlines NEWLINE"
    parser[0] = parser[1]


def p_statement_list_single(parser):
    "statement_list : statement"
    parser[0] = [parser[1]]


def p_statement_list_multiple(parser):
    "statement_list : statement_list statement_separator statement"
    parser[0] = parser[1] + [parser[3]]


def p_statement_separator(parser):
    "statement_separator : NEWLINE optional_newlines"
    parser[0] = None


def p_statement_assignment(parser):
    "statement : assignment"
    parser[0] = parser[1]


def p_statement_expression(parser):
    "statement : expression"
    parser[0] = ASTNode("expression_statement", children=[parser[1]])


def p_assignment(parser):
    """assignment : IDENTIFIER ASSIGN expression
                  | IDENTIFIER PLUS_ASSIGN expression
                  | IDENTIFIER MINUS_ASSIGN expression
                  | IDENTIFIER TIMES_ASSIGN expression
                  | IDENTIFIER DIVIDE_ASSIGN expression
                  | IDENTIFIER MOD_ASSIGN expression
                  | IDENTIFIER FLOOR_DIVIDE_ASSIGN expression
                  | IDENTIFIER POWER_ASSIGN expression"""
    parser[0] = ASTNode(
        "assignment",
        value=parser[2],
        children=[
            ASTNode("identifier", value=parser[1]),
            parser[3],
        ],
    )


def p_expression_identifier(parser):
    "expression : IDENTIFIER"
    parser[0] = ASTNode("identifier", value=parser[1])


def p_expression_integer(parser):
    "expression : INTEGER"
    parser[0] = ASTNode("integer_literal", value=parser[1])


def p_expression_float(parser):
    "expression : FLOAT"
    parser[0] = ASTNode("float_literal", value=parser[1])


def p_expression_string(parser):
    "expression : STRING"
    parser[0] = ASTNode("string_literal", value=parser[1])


def p_expression_boolean(parser):
    """expression : TRUE
                  | FALSE"""
    parser[0] = ASTNode("boolean_literal", value=(parser[1] == "True"))


def p_expression_grouped(parser):
    "expression : LPAREN expression RPAREN"
    parser[0] = ASTNode("grouped_expression", children=[parser[2]])


def p_expression_not(parser):
    "expression : NOT expression"
    parser[0] = ASTNode(
        "unary_operation",
        value=parser[1],
        children=[parser[2]],
    )


def p_expression_negative(parser):
    "expression : MINUS expression %prec UMINUS"
    parser[0] = ASTNode("unary_operation", value=parser[1], children=[parser[2]])


def p_expression_binary(parser):
    """expression : expression OR expression
                  | expression AND expression
                  | expression EQ expression
                  | expression NE expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression FLOOR_DIVIDE expression
                  | expression MODULO expression
                  | expression POWER expression"""
    parser[0] = ASTNode(
        "binary_operation",
        value=parser[2],
        children=[parser[1], parser[3]],
    )


def p_empty(parser):
    "empty :"
    parser[0] = None
