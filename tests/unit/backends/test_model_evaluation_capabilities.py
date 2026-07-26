from __future__ import annotations

import pytest

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.errors import NoCompatibleBackendError
from toetra._backends.router import BackendRouter
from toetra._compiler.ir.ir2.run_ir2 import run_ir2


def test_z3_current_profile_accepts_one_model_evaluation() -> None:
    task = run_ir2("""
        model := "linear.joblib"
        target := score

        [BOUND]:
        forall x0 => target[x0] <= 1.0 using Z3
        """)[0]

    route = BackendRouter(create_default_backend_registry()).route(task)

    assert route.capabilities.max_model_evaluations is None


def test_z3_current_profile_accepts_multiple_homogeneous_model_evaluations() -> None:
    task = run_ir2("""
        model := "linear.joblib"
        target := score

        [MONOTONICITY]:
        forall x0, x1 => target[x0] <= target[x1] using Z3
        """)[0]

    route = BackendRouter(create_default_backend_registry()).route(task)

    assert route.capabilities.max_model_evaluations is None


def test_z3_still_rejects_alternating_model_evaluations_before_translation() -> None:
    task = run_ir2("""
        model := "linear.joblib"
        target := score

        [LOGIC]:
        forall x0
        exists x1
        => target[x0] <= target[x1] using Z3
        """)[0]

    with pytest.raises(NoCompatibleBackendError, match="quantifier alternation"):
        BackendRouter(create_default_backend_registry()).route(task)
