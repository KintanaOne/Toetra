from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    BinaryArithmeticExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    DomainEntryIR,
    DomainIR,
    FiniteSetDomainIR,
    IntervalDomainIR,
    OrIR,
    ScalarValueSource,
    SymbolLiteralIR,
)
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._compiler.ir.ir2.builder import IR2Builder
from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.domain_assumptions import DomainAssumptionEncoder
from toetra._compiler.ir.ir2.enums import AssumptionSource, NormalFormKind
from toetra._compiler.ir.ir2.nodes import NNFFormulaIR2
from toetra._compiler.ir.normalization.nnf import NNFNormalizer
from toetra._language.vocabulary.domains import EnumBoundaryKind
from toetra._language.vocabulary.operators import (
    EnumArithmeticOperator,
    EnumComparisonOperator,
)
from toetra._compiler.semantic.types.enums import EnumArithmeticClass, EnumDataType


def _int(value: int) -> ConstantExpressionIR:
    return ConstantExpressionIR(value=value, dtype=EnumDataType.INT)


def test_encode_domain_lowers_open_and_closed_interval_boundaries() -> None:
    domain = DomainIR(
        entries=(
            DomainEntryIR(
                entity="x0",
                feature="age",
                constraint=IntervalDomainIR(
                    lower=_int(18),
                    upper=_int(65),
                    lower_boundary=EnumBoundaryKind.OPEN,
                    upper_boundary=EnumBoundaryKind.CLOSED,
                ),
                dtype=EnumDataType.INT,
            ),
        )
    )

    assumptions = DomainAssumptionEncoder().encode_domain(domain)

    assert len(assumptions) == 2
    lower, upper = assumptions

    assert lower.source is AssumptionSource.DOMAIN
    assert upper.source is AssumptionSource.DOMAIN
    assert isinstance(lower.formula.expression, ComparisonIR)
    assert isinstance(upper.formula.expression, ComparisonIR)

    lower_atom = lower.formula.expression
    upper_atom = upper.formula.expression

    assert lower_atom.op is EnumComparisonOperator.GT
    assert upper_atom.op is EnumComparisonOperator.LTE
    assert isinstance(lower_atom.left, AttributeExpressionIR)
    assert lower_atom.left.dtype is EnumDataType.INT
    assert isinstance(lower_atom.right, ConstantExpressionIR)
    assert lower_atom.right.value == 18
    assert isinstance(upper_atom.right, ConstantExpressionIR)
    assert upper_atom.right.value == 65

    assert lower.metadata == {
        "origin": "dsl_domain",
        "entry_index": 0,
        "entity": "x0",
        "feature": "age",
        "constraint_kind": "interval",
        "expansion_kind": "lower_bound",
        "boundary": "open",
        "operator": ">",
        "expression": "18",
    }
    assert upper.metadata["boundary"] == "closed"
    assert upper.metadata["expansion_kind"] == "upper_bound"


def test_encode_domain_preserves_arithmetic_bounds_and_constant_provenance() -> None:
    margin = ConstantExpressionIR(
        value=1.5,
        dtype=EnumDataType.FLOAT,
        source_kind=ScalarValueSource.SPECIFICATION_CONSTANT,
        source_name="margin",
    )
    lower = BinaryArithmeticExpressionIR(
        left=AttributeExpressionIR(entity="x0", feature="baseline"),
        operator=EnumArithmeticOperator.SUB,
        right=margin,
        dtype=EnumDataType.FLOAT,
        arithmetic_class=EnumArithmeticClass.AFFINE,
    )
    upper = BinaryArithmeticExpressionIR(
        left=AttributeExpressionIR(entity="x0", feature="baseline"),
        operator=EnumArithmeticOperator.ADD,
        right=margin,
        dtype=EnumDataType.FLOAT,
        arithmetic_class=EnumArithmeticClass.AFFINE,
    )
    domain = DomainIR(
        entries=(
            DomainEntryIR(
                entity="x0",
                feature="value",
                constraint=IntervalDomainIR(
                    lower=lower,
                    upper=upper,
                    lower_boundary=EnumBoundaryKind.CLOSED,
                    upper_boundary=EnumBoundaryKind.CLOSED,
                ),
            ),
        )
    )

    assumptions = DomainAssumptionEncoder().encode_domain(domain)

    assert len(assumptions) == 2
    lower_atom = assumptions[0].formula.expression
    upper_atom = assumptions[1].formula.expression
    assert isinstance(lower_atom, ComparisonIR)
    assert isinstance(upper_atom, ComparisonIR)
    assert lower_atom.right is lower
    assert upper_atom.right is upper
    assert assumptions[0].metadata["expression"] == "x0.baseline - 1.5"
    assert assumptions[1].metadata["expression"] == "x0.baseline + 1.5"


