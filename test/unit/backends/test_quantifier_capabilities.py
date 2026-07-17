from __future__ import annotations

import pytest

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import NoCompatibleBackendError
from dsl.backends.registry import BackendRegistry
from dsl.backends.router import BackendRouter
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.run_ir2 import run_ir2
from dsl.language.vocabulary.backends import EnumBackend
from dsl.semantic.types.enums import EnumDataType


def _alternating_task():
    return run_ir2(
        """
        model := "credit_risk.joblib"
        target := RiskScore

        [LOGIC]:
        forall original
        exists counterfactual
        => target[counterfactual] <= target[original]
        """,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )[0]


def _capabilities(*, native: bool, alternation: bool) -> BackendCapabilities:
    return BackendCapabilities(
        backend=EnumBackend.Z3,
        supports_boolean_logic=True,
        supports_numeric_comparisons=True,
        supports_problem_predicates=True,
        supports_model_assertions=True,
        supports_domains=True,
        supports_neighborhoods=True,
        supported_normal_forms=(NormalFormKind.NNF,),
        supports_native_quantifiers=native,
        supports_quantifier_alternation=alternation,
        supported_verification_semantics=(
            VerificationSemantics.REFUTATION,
            VerificationSemantics.SATISFACTION,
        ),
        supports_affine_arithmetic=True,
        supported_scalar_sorts=frozenset(
            {EnumDataType.INT, EnumDataType.FLOAT, EnumDataType.BOOL}
        ),
        supports_domain_assumptions=True,
    )


def test_alternating_chain_is_rejected_before_backend_translation() -> None:
    registry = BackendRegistry()
    registry.register(_capabilities(native=False, alternation=False))
    with pytest.raises(NoCompatibleBackendError, match="quantifier alternation"):
        BackendRouter(registry).route(_alternating_task())


def test_alternating_chain_requires_both_native_and_alternation_support() -> None:
    registry = BackendRegistry()
    registry.register(_capabilities(native=True, alternation=False))
    with pytest.raises(NoCompatibleBackendError, match="quantifier alternation"):
        BackendRouter(registry).route(_alternating_task())


def test_alternating_chain_routes_when_advanced_profile_is_declared() -> None:
    registry = BackendRegistry()
    registry.register(_capabilities(native=True, alternation=True))
    assert BackendRouter(registry).route(_alternating_task()).backend is EnumBackend.Z3
