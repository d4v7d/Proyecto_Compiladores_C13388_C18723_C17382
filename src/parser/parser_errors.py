"""Syntax error models for the Fangless parser."""


class ParserError:
    """Represents a syntactic error found while parsing."""

    def __init__(self, message, line=None, column=None, token=None):
        self.message = message
        self.line = line
        self.column = column
        self.token = token

    def __str__(self):
        location = ""
        if self.line is not None:
            location = f" at line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"

        token_info = ""
        if self.token is not None:
            token_info = f" near token {self.token!r}"

        return f"Syntax error: {self.message}{location}{token_info}"

    def __repr__(self):
        return (
            f"ParserError(message={self.message!r}, line={self.line!r}, "
            f"column={self.column!r}, token={self.token!r})"
        )
