from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from forml.ast.nodes.header import HeaderNode
from forml.ast.nodes.property import PropertyNode


@dataclass
class ProgramNode:
    header : HeaderNode
    body : List[PropertyNode]
