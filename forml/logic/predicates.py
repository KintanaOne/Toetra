# forml/logic/predicates.py

from forml.logic.core import Predicate, Expr


# =========================
# Distance
# =========================

def dist_l1(x: Expr, x_prime: Expr, eps: float) -> Predicate:
    return Predicate("dist_L1_leq", [x, x_prime, eps])

def dist_l2(x: Expr, x_prime: Expr, eps: float) -> Predicate:
    return Predicate("dist_L2_leq", [x, x_prime, eps])

def dist_linf(x: Expr, x_prime: Expr, eps: float) -> Predicate:
    return Predicate("dist_Linf_leq", [x, x_prime, eps])

# =========================
# Classification
# =========================

def argmax_eq(fx: Expr, fxp: Expr) -> Predicate:
    return Predicate("argmax_eq", [fx, fxp])


# =========================
# Regression (future ready)
# =========================

def abs_diff_leq(fx: Expr, fxp: Expr, eps: float) -> Predicate:
    return Predicate("abs_diff_leq", [fx, fxp, eps])