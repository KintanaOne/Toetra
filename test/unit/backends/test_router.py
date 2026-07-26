from __future__ import annotations

import pytest

from toetra._backends.capabilities import BackendCapabilities
from toetra._backends.execution import BackendExecutionCapabilities
from toetra._backends.errors import (
    BackendNotRegisteredError,
    NoCompatibleBackendError,
)
from toetra._backends.registry import BackendRegistry
from toetra._backends.router import BackendRouter
from toetra._compiler.ir.ir1.nodes import (
    AttributeExpressionIR,
    ComparisonIR,
    ConstantExpressionIR,
    ScopeIR,
)
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.nodes import (
    CNFFormulaIR2,
    ClauseIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    TermIR2,
    VerificationTaskIR2,
)
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._language.vocabulary.properties import EnumProperty
from toetra._compiler.semantic.types.enums import EnumDataType


def _requirements(
    *,
    uses_quantified_scope: bool = False,
    requires_native_quantifiers: bool = False,
    semantics: VerificationSemantics = VerificationSemantics.REFUTATION,
    form: NormalFormKind = NormalFormKind.DNF,
) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=False,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=form,
        uses_quantified_scope=uses_quantified_scope,
        requires_native_quantifiers=requires_native_quantifiers,
        required_verification_semantics=semantics,
    )


def _scope(*, quantified: bool = False) -> ScopeIR:
    if quantified:
        return ScopeIR(
            kind="quantifier",
            variables={"x0": "symbolic"},
            neighborhood=None,
            domain=None,
        )

    return ScopeIR(
        kind="pointwise",
        variables={"x0": "point"},
        neighborhood=None,
        domain=None,
    )


def _atom() -> ComparisonIR:
    return ComparisonIR(
        left=AttributeExpressionIR(entity="x0", feature="a"),
        op=EnumComparisonOperator.LTE,
        right=ConstantExpressionIR(value=1, dtype=EnumDataType.INT),
    )


def _formula(
    atom: ComparisonIR,
    form: NormalFormKind,
) -> FormulaIR2:
    literal = LiteralIR2(atom=atom)

    if form is NormalFormKind.NNF:
        return NNFFormulaIR2(expression=atom)

    if form is NormalFormKind.CNF:
        return CNFFormulaIR2(
            clauses=(
                ClauseIR2(
                    literals=(literal,),
                ),
            ),
        )

    if form is NormalFormKind.DNF:
        return DNFFormulaIR2(
            terms=(
                TermIR2(
                    literals=(literal,),
                ),
            ),
        )

    raise ValueError(f"Unsupported normal form in test fixture: {form}")


def _task(
    *,
    backend: EnumBackend | None = EnumBackend.Z3,
    requirements: IR2Requirements,
) -> VerificationTaskIR2:
    atom = _atom()

    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_scope(
            quantified=requirements.uses_quantified_scope,
        ),
        backend=backend,
        assumptions=(),
        spec_formula=NNFFormulaIR2(expression=atom),
        verification_condition=_formula(
            atom,
            requirements.normal_form,
        ),
        semantics=requirements.required_verification_semantics,
        normal_form=requirements.normal_form,
        requirements=requirements,
        metadata={},
    )


def _capabilities(
    *,
    supports_native_quantifiers: bool = False,
    supported_semantics: tuple[VerificationSemantics, ...] = (
        VerificationSemantics.REFUTATION,
    ),
    forms: tuple[NormalFormKind, ...] = (
        NormalFormKind.NNF,
        NormalFormKind.CNF,
        NormalFormKind.DNF,
    ),
) -> BackendCapabilities:
    return BackendCapabilities(
        backend=EnumBackend.Z3,
        supports_boolean_logic=True,
        supports_numeric_comparisons=True,
        supports_problem_predicates=True,
        supports_model_assertions=True,
        supports_domains=True,
        supports_neighborhoods=True,
        supported_normal_forms=forms,
        supports_native_quantifiers=supports_native_quantifiers,
        supported_verification_semantics=supported_semantics,
        execution_capabilities=BackendExecutionCapabilities(supports_timeout=True),
    )


