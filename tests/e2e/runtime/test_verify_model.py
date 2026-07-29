from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

from demo.quickstart.verify_model import (
    build_demo_artifacts,
    main,
    run_verification,
)
from toetra._backends.results import VerificationStatus

QUICKSTART_PATH = Path(__file__).parents[3] / "demo" / "quickstart" / "verify_model.py"


def test_verify_model_runs_public_api_and_writes_json(tmp_path, capsys) -> None:
    model_path, dataset_path = build_demo_artifacts(tmp_path)
    specification_path = tmp_path / "policy.toetra"
    report_path = tmp_path / "artifacts" / "verification.json"
    specification_path.write_text(
        """
model := "affine_score.joblib"
target := score

[BOUND]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= 7.0
    using Z3
""".strip() + "\n",
        encoding="utf-8",
    )

    session = run_verification(
        specification_path,
        model=model_path,
        dataset=dataset_path,
        json_output=report_path,
    )

    captured = capsys.readouterr().out
    assert "Toetra Verification Report" in captured
    assert "PROVED" in captured
    assert "JSON report written to" in captured
    assert report_path.is_file()
    assert session.reports[0].status is VerificationStatus.PROVED
    assert session.exit_code == 0


def test_verify_model_demo_mode_runs_without_external_files(tmp_path, capsys) -> None:
    report_path = tmp_path / "artifacts" / "demo-verification.json"

    exit_code = main(["--demo", "--json-output", str(report_path)])

    captured = capsys.readouterr().out
    assert "Toetra Verification Report" in captured
    assert "PROVED" in captured
    assert "WITNESS" in captured
    assert "JSON report written to" in captured
    assert report_path.is_file()
    assert exit_code == 0


def test_quickstart_script_runs_after_copy_outside_repository(tmp_path) -> None:
    copied_script = tmp_path / "verify_model.py"
    report_path = tmp_path / "artifacts" / "verification.json"
    shutil.copy2(QUICKSTART_PATH, copied_script)

    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(copied_script),
            "--demo",
            "--json-output",
            str(report_path),
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "cp1252"},
    )

    assert completed.returncode == 0, completed.stderr
    assert "Toetra Verification Report" in completed.stdout
    assert "PROVED" in completed.stdout
    assert "WITNESS" in completed.stdout
    assert report_path.is_file()
