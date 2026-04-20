from forml.semantic.errors import InvalidPropertyError
from forml.semantic.tracer import ValidationTracer


class LogicValidator:
    """
    LogicValidator validates logical expressions on the RHS of an implication.

    It ensures:
    - structural correctness (AND, OR, NOT, comparisons)
    - recursive validation of sub-expressions
    - compatibility with the semantic context (variables already bound)

    NOTE:
    Variable binding is NOT handled here.
    It is assumed that BindingValidator has already run.
    """

    def __init__(self, tracer=None):
        self.tracer = tracer or ValidationTracer()

    def validate(self, node, context):
        self.tracer.log(f"Validating logic node: {node}")

        node_type = node.__class__.__name__

        if node_type == "ComparisonNode":
            self._validate_comparison(node, context)

        elif node_type == "AndNode":
            self._validate_and(node, context)

        elif node_type == "OrNode":
            self._validate_or(node, context)

        elif node_type == "NotNode":
            self._validate_not(node, context)

        else:
            raise InvalidPropertyError(
                f"Unknown logical node type: {node_type}"
            )

    # ─────────────────────────────
    # COMPARISON
    # ─────────────────────────────

    def _validate_comparison(self, node, context):
        """
        Example:
            x.a <= 1
            a <= 1  (after binding → x'.a <= 1)
        """

        self.tracer.log(f"Validating ComparisonNode: {node}")

        if not node.left or not node.right:
            raise InvalidPropertyError("Invalid comparison: missing operands")

        self._validate_operand(node.left, context)
        self._validate_operand(node.right, context)

    # ─────────────────────────────
    # AND
    # ─────────────────────────────

    def _validate_and(self, node, context):
        self.tracer.log(f"Validating AndNode: {node}")

        self.validate(node.left, context)
        self.validate(node.right, context)

    # ─────────────────────────────
    # OR
    # ─────────────────────────────

    def _validate_or(self, node, context):
        self.tracer.log(f"Validating OrNode: {node}")

        self.validate(node.left, context)
        self.validate(node.right, context)

    # ─────────────────────────────
    # NOT
    # ─────────────────────────────

    def _validate_not(self, node, context):
        self.tracer.log(f"Validating NotNode: {node}")

        if not node.child:
            raise InvalidPropertyError("NOT expression missing child")

        self.validate(node.child, context)

    # ─────────────────────────────
    # OPERANDS
    # ─────────────────────────────

    def _validate_operand(self, node, context):
        """
        Validates leaf-level elements:
        - AttributeNode
        - ConstantNode

        NOTE:
        Binding (entity resolution) has already been done upstream.
        """

        node_type = node.__class__.__name__

        if node_type == "AttributeNode":
            self._validate_attribute(node, context)

        elif node_type == "ConstantNode":
            pass  # Always valid

        else:
            raise InvalidPropertyError(
                f"Invalid operand type: {node_type}"
            )

    # ─────────────────────────────
    # ATTRIBUTE
    # ─────────────────────────────

    def _validate_attribute(self, node, context):
        """
        Ensures:
        - attribute has a resolved entity (after binding)
        - feature name is valid (basic check only)
        """

        if not node.feature:
            raise InvalidPropertyError("Attribute missing feature name")

        if not node.entity:
            raise InvalidPropertyError(
                f"Unresolved attribute '{node.feature}' (binding failed)"
            )