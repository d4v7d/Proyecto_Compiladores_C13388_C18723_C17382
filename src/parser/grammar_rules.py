"""Grammar rules for the Fangless parser with control flow, functions, and exceptions.

This module contains rules for:
- Basic statements and expressions
- Control flow (if/elif/else, while, for)
- Function definitions and calls
- Exception handling (try/except/finally)
"""

from .ast_nodes import ASTNode


def p_program(parser):
    "program : optional_newlines statement_list optional_newlines"
    parser[0] = ASTNode("program", children=parser[2])


def p_program_with_trailing_dent(parser):
    "program : optional_newlines statement_list optional_newlines DENT"
    # Program with trailing DENT from dedentation
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
    "statement_list : statement_list NEWLINE statement"
    # Multiple statements separated by newlines
    parser[0] = parser[1] + [parser[3]]


def p_statement_list_adjacent(parser):
    "statement_list : statement_list statement"
    # Adjacent statements without separator (block statements inside a class/block)
    parser[0] = parser[1] + [parser[2]]




def p_indented_block(parser):
    "indented_block : INDENT statement_list DENT"
    # Block terminated by DENT (class body, top-level blocks)
    parser[0] = parser[2]


def p_indented_block_newline_dent(parser):
    "indented_block : INDENT statement_list NEWLINE DENT"
    # Block terminated by trailing NEWLINE then DENT (method bodies inside classes)
    parser[0] = parser[2]


def p_indented_block_newline(parser):
    "indented_block : INDENT statement_list NEWLINE"
    # Block terminated by NEWLINE only (for try/except structures)
    parser[0] = parser[2]


# ============================================================================
# STATEMENT RULES
# ============================================================================

def p_statement_assignment(parser):
    "statement : assignment"
    parser[0] = parser[1]


def p_statement_expression(parser):
    "statement : expression"
    parser[0] = ASTNode("expression_statement", children=[parser[1]])


# Control flow statements
def p_statement_if(parser):
    "statement : if_statement"
    parser[0] = parser[1]


def p_statement_while(parser):
    "statement : while_statement"
    parser[0] = parser[1]


def p_statement_for(parser):
    "statement : for_statement"
    parser[0] = parser[1]


def p_statement_function_def(parser):
    "statement : function_def"
    parser[0] = parser[1]


def p_statement_try(parser):
    "statement : try_statement"
    parser[0] = parser[1]


def p_statement_return(parser):
    "statement : return_statement"
    parser[0] = parser[1]


def p_statement_break(parser):
    "statement : break_statement"
    parser[0] = parser[1]


def p_statement_continue(parser):
    "statement : continue_statement"
    parser[0] = parser[1]


def p_statement_pass(parser):
    "statement : pass_statement"
    parser[0] = parser[1]


def p_statement_raise(parser):
    "statement : raise_statement"
    parser[0] = parser[1]


# ============================================================================
# IF/ELIF/ELSE STATEMENTS
# ============================================================================

def p_if_statement(parser):
    "if_statement : IF expression COLON NEWLINE indented_block"
    # Simple if without elif or else
    parser[0] = ASTNode("if_statement", children=[parser[2], ASTNode("block", children=parser[5])])


def p_if_statement_with_tail(parser):
    """if_statement : IF expression COLON NEWLINE indented_block elif_clause_chain
                    | IF expression COLON NEWLINE indented_block else_clause"""
    # If statement with elif/else tail
    children = [parser[2], ASTNode("block", children=parser[5])]
    if isinstance(parser[6], list):
        children.extend(parser[6])
    else:
        children.append(parser[6])
    parser[0] = ASTNode("if_statement", children=children)


def p_elif_clause_chain_single(parser):
    "elif_clause_chain : elif_clause"
    parser[0] = [parser[1]]


def p_elif_clause_chain_multiple(parser):
    "elif_clause_chain : elif_clause_chain elif_clause"
    parser[1].append(parser[2])
    parser[0] = parser[1]


def p_elif_clause_chain_with_else(parser):
    "elif_clause_chain : elif_clause_chain else_clause"
    parser[1].append(parser[2])
    parser[0] = parser[1]


def p_elif_clause(parser):
    "elif_clause : ELIF expression COLON NEWLINE indented_block"
    parser[0] = ASTNode("elif_statement", children=[parser[2], ASTNode("block", children=parser[5])])


def p_else_clause(parser):
    "else_clause : ELSE COLON NEWLINE indented_block"
    parser[0] = ASTNode("else_statement", children=[ASTNode("block", children=parser[4])])


# ============================================================================
# WHILE LOOP STATEMENT
# ============================================================================

def p_while_statement(parser):
    "while_statement : WHILE expression COLON NEWLINE indented_block"
    parser[0] = ASTNode("while_statement", children=[parser[2], ASTNode("block", children=parser[5])])


# ============================================================================
# FOR LOOP STATEMENT
# ============================================================================

def p_for_statement(parser):
    "for_statement : FOR IDENTIFIER IN expression COLON NEWLINE indented_block"
    parser[0] = ASTNode(
        "for_statement",
        children=[
            ASTNode("identifier", value=parser[2]),
            parser[4],
            ASTNode("block", children=parser[7]),
        ]
    )


