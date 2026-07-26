from __future__ import annotations

import json
from pathlib import Path

NOTEBOOK_PATH = (
    Path(__file__).parents[3] / "demo" / "regression" / "credit_risk_validation.ipynb"
)


def test_credit_risk_notebook_uses_public_api() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
    )

    assert notebook["nbformat"] == 4
    assert "from toetra import verify" in source
    assert '(candidate / "src" / "toetra").is_dir()' in source
    assert '_source_root_text = str(REPOSITORY_ROOT / "src")' in source
    assert "sys.path.insert(0, _source_root_text)" in source
    assert source.index("sys.path.insert(0, _source_root_text)") < source.index(
        "from toetra import verify"
    )
    assert "session = verify(" in source
    assert "session.write_artifacts" in source
    assert "session.to_dataframe" in source
    assert "session.first_counterexample" in source
    assert "counterexample.replay" in source
    assert "IR2BuildContext" not in source
    assert "Z3Runner" not in source
    assert "Fraction" not in source
    assert "solver_number_to_float" not in source
    assert "find_repository_root" not in source
    assert "display_name.split" not in source
    assert "from dsl." not in source
