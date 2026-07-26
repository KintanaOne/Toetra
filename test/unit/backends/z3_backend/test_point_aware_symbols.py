from __future__ import annotations

from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._backends.z3_backend.symbols import (
    Z3ModelOutputIdentity,
    Z3PointFeatureIdentity,
)
from toetra._backends.z3_backend.translator import Z3Translator
from test.unit.backends.z3_backend._point_aware_helpers import build_task

UNIVERSAL_SOURCE = """
    model := "linear.joblib"
    target := score

    [MONOTONICITY]:
    forall x0, x1
    with domain(
        x0.a: [0.0, 3.0],
        x1.a: [0.0, 3.0]
    )
    where x1.a >= x0.a
    => target[x1] >= target[x0] using Z3
"""


def test_be_pnt_001_same_feature_on_two_points_has_distinct_solver_symbols() -> None:
    translation = Z3Translator().translate(build_task(UNIVERSAL_SOURCE))

    x0_identity = translation.identity_for("x0.a")
    x1_identity = translation.identity_for("x1.a")

    assert isinstance(x0_identity, Z3PointFeatureIdentity)
    assert isinstance(x1_identity, Z3PointFeatureIdentity)
    assert x0_identity.point.name == "x0"
    assert x1_identity.point.name == "x1"
    assert x0_identity != x1_identity
    assert translation.variables["x0.a"] is not translation.variables["x1.a"]


def test_be_tgt_001_targets_on_two_points_have_distinct_solver_symbols() -> None:
    translation = Z3Translator().translate(build_task(UNIVERSAL_SOURCE))

    output_names = {
        name
        for name, identity in translation.symbol_identities.items()
        if isinstance(identity, Z3ModelOutputIdentity)
    }

    assert output_names == {"_model.score[x0]", "_model.score[x1]"}
    assert translation.identity_for("_model.score[x0]") != translation.identity_for(
        "_model.score[x1]"
    )


def test_be_map_001_result_metadata_restores_point_and_evaluation_identities() -> None:
    task = build_task("""
        model := "linear.joblib"
        target := score

        [LOGIC]:
        exists x0, x1
        with domain(
            x0.a: [0.0, 3.0],
            x1.a: [0.0, 3.0]
        )
        where x1.a > x0.a
        => target[x1] > target[x0] using Z3
        """)

    result = Z3Runner().run(task)

    assert result.status is VerificationStatus.WITNESS
    assert result.model is not None
    assert "_model.score[x0]" in result.model
    assert "_model.score[x1]" in result.model

    mapping = result.metadata["assignment_symbol_mapping"]
    assert mapping["x0.a"]["identity"]["kind"] == "point_feature"
    assert mapping["x0.a"]["identity"]["point"]["name"] == "x0"
    assert mapping["_model.score[x1]"]["identity"] == {
        "kind": "model_output",
        "model_identity": "linear.joblib",
        "point": {
            "name": "x1",
            "binding_kind": "existential",
            "lexical_depth": 2,
            "generated": False,
        },
        "target": "score",
    }
