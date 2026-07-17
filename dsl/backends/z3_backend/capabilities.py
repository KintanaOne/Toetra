from __future__ import annotations

from dsl.backends.capabilities import BackendCapabilities
from dsl.ir.ir2.enums import (
    NormalFormKind,
    VerificationSemantics,
)
from dsl.language.vocabulary.backends import EnumBackend
from dsl.semantic.types.enums import EnumDataType

Z3_CAPABILITIES = BackendCapabilities(
    backend=EnumBackend.Z3,
    supports_boolean_logic=True,
    supports_numeric_comparisons=True,
    supports_problem_predicates=False,
    supports_model_assertions=True,
    supports_domains=True,
    supports_neighborhoods=False,
    supported_normal_forms=(
        NormalFormKind.NNF,
        NormalFormKind.CNF,
        NormalFormKind.DNF,
    ),
    supports_native_quantifiers=False,
    supported_verification_semantics=(
        VerificationSemantics.REFUTATION,
        VerificationSemantics.SATISFACTION,
    ),
    supports_affine_arithmetic=True,
    supports_nonlinear_arithmetic=False,
    supports_symbolic_division=False,
    supported_scalar_sorts=frozenset(
        {
            EnumDataType.INT,
            EnumDataType.FLOAT,
        }
    ),
    supports_finite_set_membership=True,
    supports_symbolic_categories=False,
    supports_domain_assumptions=True,
    max_model_evaluations=None,
)
