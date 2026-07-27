from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).parents[3]
RUNTIME_ROOT = ROOT / "src" / "toetra" / "_runtime"


def _top_level_definitions(path: Path) -> set[str]:
    module = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_replay_responsibilities_use_focused_modules() -> None:
    assert {path.name for path in RUNTIME_ROOT.glob("replay*.py")} >= {
        "replay.py",
        "replay_engine.py",
        "replay_evaluation.py",
        "replay_rendering.py",
    }

    assert _top_level_definitions(RUNTIME_ROOT / "replay.py") == {
        "CounterexampleReplay",
        "EvaluationReplay",
        "PointReplay",
    }
    assert "replay_verification_report" in _top_level_definitions(
        RUNTIME_ROOT / "replay_engine.py"
    )
    assert "evaluate_logical" in _top_level_definitions(
        RUNTIME_ROOT / "replay_evaluation.py"
    )
    assert "render_replay_html" in _top_level_definitions(
        RUNTIME_ROOT / "replay_rendering.py"
    )
