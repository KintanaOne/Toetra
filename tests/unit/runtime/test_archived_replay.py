from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from toetra._backends.results import VerificationStatus
from toetra._runtime.archived_replay import (
    REPLAY_COLLECTION_SCHEMA,
    REPLAY_COLLECTION_SCHEMA_VERSION,
    replay_archived_report,
)
from toetra._runtime.errors import (
    ReplayUnavailableError,
    VerificationConfigurationError,
)
from toetra._runtime.replay import CounterexampleReplay

_INPUT_FINGERPRINT = "sha256:" + "1" * 64
_PROPERTY_FINGERPRINT = "sha256:" + "2" * 64


def _payload(
    *,
    status: str = "counterexample",
    property_index: int = 0,
    effective_target: str = "score",
    effective_model: str = "model.joblib",
    effective_dataset: str | None = None,
    model_overridden: bool = False,
    dataset_overridden: bool = False,
    include_execution_context: bool = True,
) -> dict[str, Any]:
    report = {
        "schema": "toetra.verification-report",
        "schema_version": 6,
        "property": {
            "index": property_index,
            "type": "BOUND",
            "semantics": "refutation",
            "specification": "target[x0] < 7.0",
        },
        "execution": {
            "backend": "Z3",
            "backend_status": "sat",
            "status": status,
            "assumption_count": 0,
            "route_reason": "test",
            "backend_execution": None,
        },
        "provenance": {
            "completeness": "complete",
            "fingerprints": {
                "inputs": _INPUT_FINGERPRINT,
                "property": _PROPERTY_FINGERPRINT,
            },
        },
        "points": [],
        "assignments": {"inputs": [], "outputs": [], "auxiliary": []},
        "diagnostics": [],
    }
    collection_provenance: dict[str, Any] = {
        "completeness": "complete",
        "fingerprints": {"inputs": _INPUT_FINGERPRINT},
    }
    if include_execution_context:
        execution_context = {
            "declared": {
                "model": "model.joblib",
                "target": "score",
                "dataset": None,
            },
            "effective": {
                "model": effective_model,
                "target": effective_target,
                "dataset": effective_dataset,
            },
            "overrides": {
                "model": model_overridden,
                "target": effective_target != "score",
                "dataset": dataset_overridden,
            },
        }
        collection_provenance["execution_context"] = execution_context
        report["provenance"]["execution_context"] = json.loads(
            json.dumps(execution_context)
        )
    return {
        "schema": "toetra.verification-report-collection",
        "schema_version": 6,
        "report_count": 1,
        "provenance": collection_provenance,
        "reports": [report],
    }


def _write_report(tmp_path: Path, payload: dict[str, Any]) -> Path:
    path = tmp_path / "verification.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _install_plan(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, Any]:
    task = object()
    plan = SimpleNamespace(
        provenance=SimpleNamespace(
            completeness=SimpleNamespace(value="complete"),
            input_fingerprint=_INPUT_FINGERPRINT,
        ),
        properties=(SimpleNamespace(index=0, task=task),),
        model=object(),
        schema=object(),
        consumed_paths=(
            (tmp_path / "policy.toetra").resolve(),
            (tmp_path / "model.joblib").resolve(),
        ),
    )
    captured: dict[str, Any] = {}

    def build_plan(*args: object, **kwargs: object) -> object:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return plan

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        build_plan,
    )
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.property_fingerprint",
        lambda _task, *, property_index: _PROPERTY_FINGERPRINT,
    )
    return captured


def _consistent_replay() -> CounterexampleReplay:
    return CounterexampleReplay(
        property_index=0,
        points={},
        relation_satisfied=None,
        assertion_satisfied=False,
        expected_assertion_satisfied=False,
        tolerance=1e-9,
    )


def test_archived_replay_returns_stable_json_without_solving(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    captured = _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        lambda *args, **kwargs: _consistent_replay(),
    )

    result = replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
    )

    assert result.exit_code == 0
    payload = result.to_dict()
    assert payload["schema"] == REPLAY_COLLECTION_SCHEMA
    assert payload["schema_version"] == REPLAY_COLLECTION_SCHEMA_VERSION
    assert payload["conclusion"] == "consistent"
    assert payload["results"][0]["formal_status"] == "counterexample"
    assert captured["kwargs"]["require_translation"] is False


def test_archived_effective_target_is_reused_when_cli_override_is_omitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(
        tmp_path,
        _payload(effective_target="risk_score"),
    )
    captured = _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        lambda *args, **kwargs: _consistent_replay(),
    )

    replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=None,
    )

    context = captured["kwargs"]["execution_context"]
    assert context.effective_target == "risk_score"
    assert captured["kwargs"]["model"] is None


