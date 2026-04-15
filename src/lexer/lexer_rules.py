"""
Lexer rules for the Fangless Python lexer.
"""

from .token_definitions import reserved


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


def t_newline(token):
    r"\n+"
    token.lexer.lineno += len(token.value)


def t_error(token):
    message = (
        f"Lexical error: illegal character '{token.value[0]}' "
        f"at line {token.lineno}"
    )
    token.lexer.errors.append(message)
    token.lexer.skip(1)