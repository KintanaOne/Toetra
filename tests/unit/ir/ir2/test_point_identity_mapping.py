from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import AttributeExpressionIR, ComparisonIR
from toetra._compiler.ir.ir2.enums import AssumptionSource
from tests.support.ir2 import compile_ir2


def test_ir2_map_001_source_points_map_to_exact_ir_points() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall source, candidate => target[source] <= target[candidate]
        """)
    assert tuple(m.source_name for m in task.point_mappings) == (
        "source",
        "candidate",
    )
    assert task.model_evaluations[0].point is task.point_mappings[0].ir_point
    assert task.model_evaluations[1].point is task.point_mappings[1].ir_point


def test_inline_anchor_facts_keep_point_identity_and_provenance() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        anchor customer := {
            age: 42,
            income: 55000
        }

        [BOUND]:
        check_at customer => target <= 0.8
        """)
    assumptions = tuple(
        item for item in task.assumptions if item.source is AssumptionSource.SCOPE
    )
    assert task.requirements.anchor_count == 1
    assert len(assumptions) == 2
    for assumption in assumptions:
        assert assumption.metadata["origin"] == "inline_anchor"
        assert assumption.metadata["point"] == "customer"
        atom = assumption.formula.expression
        assert isinstance(atom, ComparisonIR)
        assert isinstance(atom.left, AttributeExpressionIR)
        assert atom.left.point is task.point_mappings[0].ir_point


def test_domain_assumptions_keep_owning_point_identity() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [BOUND]:
        forall x0, x1
        with domain(x0.age: [18, 90], x1.age: [21, 70])
        => x0.age <= x1.age
        """)
    assumptions = tuple(
        item for item in task.assumptions if item.source is AssumptionSource.DOMAIN
    )
    assert {item.metadata["point"] for item in assumptions} == {"x0", "x1"}
    for assumption in assumptions:
        atom = assumption.formula.expression
        assert isinstance(atom, ComparisonIR)
        assert isinstance(atom.left, AttributeExpressionIR)
        assert atom.left.point is not None
        assert atom.left.point.name == assumption.metadata["point"]
