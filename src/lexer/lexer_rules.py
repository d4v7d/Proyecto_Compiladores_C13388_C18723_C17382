"""
Lexer rules for the Fangless Python lexer.
Contains all token rules that require additional logic beyond a plain
regular expression, implemented as PLY-style t_* functions:
  - t_STRING:     matches single- and double-quoted strings with escape support.
  - t_FLOAT:      matches floating-point literals and converts them to float.
  - t_INTEGER:    matches integer literals and converts them to int.
  - t_IDENTIFIER: matches identifiers and reclassifies reserved keywords.
  - t_newline:    tracks indentation changes and enqueues INDENT/DENT tokens.
                  Normalizes tabs to spaces and detects tab/space mixing.
  - t_emptyline:  silently ignores empty lines (only spaces/tabs between newlines).
  - t_WHITESPACE: silently consumes horizontal whitespace between tokens.
  - t_COMMENT:    silently consumes single-line comments starting with '#'.
  - t_error:      handles illegal characters using panic mode recovery,
                  logging each error and skipping one character to continue.
"""

import ply.lex as lex
from .token_definitions import reserved


def normalize_indentation(indent_str, tab_width=8):
    """
    Normalize indentation by converting tabs to spaces.
    
    In Python, a tab advances to the next multiple of tab_width (default 8).
    This function:
    1. Converts the indentation string to equivalent spaces
    2. Detects and reports mixing of tabs and spaces (which Python doesn't allow)
    
    Args:
        indent_str: The indentation string (spaces and/or tabs)
        tab_width: The width of a tab in spaces (default 8)
    
    Returns:
        Tuple: (normalized_indent_length, has_mixed_tabs_spaces)
        - normalized_indent_length: The column position after this indentation
        - has_mixed_tabs_spaces: True if both tabs and spaces are present
    """
    has_tabs = '\t' in indent_str
    has_spaces = ' ' in indent_str
    has_mixed = has_tabs and has_spaces
    
    # Calculate the column position by processing each character
    column = 0
    for char in indent_str:
        if char == '\t':
            # Tab advances to the next multiple of tab_width
            column = ((column // tab_width) + 1) * tab_width
        elif char == ' ':
            column += 1
    
    return column, has_mixed

def t_STRING(token):
    r'("(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\n])*\')'
    token.value = token.value[1:-1]
    return token


def t_FLOAT(token):
    r"\d*\.\d+"
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


def t_emptyline(token):
    r"\n(?:[ \t]*\n)+"
    """
    Matches one or more empty lines (lines with only spaces/tabs between newlines).
    Captures all consecutive blank lines in a single match to avoid overlap issues.
    Pattern: newline followed by one or more (optional spaces/tabs + newline).
    These lines are ignored and not tokenized.
    Must be defined BEFORE t_newline to have priority.
    """
    token.lexer.lineno += token.value.count('\n')
    token.type = "NEWLINE"
    token.value = "\n"
    return token


def t_newline(token):
    r'\n[ \t]*'
    # Update line number
    token.lexer.lineno += token.value.count('\n')
    
    # Calculate spaces (indentation) after the last newline
    last_newline_index = token.value.rfind('\n')
    indent_str = token.value[last_newline_index + 1:]
    
    # Peek ahead to see if this line is blank or only contains a comment
    # If so, don't count this indentation level
    lexpos_after_spaces = token.lexpos + len(token.value)
    remaining_input = token.lexer.lexdata[lexpos_after_spaces:]
    
    # Check if the line is blank (only spaces/tabs before next newline) or starts with comment
    first_char_match = remaining_input.lstrip('\t ')[:1] if remaining_input else ''
    
    # If this line is blank or contains only a comment, skip indentation processing
    if first_char_match in ('\n', '\r', '#', ''):
        # This is either a blank line or a comment-only line - don't emit INDENT/DENT
        return
    
    # Check if we're inside parentheses/brackets/braces (continuation line)
    # by counting unmatched opening brackets up to this point
    code_before = token.lexer.lexdata[:token.lexpos]
    paren_depth = 0
    for char in code_before:
        if char in '([{':
            paren_depth += 1
        elif char in ')]}':
            paren_depth -= 1
    
    # If we're inside parentheses/brackets/braces, don't process indentation
    if paren_depth > 0:
        return
    
    # Detect tabs vs spaces in this line (for error checking)
    has_tabs_in_line = '\t' in indent_str
    has_spaces_in_line = ' ' in indent_str
    
    # Track if we've seen tabs and/or spaces across all lines
    if has_tabs_in_line:
        token.lexer.seen_tabs = True
    if has_spaces_in_line:
        token.lexer.seen_spaces = True
    
    # Check for mixing tabs and spaces across the file
    if token.lexer.seen_tabs and token.lexer.seen_spaces:
        message = (
            f"Lexical error: inconsistent use of tabs and spaces at line {token.lexer.lineno}"
        )
        token.lexer.errors.append(message)
        return
    
    # Normalize indentation: convert tabs to spaces and detect mixing within the line
    current_indent, has_mixed_tabs_spaces = normalize_indentation(indent_str)
    
    # Python doesn't allow mixing tabs and spaces in the same indentation
    if has_mixed_tabs_spaces:
        message = (
            f"Lexical error: inconsistent use of tabs and spaces at line {token.lexer.lineno}"
        )
        token.lexer.errors.append(message)
        return
    
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
        message = (
            f"Lexical error: inconsistent indentation at line {token.lexer.lineno} "
            f"(got {current_indent} spaces, expected {token.lexer.indent_stack[-1]})"
        )
        token.lexer.errors.append(message)

    token.type = "NEWLINE"
    token.value = "\n"
    return token


def t_WHITESPACE(token):
    r"[ \t]+"
    pass


def t_COMMENT(token):
    r"\#.*"
    pass


def t_error(token):
    message = (
        f"Lexical error: illegal character '{token.value[0]}' "
        f"at line {token.lineno}"
    )
    token.lexer.errors.append(message)
    token.lexer.skip(1)
