from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import textwrap

from demo.binary_classification_policy import EXPECTED_STATUSES, run_demo


def test_binary_classification_demo_runs_reports_and_replay(tmp_path: Path) -> None:
    session = run_demo(artifact_directory=tmp_path)
    assert tuple(report.status for report in session.reports) == EXPECTED_STATUSES
    assert [len(report.model_evaluations) for report in session.reports] == [1, 1, 1, 2]
    counterexample = session.first_counterexample
    assert counterexample is not None
    replay = counterexample.replay()
    assert replay.is_consistent is True
    assert replay.assertion_satisfied is False
    reports_directory = tmp_path / "reports"
    assert (reports_directory / "forml-verification-report.json").is_file()
    assert (reports_directory / "forml-verification-report.html").is_file()


NOTEBOOK_PATH = (
    Path(__file__).parents[3]
    / "demo"
    / "notebooks"
    / "binary_classification_policy.ipynb"
)


def test_binary_classification_notebook_executes_from_notebook_directory() -> None:
    script = textwrap.dedent(f"""
        import json
        from pathlib import Path

        notebook_path = Path({str(NOTEBOOK_PATH)!r})
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        namespace = {{"__name__": "__main__"}}
        for index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))
                exec(
                    compile(source, f"{{notebook_path}}:cell-{{index}}", "exec"),
                    namespace,
                )
        assert [
            report.status.value for report in namespace["session"].reports
        ] == ["proved", "counterexample", "witness", "proved"]
        assert namespace["replay"].is_consistent is True
        print("BINARY_NOTEBOOK_OK")
        """)
    completed = subprocess.run(
        [sys.executable, "-I", "-c", script],
        cwd=NOTEBOOK_PATH.parent,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "BINARY_NOTEBOOK_OK" in completed.stdout
