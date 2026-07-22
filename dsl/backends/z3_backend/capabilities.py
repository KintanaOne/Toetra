from __future__ import annotations

import z3

from dsl.compatibility.descriptors import (
    BackendProfileDescriptor,
    NumericSemanticDescriptor,
)
from dsl.compatibility.enums import BackendKind
from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.execution import BackendExecutionCapabilities
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
    supports_model_semantic_quantities=True,
    execution_capabilities=BackendExecutionCapabilities(
        supports_timeout=True,
        supports_cancellation=True,
        supports_max_backend_units=True,
        supports_max_memory=True,
        supports_deterministic_seed=True,
        supported_backend_options=None,
    ),
    numeric_profile=BackendProfileDescriptor(
        backend_kind=BackendKind.SMT,
        adapter_id="z3",
        adapter_version=z3.get_version_string(),
        profile_id="smt_real_affine_exact",
        numeric_semantics=NumericSemanticDescriptor.exact_real(),
        supports_non_finite_values=False,
    ),
)
