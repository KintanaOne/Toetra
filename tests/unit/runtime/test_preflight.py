from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
import z3
from sklearn.linear_model import LinearRegression

from toetra._backends.z3_backend.runner import Z3Runner
from toetra._runtime.preflight import (
    INSPECTION_SCHEMA,
    VALIDATION_SCHEMA,
    ValidationLevel,
    inspect_request,
    validate_request,
)

_SOURCE = """model := "linear.joblib"
target := score
maximum_score := 7.0
anchor baseline := { a: 1.0 }

[BOUND]:
forall x0
with domain(x0.a: [0.0, 3.0])
=> target[x0] <= maximum_score using Z3
"""


def _artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    frame = pd.DataFrame(
        {
            "a": [0.0, 1.0, 2.0, 3.0],
            "score": [1.0, 3.0, 5.0, 7.0],
            "risk_score": [1.0, 3.0, 5.0, 7.0],
        }
    )
    model = LinearRegression().fit(frame[["a"]], frame["score"])
    model_path = tmp_path / "linear.joblib"
    dataset_path = tmp_path / "linear.csv"
    specification_path = tmp_path / "policy.toetra"
    joblib.dump(model, model_path)
    frame.to_csv(dataset_path, index=False)
    specification_path.write_text(_SOURCE, encoding="utf-8")
    return specification_path, model_path, dataset_path


def test_syntax_validation_stops_before_model_loading(tmp_path: Path) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(_SOURCE, encoding="utf-8")

    result = validate_request(
        specification_path,
        level=ValidationLevel.SYNTAX,
    )

    assert result.valid
    assert result.completed_level is ValidationLevel.SYNTAX
    assert result.property_count == 1
    assert result.exit_code == 0


def test_invalid_syntax_is_a_completed_negative_validation(tmp_path: Path) -> None:
    specification_path = tmp_path / "invalid.toetra"
    specification_path.write_text(
        'model := "missing.joblib"\ntarget := score\n\n[BOUND]:\ninvalid\n',
        encoding="utf-8",
    )

    result = validate_request(
        specification_path,
        level=ValidationLevel.SYNTAX,
    )

    payload = json.loads(result.to_json())
    assert not result.valid
    assert result.exit_code == 3
    assert payload["schema"] == VALIDATION_SCHEMA
    assert payload["schema_version"] == 1
    assert payload["diagnostics"][0]["stage"] == "syntax"


