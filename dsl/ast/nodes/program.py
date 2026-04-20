from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from dsl.ast.nodes.header import HeaderNode
from dsl.ast.nodes.property import PropertyNode


@dataclass
class ProgramNode:
    header : HeaderNode
    body : List[PropertyNode]
