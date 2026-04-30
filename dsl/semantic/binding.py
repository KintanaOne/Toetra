from dsl.semantic.errors import UnboundVariableError
from dsl.semantic.tracer import ValidationTracer

from dsl.ast.nodes.assertion import (
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import AttributeNode

from dsl.ast.nodes.expressions import (
    AtExprNode,
    CheckAtExprNode,
    PairwiseExprNode,
    QuantifierExprNode,
)


class BindingValidator:
    """
    Resolves variable bindings in RHS expressions.

    Responsibilities:
    - resolve explicit entities (x.a)
    - resolve implicit entities (a <= 1)
    - ensure all variables are declared in scope
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    # ─────────────────────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────────────────────

    def validate(self, scope, rhs):

        context = self._extract_context(scope)

        self.tracer.log(
            f"Binding validation context: {context}"
        )

        self._check_node(rhs, context)

    # ─────────────────────────────────────────────
    # CONTEXT EXTRACTION
    # ─────────────────────────────────────────────

    def _extract_context(self, scope):

        # --------------------------------------------------
        # CHECK_AT
        # --------------------------------------------------

        if isinstance(scope, CheckAtExprNode):

            return {
                "type": "pointwise",
                "variables": {
                    scope.variable: "anchor"
                },
                "default_entity": scope.variable,
            }

        # --------------------------------------------------
        # AT
        # --------------------------------------------------

        if isinstance(scope, AtExprNode):

            return {
                "type": "local",
                "variables": {
                    scope.variable: "anchor"
                },
                "default_entity": scope.variable,
            }

        # --------------------------------------------------
        # PAIRWISE
        # --------------------------------------------------

        if isinstance(scope, PairwiseExprNode):

            left, right = scope.pair.split("~")

            left = left.strip()
            right = right.strip()

            return {
                "type": "pairwise",
                "variables": {
                    left: "anchor",
                    right: "perturbation",
                },
                "default_entity": None,
            }

        # --------------------------------------------------
        # QUANTIFIER
        # --------------------------------------------------

        if isinstance(scope, QuantifierExprNode):

            return {
                "type": "quantifier",
                "variables": {},
                "default_entity": None,
            }

        raise TypeError(
            f"Unsupported scope type: {type(scope)}"
        )

    # ─────────────────────────────────────────────
    # CORE DISPATCH
    # ─────────────────────────────────────────────

    def _check_node(self, node, context):

        variables = context["variables"]
        default_entity = context.get("default_entity")

        # --------------------------------------------------
        # COMPARISON
        # --------------------------------------------------

        if isinstance(node, ComparisonNode):

            self._resolve_attribute(
                node.left,
                variables,
                default_entity
            )

            return

        # --------------------------------------------------
        # PROBLEM NODE
        # --------------------------------------------------

        if isinstance(node, ProblemNode):
            return

        # --------------------------------------------------
        # AND
        # --------------------------------------------------

        if isinstance(node, AndNode):

            for child in node.operands:
                self._check_node(child, context)

            return

        # --------------------------------------------------
        # OR
        # --------------------------------------------------

        if isinstance(node, OrNode):

            for child in node.operands:
                self._check_node(child, context)

            return

        # --------------------------------------------------
        # NOT
        # --------------------------------------------------

        if isinstance(node, NotNode):

            self._check_node(node.operand, context)

            return

        # --------------------------------------------------
        # IMPLICATION
        # --------------------------------------------------

        if isinstance(node, ImplicationNode):

            self._check_node(node.left, context)
            self._check_node(node.right, context)

            return

        raise TypeError(
            f"Unsupported node type: {type(node)}"
        )

    # ─────────────────────────────────────────────
    # ATTRIBUTE RESOLUTION
    # ─────────────────────────────────────────────

    def _resolve_attribute(
        self,
        attr: AttributeNode,
        variables,
        default_entity,
    ):

        # --------------------------------------------------
        # EXPLICIT ENTITY
        # --------------------------------------------------

        if attr.entity is not None:

            if attr.entity not in variables:

                if len(variables) == 1:

                    resolved = next(iter(variables.keys()))

                    self.tracer.log(
                        f"Alias resolution: "
                        f"{attr.entity} → {resolved}"
                    )

                    attr.entity = resolved

                    if attr.path:
                        attr.path[0] = resolved

                else:
                    raise UnboundVariableError(
                        f"Unknown variable '{attr.entity}', "
                        f"expected {list(variables.keys())}"
                    )

            return

        # --------------------------------------------------
        # IMPLICIT ENTITY
        # --------------------------------------------------

        if default_entity is not None:

            attr.entity = default_entity

            return

        if len(variables) == 1:

            attr.entity = next(iter(variables.keys()))

            return

        raise UnboundVariableError(
            f"Ambiguous feature '{attr.feature}' "
            f"with variables {list(variables.keys())}"
        )