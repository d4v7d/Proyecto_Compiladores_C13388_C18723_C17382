"""
Lexer builder for the Fangless Python project.
"""

import ply.lex as lex

from . import token_definitions
from . import lexer_rules


class FanglessLexer:
    tokens = token_definitions.tokens
    t_ignore = token_definitions.t_ignore

    def __init__(self):
        self.errors = []
        self.lexer = lex.lex(module=self.__class__)
        self.lexer.errors = self.errors

    def tokenize(self, source_code):
        self.errors.clear()
        self.lexer.lineno = 1
        self.lexer.input(source_code)

        tokens = []
        while True:
            token = self.lexer.token()
            if token is None:
                break
            tokens.append(token)

        return tokens


for name in dir(token_definitions):
    if name.startswith("t_") and name != "t_ignore":
        setattr(FanglessLexer, name, getattr(token_definitions, name))

for name in dir(lexer_rules):
    if name.startswith("t_"):
        setattr(FanglessLexer, name, staticmethod(getattr(lexer_rules, name)))