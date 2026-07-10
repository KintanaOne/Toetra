from __future__ import annotations

from dsl.backends.capabilities import BackendCapabilities
from dsl.ir.ir2.enums import NormalFormKind
from dsl.language.vocabulary.backends import EnumBackend

Z3_CAPABILITIES = BackendCapabilities(
    backend=EnumBackend.Z3,
    supports_boolean_logic=True,
    supports_numeric_comparisons=True,
    supports_problem_predicates=False,
    supports_model_assertions=True,
    supports_quantifiers=False,
    supports_domains=True,
    supports_neighborhoods=False,
    supported_normal_forms=(
        NormalFormKind.NNF,
        NormalFormKind.CNF,
        NormalFormKind.DNF,
    ),
)
