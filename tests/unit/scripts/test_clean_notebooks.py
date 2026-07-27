from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[3] / "scripts" / "ci" / "clean_notebooks.py"


def _write_dirty_notebook(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "execution_count": 7,
                        "metadata": {},
                        "outputs": [{"name": "stdout", "output_type": "stream"}],
                        "source": ["print('hello')\n"],
                    }
                ],
                "metadata": {
                    "widgets": {"application/vnd.jupyter.widget-state+json": {}}
                },
                "nbformat": 4,
                "nbformat_minor": 5,
            },
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )


def test_clean_notebooks_removes_transient_execution_state(tmp_path: Path) -> None:
    notebook_path = tmp_path / "demo.ipynb"
    _write_dirty_notebook(notebook_path)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(notebook_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cell = notebook["cells"][0]
    assert code_cell["execution_count"] is None
    assert code_cell["outputs"] == []
    assert "widgets" not in notebook["metadata"]


def test_clean_notebooks_check_mode_reports_dirty_files(tmp_path: Path) -> None:
    notebook_path = tmp_path / "demo.ipynb"
    _write_dirty_notebook(notebook_path)

    dirty = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(notebook_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert dirty.returncode == 1
    assert str(notebook_path) in dirty.stdout

    subprocess.run(
        [sys.executable, str(SCRIPT), str(notebook_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--check", str(notebook_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert clean.returncode == 0
