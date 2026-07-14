from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK_PATH = (
    Path(__file__).parents[3] / "demo" / "notebooks" / "credit_risk_validation.ipynb"
)


def test_credit_risk_notebook_is_clean_and_uses_public_api() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )

    assert notebook["nbformat"] == 4
    assert all(
        not cell.get("outputs")
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )
    assert "from dsl.runtime import verify" in source
    assert "session = verify(" in source
    assert "session.write_json" in source
    assert "session.write_html" in source
    assert "model.predict" in source
    assert "IR2BuildContext" not in source
    assert "Z3Runner" not in source
