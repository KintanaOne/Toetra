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
    TargetRefNode,
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

    def __init__(self, tracer=None, model_schema=None):
        self.tracer = tracer or ValidationTracer()
        self.model_schema = model_schema

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

        if isinstance(node, TargetRefNode):
            return self._validate_target_ref(node, context)

        if isinstance(node, AttributeNode):
            return self._validate_attribute(node, context)

        if isinstance(node, ConstantNode):
            return

        raise InvalidPropertyError(f"Invalid operand type: {type(node)}")

    def _validate_target_ref(self, node: TargetRefNode, context):
        semantic = node.semantic

        if semantic is None:
            raise InvalidPropertyError("Unbound target reference")

        if semantic.resolved_entity != "_model":
            raise InvalidPropertyError(
                f"Invalid target reference binding: expected '_model', "
                f"got {semantic.resolved_entity!r}"
            )

        if not semantic.resolved_path:
            raise InvalidPropertyError(
                "Invalid target reference: missing resolved path"
            )

        if context.model_target is None:
            raise InvalidPropertyError("Invalid target reference: missing model target")

        if semantic.resolved_path != ["_model", context.model_target]:
            raise InvalidPropertyError(
                f"Invalid target reference path: expected "
                f"['_model', {context.model_target!r}], "
                f"got {semantic.resolved_path!r}"
            )

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

        self._validate_attribute_against_schema(node)

    def _validate_attribute_against_schema(self, node: AttributeNode):
        """
        Validate that an attribute references a known model feature.

        This validation is optional and only runs when a ModelSchema
        is provided by the caller.
        """

        if self.model_schema is None:
            return

        feature_name = node.feature

        if feature_name not in self.model_schema.features:
            available = ", ".join(sorted(self.model_schema.features.keys()))

            raise InvalidPropertyError(
                f"Unknown feature '{feature_name}'. " f"Available features: {available}"
            )

        feature_schema = self.model_schema.features[feature_name]

        if node.semantic is not None:
            node.semantic.resolved_type = feature_schema.dtype.value