# ============================================================================
# BREAK, CONTINUE, PASS STATEMENTS
# ============================================================================

def p_break_statement(parser):
    "break_statement : BREAK"
    parser[0] = ASTNode("break_statement")


def p_continue_statement(parser):
    "continue_statement : CONTINUE"
    parser[0] = ASTNode("continue_statement")


def p_pass_statement(parser):
    "pass_statement : PASS"
    parser[0] = ASTNode("pass_statement")


# ============================================================================
# RETURN STATEMENT
# ============================================================================

def p_return_statement_value(parser):
    "return_statement : RETURN expression"
    parser[0] = ASTNode("return_statement", children=[parser[2]])


def p_return_statement_empty(parser):
    "return_statement : RETURN"
    parser[0] = ASTNode("return_statement")


# ============================================================================
# FUNCTION DEFINITION
# ============================================================================

def p_function_def_no_params(parser):
    "function_def : DEF IDENTIFIER LPAREN RPAREN COLON NEWLINE indented_block"
    parser[0] = ASTNode(
        "function_def",
        value=parser[2],
        children=[
            ASTNode("parameters", children=[]),
            ASTNode("block", children=parser[7]),
        ]
    )


def p_function_def_with_params(parser):
    "function_def : DEF IDENTIFIER LPAREN parameter_list RPAREN COLON NEWLINE indented_block"
    parser[0] = ASTNode(
        "function_def",
        value=parser[2],
        children=[
            ASTNode("parameters", children=parser[4]),
            ASTNode("block", children=parser[8]),
        ]
    )


def p_parameter_list_single(parser):
    "parameter_list : parameter"
    parser[0] = [parser[1]]


def p_parameter_list_multiple(parser):
    "parameter_list : parameter_list COMMA parameter"
    parser[0] = parser[1] + [parser[3]]


def p_parameter_simple(parser):
    "parameter : IDENTIFIER"
    parser[0] = ASTNode("parameter", value=parser[1])


def p_parameter_with_default(parser):
    "parameter : IDENTIFIER ASSIGN expression"
    parser[0] = ASTNode(
        "parameter",
        value=parser[1],
        children=[parser[3]]
    )


def p_parameter_var_args(parser):
    "parameter : TIMES IDENTIFIER"
    parser[0] = ASTNode("var_args", value=parser[2])


def p_parameter_var_kwargs(parser):
    "parameter : TIMES TIMES IDENTIFIER"
    parser[0] = ASTNode("var_kwargs", value=parser[3])


# ============================================================================
# TRY/EXCEPT/FINALLY STATEMENT
# ============================================================================

def p_try_statement_except(parser):
    "try_statement : TRY COLON NEWLINE indented_block except_clause_list"
    parser[0] = ASTNode(
        "try_statement",
        children=[ASTNode("block", children=parser[4])] + parser[5]
    )


def p_try_statement_finally(parser):
    "try_statement : TRY COLON NEWLINE indented_block finally_clause"
    parser[0] = ASTNode(
        "try_statement",
        children=[ASTNode("block", children=parser[4]), parser[5]]
    )


def p_except_clause_list_single(parser):
    "except_clause_list : except_clause"
    parser[0] = [parser[1]]


def p_except_clause_list_multiple(parser):
    "except_clause_list : except_clause_list except_clause"
    parser[0] = parser[1] + [parser[2]]


def p_except_clause_generic(parser):
    "except_clause : DENT EXCEPT COLON NEWLINE indented_block"
    parser[0] = ASTNode("except_clause", children=[ASTNode("block", children=parser[5])])


def p_except_clause_typed(parser):
    "except_clause : DENT EXCEPT IDENTIFIER COLON NEWLINE indented_block"
    parser[0] = ASTNode(
        "except_clause",
        children=[
            ASTNode("exception_type", value=parser[3]),
            ASTNode("block", children=parser[6]),
        ]
    )


def p_except_clause_typed_as(parser):
    "except_clause : DENT EXCEPT IDENTIFIER AS IDENTIFIER COLON NEWLINE indented_block"
    parser[0] = ASTNode(
        "except_clause",
        children=[
            ASTNode("exception_type", value=parser[3]),
            ASTNode("exception_var", value=parser[5]),
            ASTNode("block", children=parser[8]),
        ]
    )


def p_finally_clause(parser):
    "finally_clause : DENT FINALLY COLON NEWLINE indented_block"
    parser[0] = ASTNode("finally_clause", children=[ASTNode("block", children=parser[5])])


# ============================================================================
# RAISE STATEMENT
# ============================================================================

def p_raise_statement(parser):
    "raise_statement : RAISE"
    parser[0] = ASTNode("raise_statement")


def p_raise_statement_type(parser):
    "raise_statement : RAISE expression"
    parser[0] = ASTNode("raise_statement", children=[parser[2]])


# ============================================================================
# ASSIGNMENT
# ============================================================================

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


