"""Operator precedence definitions for the Fangless parser."""


precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("nonassoc", "EQ", "NE", "LT", "LE", "GT", "GE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "FLOOR_DIVIDE", "MODULO"),
    ("right", "UMINUS"),
    ("right", "POWER"),
)
