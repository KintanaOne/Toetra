from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from forml.ast.nodes.assertion import AssertionNode
from forml.ast.nodes.expressions import ExpressionNode
from forml.ast.nodes.backends import BackendNode
from forml.ast.nodes.implication import ImplicationNode


@dataclass
class PropertyNode:
    type: str
    implication: ImplicationNode
    backend: Optional[BackendNode]