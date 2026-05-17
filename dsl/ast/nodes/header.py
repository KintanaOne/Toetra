from dataclasses import dataclass


@dataclass
class HeaderNode:
    model: str
    target: str