from __future__ import annotations

from dsl.backends.capabilities import BackendCapabilities
from dsl.ir.ir2.enums import (
    NormalFormKind,
    VerificationSemantics,
)
from dsl.language.vocabulary.backends import EnumBackend

Z3_CAPABILITIES = BackendCapabilities(
    backend=EnumBackend.Z3,
    supports_boolean_logic=True,
    supports_numeric_comparisons=True,
    supports_problem_predicates=False,
    supports_model_assertions=True,
    # Compatibility field retained during migration.
    supports_quantifiers=False,
    supports_domains=True,
    supports_neighborhoods=False,
    supported_normal_forms=(
        NormalFormKind.NNF,
        NormalFormKind.CNF,
        NormalFormKind.DNF,
    ),
    # Explicit capability contract.
    #
    # The current adapter does not emit z3.ForAll or z3.Exists.
    # A source-level `forall` can nevertheless be executed after IR2 lowers
    # it to a refutation condition: Gamma AND NOT P.
    supports_native_quantifiers=False,
    # The current runner knows how to interpret:
    #   SAT     -> COUNTEREXAMPLE
    #   UNSAT   -> PROVED
    #   UNKNOWN -> UNKNOWN
    #
    # SATISFACTION will be added when witness/no-witness interpretation is
    # implemented by the runner.
    supported_verification_semantics=(
        VerificationSemantics.REFUTATION,
        VerificationSemantics.SATISFACTION,
    ),
)
