"""Variable scope tracking for C++ code generation."""

from __future__ import annotations

# Python identifiers that collide with C++ keywords.
CPP_RESERVED = {
    "alignas",
    "alignof",
    "and",
    "and_eq",
    "asm",
    "auto",
    "bitand",
    "bitor",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "class",
    "compl",
    "const",
    "const_cast",
    "constexpr",
    "continue",
    "decltype",
    "default",
    "delete",
    "do",
    "double",
    "dynamic_cast",
    "else",
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "mutable",
    "namespace",
    "new",
    "noexcept",
    "not",
    "not_eq",
    "nullptr",
    "operator",
    "or",
    "or_eq",
    "private",
    "protected",
    "public",
    "register",
    "reinterpret_cast",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    "typeid",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "wchar_t",
    "while",
    "xor",
    "xor_eq",
}


def sanitize_identifier(name: str) -> str:
    """Return a C++-safe identifier for a Python name."""
    if name in CPP_RESERVED:
        return f"_{name}_"
    return name


class ScopeFrame:
    """One lexical scope level."""

    def __init__(self) -> None:
        self.declared: set[str] = set()

    def declare(self, name: str) -> None:
        self.declared.add(name)

    def is_declared(self, name: str) -> bool:
        return name in self.declared


class ScopeManager:
    """Stack of lexical scopes used while emitting C++."""

    def __init__(self) -> None:
        self._frames: list[ScopeFrame] = [ScopeFrame()]

    def push(self) -> None:
        self._frames.append(ScopeFrame())

    def pop(self) -> None:
        if len(self._frames) > 1:
            self._frames.pop()

    def declare(self, name: str) -> None:
        self._frames[-1].declare(name)

    def is_declared(self, name: str) -> bool:
        return any(frame.is_declared(name) for frame in reversed(self._frames))
