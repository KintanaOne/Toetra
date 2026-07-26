from __future__ import annotations

from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._compatibility.policy import (
    SEMANTIC_LOWERING_CONCLUSION_NOT_PERMITTED,
    apply_semantic_lowering_policy,
)
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._language.vocabulary.backends import EnumBackend
from toetra._models.semantics.lowering import ModelSemanticLowerer
from test.fixtures.model_semantic_lowering import make_binary_logistic_schema


def _evidence():
    schema = make_binary_logistic_schema()
    task = run_ir(
        """
        model := "credit.joblib"
        target := decision
        [LOGIC]:
        forall applicant =>
            target[applicant].probability("approved") >= 0.8
        """,
        model_schema=schema,
    )[0]
    return ModelSemanticLowerer().lower_task(task, schema=schema).evidence


def test_approximate_lowering_keeps_permitted_proof() -> None:
    result = VerificationResult(
        status=VerificationStatus.PROVED,
        backend=EnumBackend.Z3,
        backend_status="unsat",
        message="proved",
    )

    interpreted = apply_semantic_lowering_policy(result, _evidence())

    assert interpreted.status is VerificationStatus.PROVED
    assert interpreted.metadata["semantic_lowering"]["permitted_conclusions"] == (
        "universal_proof",
        "existential_witness",
    )


def test_approximate_lowering_downgrades_counterexample_to_unknown() -> None:
    result = VerificationResult(
        status=VerificationStatus.COUNTEREXAMPLE,
        backend=EnumBackend.Z3,
        backend_status="sat",
        message="counterexample",
    )

    interpreted = apply_semantic_lowering_policy(result, _evidence())

    assert interpreted.status is VerificationStatus.UNKNOWN
    assert interpreted.metadata["backend_interpreted_status"] == "counterexample"
    assert (
        interpreted.diagnostics[-1].code == SEMANTIC_LOWERING_CONCLUSION_NOT_PERMITTED
    )
