from __future__ import annotations

from dsl.ast.nodes.program import ProgramNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code


def build_program(
    *, declarations: str = "", body: str, property_type: str = "LOGIC"
) -> ProgramNode:
    source = f"""
    model := "demo.onnx"
    target := MyTarget

    {declarations}

    [{property_type}]:
    {body}
    """
    return parse_program(parse_toetra_code(source))