def test_backend_router_routes_requested_backend_when_capabilities_match():
    registry = BackendRegistry()
    registry.register(_capabilities())

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(),
    )

    route = BackendRouter(registry).route(task)

    assert route.backend is EnumBackend.Z3
    assert route.reason == "requested backend satisfies IR2 requirements"


def test_backend_router_accepts_lowered_forall_without_native_quantifiers():
    registry = BackendRegistry()
    registry.register(
        _capabilities(
            supports_native_quantifiers=False,
            supported_semantics=(VerificationSemantics.REFUTATION,),
        )
    )

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(
            uses_quantified_scope=True,
            requires_native_quantifiers=False,
            semantics=VerificationSemantics.REFUTATION,
        ),
    )

    route = BackendRouter(registry).route(task)

    assert task.scope.kind == "quantifier"
    assert task.requirements.uses_quantified_scope is True

    assert task.requirements.requires_native_quantifiers is False

    assert (
        task.requirements.required_verification_semantics
        is VerificationSemantics.REFUTATION
    )

    assert route.backend is EnumBackend.Z3


def test_backend_router_rejects_unregistered_requested_backend():
    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(),
    )

    with pytest.raises(BackendNotRegisteredError):
        BackendRouter(BackendRegistry()).route(task)


def test_backend_router_rejects_missing_native_quantifier_capability():
    registry = BackendRegistry()
    registry.register(
        _capabilities(
            supports_native_quantifiers=False,
        )
    )

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(
            uses_quantified_scope=True,
            requires_native_quantifiers=True,
        ),
    )

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)


def test_backend_router_accepts_native_quantifiers_when_supported():
    registry = BackendRegistry()
    registry.register(
        _capabilities(
            supports_native_quantifiers=True,
        )
    )

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(
            uses_quantified_scope=True,
            requires_native_quantifiers=True,
        ),
    )

    route = BackendRouter(registry).route(task)

    assert route.backend is EnumBackend.Z3


def test_backend_router_rejects_unsupported_verification_semantics():
    registry = BackendRegistry()
    registry.register(
        _capabilities(
            supported_semantics=(VerificationSemantics.REFUTATION,),
        )
    )

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(
            semantics=VerificationSemantics.SATISFACTION,
        ),
    )

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)


def test_backend_router_rejects_backend_without_required_normal_form():
    registry = BackendRegistry()
    registry.register(
        _capabilities(
            forms=(NormalFormKind.NNF,),
        )
    )

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(
            form=NormalFormKind.DNF,
        ),
    )

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)


def test_backend_router_rejects_execution_controls_the_backend_cannot_enforce():
    from dataclasses import replace

    from toetra._backends.execution import (
        BackendCancellationToken,
        BackendExecutionCapabilities,
        BackendExecutionPolicy,
    )

    registry = BackendRegistry()
    registry.register(
        replace(
            _capabilities(),
            execution_capabilities=BackendExecutionCapabilities(
                supports_timeout=True,
                supports_cancellation=False,
            ),
        )
    )

    with pytest.raises(
        NoCompatibleBackendError, match="execution policy: cancellation"
    ):
        BackendRouter(registry).route(
            _task(requirements=_requirements()),
            execution_policy=BackendExecutionPolicy(
                cancellation_token=BackendCancellationToken()
            ),
        )


def test_backend_router_accepts_a_backend_neutral_execution_policy():
    from dataclasses import replace

    from toetra._backends.execution import (
        BackendCancellationToken,
        BackendExecutionCapabilities,
        BackendExecutionPolicy,
        BackendResourceLimits,
    )

    registry = BackendRegistry()
    registry.register(
        replace(
            _capabilities(),
            execution_capabilities=BackendExecutionCapabilities(
                supports_timeout=True,
                supports_cancellation=True,
                supports_max_backend_units=True,
                supports_max_memory=True,
                supports_deterministic_seed=True,
                supported_backend_options=None,
            ),
        )
    )

    route = BackendRouter(registry).route(
        _task(requirements=_requirements()),
        execution_policy=BackendExecutionPolicy(
            timeout_ms=1_000,
            resources=BackendResourceLimits(
                max_backend_units=100,
                max_memory_mb=64,
            ),
            deterministic_seed=3,
            cancellation_token=BackendCancellationToken(),
            backend_options={"adapter_specific": True},
        ),
    )

    assert route.backend is EnumBackend.Z3
