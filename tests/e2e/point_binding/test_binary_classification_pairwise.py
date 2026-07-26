from __future__ import annotations

from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.runner import Z3Runner
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from tests.support.binary_classification import make_sklearn_logistic_schema


def _source(*, domains: str, assertion: str) -> str:
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
forall left, right
with domain({domains})
=> {assertion} using Z3
"""


def _run(*, domains: str, assertion: str):
    task = run_ir2_with_model_schema(
        _source(domains=domains, assertion=assertion),
        schema=make_sklearn_logistic_schema(coefficient=1.0, intercept=0.0),
    )[0]
    return task, Z3Runner().run(task)


def test_pair_bc_005_pairwise_equality_is_proved_for_two_positive_regions() -> None:
    task, result = _run(
        domains="left.income: [1.0, 2.0], right.income: [3.0, 4.0]",
        assertion="target[left].label == target[right].label",
    )
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"
    assert len(task.model_evaluations) == 2
    assert len(task.lowering_evidence) == 1


def test_pair_bc_005_pairwise_equality_finds_opposite_region_counterexample() -> None:
    _task, result = _run(
        domains="left.income: [1.0, 2.0], right.income: [-2.0, -1.0]",
        assertion="target[left].label == target[right].label",
    )
    assert result.status is VerificationStatus.COUNTEREXAMPLE
    assert result.solver_status == "sat"
    assert result.model is not None


def test_pair_bc_002_zero_boundary_and_negative_region_share_negative_label() -> None:
    _task, result = _run(
        domains="left.income: [0.0, 0.0], right.income: [-1.0, -1.0]",
        assertion="target[left].label == target[right].label",
    )
    assert result.status is VerificationStatus.PROVED


def test_pair_bc_003_sugar_executes_like_explicit_equality() -> None:
    domains = "left.income: [1.0, 2.0], right.income: [3.0, 4.0]"
    explicit_task, explicit_result = _run(
        domains=domains, assertion="target[left].label == target[right].label"
    )
    sugar_task, sugar_result = _run(domains=domains, assertion="CLASSIFICATION.EQUAL()")
    assert explicit_result.status is sugar_result.status is VerificationStatus.PROVED
    assert explicit_task.spec_formula.expression == sugar_task.spec_formula.expression
