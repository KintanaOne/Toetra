from dsl.semantic.errors.errors import InvalidPropertyError
from dsl.semantic.core.problem import ProblemValidator
from dsl.semantic.runtime.tracer import ValidationTracer

from dsl.ast.nodes.assertion import (
    ComparisonNode,
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ProblemNode,
)

from dsl.ast.nodes.primitives import (
    AttributeNode,
    ConstantNode,
)


class LogicValidator:
    """
    Validates logical expressions AFTER:
        - parsing
        - binding

    Responsibilities:
        - structural correctness
        - recursive validation
        - leaf validation
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    # ─────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────

    def validate(self, node, context):

        self.tracer.log(f"Validating logic node: {node}")

        if isinstance(node, ComparisonNode):
            return self._validate_comparison(node, context)

        if isinstance(node, AndNode):
            return self._validate_and(node, context)

        if isinstance(node, OrNode):
            return self._validate_or(node, context)

        if isinstance(node, NotNode):
            return self._validate_not(node, context)

        if isinstance(node, ImplicationNode):
            return self._validate_implication(node, context)

        if isinstance(node, ProblemNode):
            return self._validate_problem(node, context)

        raise InvalidPropertyError(f"Unknown logical node type: {type(node)}")

    # ─────────────────────────────
    # COMPARISON
    # ─────────────────────────────

    def _validate_comparison(self, node, context):

        self.tracer.log(f"Validating ComparisonNode: {node}")

        if node.left is None or node.right is None:

            raise InvalidPropertyError("Invalid comparison: missing operands")

        self._validate_operand(node.left, context)
        self._validate_operand(node.right, context)

    # ─────────────────────────────
    # AND
    # ─────────────────────────────

    def _validate_and(self, node, context):

        self.tracer.log(f"Validating AndNode: {node}")

        if not node.operands:

            raise InvalidPropertyError("AND node has no operands")

        for op in node.operands:
            self.validate(op, context)

    # ─────────────────────────────
    # OR
    # ─────────────────────────────

    def _validate_or(self, node, context):

        self.tracer.log(f"Validating OrNode: {node}")

        if not node.operands:

            raise InvalidPropertyError("OR node has no operands")

        for op in node.operands:
            self.validate(op, context)

    # ─────────────────────────────
    # NOT
    # ─────────────────────────────

    def _validate_not(self, node, context):

        self.tracer.log(f"Validating NotNode: {node}")

        if node.operand is None:

            raise InvalidPropertyError("NOT expression missing operand")

        self.validate(node.operand, context)

    # ─────────────────────────────
    # IMPLICATION
    # ─────────────────────────────

    def _validate_implication(self, node, context):

        self.tracer.log(f"Validating ImplicationNode: {node}")

        if node.left is None or node.right is None:

            raise InvalidPropertyError("Implication missing left or right operand")

        self.validate(node.left, context)
        self.validate(node.right, context)

    # ─────────────────────────────
    # PROBLEM
    # ─────────────────────────────

    def _validate_problem(self, node, context):

        self.tracer.log(f"Validating ProblemNode: {node}")

        ProblemValidator(tracer=self.tracer).validate(node)

    # ─────────────────────────────
    # OPERANDS (LEAVES)
    # ─────────────────────────────

    def _validate_operand(self, node, context):
        """
        Leaf validation only.

        Binding has already been performed upstream.
        """

        if isinstance(node, AttributeNode):
            return self._validate_attribute(node, context)

        if isinstance(node, ConstantNode):
            return

        raise InvalidPropertyError(f"Invalid operand type: {type(node)}")

    # ─────────────────────────────
    # ATTRIBUTE
    # ─────────────────────────────

    def _validate_attribute(self, node, context):

        self.tracer.log(f"Validating AttributeNode: {node}")

        if not node.feature:
            raise InvalidPropertyError("Attribute missing feature name")

        if node.semantic is None:
            raise InvalidPropertyError(
                f"Attribute '{node.feature}' has no semantic annotations"
            )

        semantic = node.semantic

        if not semantic.resolved_entity:
            raise InvalidPropertyError(
                f"Unresolved attribute '{node.feature}' (binding failed)"
            )
