from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from dsl.ast.nodes.assertion import AssertionNode
from dsl.ast.nodes.expressions import ExpressionNode
from dsl.ast.nodes.backends import BackendNode
from dsl.ast.nodes.implication import ImplicationNode


@dataclass
class PropertyNode:
    type: str
    implication: ImplicationNode
    backend: Optional[BackendNode]