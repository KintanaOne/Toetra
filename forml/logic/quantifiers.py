# forml/logic/quantifiers.py

from dataclasses import dataclass
from typing import List, Optional

from forml.logic.core import Expr, Var


@dataclass(frozen=True)
class ForAll(Expr):
    vars: List[Var]
    body: Expr
    domain: Optional[Expr] = None

    def __repr__(self):
        vars_str = ", ".join(map(str, self.vars))
        if self.domain:
            return f"∀{vars_str} : {self.domain} → {self.body}"
        return f"∀{vars_str} : {self.body}"


@dataclass(frozen=True)
class Exists(Expr):
    vars: List[Var]
    body: Expr
    domain: Optional[Expr] = None

    def __repr__(self):
        vars_str = ", ".join(map(str, self.vars))
        if self.domain:
            return f"∃{vars_str} : {self.domain} ∧ {self.body}"
        return f"∃{vars_str} : {self.body}"