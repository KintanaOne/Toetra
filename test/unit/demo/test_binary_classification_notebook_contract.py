from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK_PATH = (
    Path(__file__).parents[3]
    / "demo"
    / "classification"
    / "binary_classification_policy.ipynb"
)


def test_binary_classification_notebook_uses_only_public_api() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )
    assert notebook["nbformat"] == 4
    assert "from forml import verify" in source
    assert "target[applicant].probability" not in source  # policy remains in .forml
    assert "session = verify(" in source
    assert "counterexample.replay" in source
    assert "session.write_artifacts" in source
    assert "from dsl." not in source
    assert "Z3Runner" not in source
