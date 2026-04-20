from __future__ import annotations

from dataclasses import dataclass
from typing import List

from forml.ast.nodes.primitives import ArgNode


# ============================================================================
# BACKEND SPECIFICATION NODE
# ============================================================================

@dataclass
class BackendNode:
    """
    Defines WHICH engine is used to verify the property.
    """

    name: str  # Z3 / ERAN / FUZZ / CUSTOM
    args: List[ArgNode]