from __future__ import annotations

from dsl.backends.capabilities import BackendCapabilities
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend
from dsl.semantic.types.enums import EnumDataType


def _requirements(**overrides) -> IR2Requirements:
    values = {
        "requires_boolean_logic": True,
        "requires_numeric_comparisons": True,
        "requires_problem_predicates": False,
        "requires_model_assertions": False,
        "requires_domains": False,
        "requires_neighborhoods": False,
        "normal_form": NormalFormKind.NNF,
        "required_verification_semantics": VerificationSemantics.REFUTATION,
    }
    values.update(overrides)
    return IR2Requirements(**values)


def _capabilities(**overrides) -> BackendCapabilities:
    values = {
        "backend": EnumBackend.Z3,
        "supports_boolean_logic": True,
        "supports_numeric_comparisons": True,
        "supports_problem_predicates": False,
        "supports_model_assertions": True,
        "supports_domains": True,
        "supports_neighborhoods": False,
        "supported_normal_forms": (NormalFormKind.NNF,),
        "supported_verification_semantics": (VerificationSemantics.REFUTATION,),
        "supports_affine_arithmetic": True,
        "supports_nonlinear_arithmetic": False,
        "supports_symbolic_division": False,
        "supported_scalar_sorts": frozenset({EnumDataType.INT, EnumDataType.FLOAT}),
        "supports_finite_set_membership": True,
        "supports_symbolic_categories": False,
        "supports_domain_assumptions": True,
    }
    values.update(overrides)
    return BackendCapabilities(**values)


def test_capabilities_accept_supported_affine_numeric_requirements() -> None:
    requirements = _requirements(
        requires_affine_arithmetic=True,
        required_scalar_sorts=frozenset({EnumDataType.INT, EnumDataType.FLOAT}),
    )
    assert _capabilities().supports(requirements) is True
    assert _capabilities().incompatibilities(requirements) == ()


def test_capabilities_reject_nonlinear_arithmetic() -> None:
    requirements = _requirements(requires_nonlinear_arithmetic=True)
    assert _capabilities().incompatibilities(requirements) == ("nonlinear arithmetic",)


def test_capabilities_reject_symbolic_division() -> None:
    requirements = _requirements(requires_symbolic_division=True)
    assert _capabilities().incompatibilities(requirements) == ("symbolic division",)


def test_capabilities_reject_unsupported_scalar_sort() -> None:
    requirements = _requirements(required_scalar_sorts=frozenset({EnumDataType.STRING}))
    assert _capabilities().incompatibilities(requirements) == ("scalar sorts {string}",)


def test_capabilities_reject_symbolic_finite_set_profile() -> None:
    requirements = _requirements(
        requires_finite_set_membership=True,
        requires_symbolic_categories=True,
        requires_domain_assumptions=True,
    )
    assert _capabilities().incompatibilities(requirements) == ("symbolic categories",)
