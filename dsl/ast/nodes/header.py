from dataclasses import dataclass
from typing import Optional


@dataclass
class HeaderNode:
    model: str
    target: str