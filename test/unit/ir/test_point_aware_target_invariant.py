from __future__ import annotations

import pytest

from toetra._compiler.ast.nodes.primitives import TargetRefNode
from toetra._compiler.ir.ir1.scalar_translator import ScalarExpressionTranslator
from toetra._compiler.semantic.runtime.annotations import SemanticAnnotations


def test_source_target_cannot_reach_ir1_without_point_evaluation_identity() -> None:
    target = TargetRefNode()
    target.semantic = SemanticAnnotations(
        resolved_entity="_model",
        resolved_path=["_model", "score"],
        resolved_type="model_output",
    )

    with pytest.raises(ValueError, match="without a model evaluation identity"):
        ScalarExpressionTranslator().translate(target)