def test_executable_validation_translates_without_running_solver(
    tmp_path: Path,
    monkeypatch,
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    def fail_if_executed(*_args, **_kwargs):
        raise AssertionError("executable validation must not invoke the solver")

    monkeypatch.setattr(Z3Runner, "run", fail_if_executed)
    monkeypatch.setattr(z3, "Solver", fail_if_executed)

    result = validate_request(
        specification_path,
        dataset=dataset_path,
        level=ValidationLevel.EXECUTABLE,
    )

    assert result.valid
    assert result.completed_level is ValidationLevel.EXECUTABLE
    assert "backend_translated" in result.checks
    assert result.exit_code == 0


def test_inspection_is_public_and_contains_no_private_ir(tmp_path: Path) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    result = inspect_request(
        specification_path,
        dataset=dataset_path,
    )
    payload = json.loads(result.to_json())
    rendered = result.to_json()

    assert payload["schema"] == INSPECTION_SCHEMA
    assert payload["schema_version"] == 1
    assert payload["model"]["framework"] == "sklearn"
    assert payload["model"]["family"] == "LinearRegression"
    assert payload["execution"]["translation_ready"] is True
    assert payload["specification"]["constants"] == [
        {"name": "maximum_score", "dtype": "float", "value": 7.0}
    ]
    assert payload["specification"]["anchors"] == [
        {
            "name": "baseline",
            "binding_kind": "inline",
            "features": ["a"],
            "reference_arguments": [],
            "resolved": False,
            "resolution": None,
        }
    ]
    assert payload["properties"][0]["backend"] == "Z3"
    assert payload["properties"][0]["requested_observables"] == ["regression_value"]
    assert payload["properties"][0]["backend_runner_available"] is True
    assert payload["properties"][0]["execution_policy_compatible"] is True
    assert "IR1" not in rendered
    assert "IR2" not in rendered
    assert "toetra._" not in rendered
    assert "ArithRef" not in rendered
    assert "BoolRef" not in rendered


def test_validation_artifact_shape_is_stable_across_levels(tmp_path: Path) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    syntax = validate_request(specification_path, level=ValidationLevel.SYNTAX)
    executable = validate_request(
        specification_path,
        dataset=dataset_path,
        level=ValidationLevel.EXECUTABLE,
    )

    for payload in (syntax.to_dict(), executable.to_dict()):
        artifacts = payload["artifacts"]
        assert {
            "specification",
            "model",
            "dataset",
            "anchor_source",
        } <= set(artifacts)
        for artifact in artifacts.values():
            assert set(artifact) == {
                "role",
                "source_kind",
                "status",
                "name",
                "fingerprint",
                "unavailable_reason",
            }


def test_inspection_never_runs_backend_solver(
    tmp_path: Path,
    monkeypatch,
) -> None:
    specification_path, _, dataset_path = _artifacts(tmp_path)

    def fail_if_executed(*_args, **_kwargs):
        raise AssertionError("inspection must not invoke the solver")

    monkeypatch.setattr(Z3Runner, "run", fail_if_executed)
    monkeypatch.setattr(z3, "Solver", fail_if_executed)

    result = inspect_request(specification_path, dataset=dataset_path)

    assert result.to_dict()["execution"]["translation_ready"] is True


def test_inspection_distinguishes_declared_and_effective_artifacts(
    tmp_path: Path,
) -> None:
    specification_path, model_path, dataset_path = _artifacts(tmp_path)
    specification_path.write_text(
        _SOURCE.replace(
            "target := score\n",
            'target := score\ndataset := "linear.csv"\n',
            1,
        ),
        encoding="utf-8",
    )

    declared = inspect_request(specification_path).to_dict()

    assert declared["specification"]["declarations"] == {
        "model": "linear.joblib",
        "target": "score",
        "dataset": "linear.csv",
    }
    assert declared["model"]["declared_reference"] == "linear.joblib"
    assert declared["model"]["path"] == str(model_path.resolve())
    assert declared["model"]["overridden"] is False
    assert declared["model"]["dataset"] == {
        "declared_reference": "linear.csv",
        "effective_reference": "linear.csv",
        "path": str(dataset_path.resolve()),
        "overridden": False,
        "provided": True,
    }

    override_model = tmp_path / "candidate.joblib"
    override_model.write_bytes(model_path.read_bytes())
    override_dataset = tmp_path / "override.csv"
    pd.read_csv(dataset_path).to_csv(override_dataset, index=False)
    overridden = inspect_request(
        specification_path,
        model=override_model,
        dataset=override_dataset,
    ).to_dict()

    assert overridden["model"]["declared_reference"] == "linear.joblib"
    assert overridden["model"]["path"] == str(override_model.resolve())
    assert overridden["model"]["overridden"] is True
    assert overridden["model"]["dataset"]["declared_reference"] == "linear.csv"
    assert overridden["model"]["dataset"]["path"] == str(override_dataset.resolve())
    assert overridden["model"]["dataset"]["overridden"] is True

    retargeted = inspect_request(
        specification_path,
        target="risk_score",
    ).to_dict()

    assert retargeted["specification"]["declarations"]["target"] == "score"
    assert retargeted["specification"]["effective"]["target"] == "risk_score"
    assert retargeted["specification"]["overrides"]["target"] is True
    assert retargeted["model"]["output"]["declared_name"] == "score"
    assert retargeted["model"]["output"]["name"] == "risk_score"
    assert retargeted["model"]["output"]["overridden"] is True


def test_syntax_validation_reports_declarations_without_consuming_artifacts(
    tmp_path: Path,
) -> None:
    specification_path = tmp_path / "policy.toetra"
    specification_path.write_text(
        _SOURCE.replace(
            "target := score\n",
            'target := score\ndataset := "missing.csv"\n',
            1,
        ),
        encoding="utf-8",
    )

    result = validate_request(specification_path, level=ValidationLevel.SYNTAX)
    payload = result.to_dict()

    assert result.valid
    assert payload["declarations"] == {
        "model": "linear.joblib",
        "target": "score",
        "dataset": "missing.csv",
    }
    assert payload["effective"] == {
        "model": "linear.joblib",
        "target": "score",
        "dataset": "missing.csv",
    }
    assert payload["overrides"] == {
        "model": False,
        "target": False,
        "dataset": False,
    }
    assert result.consumed_paths == (specification_path.resolve(),)
