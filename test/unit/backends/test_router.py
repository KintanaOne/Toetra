
import pytest

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import BackendNotRegisteredError, NoCompatibleBackendError
from dsl.backends.registry import BackendRegistry
from dsl.backends.router import BackendRouter
from dsl.ir.ir1.nodes import ComparisonIR, ScopeIR
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.nodes import (
    CNFFormulaIR2,
    ClauseIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    TermIR2,
    VerificationTaskIR2,
)
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.language.vocabulary.properties import EnumProperty


def _requirements(
    *,
    quantifiers: bool = False,
    form: NormalFormKind = NormalFormKind.DNF,
) -> IR2Requirements:
    return IR2Requirements(
        requires_boolean_logic=True,
        requires_numeric_comparisons=True,
        requires_problem_predicates=False,
        requires_model_assertions=False,
        requires_quantifiers=quantifiers,
        requires_domains=False,
        requires_neighborhoods=False,
        normal_form=form,
    )


def _scope() -> ScopeIR:
    return ScopeIR(
        kind="pointwise",
        variables={"x0": "point"},
        neighborhood=None,
        domain=None,
    )


def _atom() -> ComparisonIR:
    return ComparisonIR(
        entity="x0",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=1,
    )


def _formula(atom: ComparisonIR, form: NormalFormKind) -> FormulaIR2:
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


def _semantics() -> VerificationSemantics:
    return next(iter(VerificationSemantics))


def _task(
    *,
    backend: EnumBackend | None = EnumBackend.Z3,
    requirements: IR2Requirements,
) -> VerificationTaskIR2:
    atom = _atom()

    return VerificationTaskIR2(
        property_type=EnumProperty.LOGIC,
        scope=_scope(),
        backend=backend,
        assumptions=(),
        spec_formula=NNFFormulaIR2(expression=atom),
        verification_condition=_formula(atom, requirements.normal_form),
        semantics=_semantics(),
        normal_form=requirements.normal_form,
        requirements=requirements,
        metadata={},
    )


def _capabilities(
    *,
    quantifiers: bool = True,
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
        supports_quantifiers=quantifiers,
        supports_domains=True,
        supports_neighborhoods=True,
        supported_normal_forms=forms,
    )


def test_backend_router_routes_requested_backend_when_capabilities_match():
    registry = BackendRegistry()
    registry.register(_capabilities())

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(quantifiers=True),
    )

    route = BackendRouter(registry).route(task)

    assert route.backend == EnumBackend.Z3
    assert route.reason == "requested backend satisfies IR2 requirements"


def test_backend_router_rejects_unregistered_requested_backend():
    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(),
    )

    with pytest.raises(BackendNotRegisteredError):
        BackendRouter(BackendRegistry()).route(task)


def test_backend_router_rejects_backend_without_required_capability():
    registry = BackendRegistry()
    registry.register(_capabilities(quantifiers=False))

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(quantifiers=True),
    )

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)


def test_backend_router_rejects_backend_without_required_normal_form():
    registry = BackendRegistry()
    registry.register(_capabilities(forms=(NormalFormKind.NNF,)))

    task = _task(
        backend=EnumBackend.Z3,
        requirements=_requirements(form=NormalFormKind.DNF),
    )

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)