from dsl.semantic.errors import InvalidPropertyError
from dsl.semantic.tracer import ValidationTracer


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

        node_type = lhs.__class__.__name__

        if node_type == "CheckAtExprNode":
            return self._validate_check_at(lhs)

        elif node_type == "AtExprNode":
            return self._validate_at(lhs)

        elif node_type == "PairwiseExprNode":
            return self._validate_pairwise(lhs)

        elif node_type == "QuantifierExprNode":
            return self._validate_quantifier(lhs)

        else:
            raise InvalidPropertyError(f"Unknown LHS type: {node_type}")

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

        return {
            "type": "pointwise",
            "variables": {
                lhs.variable: "anchor"
            },
            "default_entity": lhs.variable
        }

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

        return {
            "type": "local",
            "variables": {
                x: "anchor",
                x_prime: "perturbation"
            },
            "default_entity": x_prime,  # 🔥 implicit resolution goes to x'
            "domain": lhs.domain,
            "neighborhood": lhs.neighborhood
        }

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

        return {
            "type": "pairwise",
            "variables": {
                left: "anchor",
                right: "perturbation"
            },
            "default_entity": right,  # 🔥 implicit resolution goes to x'
            "domain": lhs.domain,
            "neighborhood": lhs.neighborhood
        }

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

        return {
            "type": "quantifier",
            "quantifier": quantifier,
            "variables": {
                var: "symbolic"
            },
            "default_entity": var,
            "domain": lhs.domain
        }