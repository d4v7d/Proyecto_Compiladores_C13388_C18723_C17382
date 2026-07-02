"""Parser builder for the Fangless Python project."""

import ply.yacc as yacc

from lexer.lexer_builder import FanglessLexer
from lexer.token_definitions import tokens

from . import grammar_rules
from . import grammar_extensions
from .ast_nodes import propagate_locations, set_parse_source
from .parser_errors import ParserError
from .precedence import precedence


class _TokenStream:
    """Small adapter that lets yacc consume a pre-tokenized list."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def token(self):
        if self.index >= len(self.tokens):
            return None

        token = self.tokens[self.index]
        self.index += 1
        return token


class FanglessParser:
    """Builds and runs the Fangless parser with PLY yacc."""

    tokens = tokens
    precedence = precedence

    def __init__(self, **yacc_options):
        self.errors = []
        self.lexer = FanglessLexer()
        self.source_code = ""
        self._last_token_list = []
        yacc_options.setdefault("debug", False)
        yacc_options.setdefault("write_tables", False)
        #yacc_options.setdefault("errorlog", yacc.NullLogger())
        self.parser = yacc.yacc(module=self, **yacc_options)

    def parse(self, source_code):
        self.errors.clear()
        self.source_code = source_code
        set_parse_source(source_code)
        token_list = self.lexer.tokenize(source_code)
        token_stream = _TokenStream(token_list)
        # Kept so p_error can recover a line number when PLY reports EOF
        # (it calls p_error(None), which carries no position information).
        self._last_token_list = token_list
        ast = self.parser.parse(lexer=token_stream)

        for error in self.lexer.errors:
            self.errors.append(ParserError(error))

        if self.errors:
            return None

        if ast is not None:
            propagate_locations(ast)

        return ast

    @staticmethod
    def find_column(source_code, token):
        line_start = source_code.rfind("\n", 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

    def p_error(self, token):
        if token is None:
            last_line = self._last_token_list[-1].lineno if self._last_token_list else None
            self.errors.append(
                ParserError("unexpected end of input", line=last_line)
            )
            return

        self.errors.append(
            ParserError(
                "unexpected token",
                line=token.lineno,
                column=self.find_column(self.source_code, token),
                token=f"{token.type}({token.value!r})",
            )
        )


for name in dir(grammar_rules):
    if name.startswith("p_"):
        setattr(FanglessParser, name, staticmethod(getattr(grammar_rules, name)))

# Load extensions AFTER base rules. They override limited versions:
#   p_expression_attribute  (was IDENTIFIER.IDENTIFIER, now expression.IDENTIFIER)
#   p_expression_subscript  (was IDENTIFIER[expr], now expression[expr])

#   adds new rules for: class_def, method_call, slicing, tuples, dicts, sets,
#   attribute_assignment, subscript_assignment.
for name in dir(grammar_extensions):
    if name.startswith("p_"):
        setattr(FanglessParser, name, staticmethod(getattr(grammar_extensions, name)))