from __future__ import annotations

from toetra._backends.results import VerificationResult, VerificationStatus
from toetra._backends.z3_backend.runner import Z3VerificationResult
from toetra._language.vocabulary.backends import EnumBackend


def test_generic_verification_result_exposes_backend_neutral_fields() -> None:
    result = VerificationResult(
        status=VerificationStatus.WITNESS,
        backend=EnumBackend.Z3,
        backend_status="sat",
        assignments={"x.a": 2},
        message="witness",
    )

    assert result.backend is EnumBackend.Z3
    assert result.backend_status == "sat"
    assert result.assignments == {"x.a": 2}
    assert result.has_assignments is True


def test_generic_result_preserves_historical_solver_aliases() -> None:
    result = VerificationResult(
        status=VerificationStatus.PROVED,
        backend=EnumBackend.Z3,
        backend_status="unsat",
    )

    assert result.solver_status == "unsat"
    assert result.model is None
    assert result.has_assignments is False


def test_z3_result_is_a_generic_verification_result() -> None:
    result = Z3VerificationResult(
        status=VerificationStatus.COUNTEREXAMPLE,
        solver_status="sat",
        model={"x.a": "3"},
        message="counterexample",
    )

    assert isinstance(result, VerificationResult)
    assert result.backend is EnumBackend.Z3
    assert result.backend_status == "sat"
    assert result.assignments == {"x.a": "3"}
    assert result.solver_status == "sat"
    assert result.model == {"x.a": "3"}
