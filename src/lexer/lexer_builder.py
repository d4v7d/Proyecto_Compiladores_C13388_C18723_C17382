"""
Lexer builder for the Fangless Python project.
FanglessLexer is the central class that combines token definitions and
lexer rules into a single PLY lexer instance. It manages two key shared
data structures:
  - indent_stack.
  - token_queue.
All t_* attributes from token_definitions and lexer_rules are copied onto
the class dynamically via setattr so that PLY can discover them.
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

        self.indent_stack = [0]
        self.token_queue = []

        self.lexer.indent_stack = self.indent_stack
        self.lexer.token_queue = self.token_queue

    def tokenize(self, source_code):
        self.errors.clear()
        self.indent_stack.clear()
        self.indent_stack.append(0)
        self.token_queue.clear()

        self.lexer.lineno = 1
        self.lexer.input(source_code)

        tokens = []
        while True:
            if self.token_queue:
                token = self.token_queue.pop(0)
            else:
                token = self.lexer.token()

            if token is None:

                while len(self.indent_stack) > 1:
                    self.indent_stack.pop()

                    dedent_token = lex.LexToken()
                    dedent_token.type = "DENT"
                    dedent_token.value = ""
                    dedent_token.lineno = self.lexer.lineno
                    dedent_token.lexpos = self.lexer.lexpos
                    tokens.append(dedent_token)

                break
            tokens.append(token)

        return tokens


for name in dir(token_definitions):
    if name.startswith("t_") and name != "t_ignore":
        setattr(FanglessLexer, name, getattr(token_definitions, name))

for name in dir(lexer_rules):
    if name.startswith("t_"):
        setattr(FanglessLexer, name, staticmethod(getattr(lexer_rules, name)))