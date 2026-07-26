from __future__ import annotations

import pytest

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.errors import (
    NoCompatibleBackendError,
    UnsupportedBackendRequirementsError,
)
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.runner import VerificationStatus, Z3Runner
from toetra._backends.z3_backend.translator import Z3Translator
from tests.support.backend_tasks import build_task


def test_be_qp_001_homogeneous_universal_chain_executes_by_refutation() -> None:
    task = build_task("""
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
        """)

    route = BackendRouter(create_default_backend_registry()).route(task)
    result = Z3Runner().run(task)

    assert route.capabilities.max_model_evaluations is None
    assert result.status is VerificationStatus.PROVED
    assert result.solver_status == "unsat"


def test_be_qp_002_homogeneous_existential_chain_executes_by_witness() -> None:
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
    assert result.solver_status == "sat"
    assert result.model is not None


def test_be_qp_003_alternating_chain_is_rejected_before_solver_translation() -> None:
    task = build_task("""
        model := "linear.joblib"
        target := score

        [LOGIC]:
        forall x0
        exists x1
        with domain(
            x0.a: [0.0, 3.0],
            x1.a: [0.0, 3.0]
        )
        => target[x1] >= target[x0] using Z3
        """)

    with pytest.raises(NoCompatibleBackendError, match="quantifier alternation"):
        BackendRouter(create_default_backend_registry()).route(task)

    with pytest.raises(
        UnsupportedBackendRequirementsError,
        match="quantifier alternation",
    ):
        Z3Translator().translate(task)
