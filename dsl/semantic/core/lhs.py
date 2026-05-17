from dsl.semantic.context.context import SemanticContext
from dsl.semantic.context.scope import SemanticScope
from dsl.semantic.errors.errors import InvalidPropertyError
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.ast.nodes.expressions import (
    CheckAtExprNode,
    AtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)

from dsl.semantic.symbols.table import Symbol

class LHSValidator:
    """
    LHSValidator is responsible for validating the LEFT-HAND SIDE (LHS)
    of an implication and producing a semantic context.

    This context is later used by:
    - BindingValidator (variable resolution)
    - LogicValidator (semantic correctness)

    The LHS defines:
    - which variables exist
    - their semantic role (anchor, perturbation, symbolic, etc.)
    - the default entity used for implicit feature access (e.g., `a <= 1`)
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, lhs):
        self.tracer.log(f"Validating LHS: {lhs}")

        if isinstance(lhs, CheckAtExprNode):
            return self._validate_check_at(lhs)

        if isinstance(lhs, AtExprNode):
            return self._validate_at(lhs)

        if isinstance(lhs, PairwiseExprNode):
            return self._validate_pairwise(lhs)

        if isinstance(lhs, QuantifierExprNode):
            return self._validate_quantifier(lhs)

        else:
            raise InvalidPropertyError(f"Unknown LHS type: {type(lhs)}")

    # ─────────────────────────────
    # CHECK_AT (point evaluation)
    # ─────────────────────────────

    def _validate_check_at(self, lhs):
        """
        Example:
            check_at x0 => ...

        Semantics:
            Evaluate the property at a single concrete point.
        """

        self.tracer.log(f"Validating CheckAtExprNode: {lhs}")

        if not lhs.variable:
            raise InvalidPropertyError("Missing variable in check_at")

        context = SemanticContext(
            type=SemanticScope.POINTWISE,
            variables={
                lhs.variable: "anchor"
            },
            default_entity=lhs.variable
        )

        # ---------------------------------------------
        # Register semantic symbol
        # ---------------------------------------------

        context.symbol_table.register(
            Symbol(
                name=lhs.variable,
                kind="anchor",
            )
        )

        return context

    # ─────────────────────────────
    # AT (local neighborhood)
    # ─────────────────────────────

    def _validate_at(self, lhs):
        """
        Example:
            at x => ...

        Semantics:
            x is the anchor point
            x' is implicitly introduced as a perturbation

        Implicit rule:
            a <= 1  →  x'.a <= 1
        """

        self.tracer.log(f"Validating AtExprNode: {lhs}")

        if not lhs.variable:
            raise InvalidPropertyError("Missing variable in at")

        x = lhs.variable
        x_prime = f"{x}'"

        context = SemanticContext(
            type=SemanticScope.LOCAL,
            variables={
                x: "anchor",
                x_prime: "perturbation"
            },
            default_entity=x_prime,
            domain=lhs.domain,
            neighborhood=lhs.neighborhood
        )

        # ---------------------------------------------
        # Register semantic symbols
        # ---------------------------------------------

        context.symbol_table.register(
            Symbol(
                name=x,
                kind="anchor",
            )
        )

        context.symbol_table.register(
            Symbol(
                name=x_prime,
                kind="perturbation",
            )
        )

        return context

    # ─────────────────────────────
    # PAIRWISE (x ~ x')
    # ─────────────────────────────

    def _validate_pairwise(self, lhs):
        """
        Example:
            x ~ x' => ...

        Semantics:
            x is a fixed anchor
            x' is a perturbation sampled from a neighborhood of x

        Implicit rule:
            a <= 1  →  x'.a <= 1
        """

        self.tracer.log(f"Validating PairwiseExprNode: {lhs}")

        if not lhs.pair:
            raise InvalidPropertyError("Pairwise requires a pair")

        try:
            left, right = [v.strip() for v in lhs.pair.split("~")]
        except Exception:
            raise InvalidPropertyError(
                f"Invalid pair format '{lhs.pair}', expected 'x ~ x\\''"
            )

        if not left or not right:
            raise InvalidPropertyError("Pairwise requires two variables")

        if not right.endswith("'"):
            raise InvalidPropertyError(
                f"Right variable '{right}' must be a primed version of '{left}'"
            )

        if right[:-1] != left:
            raise InvalidPropertyError(
                f"Invalid pair '{lhs.pair}': expected '{left} ~ {left}\\''"
            )

        context = SemanticContext(
            type=SemanticScope.PAIRWISE,
            variables={
                left: "anchor",
                right: "perturbation"
            },
            default_entity=right,
            domain=lhs.domain,
            neighborhood=lhs.neighborhood
        )

        # ---------------------------------------------
        # Register semantic symbols
        # ---------------------------------------------

        context.symbol_table.register(
            Symbol(
                name=left,
                kind="anchor",
            )
        )

        context.symbol_table.register(
            Symbol(
                name=right,
                kind="perturbation",
            )
        )

        return context

    # ─────────────────────────────
    # QUANTIFIER (forall / exists)
    # ─────────────────────────────

    def _validate_quantifier(self, lhs):
        """
        Example:
            forall => ...
            exists => ...

        Semantics:
            Introduces a symbolic variable implicitly.

        Convention:
            Internal variable name = _x

        Implicit rule:
            a <= 1 → _x.a <= 1
        """

        self.tracer.log(f"Validating QuantifierExprNode: {lhs}")

        if not lhs.quantifier:
            raise InvalidPropertyError("Missing quantifier")

        quantifier = lhs.quantifier.strip()

        if quantifier not in {"forall", "exists"}:
            raise InvalidPropertyError(
                f"Unknown quantifier '{quantifier}'"
            )

        var = "_x"

        context = SemanticContext(
            type=SemanticScope.QUANTIFIER,
            quantifier=quantifier,
            variables={
                var: "symbolic"
            },
            default_entity=var,
            domain=lhs.domain
        )

        # ---------------------------------------------
        # Register semantic symbol
        # ---------------------------------------------

        context.symbol_table.register(
            Symbol(
                name=var,
                kind="symbolic",
            )
        )

        return context