from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from copy import deepcopy

from dsl.ast.nodes.assertion import (
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
    ComparisonNode,
    LogicalNode,
)

from dsl.ast.nodes.assertion import (
    AndNode,
    OrNode,
    NotNode,
    ImplicationNode,
)
from dsl.ast.nodes.primitives import AttributeNode
from test.hypothesis.mutation.functions.semantic.helper.constraint import SemanticConstraint, SemanticConstraintSet



class SemanticConstraintExtractor:
    """
    AST → SemanticConstraintSet extractor.

    NOW STRICTLY ALIGNED WITH REAL AST STRUCTURE.
    """

    # =========================================================
    # ENTRY POINT
    # =========================================================

    def extract(self, ast) -> SemanticConstraintSet:

        constraints = SemanticConstraintSet()

        for p in ast.body:
            root = p.rule.assertion.root

            constraints.extend(self._extract_node(root))

        return constraints

    # =========================================================
    # DISPATCHER
    # =========================================================

    def _extract_node(self, node: LogicalNode) -> List[SemanticConstraint]:

        if isinstance(node, AndNode):
            return self._extract_and(node)

        if isinstance(node, OrNode):
            return self._extract_or(node)

        if isinstance(node, NotNode):
            return self._extract_not(node)

        if isinstance(node, ImplicationNode):
            return self._extract_implication(node)

        if isinstance(node, ComparisonNode):
            return self._extract_comparison(node)

        return []
    

    # =========================================================
    # LOGICAL NODES
    # =========================================================

    def _extract_and(self, node: AndNode) -> List[SemanticConstraint]:
        out = []
        for op in node.operands:
            out.extend(self._extract_node(op))
        return out

    def _extract_or(self, node: OrNode) -> List[SemanticConstraint]:
        out = []
        for op in node.operands:
            out.extend(self._extract_node(op))
        return out

    def _extract_not(self, node: NotNode) -> List[SemanticConstraint]:
        inner = self._extract_node(node.operand)

        return [
            self._invert_constraint(c)
            for c in inner
        ]

    def _extract_implication(self, node: ImplicationNode) -> List[SemanticConstraint]:
        left = self._extract_node(node.left)
        right = self._extract_node(node.right)

        # semantic interpretation:
        return left + right
    

    # =========================================================
    # LEAF EXTRACTION (IMPORTANT PLACEHOLDER)
    # =========================================================

    def _extract_comparison(self, node: ComparisonNode) -> List[SemanticConstraint]:

        attr = node.left
        const = node.right

        return [
            SemanticConstraint(
                field=self._extract_field(attr),
                operator=node.op.value
                if hasattr(node.op, "value")
                else str(node.op),
                value=const.value,
                context=None,
            )
        ]
    
    def _extract_field(self, node: AttributeNode) -> str:
        """
        Convert AttributeNode → semantic field name.
        """

        if node.path:
            return ".".join(node.path)

        if node.feature:
            return node.feature

        if node.entity:
            return node.entity

        return "unknown"

    # =========================================================
    # CONSTRAINT INVERSION
    # =========================================================

    def _invert_constraint(self, c: SemanticConstraint) -> SemanticConstraint:

        inverse_map = {
            ">": "<=",
            "<": ">=",
            ">=": "<",
            "<=": ">",
            "==": "!=",
            "!=": "==",
        }

        return SemanticConstraint(
            field=c.field,
            operator=inverse_map.get(c.operator, c.operator),
            value=c.value,
            context=c.context,
        )