from __future__ import annotations

from toetra._compiler.builder.program import parse_program
from toetra._compiler.ir.ir1.nodes import (
    AndIR,
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ImplyIR,
    LogicalIR,
    NotIR,
    OrIR,
    ProblemIR,
    PointBindingIR,
    ScalarExpressionIR,
    SourceSpanIR,
    TargetExpressionIR,
    UnaryArithmeticExpressionIR,
    VerificationTask,
)
from toetra._compiler.ir.ir1.outputs import OutputObservableExpressionIR
from toetra._compiler.ir.ir1.scalar import iter_scalar_expressions
from toetra._compiler.ir.ir1.translator import IRTranslator
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer


def translate_source(source: str, model_schema=None) -> list[VerificationTask]:
    ast = parse_program(parse_toetra_code(source))

    ToetraValidator().validate(
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
    result: dict[str, ComparisonIR] = {}

    for comparison in collect_comparisons(task.query.expression):
        for scalar in iter_scalar_expressions(comparison.left):
            if isinstance(scalar, AttributeExpressionIR):
                result[scalar.feature] = comparison
                break

    return result


def serialize_scalar(node: ScalarExpressionIR):
    if isinstance(node, ConstantExpressionIR):
        return {
            "type": "constant",
            "value": node.value,
            "dtype": node.dtype.value,
            "source_kind": node.source_kind.value,
            "source_name": node.source_name,
        }

    if isinstance(node, AttributeExpressionIR):
        return {
            "type": "attribute",
            "entity": node.entity,
            "feature": node.feature,
            "dtype": node.dtype.value if node.dtype is not None else None,
            "point": serialize_point(node.point),
        }

    if isinstance(node, TargetExpressionIR):
        return {
            "type": "target",
            "entity": node.entity,
            "feature": node.feature,
            "dtype": node.dtype.value if node.dtype is not None else None,
            "evaluation": (
                {
                    "model_identity": node.evaluation.model_identity,
                    "point": serialize_point(node.evaluation.point),
                    "target_name": node.evaluation.target_name,
                }
                if node.evaluation is not None
                else None
            ),
        }

    if isinstance(node, OutputObservableExpressionIR):
        return {
            "type": "output_observable",
            "observable": node.observable.value,
            "dtype": node.dtype.value if node.dtype is not None else None,
            "label": (
                {
                    "value": node.label.value,
                    "dtype": node.label.dtype.value,
                    "source_lexeme": node.label.source_lexeme,
                }
                if node.label is not None
                else None
            ),
            "evaluation": {
                "model_identity": node.evaluation.model_identity,
                "point": serialize_point(node.evaluation.point),
                "output_name": node.evaluation.output_name,
            },
        }

    if isinstance(node, UnaryArithmeticExpressionIR):
        return {
            "type": "unary",
            "operator": node.operator.value,
            "operand": serialize_scalar(node.operand),
            "dtype": node.dtype.value if node.dtype is not None else None,
            "arithmetic_class": (
                node.arithmetic_class.value
                if node.arithmetic_class is not None
                else None
            ),
        }

    if isinstance(node, BinaryArithmeticExpressionIR):
        return {
            "type": "binary",
            "left": serialize_scalar(node.left),
            "operator": node.operator.value,
            "right": serialize_scalar(node.right),
            "dtype": node.dtype.value if node.dtype is not None else None,
            "arithmetic_class": (
                node.arithmetic_class.value
                if node.arithmetic_class is not None
                else None
            ),
        }

    raise TypeError(f"Unsupported scalar IR node type: {type(node)}")


def serialize_logical(node: LogicalIR):
    if isinstance(node, ComparisonIR):
        return {
            "type": "comparison",
            "left": serialize_scalar(node.left),
            "op": node.op.value,
            "right": serialize_scalar(node.right),
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
            "points": [serialize_point(point) for point in task.scope.points],
            "binders": [
                {
                    "quantifier": binder.quantifier,
                    "point": binder.point.name,
                    "generated": binder.generated,
                    "source_span": serialize_span(binder.source_span),
                }
                for binder in task.scope.binders
            ],
            "default_point": (
                task.scope.default_point.name
                if task.scope.default_point is not None
                else None
            ),
            "provenance": (
                {
                    "source_kind": task.scope.provenance.source_kind,
                    "source_span": serialize_span(task.scope.provenance.source_span),
                    "legacy_compatibility": (
                        task.scope.provenance.legacy_compatibility
                    ),
                }
                if task.scope.provenance is not None
                else None
            ),
            "restriction": (
                {
                    "origin": task.scope.restriction.provenance.origin,
                    "source_span": serialize_span(
                        task.scope.restriction.provenance.source_span
                    ),
                    "expression": serialize_logical(task.scope.restriction.expression),
                }
                if task.scope.restriction is not None
                else None
            ),
        },
        "query": serialize_logical(task.query.expression),
    }


def serialize_point(point: PointBindingIR | None):
    if point is None:
        return None
    return {
        "name": point.name,
        "binding_kind": point.binding_kind,
        "lexical_depth": point.lexical_depth,
        "generated": point.generated,
        "source_span": serialize_span(point.source_span),
    }


def serialize_span(span: SourceSpanIR | None):
    if span is None:
        return None
    return {
        "line": span.line,
        "column": span.column,
        "end_line": span.end_line,
        "end_column": span.end_column,
    }
