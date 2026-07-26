from __future__ import annotations

from tests.support.ir2 import compile_ir2


def test_ir2_req_001_two_outputs_require_two_model_evaluations() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall x0, x1 => target[x0] <= target[x1]
        """)
    assert task.requirements.point_count == 2
    assert task.requirements.model_evaluation_count == 2
    assert tuple(e.point.name for e in task.model_evaluations) == ("x0", "x1")


def test_ir2_req_001_repeated_output_is_deduplicated() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall x0 => target[x0] <= target[x0] + 0.1
        """)
    assert task.requirements.model_evaluation_count == 1
    assert len(task.model_evaluations) == 1


def test_ir2_req_002_point_only_property_requires_no_model_evaluation() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall x0, x1 => x0.age <= x1.age
        """)
    assert task.requirements.point_count == 2
    assert task.requirements.model_evaluation_count == 0
    assert task.model_evaluations == ()


def test_ir2_req_003_alternating_quantifiers_require_advanced_capability() -> None:
    task = compile_ir2("""
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall original
        exists counterfactual
        => target[counterfactual] <= target[original]
        """)
    requirements = task.requirements
    assert requirements.binder_sequence == ("forall", "exists")
    assert requirements.alternation_depth == 1
    assert requirements.requires_native_quantifiers is True
    assert requirements.requires_quantifier_alternation is True
