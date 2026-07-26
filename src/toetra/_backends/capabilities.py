from __future__ import annotations

from dataclasses import dataclass

from toetra._compatibility.descriptors import BackendProfileDescriptor
from toetra._backends.execution import BackendExecutionCapabilities
from toetra._compiler.ir.ir2.enums import NormalFormKind, VerificationSemantics
from toetra._compiler.ir.ir2.requirements import IR2Requirements
from toetra._language.vocabulary.backends import EnumBackend
from toetra._compiler.semantic.types.enums import EnumDataType


@dataclass(frozen=True)
class BackendCapabilities:
    """Backend-neutral capability declaration.

    The router compares these capabilities with :class:`IR2Requirements`.
    Coarse historical flags remain available, while scalar-expression fields
    make arithmetic and domain support explicit.

    Quantifier distinction
    ----------------------
    ``supports_native_quantifiers`` means that the backend adapter can receive
    native quantified expressions. A quantified Toetra scope can still be
    lowered to a quantifier-free refutation or witness condition, in which case
    this capability is not required.
    """

    backend: EnumBackend
    supports_boolean_logic: bool
    supports_numeric_comparisons: bool
    supports_problem_predicates: bool
    supports_model_assertions: bool
    supports_domains: bool
    supports_neighborhoods: bool
    supported_normal_forms: tuple[NormalFormKind, ...]

    supports_native_quantifiers: bool = False
    supports_quantifier_alternation: bool = False
    supported_verification_semantics: tuple[VerificationSemantics, ...] = (
        VerificationSemantics.REFUTATION,
    )

    supports_affine_arithmetic: bool = False
    supports_nonlinear_arithmetic: bool = False
    supports_symbolic_division: bool = False
    supported_scalar_sorts: frozenset[EnumDataType] = frozenset()
    supports_finite_set_membership: bool = False
    supports_symbolic_categories: bool = False
    supports_domain_assumptions: bool = False
    max_model_evaluations: int | None = None
    supports_model_semantic_quantities: bool = False
    numeric_profile: BackendProfileDescriptor | None = None
    execution_capabilities: BackendExecutionCapabilities = (
        BackendExecutionCapabilities()
    )

    def supports(self, requirements: IR2Requirements) -> bool:
        """Return whether all requirements are satisfied."""
        return not self.incompatibilities(requirements)

    def incompatibilities(self, requirements: IR2Requirements) -> tuple[str, ...]:
        """Describe every unsupported requirement in deterministic order."""
        reasons: list[str] = []

        if requirements.requires_boolean_logic and not self.supports_boolean_logic:
            reasons.append("boolean logic")

        if (
            requirements.requires_numeric_comparisons
            and not self.supports_numeric_comparisons
        ):
            reasons.append("numeric comparisons")

        if (
            requirements.requires_problem_predicates
            and not self.supports_problem_predicates
        ):
            reasons.append("problem predicates")

        if (
            requirements.requires_model_assertions
            and not self.supports_model_assertions
        ):
            reasons.append("model assertions")

        if (
            requirements.requires_model_semantic_quantities
            and not self.supports_model_semantic_quantities
        ):
            reasons.append("model semantic quantities")

        if (
            self.max_model_evaluations is not None
            and requirements.model_evaluation_count > self.max_model_evaluations
        ):
            reasons.append(
                "model evaluations "
                f"{requirements.model_evaluation_count} exceed backend maximum "
                f"{self.max_model_evaluations}"
            )

        if (
            requirements.requires_native_quantifiers
            and not self.supports_native_quantifiers
        ):
            reasons.append("native quantifiers")

        if (
            requirements.requires_quantifier_alternation
            and not self.supports_quantifier_alternation
        ):
            reasons.append("quantifier alternation")

        if (
            requirements.required_verification_semantics
            not in self.supported_verification_semantics
        ):
            reasons.append(
                "verification semantics "
                f"'{requirements.required_verification_semantics.value}'"
            )

        if requirements.requires_domains and not self.supports_domains:
            reasons.append("domains")

        if requirements.requires_neighborhoods and not self.supports_neighborhoods:
            reasons.append("neighborhoods")

        if requirements.normal_form not in self.supported_normal_forms:
            reasons.append(f"normal form '{requirements.normal_form.value}'")

        if (
            requirements.requires_affine_arithmetic
            and not self.supports_affine_arithmetic
        ):
            reasons.append("affine arithmetic")

        if (
            requirements.requires_nonlinear_arithmetic
            and not self.supports_nonlinear_arithmetic
        ):
            reasons.append("nonlinear arithmetic")

        if (
            requirements.requires_symbolic_division
            and not self.supports_symbolic_division
        ):
            reasons.append("symbolic division")

        unsupported_sorts = (
            requirements.required_scalar_sorts - self.supported_scalar_sorts
        )
        if unsupported_sorts:
            labels = ", ".join(sorted(dtype.value for dtype in unsupported_sorts))
            reasons.append(f"scalar sorts {{{labels}}}")

        if (
            requirements.requires_finite_set_membership
            and not self.supports_finite_set_membership
        ):
            reasons.append("finite-set membership")

        if (
            requirements.requires_symbolic_categories
            and not self.supports_symbolic_categories
        ):
            reasons.append("symbolic categories")

        if (
            requirements.requires_domain_assumptions
            and not self.supports_domain_assumptions
        ):
            reasons.append("domain assumptions")

        return tuple(reasons)
