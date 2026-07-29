from __future__ import annotations

from pathlib import Path

import pytest

from demo.quickstart.verify_model import DEMO_POLICY, main

DEMO_POLICY_PATH = (
    Path(__file__).parents[3] / "demo" / "quickstart" / "verification_policy.toetra"
)


def test_embedded_quickstart_policy_matches_readable_policy_file() -> None:
    assert DEMO_POLICY == DEMO_POLICY_PATH.read_text(encoding="utf-8")


def test_cli_requires_a_specification_outside_demo_mode(capsys) -> None:
    with pytest.raises(SystemExit) as raised:
        main([])

    assert raised.value.code == 2
    error = capsys.readouterr().err
    assert "a specification path is required unless --demo is used" in error


def test_cli_reports_a_missing_specification_without_a_traceback(capsys) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["missing-policy.toetra"])

    assert raised.value.code == 2
    error = capsys.readouterr().err
    assert "Toetra specification not found" in error
    assert "Traceback" not in error


def test_cli_rejects_project_artifacts_in_demo_mode(capsys) -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--demo", "--model", "model.joblib"])

    assert raised.value.code == 2
    assert "--model and --dataset cannot be used with --demo" in capsys.readouterr().err
