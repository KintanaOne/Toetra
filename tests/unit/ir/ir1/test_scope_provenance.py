from __future__ import annotations

from toetra._compiler.ir.ir1.nodes import ImplyIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from tests.support.semantic_restrictions import numeric_schema


def test_ir1_prov_001_at_sugar_keeps_generated_binder_and_source_origin() -> None:
    task = run_ir(
        """
        model := "credit.joblib"
        target := score

        anchor customer := {
            a: 1.0,
            b: 2
        }

        [ROBUSTNESS]:
        at customer with perturbed in neighborhood(
            metric = Linf,
            eps = 0.05
        )
        => target[perturbed] <= target[customer] + 0.1
        """,
        model_schema=numeric_schema(),
    )[0]

    assert task.scope.provenance is not None
    assert task.scope.provenance.source_kind == "at_sugar"
    assert task.scope.provenance.legacy_compatibility is False
    assert task.scope.restriction is not None
    assert task.scope.restriction.provenance.origin == "at_sugar"
    assert task.scope.restriction.provenance.source_span is not None
    assert len(task.scope.binders) == 1
    assert task.scope.binders[0].generated is True
    assert task.scope.binders[0].point.generated is True
    assert task.scope.binders[0].point.name == "perturbed"
    assert isinstance(task.query.expression, ImplyIR)
