"""Operator precedence definitions for the Fangless parser."""


#precedence = (
#    ("left", "OR"),
#    ("left", "AND"),
#    ("right", "NOT"),
#    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
#    ("left", "PLUS", "MINUS"),
#    ("left", "TIMES", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
#    ("right", "UMINUS"),
#    ("right", "POWER"),
#)

precedence = (
    # Logical operators — lowest precedence
    ("left",     "OR"),
    ("left",     "AND"),
    ("right",    "NOT"),
 
    # Comparisons — non-associative (a < b < c is not allowed)
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
 
    # Arithmetic
    ("left",     "PLUS", "MINUS"),
    ("left",     "TIMES", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
 
    # Unary arithmetic  (UMINUS/UPLUS used via %prec in the rules)
    ("right",    "UMINUS", "UPLUS"),
 
    # Exponentiation — right-associative: 2**3**2 = 2**(3**2)
    ("right",    "POWER"),
 
    # Attribute access and subscript — highest precedence
    # Ensures a.b + c parses as (a.b) + c, not a.(b + c)
    ("left",     "DOT", "LBRACKET"),
)