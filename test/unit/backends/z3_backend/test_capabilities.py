from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES
from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.semantic.types.enums import EnumDataType


def test_z3_declares_numeric_affine_profile() -> None:
    assert Z3_CAPABILITIES.supports_numeric_comparisons is True
    assert Z3_CAPABILITIES.supports_affine_arithmetic is True
    assert Z3_CAPABILITIES.supports_nonlinear_arithmetic is False
    assert Z3_CAPABILITIES.supports_symbolic_division is False
    assert Z3_CAPABILITIES.supported_scalar_sorts == frozenset(
        {EnumDataType.INT, EnumDataType.FLOAT}
    )


def test_z3_declares_domain_profile() -> None:
    assert Z3_CAPABILITIES.supports_domains is True
    assert Z3_CAPABILITIES.supports_domain_assumptions is True
    assert Z3_CAPABILITIES.supports_finite_set_membership is True
    assert Z3_CAPABILITIES.supports_symbolic_categories is False


def test_z3_keeps_existing_normal_forms_and_semantics() -> None:
    assert Z3_CAPABILITIES.supported_normal_forms == (
        NormalFormKind.NNF,
        NormalFormKind.CNF,
        NormalFormKind.DNF,
    )
    assert Z3_CAPABILITIES.supported_verification_semantics == (
        VerificationSemantics.REFUTATION,
        VerificationSemantics.SATISFACTION,
    )
