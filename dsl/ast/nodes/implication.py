from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from dsl.ast.nodes.expressions import ExpressionNode
from dsl.ast.nodes.assertion import AssertionNode


@dataclass
class ImplicationNode:
    left: ExpressionNode
    right: AssertionNode