from __future__ import annotations

from toetra._backends.results import VerificationStatus
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._runtime import verify
from test.e2e.point_binding._helpers import build_linear_artifacts, source


def _point_contract(task) -> tuple[tuple[str, str], ...]:
    return tuple(
        (mapping.source_name, mapping.ir_point.binding_kind)
        for mapping in task.point_mappings
    )


def _evaluation_contract(task) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (
            evaluation.model_identity,
            evaluation.point.name,
            evaluation.target_name,
        )
        for evaluation in task.model_evaluations
    )


def test_e2e_04_local_sugar_and_explicit_core_are_semantically_equivalent(
    tmp_path,
) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(1.0,),
        intercept=0.0,
    )

    sugar = verify(
        source("e2e_04_local_sugar"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )
    explicit = verify(
        source("e2e_04_local_explicit"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    assert sugar.reports[0].status is VerificationStatus.PROVED
    assert explicit.reports[0].status is VerificationStatus.PROVED

    sugar_task = sugar.executions[0].task
    explicit_task = explicit.executions[0].task
    assert sugar_task.semantics == explicit_task.semantics
    assert sugar_task.requirements == explicit_task.requirements
    assert _point_contract(sugar_task) == _point_contract(explicit_task)
    assert _evaluation_contract(sugar_task) == _evaluation_contract(explicit_task)

    sugar_query = Z3Translator().translate(sugar_task).expression.sexpr()
    explicit_query = Z3Translator().translate(explicit_task).expression.sexpr()
    assert sugar_query == explicit_query

    assert sugar_task.scope.restriction is not None
    assert explicit_task.scope.restriction is not None
    assert sugar_task.scope.restriction.provenance.origin == "at_sugar"
    assert explicit_task.scope.restriction.provenance.origin == "where"
