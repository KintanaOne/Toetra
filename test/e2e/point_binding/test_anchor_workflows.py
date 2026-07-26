from __future__ import annotations

import pandas as pd

from toetra._backends.results import VerificationStatus
from toetra._runtime.api import verify
from test.e2e.point_binding._helpers import build_linear_artifacts, source


def test_e2e_01_inline_anchor_direct_check_replays_real_model(tmp_path) -> None:
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a", "b"),
        coefficients=(2.0, 3.0),
        intercept=0.0,
    )

    session = verify(
        source("e2e_01_inline_anchor"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    finding = session.first_counterexample
    assert finding is not None
    assert finding.status is VerificationStatus.COUNTEREXAMPLE
    assert finding.point_values == {"x0": {"a": 1.0, "b": 2.0}}
    assert tuple(finding.output_values_by_point) == ("x0",)
    assert finding.report.points[0].binding_kind == "inline_anchor"
    assert finding.report.points[0].provenance is not None
    assert finding.report.points[0].provenance["kind"] == "inline_anchor"

    replay = finding.replay()
    assert replay.is_consistent is True
    assert bool(replay.assertion_satisfied) is False
    assert replay.inputs_by_point["x0"] == {"a": 1.0, "b": 2.0}


def test_e2e_02_referenced_anchor_check_at_keeps_lookup_provenance(tmp_path) -> None:
    metadata = pd.DataFrame({"id": ["R-00", "R-01", "R-02", "R-42", "R-99"]})
    artifacts = build_linear_artifacts(
        tmp_path,
        feature_names=("a",),
        coefficients=(2.0,),
        intercept=1.0,
        metadata=metadata,
    )

    session = verify(
        source("e2e_02_referenced_anchor"),
        model=artifacts.model_path,
        dataset=artifacts.dataset_path,
    )

    finding = session.first_counterexample
    assert finding is not None
    assert finding.point_values == {"row": {"a": 4.0}}
    assert "id" not in finding.point_values["row"]
    assert tuple(finding.output_values_by_point) == ("row",)

    point = finding.report.points[0]
    assert point.name == "row"
    assert point.binding_kind == "referenced_anchor"
    assert point.provenance is not None
    assert point.provenance["kind"] == "referenced_anchor"
    assert point.provenance["key"] == "id"
    assert point.provenance["lookup_value"] == "R-42"
    assert point.provenance["source_kind"] == "csv"

    replay = finding.replay()
    assert replay.is_consistent is True
    assert bool(replay.assertion_satisfied) is False
