from __future__ import annotations

from io import BytesIO, StringIO, TextIOWrapper

from toetra._backends.results import VerificationStatus
from toetra._runtime.api import verify
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema

_SOURCE = """
model := "model.joblib"
target := score

[LOGIC]:
forall x0
    with domain(x0.a: [0.0, 3.0])
    => target <= 7.0
    using Z3
"""


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
        target="score",
        task="regression",
        target_dtype=EnumDataType.FLOAT,
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def test_session_exposes_reports_results_and_sequence_protocol() -> None:
    session = verify(_SOURCE, schema=_schema())

    assert len(session) == 1
    assert session[0].report is session.reports[0]
    assert session[0].result is session.results[0]
    assert tuple(session) == session.executions
    assert session.reports[0].status is VerificationStatus.PROVED
    assert session.is_successful is True
    assert session.has_failures is False
    assert session.has_unknown is False
    assert session.exit_code == 0


def test_session_renders_and_serializes_report_collection(tmp_path) -> None:
    session = verify(_SOURCE, schema=_schema())

    text = session.to_text()
    assert "Toetra Verification Report" in text
    assert "PROVED" in text

    stream = StringIO()
    session.print(file=stream)
    assert stream.getvalue().rstrip() == text

    payload = session.to_dict()
    assert payload["schema"] == "toetra.verification-report-collection"
    assert payload["report_count"] == 1
    assert '"status": "proved"' in session.to_json()

    output = session.write_json(tmp_path / "reports" / "verification.json")
    assert output.is_file()
    assert output.read_text(encoding="utf-8").endswith("\n")

    html = session.to_html()
    assert "Toetra Verification Session" in html
    assert "LinearRegression · target score · 1 properties" in html
    assert session._repr_html_() == html

    html_output = session.write_html(tmp_path / "reports" / "verification.html")
    assert html_output.is_file()
    assert html_output.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_session_print_falls_back_to_ascii_for_legacy_windows_stream() -> None:
    session = verify(_SOURCE, schema=_schema())
    buffer = BytesIO()
    stream = TextIOWrapper(buffer, encoding="cp1252")

    session.print(file=stream)
    stream.flush()
    rendered = buffer.getvalue().decode("cp1252")

    assert "Toetra Verification Report" in rendered
    assert "PASS PROVED" in rendered
    assert "=" * 80 in rendered
    assert "━" not in rendered
