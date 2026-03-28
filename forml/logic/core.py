# forml/logic/core.py

from dataclasses import dataclass
from typing import List, Optional, Union


# =========================
# Base
# =========================

class Expr:
    pass


# =========================
# Variables
# =========================

@dataclass(frozen=True)
class Var(Expr):
    name: str
    type: str = "Input"

    def __repr__(self):
        return self.name


# =========================
# Functions (f(x))
# =========================

@dataclass(frozen=True)
class Func(Expr):
    name: str
    args: List[Expr]

    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"


# =========================
# Predicates
# =========================

@dataclass(frozen=True)
class Predicate(Expr):
    name: str
    args: List[Union[Expr, float, int]]

    def __repr__(self):
        return f"{self.name}({', '.join(map(str, self.args))})"


# =========================
# Logical operators
# =========================

@dataclass(frozen=True)
class Not(Expr):
    expr: Expr

    def __repr__(self):
        return f"¬({self.expr})"


@dataclass(frozen=True)
class And(Expr):
    left: Expr
    right: Expr

    def __repr__(self):
        return f"({self.left} ∧ {self.right})"


@dataclass(frozen=True)
class Implies(Expr):
    premise: Expr
    conclusion: Expr

    def __repr__(self):
        return f"({self.premise} → {self.conclusion})"


# =========================
# Model abstraction
# =========================

@dataclass(frozen=True)
class Model:
    name: str
    path: str
    output_type: str  # classification | regression

    def __call__(self, x: Expr) -> Func:
        return Func(self.name, [x])