from __future__ import annotations

from dataclasses import dataclass

from dsl.ir.ir2.enums import NormalFormKind, VerificationSemantics
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend


@dataclass(frozen=True)
class BackendCapabilities:
    """Backend-neutral capability declaration.

    The router compares these capabilities with ``IR2Requirements``.

    Quantifier distinction
    ----------------------
    ``supports_quantifiers`` is the historical compatibility field.

    ``supports_native_quantifiers`` explicitly means that the backend adapter
    can receive and encode native quantified expressions such as ``ForAll`` or
    ``Exists``.

    A FORML specification may use a quantified scope without requiring native
    backend quantifiers. For example::

        forall x0 => P(x0)

    can be lowered by IR2 to the refutation condition::

        Gamma(x0) AND NOT P(x0)

    In that case, the backend only needs to support refutation semantics.
    """

    backend: EnumBackend
    supports_boolean_logic: bool
    supports_numeric_comparisons: bool
    supports_problem_predicates: bool
    supports_model_assertions: bool

    # Historical compatibility field.
    # It will be removed after all backend declarations and tests migrate to
    # ``supports_native_quantifiers``.
    supports_quantifiers: bool

    supports_domains: bool
    supports_neighborhoods: bool
    supported_normal_forms: tuple[NormalFormKind, ...]

    # New explicit backend contracts.
    supports_native_quantifiers: bool = False
    supported_verification_semantics: tuple[VerificationSemantics, ...] = (
        VerificationSemantics.REFUTATION,
    )

    def supports(self, requirements: IR2Requirements) -> bool:
        if requirements.requires_boolean_logic and not self.supports_boolean_logic:
            return False

        if (
            requirements.requires_numeric_comparisons
            and not self.supports_numeric_comparisons
        ):
            return False

        if (
            requirements.requires_problem_predicates
            and not self.supports_problem_predicates
        ):
            return False

        if (
            requirements.requires_model_assertions
            and not self.supports_model_assertions
        ):
            return False

        # The requirement contract is now explicit: only a representation that
        # actually reaches the backend with native quantifiers requires this
        # capability.
        #
        # The historical backend field remains temporarily accepted until all
        # backend declarations have migrated.
        supports_native_quantifiers = (
            self.supports_native_quantifiers or self.supports_quantifiers
        )

        if requirements.requires_native_quantifiers and not supports_native_quantifiers:
            return False

        if (
            requirements.required_verification_semantics
            not in self.supported_verification_semantics
        ):
            return False

        if requirements.requires_domains and not self.supports_domains:
            return False

        if requirements.requires_neighborhoods and not self.supports_neighborhoods:
            return False

        if requirements.normal_form not in self.supported_normal_forms:
            return False

        return True
