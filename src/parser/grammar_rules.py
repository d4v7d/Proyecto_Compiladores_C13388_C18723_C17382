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


def p_statement_list_with_dent(parser):
    "statement_list : statement_list NEWLINE DENT statement"
    # Statements with DENT appearing between (lexer timing issue workaround)
    parser[0] = parser[1] + [parser[4]]


def p_indented_block(parser):
    "indented_block : INDENT statement_list DENT"
    # Statements in block terminated by DENT (standard case)
    parser[0] = parser[2]


def p_indented_block_newline(parser):
    "indented_block : INDENT statement_list NEWLINE"
    # Statements in block terminated by NEWLINE (for try/except structures)
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
# IF/ELIF/ELSE STATEMENTS - SIMPLE FORM ONLY (no elif/else for now)
# ============================================================================

def p_if_statement(parser):
    "if_statement : IF expression COLON NEWLINE indented_block"
    # Simple if without elif or else
    parser[0] = ASTNode("if_statement", children=[parser[2], ASTNode("block", children=parser[5])])


# ============================================================================
# WHILE LOOP STATEMENT
# ============================================================================

def p_while_statement(parser):
    "while_statement : WHILE expression COLON NEWLINE indented_block"
    # While loop with condition and block
    parser[0] = ASTNode("while_statement", children=[parser[2], ASTNode("block", children=parser[5])])


# ============================================================================
# FOR LOOP STATEMENT
# ============================================================================

