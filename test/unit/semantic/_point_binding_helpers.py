from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import (
    AndNode,
    ComparisonNode,
    ImplicationNode,
    NotNode,
    OrNode,
)
from toetra._compiler.ast.nodes.primitives import AttributeNode, TargetRefNode
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer


def build_and_validate(source: str):
    program = parse_program(parse_toetra_code(source))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
    )
    return program


def semantic_context(program, property_index: int = 0):
    semantic = program.body[property_index].semantic
    assert semantic is not None
    assert semantic.context is not None
    return semantic.context


def collect_targets(node: object) -> list[TargetRefNode]:
    if isinstance(node, ComparisonNode):
        result: list[TargetRefNode] = []
        if isinstance(node.left, TargetRefNode):
            result.append(node.left)
        if isinstance(node.right, TargetRefNode):
            result.append(node.right)
        return result
    if isinstance(node, (AndNode, OrNode)):
        return [target for child in node.operands for target in collect_targets(child)]
    if isinstance(node, NotNode):
        return collect_targets(node.operand)
    if isinstance(node, ImplicationNode):
        return collect_targets(node.left) + collect_targets(node.right)
    return []


def collect_attributes(node: object) -> list[AttributeNode]:
    if isinstance(node, ComparisonNode):
        return [
            operand
            for operand in (node.left, node.right)
            if isinstance(operand, AttributeNode)
        ]
    if isinstance(node, (AndNode, OrNode)):
        return [attr for child in node.operands for attr in collect_attributes(child)]
    if isinstance(node, NotNode):
        return collect_attributes(node.operand)
    if isinstance(node, ImplicationNode):
        return collect_attributes(node.left) + collect_attributes(node.right)
    return []
