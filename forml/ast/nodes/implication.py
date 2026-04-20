from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from forml.ast.nodes.expressions import ExpressionNode
from forml.ast.nodes.assertion import AssertionNode


@dataclass
class ImplicationNode:
    left: ExpressionNode
    right: AssertionNode