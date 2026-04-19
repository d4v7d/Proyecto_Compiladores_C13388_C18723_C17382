"""
Lexer rules for the Fangless Python lexer.
"""

import ply.lex as lex
from .token_definitions import reserved

def t_STRING(token):
    r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    token.value = token.value[1:-1]  # Remove quotes
    return token

def t_FLOAT(token):
    r"\d+\.\d+"
    token.value = float(token.value)
    return token


def t_INTEGER(token):
    r"\d+"
    token.value = int(token.value)
    return token


def t_IDENTIFIER(token):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    token.type = reserved.get(token.value, "IDENTIFIER")
    return token


def t_error(token):
    message = (
        f"Lexical error: illegal character '{token.value[0]}' "
        f"at line {token.lineno}"
    )
    token.lexer.errors.append(message)
    token.lexer.skip(1)


def t_newline(token):
    r'\n[ \t]*'
    # Update line number
    token.lexer.lineno += token.value.count('\n')
    
    # Calculate spaces (indentation) after the last newline
    last_newline_index = token.value.rfind('\n')
    indent_str = token.value[last_newline_index + 1:]
    
    # Assuming 1 space = 1 level for simplicity, adjust if tabs are mixed
    current_indent = len(indent_str) 
    last_indent = token.lexer.indent_stack[-1]

    if current_indent > last_indent:
        # Indentation increased
        token.lexer.indent_stack.append(current_indent)
        tok = lex.LexToken()
        tok.type = 'INDENT'
        tok.value = indent_str
        tok.lineno = token.lexer.lineno
        tok.lexpos = token.lexpos
        token.lexer.token_queue.append(tok)
        
    elif current_indent < last_indent:
        # Indentation decreased
        while token.lexer.indent_stack[-1] > current_indent:
            token.lexer.indent_stack.pop()
            tok = lex.LexToken()
            tok.type = 'DENT'
            tok.value = ''
            tok.lineno = token.lexer.lineno
            tok.lexpos = token.lexpos
            token.lexer.token_queue.append(tok)
            
        if token.lexer.indent_stack[-1] != current_indent:
             # Indentation error - only report if line is not empty
             # Check if this is just a blank line with inconsistent indentation
             pass
             
    # t_newline itself doesn't return a token to PLY's main loop
    pass


def t_WHITESPACE(token):
    r"[ \t]+"
    pass


def t_COMMENT(token):
    r"\#.*"
    pass
