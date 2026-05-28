"""
Token definitions for the Fangless Python lexer.
Defines the 'reserved' dictionary mapping keyword strings to their token
types, the master 'tokens' list required by PLY, and all simple pattern
rules (t_* string variables).
"""

reserved = {
    "if": "IF",
    "else": "ELSE",
    "elif": "ELIF",
    "while": "WHILE",
    "for": "FOR",
    "break": "BREAK",
    "continue": "CONTINUE",
    "pass": "PASS",
    "def": "DEF",
    "return": "RETURN",
    "class": "CLASS",
    "True": "TRUE",
    "False": "FALSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
}

tokens = [
    "IDENTIFIER",
    "INTEGER",
    "FLOAT",
    "STRING",
    "NEWLINE",

    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "FLOOR_DIVIDE",
    "MODULO",
    "POWER",

    "EQ",
    "NE",
    "LT",
    "GT",
    "LE",
    "GE",

    "ASSIGN",
    "PLUS_ASSIGN",
    "MINUS_ASSIGN",
    "TIMES_ASSIGN",
    "DIVIDE_ASSIGN",
    "MOD_ASSIGN",
    "FLOOR_DIVIDE_ASSIGN",
    "POWER_ASSIGN",

    "LPAREN",
    "RPAREN",
    "LBRACKET",
    "RBRACKET",
    "LBRACE",
    "RBRACE",
    "COLON",
    "COMMA",
    "DOT",
    "PIPE",

    "INDENT",
    "DENT",

] + list(reserved.values())

t_FLOOR_DIVIDE_ASSIGN = r"//="
t_POWER_ASSIGN = r"\*\*="
t_PLUS_ASSIGN = r"\+="
t_MINUS_ASSIGN = r"-="
t_TIMES_ASSIGN = r"\*="
t_DIVIDE_ASSIGN = r"/="
t_MOD_ASSIGN = r"%="

t_FLOOR_DIVIDE = r"//"
t_POWER = r"\*\*"
t_EQ = r"=="
t_NE = r"!="
t_LE = r"<="
t_GE = r">="

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_MODULO = r"%"
t_ASSIGN = r"="
t_LT = r"<"
t_GT = r">"

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COLON = r":"
t_COMMA = r","
t_DOT = r"\."
t_PIPE = r"\|"

t_ignore = ""
