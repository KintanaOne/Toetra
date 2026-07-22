from __future__ import annotations

from dsl.ir.ir2.dsl.nodes import (
    AssumptionIR2,
    AtomIR2,
    ClauseIR2,
    CNFFormulaIR2,
    DNFFormulaIR2,
    FormulaIR2,
    LiteralIR2,
    NNFFormulaIR2,
    PointIdentityMapIR2,
    QuantifierStructureIR2,
    TermIR2,
    VerificationTaskIR2,
)
from dsl.ir.ir2.model import (
    AffineExpressionIR2,
    AffineModelQuantityConstraintIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
    ModelConstraintIR2,
)

"""Compatibility exports for IR2 nodes.

IR2 nodes are now split by responsibility:
- dsl.ir.ir2.dsl.* contains DSL/formula/task-level nodes;
- dsl.ir.ir2.model.* contains backend-neutral model constraint nodes.

This module intentionally re-exports the historical public API so existing
imports such as ``from dsl.ir.ir2.nodes import VerificationTaskIR2`` remain
valid during the refactor.
"""

__all__ = [
    "AffineExpressionIR2",
    "AffineModelQuantityConstraintIR2",
    "AffineOutputConstraintIR2",
    "AffineTermIR2",
    "AssumptionIR2",
    "AtomIR2",
    "ClauseIR2",
    "CNFFormulaIR2",
    "DNFFormulaIR2",
    "FormulaIR2",
    "LiteralIR2",
    "ModelConstraintIR2",
    "NNFFormulaIR2",
    "PointIdentityMapIR2",
    "QuantifierStructureIR2",
    "TermIR2",
    "VerificationTaskIR2",
]
