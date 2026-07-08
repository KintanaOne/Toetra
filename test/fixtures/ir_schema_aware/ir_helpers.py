from __future__ import annotations

from dsl.builder.program import parse_program
from dsl.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    VerificationTask,
)
from dsl.ir.ir1.translator import IRTranslator
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer


def translate_source(source: str, model_schema=None) -> list[VerificationTask]:
    ast = parse_program(parse_forml_code(source))

    FORMLValidator().validate(
        ast,
        tracer=ValidationTracer(enabled=False),
        model_schema=model_schema,
    )

    return IRTranslator().translate(ast)


def collect_comparisons(node: LogicalIR) -> list[ComparisonIR]:
    if isinstance(node, ComparisonIR):
        return [node]

    if isinstance(node, AndIR):
        result: list[ComparisonIR] = []
        for child in node.operands:
            result.extend(collect_comparisons(child))
        return result

    if isinstance(node, OrIR):
        result: list[ComparisonIR] = []
        for child in node.operands:
            result.extend(collect_comparisons(child))
        return result

    if isinstance(node, NotIR):
        return collect_comparisons(node.operand)

    if isinstance(node, ImplyIR):
        return collect_comparisons(node.left) + collect_comparisons(node.right)

    if isinstance(node, ProblemIR):
        return []

    raise TypeError(f"Unsupported IR node type: {type(node)}")


def comparison_by_feature(task: VerificationTask) -> dict[str, ComparisonIR]:
    comparisons = collect_comparisons(task.query.expression)
    return {comparison.feature: comparison for comparison in comparisons}


def serialize_logical(node: LogicalIR):
    if isinstance(node, ComparisonIR):
        return {
            "type": "comparison",
            "entity": node.entity,
            "feature": node.feature,
            "op": node.op.value,
            "value": node.value,
            "feature_dtype": (
                node.feature_dtype.value if node.feature_dtype is not None else None
            ),
            "value_dtype": (
                node.value_dtype.value if node.value_dtype is not None else None
            ),
        }

    if isinstance(node, AndIR):
        return {
            "type": "and",
            "operands": [serialize_logical(child) for child in node.operands],
        }

    if isinstance(node, OrIR):
        return {
            "type": "or",
            "operands": [serialize_logical(child) for child in node.operands],
        }

    if isinstance(node, NotIR):
        return {
            "type": "not",
            "operand": serialize_logical(node.operand),
        }

    if isinstance(node, ImplyIR):
        return {
            "type": "imply",
            "left": serialize_logical(node.left),
            "right": serialize_logical(node.right),
        }

    if isinstance(node, ProblemIR):
        return {
            "type": "problem",
            "problem": node.problem.value,
            "function": node.function.value if node.function is not None else None,
            "args": node.args,
        }

    raise TypeError(f"Unsupported IR node type: {type(node)}")


def serialize_task(task: VerificationTask):
    return {
        "property_type": task.property_type.value,
        "backend": task.backend.value if task.backend is not None else None,
        "scope": {
            "kind": task.scope.kind,
            "variables": task.scope.variables,
            "neighborhood": None,
            "domain": None,
        },
        "query": serialize_logical(task.query.expression),
    }
