from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from dsl.ast.nodes.base import ASTNode
from dsl.ast.nodes.primitives import AttributeNode, ConstantNode
from dsl.language.vocabulary.operators import EnumComparisonOperator


# ----------------------------------------------------------------------------------------------------------------------
# ASSERTION (WRAPPER)
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class AssertionNode(ASTNode):
    """Top-level assertion (WHAT must be true)."""
    root: LogicalNode
    context: ProblemNode | None = None
# ----------------------------------------------------------------------------------------------------------------------
# LOGICAL NODES
# ----------------------------------------------------------------------------------------------------------------------

class LogicalNode(ASTNode):
    """Base class for all logical expressions."""
    pass


@dataclass
class ComparisonNode(LogicalNode):
    left: AttributeNode
    op: EnumComparisonOperator
    right: ConstantNode


@dataclass
class AndNode(LogicalNode):
    operands: list[LogicalNode]


@dataclass
class OrNode(LogicalNode):
    operands: list[LogicalNode]


@dataclass
class NotNode(LogicalNode):
    operand: LogicalNode


@dataclass
class ImplicationNode(LogicalNode):
    left: LogicalNode
    right: LogicalNode


# ----------------------------------------------------------------------------------------------------------------------
# CONTEXT
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class ProblemNode(LogicalNode):
    problem: str
    function: str | None


# ----------------------------------------------------------------------------------------------------------------------
# FALLBACK
# ----------------------------------------------------------------------------------------------------------------------

@dataclass
class UnknownNode(LogicalNode):
    raw: str