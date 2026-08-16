from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[4]
SEMANTICS_ROOT = ROOT / "src" / "toetra" / "_models" / "semantics"


def _top_level_definitions(path: Path) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _class_methods(path: Path, class_name: str) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    class_node = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    return {
        node.name
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_binary_classification_lowering_uses_focused_modules() -> None:
    facade = SEMANTICS_ROOT / "binary_classification.py"

    assert _top_level_definitions(facade) == {
        "BinaryLogisticAffineClassificationProfile"
    }
    assert _class_methods(
        facade,
        "BinaryLogisticAffineClassificationProfile",
    ) == {"lower_task"}
    assert "lower_binary_classification_task" in _top_level_definitions(
        SEMANTICS_ROOT / "binary_classification_lowering.py"
    )
    assert "lower_label_comparison" in _top_level_definitions(
        SEMANTICS_ROOT / "binary_classification_labels.py"
    )
    assert "lower_probability_comparison" in _top_level_definitions(
        SEMANTICS_ROOT / "binary_classification_probability.py"
    )
    assert "lower_pairwise_label_relation" in _top_level_definitions(
        SEMANTICS_ROOT / "binary_classification_pairwise.py"
    )
    assert "BinaryClassificationLoweringProfile" in _top_level_definitions(
        SEMANTICS_ROOT / "binary_classification_common.py"
    )
