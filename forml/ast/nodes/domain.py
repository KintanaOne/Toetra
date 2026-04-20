from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class DomainNode:
    name : str
    values : List[str]