def test_replay_uses_archived_identity_with_a_relocated_model_locator(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(
        tmp_path,
        _payload(
            effective_model="runs/original/model.joblib",
            model_overridden=True,
        ),
    )
    captured = _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        lambda *args, **kwargs: _consistent_replay(),
    )
    relocated = tmp_path / "relocated" / "model.joblib"

    replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=relocated,
    )

    context = captured["kwargs"]["execution_context"]
    assert context.effective_model_reference == "runs/original/model.joblib"
    assert captured["kwargs"]["model"] == relocated


def test_replay_rejects_a_target_different_from_archived_context(
    tmp_path: Path,
) -> None:
    report = _write_report(
        tmp_path,
        _payload(effective_target="risk_score"),
    )

    with pytest.raises(VerificationConfigurationError) as caught:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            target="another_score",
        )

    assert caught.value.code == "REPLAY_EXECUTION_CONTEXT_MISMATCH"


def test_legacy_archive_uses_declared_header_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(
        tmp_path,
        _payload(include_execution_context=False),
    )
    policy = tmp_path / "policy.toetra"
    policy.write_text(
        'model := "model.joblib"\ntarget := score\n\n'
        "[BOUND]:\nforall x0 => target[x0] <= 7 using Z3\n",
        encoding="utf-8",
    )
    captured = _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        lambda *args, **kwargs: _consistent_replay(),
    )
    relocated = tmp_path / "relocated.joblib"

    replay_archived_report(
        report,
        specification=policy,
        model=relocated,
    )

    context = captured["kwargs"]["execution_context"]
    assert context.effective_model_reference == "model.joblib"
    assert context.effective_target == "score"
    assert captured["kwargs"]["model"] == relocated


def test_default_selection_with_no_replayable_finding_is_inconclusive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload(status="proved"))
    _install_plan(monkeypatch, tmp_path)

    result = replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
    )

    assert result.exit_code == 2
    assert result.results == ()
    assert result.to_dict()["conclusion"] == "inconclusive"


def test_explicit_non_replayable_property_is_reported_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload(status="proved"))
    _install_plan(monkeypatch, tmp_path)

    result = replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
        property_indices=(0, 0),
    )

    assert result.exit_code == 2
    assert result.requested_properties == (0,)
    assert result.results[0].conclusion == "unavailable"


def test_replay_unavailable_is_a_completed_inconclusive_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    _install_plan(monkeypatch, tmp_path)

    def unavailable(*args: object, **kwargs: object) -> CounterexampleReplay:
        raise ReplayUnavailableError("missing archived point")

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        unavailable,
    )

    result = replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
    )

    assert result.exit_code == 2
    assert result.results[0].availability == "unavailable"
    assert result.results[0].reason == "missing archived point"


def test_concrete_contradiction_uses_logical_failure_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    _install_plan(monkeypatch, tmp_path)
    inconsistent = CounterexampleReplay(
        property_index=0,
        points={},
        relation_satisfied=None,
        assertion_satisfied=True,
        expected_assertion_satisfied=False,
        tolerance=1e-9,
    )
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        lambda *args, **kwargs: inconsistent,
    )

    result = replay_archived_report(
        report,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
    )

    assert result.exit_code == 1
    assert result.results[0].conclusion == "inconsistent"


def test_replay_rejects_input_provenance_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        lambda *args, **kwargs: SimpleNamespace(
            provenance=SimpleNamespace(
                completeness=SimpleNamespace(value="complete"),
                input_fingerprint="sha256:" + "9" * 64,
            ),
            properties=(),
            model=object(),
            schema=object(),
            consumed_paths=(),
        ),
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
        )

    assert raised.value.code == "REPLAY_INPUT_FINGERPRINT_MISMATCH"


def test_replay_rejects_property_fingerprint_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    _install_plan(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "toetra._runtime.archived_replay.property_fingerprint",
        lambda _task, *, property_index: "sha256:" + "8" * 64,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
        )

    assert raised.value.code == "REPLAY_PROPERTY_FINGERPRINT_MISMATCH"


def test_replay_rejects_unknown_property_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _write_report(tmp_path, _payload())
    _install_plan(monkeypatch, tmp_path)

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
            property_indices=(7,),
        )

    assert raised.value.code == "REPLAY_PROPERTY_NOT_FOUND"


