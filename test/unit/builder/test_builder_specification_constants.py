from __future__ import annotations

from dsl.ast.nodes.assertion import ComparisonNode
from dsl.ast.nodes.domain import FiniteSetDomainNode
from dsl.ast.nodes.expressions import QuantifierExprNode
from dsl.ast.nodes.primitives import AttributeNode, NameRefNode, TargetRefNode
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.types.enums import EnumDataType


def _build(source: str):
    return parse_program(parse_toetra_code(source))


def test_builder_preserves_typed_declarations_in_source_order() -> None:
    program = _build("""
        model := "model.onnx"
        target := MyTarget

        minimum_income := 25000
        max_risk := 0.2
        temperature_floor := -0.1
        strict_mode := true
        region := "EU"

        [LOGIC]:
        forall applicant => target <= max_risk
        """)

    declarations = program.header.specification_constants

    assert [declaration.name for declaration in declarations] == [
        "minimum_income",
        "max_risk",
        "temperature_floor",
        "strict_mode",
        "region",
    ]
    assert [declaration.value.value for declaration in declarations] == [
        25000,
        0.2,
        -0.1,
        True,
        "EU",
    ]
    assert [declaration.value.dtype for declaration in declarations] == [
        EnumDataType.INT,
        EnumDataType.FLOAT,
        EnumDataType.FLOAT,
        EnumDataType.BOOL,
        EnumDataType.STRING,
    ]


def test_builder_preserves_bare_name_without_guessing() -> None:
    program = _build("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7

        [LOGIC]:
        forall x0 => x0.score <= threshold
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)

    assert comparison.left == AttributeNode(
        entity="x0",
        feature="score",
        path=["x0", "score"],
    )
    assert comparison.right == NameRefNode(name="threshold")


def test_builder_keeps_target_distinct_from_bare_names() -> None:
    program = _build("""
        model := "model.onnx"
        target := MyTarget

        threshold := 7

        [LOGIC]:
        forall x0 => target <= threshold
        """)

    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)

    assert isinstance(comparison.left, TargetRefNode)
    assert comparison.right == NameRefNode(name="threshold")


def test_finite_set_identifiers_remain_unresolved_for_semantics() -> None:
    program = _build("""
        model := "model.onnx"
        target := MyTarget

        preferred_region := "EU"

        [LOGIC]:
        forall applicant
            with domain(applicant.region: {preferred_region, US})
            => target <= 1
        """)

    scope = program.body[0].rule.scope
    assert isinstance(scope, QuantifierExprNode)
    assert scope.domain is not None

    constraint = scope.domain.entries[0].constraint
    assert isinstance(constraint, FiniteSetDomainNode)
    assert constraint.values == [
        NameRefNode(name="preferred_region"),
        NameRefNode(name="US"),
    ]
