from toetra._compiler.ast.nodes.assertion import (
    AndNode,
    LogicalNode,
    ComparisonNode,
)

from toetra._compiler.ast.nodes.primitives import AttributeNode, ConstantNode

from toetra._language.vocabulary.operators import EnumComparisonOperator
from test.hypothesis.mutation.functions.semantic.helper.constraint import (
    SemanticConstraint,
    SemanticConstraintSet,
)


class SemanticASTRebuilder:
    """
    Rebuild AST from SemanticConstraintSet.

    GOAL:
        Close the loop:
            AST → semantic → AST

    IMPORTANT:
        This is a STRUCTURAL reconstruction, not semantic truth recovery.
    """

    # =========================================================
    # ENTRY POINT
    # =========================================================

    def rebuild(self, constraints: SemanticConstraintSet):

        if not constraints.constraints:
            return None

        ast_nodes = [self._build_comparison(c) for c in constraints.constraints]

        # if only one constraint
        if len(ast_nodes) == 1:
            return ast_nodes[0]

        return AndNode(operands=ast_nodes)

    def _build_comparison(self, c: SemanticConstraint) -> LogicalNode:

        field_parts = c.field.split(".")

        # Build AttributeNode
        attr = AttributeNode(
            entity=field_parts[0] if field_parts else None,
            feature=field_parts[-1],
            path=field_parts,
        )

        # Build ConstantNode
        const = ConstantNode(
            value=c.value,
            dtype=self._infer_dtype(c.value),
        )

        return ComparisonNode(
            left=attr,
            op=EnumComparisonOperator(c.operator),
            right=const,
        )

    def _normalize_operator(self, op: str):
        """
        Ensure AST-compatible operator format.
        """

        return op  # assume EnumComparisonOperator handled upstream

    def _infer_dtype(self, value):

        from toetra._compiler.semantic.types.enums import EnumDataType

        if isinstance(value, bool):
            return EnumDataType.BOOL

        if isinstance(value, int):
            return EnumDataType.INT

        if isinstance(value, float):
            return EnumDataType.FLOAT

        if isinstance(value, str):
            return EnumDataType.STRING

        raise ValueError(f"Unsupported constant type: {type(value)}")