def test_replay_rejects_duplicate_archived_property_indices(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["reports"].append(dict(payload["reports"][0]))
    payload["report_count"] = 2
    report = _write_report(tmp_path, payload)
    _install_plan(monkeypatch, tmp_path)

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
        )

    assert raised.value.code == "REPLAY_REPORT_DUPLICATE_PROPERTY"


def test_archived_json_evidence_is_reconstructed_for_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload(status="witness")
    payload["reports"][0]["points"] = [
        {
            "name": "x0",
            "binding_kind": "quantified",
            "provenance": None,
            "inputs": [
                {
                    "name": "x0.a",
                    "raw_name": "x0.a",
                    "kind": "input",
                    "value": {"kind": "rational", "numerator": 3, "denominator": 2},
                    "point": "x0",
                    "binding_kind": "quantified",
                }
            ],
            "outputs": [
                {
                    "name": "score",
                    "raw_name": "score",
                    "kind": "output",
                    "value": 4.0,
                    "point": "x0",
                    "binding_kind": "quantified",
                    "target": "score",
                }
            ],
        }
    ]
    payload["reports"][0]["model_evaluations"] = [
        {
            "model_identity": "model",
            "point": "x0",
            "binding_kind": "quantified",
            "output_name": "score",
            "decision_policy": {
                "native_probability_threshold": None,
                "native_decision_threshold": None,
                "equality_label": None,
            },
            "predicted_label": None,
            "probabilities": [],
            "quantities": [
                {
                    "kind": "regression_value",
                    "semantic_profile_id": "regression.identity",
                    "value": 4.0,
                }
            ],
            "lowerings": [],
        }
    ]
    report_path = _write_report(tmp_path, payload)
    _install_plan(monkeypatch, tmp_path)
    captured: dict[str, Any] = {}

    def replay(report: object, **kwargs: object) -> CounterexampleReplay:
        captured["report"] = report
        return _consistent_replay()

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.replay_verification_report",
        replay,
    )

    result = replay_archived_report(
        report_path,
        specification=tmp_path / "policy.toetra",
        model=tmp_path / "model.joblib",
    )

    archived = captured["report"]
    assert archived.status is VerificationStatus.WITNESS
    assert archived.points[0].input_values == {"a": Fraction(3, 2)}
    assert archived.points[0].output_values == {"score": 4.0}
    assert archived.model_evaluations[0].quantity_values == {"regression_value": 4.0}
    assert result.exit_code == 0


def test_archived_replay_rejects_invalid_json_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = tmp_path / "verification.json"
    report.write_text("{", encoding="utf-8")
    called = False

    def build_plan(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        return object()

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        build_plan,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
        )

    assert raised.value.code == "REPLAY_REPORT_JSON_INVALID"
    assert called is False


def test_archived_replay_rejects_wrong_collection_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["schema"] = "other.schema"
    report = _write_report(tmp_path, payload)
    called = False

    def build_plan(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        return object()

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        build_plan,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
            model=tmp_path / "model.joblib",
        )

    assert raised.value.code == "REPLAY_REPORT_CONTRACT_INVALID"
    assert called is False


def test_archived_replay_rejects_report_context_mismatch_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["reports"][0]["provenance"]["execution_context"]["effective"][
        "target"
    ] = "other_score"
    report = _write_report(tmp_path, payload)
    called = False

    def build_plan(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        return object()

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        build_plan,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
        )

    assert raised.value.code == "REPLAY_REPORT_CONTRACT_INVALID"
    assert called is False


def test_archived_replay_rejects_malformed_execution_context_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _payload()
    payload["provenance"]["execution_context"]["overrides"]["model"] = "yes"
    report = _write_report(tmp_path, payload)
    called = False

    def build_plan(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        return object()

    monkeypatch.setattr(
        "toetra._runtime.archived_replay.build_executable_plan",
        build_plan,
    )

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
        )

    assert raised.value.code == "REPLAY_REPORT_CONTRACT_INVALID"
    assert called is False


def test_archived_replay_rejects_unflagged_effective_context_change(
    tmp_path: Path,
) -> None:
    payload = _payload()
    for provenance in (
        payload["provenance"],
        payload["reports"][0]["provenance"],
    ):
        provenance["execution_context"]["effective"]["model"] = "other.joblib"
    report = _write_report(tmp_path, payload)

    with pytest.raises(VerificationConfigurationError) as raised:
        replay_archived_report(
            report,
            specification=tmp_path / "policy.toetra",
        )

    assert raised.value.code == "REPLAY_REPORT_CONTRACT_INVALID"
