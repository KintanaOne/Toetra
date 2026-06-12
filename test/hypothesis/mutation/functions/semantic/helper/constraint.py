from dataclasses import dataclass, field
from typing import Any, List, Optional



@dataclass(frozen=True, slots=True)
class SemanticConstraint:
    """
    Represents a domain-level constraint.

    Example:
        field = "age"
        operator = "<"
        value = 18
    """

    field: str
    operator: str
    value: Any
    context: Optional[str] = None  # optional domain grouping

    
@dataclass
class SemanticConstraintSet:
    """
    A collection of semantic constraints attached to a rule.
    """

    constraints: List[SemanticConstraint] = field(default_factory=list)

    def add(self, constraint: SemanticConstraint) -> None:
        self.constraints.append(constraint)

    def extend(self, constraints: List[SemanticConstraint]) -> None:
        self.constraints.extend(constraints)