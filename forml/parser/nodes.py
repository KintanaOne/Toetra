# forml/parser/nodes.py

from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict
from forml.grammar.official_contents.distances import EnumDistance
from forml.grammar.official_contents.properties import official_properties

from forml.grammar.official_contents.backends import EnumBackend
from forml.grammar.official_contents.functions import EnumFunction
from forml.grammar.official_contents.problems import EnumProblem
from forml.grammar.official_contents.properties import EnumProperty
from forml.grammar.official_contents.protected_words import EnumProtectedWord
from forml.grammar.official_contents.quantifiers import EnumQuantifier
from forml.grammar.official_contents.sets import EnumSet

# ───────────────────────────────
# Base Classes
# ───────────────────────────────

@dataclass
class Node:
    """Base class for all AST nodes."""
    pass


# ───────────────────────────────
# Header Section
# ───────────────────────────────

@dataclass
class Comment(Node):
    value: str

@dataclass
class TargetDeclaration(Node):
    target: str

@dataclass
class ModelDeclaration(Node):
    path: str

@dataclass
class Header(Node):
    comments: List[Comment] = field(default_factory=list)
    target: Optional[TargetDeclaration] = None
    model: Optional[ModelDeclaration] = None


# ───────────────────────────────
# Body Section
# ───────────────────────────────

    # ───────────────────────────────
    # property section nodes
    # ───────────────────────────────

        # ───────────────────────────────
        # Universal Expression
        # ───────────────────────────────

@dataclass
class UniversalSet(Node):
    func: EnumSet
    args: List[Union[str, int, float]]

@dataclass
class UniversalExpr(Node):
    quantifier: EnumQuantifier
    variable: Optional[str] = None

        # ───────────────────────────────
        # Domain Expression
        # ───────────────────────────────
@dataclass
class Domain(Node):
    """
    sexe("male","female")
    """
    name: str
    values: List[Union[int, float, str]] = field(default_factory=list)

        # ───────────────────────────────
        # Anchor Expression
        # ───────────────────────────────
@dataclass
class AnchorExpr(Node):
    """
    exemples :
        - at x 
        - at x in hyperball(L2, 0.01)
        - at x with sexe("male", "female")
        - at x in hyperball(L2, 0.01) with sexe("male", "female")
    """
    anchor: str
    set_expr: Optional["UniversalExpr"] = None
    domain: Optional[Domain] = None

        # ───────────────────────────────
        # Check Expression
        # ───────────────────────────────
@dataclass
class CheckExpr(Node):
    check: str

        # ───────────────────────────────
        # Pair Wise Expression
        # ───────────────────────────────
@dataclass
class PairwiseExpr(Node):
    left: str
    right: str
    feature: str
    distance_func: EnumDistance
    threshold: Union[int, float]

        # ───────────────────────────────
        # Function Expression
        # ───────────────────────────────
@dataclass
class FunctionExpr(Node):
    function: EnumFunction
    args: Optional[Dict[str, Union[str, int, float]]] = None

        # ───────────────────────────────
        # Problem Expression
        # ───────────────────────────────
@dataclass
class ProblemExpr(Node):
    problem: str
    function: FunctionExpr

        # ───────────────────────────────
        # Logic Expression
        # ───────────────────────────────
@dataclass
class LogicExpr(Node):
    """ [not] key comparison value """
    key : str
    comparison: str
    value: Union[str, int, float]
    negate: bool = False

@dataclass
class LogicImplication(Node):
    """ condition -> consequence """
    condition: LogicExpr
    consequence: LogicExpr

@dataclass
class LogicAssertion(Node):
    implications: List[LogicImplication]
    connections: Optional[List[str]] = None

        # ───────────────────────────────
        # Assertion
        # ───────────────────────────────
@dataclass
class Assertion(Node):
    expr: LogicAssertion
    
@dataclass
class Property(Node):
    property_type: Union[str, EnumProperty]  # ← accepte officiel ou custom
    quantifier_expr: Optional[UniversalExpr] = None
    anchor_expr: Optional[AnchorExpr] = None
    check_expr: Optional[CheckExpr] = None
    pairwise_expr: Optional[PairwiseExpr] = None
    assertion: Optional[Assertion] = None

    @property
    def type_name(self) -> str:
        """
        Retourne le nom normalisé de la propriété (en majuscule).
        """
        return self.property_type.strip().upper()

    @property
    def is_official(self) -> bool:
        """
        Vérifie si la propriété fait partie des types officiels.
        """
        return self.type_name in official_properties

    @property
    def is_custom(self) -> bool:
        """
        Inverse logique — utile pour filtrer des propriétés non officielles.
        """
        return not self.is_official



@dataclass
class Abstractor(Node):
    backend: EnumBackend
    params: Dict[str, Union[str, int, float]] = field(default_factory=dict)

@dataclass
class Section(Node):
    pass

@dataclass
class DeclarationSection(Node):
    key: str
    value: Union[str, int, float, bool]

@dataclass
class PropertySection(Section):
    property: Property
    abstractor: Optional[Abstractor] = None


@dataclass
class Body(Node):
    sections: List[Union[DeclarationSection, PropertySection]] = field(default_factory=list)


# ───────────────────────────────
# Footer Section
# ───────────────────────────────

@dataclass
class Footer(Node):
    comments: List[Comment] = field(default_factory=list)


# ───────────────────────────────
# Root Program
# ───────────────────────────────

@dataclass
class Program(Node):
    header: Header
    body: Body
    footer: Optional[Footer] = None