def test_encode_domain_lowers_numeric_finite_set_to_membership_disjunction() -> None:
    domain = DomainIR(
        entries=(
            DomainEntryIR(
                entity="x0",
                feature="level",
                constraint=FiniteSetDomainIR(values=(_int(1), _int(3), _int(7))),
            ),
        )
    )

    (assumption,) = DomainAssumptionEncoder().encode_domain(domain)

    assert assumption.source is AssumptionSource.DOMAIN
    assert isinstance(assumption.formula, NNFFormulaIR2)
    expression = assumption.formula.expression
    assert isinstance(expression, OrIR)
    assert len(expression.operands) == 3

    values: list[int] = []
    for operand in expression.operands:
        assert isinstance(operand, ComparisonIR)
        assert operand.op is EnumComparisonOperator.EQ
        assert isinstance(operand.right, ConstantExpressionIR)
        values.append(operand.right.value)

    assert values == [1, 3, 7]
    assert assumption.metadata["constraint_kind"] == "finite_set"
    assert assumption.metadata["member_count"] == 3


def test_encode_domain_preserves_symbolic_categories_and_member_provenance() -> None:
    domain = DomainIR(
        entries=(
            DomainEntryIR(
                entity="x0",
                feature="region",
                constraint=FiniteSetDomainIR(
                    values=(SymbolLiteralIR("EU"), SymbolLiteralIR("US"))
                ),
            ),
        )
    )

    (assumption,) = DomainAssumptionEncoder().encode_domain(domain)

    expression = assumption.formula.expression
    assert isinstance(expression, OrIR)
    for operand, expected in zip(expression.operands, ("EU", "US"), strict=True):
        assert isinstance(operand, ComparisonIR)
        assert isinstance(operand.right, SymbolLiteralIR)
        assert operand.right.name == expected

    assert assumption.metadata["members"] == [
        {"member_index": 0, "kind": "symbolic_category", "value": "EU"},
        {"member_index": 1, "kind": "symbolic_category", "value": "US"},
    ]


def test_ir2_builder_injects_dsl_domain_assumptions_automatically() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0
        with domain(
            x0.a: ]0, 3],
            x0.level: {1, 2}
        )
        => x0.a <= 3
    """

    (task_ir1,) = NNFNormalizer().normalize_tasks(run_ir(source))
    task = IR2Builder().build(
        task_ir1,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    assert len(task.assumptions) == 3
    assert all(
        assumption.source is AssumptionSource.DOMAIN for assumption in task.assumptions
    )
    assert task.metadata["domain_assumption_count"] == 3
    assert task.requirements.requires_domains is True
    assert task.requirements.requires_domain_assumptions is True
    assert task.requirements.requires_finite_set_membership is True
    assert task.requirements.required_scalar_sorts == frozenset({EnumDataType.INT})


def test_ir2_builder_combines_automatic_domain_and_external_assumptions() -> None:
    source = """
    model := "model.onnx"
    target := MyTarget

    [LOGIC]:
    forall x0 with domain(x0.a: [0, 3]) => x0.a <= 3
    """

    (task_ir1,) = NNFNormalizer().normalize_tasks(run_ir(source))
    external = DomainAssumptionEncoder().encode_domain(
        DomainIR(
            entries=(
                DomainEntryIR(
                    entity="x0",
                    feature="b",
                    constraint=FiniteSetDomainIR(values=(_int(1),)),
                ),
            )
        )
    )
    task = IR2Builder().build(task_ir1, assumptions=external)

    assert len(task.assumptions) == 3
    assert task.assumptions[0].metadata["feature"] == "a"
    assert task.assumptions[1].metadata["feature"] == "a"
    assert task.assumptions[2].metadata["feature"] == "b"
    assert task.metadata["domain_assumption_count"] == 2
