from types import SimpleNamespace

import pytest

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import BackendNotRegisteredError, NoCompatibleBackendError
from dsl.backends.registry import BackendRegistry
from dsl.backends.router import BackendRouter
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend


def _requirements(*, quantifiers: bool = False, form: NormalFormKind = NormalFormKind.DNF) -> IR2Requirements:
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


def _capabilities(*, quantifiers: bool = True, forms=(NormalFormKind.NNF, NormalFormKind.CNF, NormalFormKind.DNF)):
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
    task = SimpleNamespace(backend=EnumBackend.Z3, requirements=_requirements(quantifiers=True))

    route = BackendRouter(registry).route(task)

    assert route.backend == EnumBackend.Z3
    assert route.reason == "requested backend satisfies IR2 requirements"


def test_backend_router_rejects_unregistered_requested_backend():
    task = SimpleNamespace(backend=EnumBackend.Z3, requirements=_requirements())

    with pytest.raises(BackendNotRegisteredError):
        BackendRouter(BackendRegistry()).route(task)


def test_backend_router_rejects_backend_without_required_capability():
    registry = BackendRegistry()
    registry.register(_capabilities(quantifiers=False))
    task = SimpleNamespace(backend=EnumBackend.Z3, requirements=_requirements(quantifiers=True))

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)


def test_backend_router_rejects_backend_without_required_normal_form():
    registry = BackendRegistry()
    registry.register(_capabilities(forms=(NormalFormKind.NNF,)))
    task = SimpleNamespace(backend=EnumBackend.Z3, requirements=_requirements(form=NormalFormKind.DNF))

    with pytest.raises(NoCompatibleBackendError):
        BackendRouter(registry).route(task)
