"""High-level API for transpiling Fangless Python AST to C++."""

from __future__ import annotations

from parser.ast_nodes import ASTNode

from .cpp_emitter import CppEmitter, TranspileError
from .cpp_runtime import get_cpp_runtime


def transpile_ast(ast: ASTNode) -> str:
    """Convert a parsed AST into a complete, compilable C++ translation unit."""
    emitter = CppEmitter()
    generated_lines = emitter.emit_program(ast)
    runtime_source = get_cpp_runtime().strip()
    return runtime_source + "\n\n" + "\n".join(generated_lines) + "\n"


def transpile_source(source_code: str, parser) -> str:
    """Parse source code and return generated C++."""
    ast = parser.parse(source_code)
    if parser.errors:
        messages = "\n".join(str(error) for error in parser.errors)
        raise TranspileError(f"Parse failed:\n{messages}")
    if ast is None:
        raise TranspileError("Parser returned no AST")
    return transpile_ast(ast)
