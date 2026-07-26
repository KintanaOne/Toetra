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
    assert "from toetra import verify" in source
    assert '(candidate / "src" / "toetra").is_dir()' in source
    assert '_source_root_text = str(_repository_root / "src")' in source
    assert "sys.path.insert(0, _source_root_text)" in source
    assert source.index("sys.path.insert(0, _source_root_text)") < source.index(
        "from toetra import verify"
    )
    assert "target[applicant].probability" not in source  # policy remains in .toetra
    assert "session = verify(" in source
    assert "counterexample.replay" in source
    assert "session.write_artifacts" in source
    assert "from dsl." not in source
    assert "Z3Runner" not in source
