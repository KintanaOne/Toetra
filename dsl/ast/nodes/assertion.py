from __future__ import annotations

from dataclasses import dataclass
from typing import List

from dsl.ast.nodes.primitives import AttributeNode, ConstantNode


# ============================================================================
# BASE
# ============================================================================

@dataclass
class AssertionNode:
    """
    Base class for all logical assertions.
    Represents WHAT must be true.
    """
    pass


# ============================================================================
# COMPARISON
# ============================================================================

@dataclass
class ComparisonNode(AssertionNode):
    left: AttributeNode
    op: str
    right: ConstantNode


# ============================================================================
# BOOLEAN OPERATORS
# ============================================================================

@dataclass
class AndNode(AssertionNode):
    operands: List[AssertionNode]


@dataclass
class OrNode(AssertionNode):
    operands: List[AssertionNode]


@dataclass
class NotNode(AssertionNode):
    operand: AssertionNode


# ============================================================================
# DOMAIN SPECIFIC
# ============================================================================

@dataclass
class ProblemNode(AssertionNode):
    problem: str
    function: str | None


# ============================================================================
# FALLBACK
# ============================================================================

@dataclass
class UnknownNode(AssertionNode):
    raw: str