def p_for_statement(parser):
    "for_statement : FOR IDENTIFIER IN expression COLON NEWLINE indented_block"
    # For loop: iterate over expression binding values to identifier
    parser[0] = ASTNode(
        "for_statement",
        children=[
            ASTNode("identifier", value=parser[2]),
            parser[4],  # iterable expression
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
    # Function with no parameters
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
    # Function with parameters
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
    # Simple parameter
    parser[0] = ASTNode("parameter", value=parser[1])


def p_parameter_with_default(parser):
    "parameter : IDENTIFIER ASSIGN expression"
    # Parameter with default value
    parser[0] = ASTNode(
        "parameter",
        value=parser[1],
        children=[parser[3]]  # default value
    )


# ============================================================================
# TRY/EXCEPT/FINALLY STATEMENT
# ============================================================================

def p_try_statement_except(parser):
    "try_statement : TRY COLON NEWLINE indented_block except_clause_list"
    # Try with except(s)
    parser[0] = ASTNode(
        "try_statement",
        children=[ASTNode("block", children=parser[4])] + parser[5]
    )


def p_try_statement_except_finally(parser):
    "try_statement : TRY COLON NEWLINE indented_block except_clause_list finally_clause"
    # Try with except(s) and finally
    parser[0] = ASTNode(
        "try_statement",
        children=[ASTNode("block", children=parser[4])] + parser[5] + [parser[6]]
    )


def p_try_statement_finally(parser):
    "try_statement : TRY COLON NEWLINE indented_block finally_clause"
    # Try with finally only
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
    # Generic except (catches all exceptions)
    parser[0] = ASTNode("except_clause", children=[ASTNode("block", children=parser[5])])


def p_except_clause_typed(parser):
    "except_clause : DENT EXCEPT IDENTIFIER COLON NEWLINE indented_block"
    # Except with exception type
    parser[0] = ASTNode(
        "except_clause",
        children=[
            ASTNode("exception_type", value=parser[3]),
            ASTNode("block", children=parser[6]),
        ]
    )


def p_except_clause_typed_as(parser):
    "except_clause : DENT EXCEPT IDENTIFIER AS IDENTIFIER COLON NEWLINE indented_block"
    # Except with exception type and variable
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
    # Finally clause
    parser[0] = ASTNode("finally_clause", children=[ASTNode("block", children=parser[5])])


# ============================================================================
# RAISE STATEMENT
# ============================================================================

def p_raise_statement(parser):
    "raise_statement : RAISE"
    parser[0] = ASTNode("raise_statement")


def p_raise_statement_type(parser):
    "raise_statement : RAISE IDENTIFIER"
    parser[0] = ASTNode("raise_statement", children=[ASTNode("identifier", value=parser[2])])


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
    # Function call with no arguments
    parser[0] = ASTNode(
        "function_call",
        value=parser[1],
        children=[]
    )


def p_expression_function_call_with_args(parser):
    "expression : IDENTIFIER LPAREN argument_list RPAREN"
    # Function call with arguments
    parser[0] = ASTNode(
        "function_call",
        value=parser[1],
        children=parser[3]
    )


def p_argument_list_single(parser):
    "argument_list : expression"
    parser[0] = [parser[1]]


def p_argument_list_multiple(parser):
    "argument_list : argument_list COMMA expression"
    parser[0] = parser[1] + [parser[3]]


def p_expression_subscript(parser):
    "expression : IDENTIFIER LBRACKET expression RBRACKET"
    # Array/list subscript
    parser[0] = ASTNode(
        "subscript",
        children=[
            ASTNode("identifier", value=parser[1]),
            parser[3],
        ]
    )


def p_expression_attribute(parser):
    "expression : IDENTIFIER DOT IDENTIFIER"
    # Attribute access
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
    pass


def p_error(parser):
    if parser:
        print(f"Syntax error: unexpected token at line {parser.lineno}, column {parser.lexpos} near token \"{parser.type}('{parser.value}')\"")
    else:
        print("Syntax error: unexpected end of input")
WLINE indented_block"
    # If statement without elif/else
    parser[0] = ASTNode("if_statement", children=[parser[2], ASTNode("block", children=parser[5])])


def p_if_statement_with_tail(parser):
    """if_statement : IF expression COLON NEWLINE indented_block elif_clause_chain
                    | IF expression COLON NEWLINE indented_block else_clause"""
    # If statement with elif/else tail
    children = [parser[2], ASTNode("block", children=parser[5])]
    if len(parser) == 7:
        # elif chain
        if isinstance(parser[6], list):
            children.extend(parser[6])
        else:
            children.append(parser[6])
    else:
        # else clause
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
    # Elif clause
    parser[0] = ASTNode("elif_statement", children=[parser[2], ASTNode("block", children=parser[5])])


def p_else_clause(parser):
    "else_clause : ELSE COLON NEWLINE indented_block"
    # Else clause
    parser[0] = ASTNode("else_statement", children=[ASTNode("block", children=parser[4])])


# ============================================================================
# WHILE LOOP STATEMENT
# ============================================================================

def p_while_statement(parser):
    "while_statement : WHILE expression COLON NEWLINE indented_block"
    # While loop with condition and block
    parser[0] = ASTNode("while_statement", children=[parser[2], ASTNode("block", children=parser[5])])


# ============================================================================
# FOR LOOP STATEMENT
# ============================================================================

def p_for_statement(parser):
    "for_statement : FOR IDENTIFIER IN expression COLON NEWLINE indented_block"
    # For loop: iterate over expression binding values to identifier
    parser[0] = ASTNode(
        "for_statement",
        children=[
            ASTNode("identifier", value=parser[2]),
            parser[4],  # iterable expression
            ASTNode("block", children=parser[7]),
        ]
    )


# ============================================================================
# BREAK, CONTINUE, PASS STATEMENTS
# ============================================================================

def p_break_statement(parser):
    "break_statement : BREAK"
    # Break statement to exit loops
    parser[0] = ASTNode("break_statement")


def p_continue_statement(parser):
    "continue_statement : CONTINUE"
    # Continue statement to skip to next iteration
    parser[0] = ASTNode("continue_statement")


def p_pass_statement(parser):
    "pass_statement : PASS"
    # Pass statement (no-op placeholder)
    parser[0] = ASTNode("pass_statement")


# ============================================================================
# FUNCTION DEFINITION
# ============================================================================

def p_function_def(parser):
    """function_def : DEF IDENTIFIER LPAREN RPAREN COLON NEWLINE indented_block
                    | DEF IDENTIFIER LPAREN parameter_list RPAREN COLON NEWLINE indented_block"""
    # Function definition with optional parameters
    func_name = ASTNode("identifier", value=parser[2])
    if len(parser) == 8:
        # No parameters
        params = ASTNode("parameter_list", children=[])
        block = parser[7]
    else:
        # With parameters
        params = parser[4]
        block = parser[8]
    
    parser[0] = ASTNode(
        "function_def",
        value=parser[2],
        children=[func_name, params, ASTNode("block", children=block)]
    )


def p_parameter_list_single(parser):
    "parameter_list : parameter"
    # Single parameter
    parser[0] = ASTNode("parameter_list", children=[parser[1]])


def p_parameter_list_multiple(parser):
    "parameter_list : parameter_list COMMA parameter"
    # Multiple parameters
    parser[1].children.append(parser[3])
    parser[0] = parser[1]


def p_parameter_simple(parser):
    "parameter : IDENTIFIER"
    # Simple positional parameter
    parser[0] = ASTNode("identifier", value=parser[1])


def p_parameter_default(parser):
    "parameter : IDENTIFIER ASSIGN expression"
    # Parameter with default value
    parser[0] = ASTNode(
        "parameter",
        value=parser[1],
        children=[parser[3]]  # default value
    )


def p_parameter_var_args(parser):
    "parameter : TIMES IDENTIFIER"
    # *args parameter for variable positional arguments
    parser[0] = ASTNode("var_args", value=parser[2])


def p_parameter_var_kwargs(parser):
    "parameter : TIMES TIMES IDENTIFIER"
    # **kwargs parameter for variable keyword arguments
    parser[0] = ASTNode("var_kwargs", value=parser[3])


# ============================================================================
# RETURN STATEMENT
# ============================================================================

def p_return_statement_empty(parser):
    "return_statement : RETURN"
    # Return with no value
    parser[0] = ASTNode("return_statement")


def p_return_statement_value(parser):
    "return_statement : RETURN expression"
    # Return with value
    parser[0] = ASTNode("return_statement", children=[parser[2]])


# ============================================================================
# FUNCTION CALL (as expression)
# ============================================================================

def p_expression_function_call(parser):
    """expression : IDENTIFIER LPAREN RPAREN
                  | IDENTIFIER LPAREN argument_list RPAREN"""
    # Function call with optional arguments
    if len(parser) == 4:
        args = ASTNode("argument_list", children=[])
    else:
        args = parser[3]
    
    parser[0] = ASTNode(
        "function_call",
        value=parser[1],
        children=[args]
    )


def p_argument_list_single(parser):
    "argument_list : argument"
    # Single argument
    parser[0] = ASTNode("argument_list", children=[parser[1]])


def p_argument_list_multiple(parser):
    "argument_list : argument_list COMMA argument"
    # Multiple arguments
    parser[1].children.append(parser[3])
    parser[0] = parser[1]


def p_argument_positional(parser):
    "argument : expression"
    # Positional argument
    parser[0] = parser[1]


def p_argument_keyword(parser):
    "argument : IDENTIFIER ASSIGN expression"
    # Keyword argument
    parser[0] = ASTNode(
        "keyword_arg",
        value=parser[1],
        children=[parser[3]]
    )


# ============================================================================
# TRY/EXCEPT/FINALLY STATEMENTS
# ============================================================================

def p_try_statement(parser):
    """try_statement : TRY COLON NEWLINE indented_block except_chain
                     | TRY COLON NEWLINE indented_block except_chain finally_clause
                     | TRY COLON NEWLINE indented_block except_chain else_try_clause
                     | TRY COLON NEWLINE indented_block except_chain else_try_clause finally_clause"""
    # Try statement with except clauses and optional else/finally
    try_block = parser[4]
    except_clauses = parser[5]  # list of except clauses
    
    children = [ASTNode("block", children=try_block)]
    children.extend(except_clauses)
    
    if len(parser) == 6:
        # Try with only except clauses
        pass
    elif len(parser) == 7:
        # Try with except + finally OR except + else
        if isinstance(parser[6], ASTNode) and parser[6].node_type == "finally_clause":
            children.append(parser[6])
        else:  # else_try_clause
            children.append(parser[6])
    elif len(parser) == 8:
        # Try with except + else + finally
        children.append(parser[6])  # else clause
        children.append(parser[7])  # finally clause
    
    parser[0] = ASTNode("try_statement", children=children)


def p_except_chain_single(parser):
    "except_chain : except_clause"
    # Single except clause
    parser[0] = [parser[1]]


def p_except_chain_multiple(parser):
    "except_chain : except_chain except_clause"
    # Multiple except clauses
    parser[1].append(parser[2])
    parser[0] = parser[1]


def p_except_clause_bare(parser):
    """except_clause : EXCEPT COLON NEWLINE indented_block
                     | DENT EXCEPT COLON NEWLINE indented_block"""
    # Bare except clause (catches any exception), optionally preceded by DENT
    if len(parser) == 5:
        parser[0] = ASTNode("except_clause", children=[ASTNode("block", children=parser[4])])
    else:
        parser[0] = ASTNode("except_clause", children=[ASTNode("block", children=parser[5])])


def p_except_clause_typed(parser):
    """except_clause : EXCEPT IDENTIFIER COLON NEWLINE indented_block
                     | DENT EXCEPT IDENTIFIER COLON NEWLINE indented_block"""
    # Except clause with exception type
    if len(parser) == 6:
        parser[0] = ASTNode(
            "except_clause",
            children=[
                ASTNode("identifier", value=parser[2]),
                ASTNode("block", children=parser[5])
            ]
        )
    else:
        parser[0] = ASTNode(
            "except_clause",
            children=[
                ASTNode("identifier", value=parser[3]),
                ASTNode("block", children=parser[6])
            ]
        )


def p_except_clause_typed_as(parser):
    """except_clause : EXCEPT IDENTIFIER AS IDENTIFIER COLON NEWLINE indented_block
                     | DENT EXCEPT IDENTIFIER AS IDENTIFIER COLON NEWLINE indented_block"""
    # Except clause with exception type bound to variable
    if len(parser) == 8:
        parser[0] = ASTNode(
            "except_clause",
            children=[
                ASTNode("identifier", value=parser[2]),
                ASTNode("identifier", value=parser[4]),
                ASTNode("block", children=parser[7])
            ]
        )
    else:
        parser[0] = ASTNode(
            "except_clause",
            children=[
                ASTNode("identifier", value=parser[3]),
                ASTNode("identifier", value=parser[5]),
                ASTNode("block", children=parser[8])
            ]
        )


def p_else_try_clause(parser):
    "else_try_clause : ELSE COLON NEWLINE indented_block"
    # Else clause within try/except (executes if no exception)
    parser[0] = ASTNode("else_statement", children=[ASTNode("block", children=parser[4])])


def p_finally_clause(parser):
    "finally_clause : FINALLY COLON NEWLINE indented_block"
    # Finally clause (always executes)
    parser[0] = ASTNode("finally_clause", children=[ASTNode("block", children=parser[4])])


# ============================================================================
# RAISE STATEMENT
# ============================================================================

def p_raise_statement_bare(parser):
    "raise_statement : RAISE"
    # Re-raise current exception
    parser[0] = ASTNode("raise_statement")


def p_raise_statement_exception(parser):
    "raise_statement : RAISE expression"
    # Raise specific exception
    parser[0] = ASTNode("raise_statement", children=[parser[2]])


# ============================================================================
# ASSIGNMENT RULES
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
# EXPRESSION RULES
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


# ============================================================================
# LIST EXPRESSION RULES
# ============================================================================

def p_expression_list(parser):
    """expression : LBRACKET RBRACKET
                  | LBRACKET expression_list RBRACKET"""
    # List literal, empty or with elements
    if len(parser) == 3:
        # Empty list
        parser[0] = ASTNode("list_literal", children=[])
    else:
        # List with elements
        parser[0] = ASTNode("list_literal", children=parser[2])


def p_expression_list_single(parser):
    "expression_list : expression"
    # Single element in list
    parser[0] = [parser[1]]


def p_expression_list_multiple(parser):
    "expression_list : expression_list COMMA expression"
    # Multiple elements separated by comma
    parser[0] = parser[1] + [parser[3]]


def p_empty(parser):
    "empty :"
    parser[0] = None