# ============================================================================
# EXPRESSIONS
# ============================================================================

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


def p_expression_list(parser):
    "expression : LBRACKET expression_list_content RBRACKET"
    parser[0] = ASTNode("list_literal", children=parser[2])


def p_expression_list_empty(parser):
    "expression : LBRACKET RBRACKET"
    parser[0] = ASTNode("list_literal", children=[])


def p_expression_list_content_single(parser):
    "expression_list_content : expression"
    parser[0] = [parser[1]]


def p_expression_list_content_multiple(parser):
    "expression_list_content : expression_list_content COMMA expression"
    parser[0] = parser[1] + [parser[3]]


def p_expression_binary_addition(parser):
    "expression : expression PLUS expression"
    parser[0] = ASTNode("binary_operation", value="+", children=[parser[1], parser[3]])


def p_expression_binary_subtraction(parser):
    "expression : expression MINUS expression"
    parser[0] = ASTNode("binary_operation", value="-", children=[parser[1], parser[3]])


def p_expression_binary_multiplication(parser):
    "expression : expression TIMES expression"
    parser[0] = ASTNode("binary_operation", value="*", children=[parser[1], parser[3]])


def p_expression_binary_division(parser):
    "expression : expression DIVIDE expression"
    parser[0] = ASTNode("binary_operation", value="/", children=[parser[1], parser[3]])


def p_expression_binary_floor_division(parser):
    "expression : expression FLOOR_DIVIDE expression"
    parser[0] = ASTNode("binary_operation", value="//", children=[parser[1], parser[3]])


def p_expression_binary_modulo(parser):
    "expression : expression MODULO expression"
    parser[0] = ASTNode("binary_operation", value="%", children=[parser[1], parser[3]])


def p_expression_binary_power(parser):
    "expression : expression POWER expression"
    parser[0] = ASTNode("binary_operation", value="**", children=[parser[1], parser[3]])


def p_expression_comparison_eq(parser):
    "expression : expression EQ expression"
    parser[0] = ASTNode("binary_operation", value="==", children=[parser[1], parser[3]])


def p_expression_comparison_ne(parser):
    "expression : expression NE expression"
    parser[0] = ASTNode("binary_operation", value="!=", children=[parser[1], parser[3]])


def p_expression_comparison_lt(parser):
    "expression : expression LT expression"
    parser[0] = ASTNode("binary_operation", value="<", children=[parser[1], parser[3]])


def p_expression_comparison_le(parser):
    "expression : expression LE expression"
    parser[0] = ASTNode("binary_operation", value="<=", children=[parser[1], parser[3]])


def p_expression_comparison_gt(parser):
    "expression : expression GT expression"
    parser[0] = ASTNode("binary_operation", value=">", children=[parser[1], parser[3]])


def p_expression_comparison_ge(parser):
    "expression : expression GE expression"
    parser[0] = ASTNode("binary_operation", value=">=", children=[parser[1], parser[3]])


def p_expression_logical_and(parser):
    "expression : expression AND expression"
    parser[0] = ASTNode("binary_operation", value="and", children=[parser[1], parser[3]])


def p_expression_logical_or(parser):
    "expression : expression OR expression"
    parser[0] = ASTNode("binary_operation", value="or", children=[parser[1], parser[3]])


def p_expression_logical_not(parser):
    "expression : NOT expression"
    parser[0] = ASTNode("unary_operation", value="not", children=[parser[2]])


def p_expression_unary_minus(parser):
    "expression : MINUS expression %prec UMINUS"
    parser[0] = ASTNode("unary_operation", value="-", children=[parser[2]])


def p_expression_unary_plus(parser):
    "expression : PLUS expression %prec UPLUS"
    parser[0] = ASTNode("unary_operation", value="+", children=[parser[2]])


def p_expression_function_call(parser):
    "expression : IDENTIFIER LPAREN RPAREN"
    parser[0] = ASTNode("function_call", value=parser[1], children=[])


def p_expression_function_call_with_args(parser):
    "expression : IDENTIFIER LPAREN argument_list RPAREN"
    parser[0] = ASTNode("function_call", value=parser[1], children=parser[3])


def p_argument_list_single(parser):
    "argument_list : expression"
    parser[0] = [parser[1]]


def p_argument_list_multiple(parser):
    "argument_list : argument_list COMMA expression"
    parser[0] = parser[1] + [parser[3]]


def p_expression_subscript(parser):
    "expression : IDENTIFIER LBRACKET expression RBRACKET"
    parser[0] = ASTNode(
        "subscript",
        children=[
            ASTNode("identifier", value=parser[1]),
            parser[3],
        ]
    )


def p_expression_attribute(parser):
    "expression : IDENTIFIER DOT IDENTIFIER"
    parser[0] = ASTNode(
        "attribute_access",
        children=[
            ASTNode("identifier", value=parser[1]),
            ASTNode("identifier", value=parser[3]),
        ]
    )


# ============================================================================
# ERROR HANDLING AND EMPTY RULE
# ============================================================================

def p_empty(parser):
    "empty :"
    parser[0] = None
