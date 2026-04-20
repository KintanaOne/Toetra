from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any

from forml.ast.nodes.primitives import ArgNode


@dataclass
class NeighborhoodNode:
    metric: str
    args: List[ArgNode]