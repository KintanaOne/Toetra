from __future__ import annotations

from dataclasses import dataclass

from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.requirements import IR2Requirements
from dsl.language.vocabulary.backends import EnumBackend


@dataclass(frozen=True)
class BackendCapabilities:
    """Backend-neutral capability declaration.

    The router compares this object with IR2Requirements. This avoids hard-coded
    checks such as ``if backend == Z3`` inside IR2.
    """

    backend: EnumBackend
    supports_boolean_logic: bool
    supports_numeric_comparisons: bool
    supports_problem_predicates: bool
    supports_model_assertions: bool
    supports_quantifiers: bool
    supports_domains: bool
    supports_neighborhoods: bool
    supported_normal_forms: tuple[NormalFormKind, ...]

    def supports(self, requirements: IR2Requirements) -> bool:
        if requirements.requires_boolean_logic and not self.supports_boolean_logic:
            return False
        if requirements.requires_numeric_comparisons and not self.supports_numeric_comparisons:
            return False
        if requirements.requires_problem_predicates and not self.supports_problem_predicates:
            return False
        if requirements.requires_model_assertions and not self.supports_model_assertions:
            return False
        if requirements.requires_quantifiers and not self.supports_quantifiers:
            return False
        if requirements.requires_domains and not self.supports_domains:
            return False
        if requirements.requires_neighborhoods and not self.supports_neighborhoods:
            return False
        if requirements.normal_form not in self.supported_normal_forms:
            return False
        return True
