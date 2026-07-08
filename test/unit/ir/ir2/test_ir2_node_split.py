from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.model.base import ModelConstraintIR2
from dsl.ir.ir2.nodes import (
    AffineOutputConstraintIR2 as CompatAffineOutputConstraintIR2,
)


def test_ir2_nodes_compat_exports_split_model_nodes():
    assert CompatAffineOutputConstraintIR2 is AffineOutputConstraintIR2
    assert issubclass(AffineOutputConstraintIR2, ModelConstraintIR2)
