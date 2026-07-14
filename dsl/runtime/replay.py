from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any, Mapping, Protocol, cast

import pandas as pd

from dsl.reporting.model import VerificationReport
from dsl.reporting.values import python_report_value
from dsl.runtime.errors import ReplayUnavailableError
from model.schema.model_schema import ModelSchema


class _Predictor(Protocol):
    def predict(self, values: Any) -> Any: ...


@dataclass(frozen=True)
class CounterexampleReplay:
    """Comparison between a formal assignment and the original model output."""

    property_index: int
    inputs: Mapping[str, Any]
    backend_outputs: Mapping[str, Any]
    model_outputs: Mapping[str, Any]
    absolute_errors: Mapping[str, float | None]
    tolerance: float

    @property
    def max_absolute_error(self) -> float | None:
        errors = [value for value in self.absolute_errors.values() if value is not None]
        return max(errors) if errors else None

    @property
    def is_consistent(self) -> bool:
        return all(
            error is not None and error <= self.tolerance
            for error in self.absolute_errors.values()
        )

    def to_record(self) -> dict[str, Any]:
        """Return one flat record convenient for tables and data frames."""

        record = dict(self.inputs)
        for name, value in self.backend_outputs.items():
            record[f"forml_{name}"] = value
        for name, value in self.model_outputs.items():
            record[f"model_{name}"] = value
        for name, value in self.absolute_errors.items():
            record[f"absolute_error_{name}"] = value
        record["is_consistent"] = self.is_consistent
        return record

    def to_dataframe(self) -> pd.DataFrame:
        """Return the replay as a one-row pandas data frame."""

        return pd.DataFrame([self.to_record()])

    def to_text(self) -> str:
        """Render a concise user-facing replay summary."""

        lines = [
            "FORML Counterexample Replay",
            f"Property      : {self.property_index + 1}",
            f"Consistent    : {'yes' if self.is_consistent else 'no'}",
            f"Tolerance     : {self.tolerance:g}",
            "Inputs",
        ]
        lines.extend(f"  {name} = {value}" for name, value in self.inputs.items())
        lines.append("Outputs")
        for name in self.backend_outputs:
            lines.append(f"  {name} (FORML) = {self.backend_outputs[name]}")
            lines.append(f"  {name} (model) = {self.model_outputs.get(name)}")
            lines.append(f"  absolute error = {self.absolute_errors.get(name)}")
        return "\n".join(lines)

    def to_html(self) -> str:
        """Render a notebook-safe HTML card for the replay."""

        status = "consistent" if self.is_consistent else "mismatch"
        rows = "".join(
            "<tr>"
            f"<td>{escape(name)}</td>"
            f"<td>{escape(str(self.backend_outputs[name]))}</td>"
            f"<td>{escape(str(self.model_outputs.get(name)))}</td>"
            f"<td>{escape(str(self.absolute_errors.get(name)))}</td>"
            "</tr>"
            for name in self.backend_outputs
        )
        inputs = "".join(
            f"<li><code>{escape(name)}</code> = {escape(str(value))}</li>"
            for name, value in self.inputs.items()
        )
        return (
            '<div class="forml-replay" style="font-family:system-ui;'
            'border:1px solid #dbe3ee;border-radius:12px;padding:1rem">'
            f'<h3 style="margin-top:0">Counterexample replay · {status}</h3>'
            f"<p>Tolerance: <code>{self.tolerance:g}</code></p>"
            f"<ul>{inputs}</ul>"
            '<table style="border-collapse:collapse;width:100%">'
            "<thead><tr><th>Output</th><th>FORML</th><th>Model</th>"
            "<th>Absolute error</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>"
        )

    def _repr_html_(self) -> str:
        return self.to_html()


def replay_verification_report(
    report: VerificationReport,
    *,
    schema: ModelSchema,
    model: object,
    tolerance: float = 1e-9,
) -> CounterexampleReplay:
    """Replay one report assignment against a model exposing ``predict``."""

    predictor = getattr(model, "predict", None)
    if not callable(predictor):
        raise ReplayUnavailableError(
            "The supplied model does not expose a callable 'predict' method"
        )
    if not report.inputs:
        raise ReplayUnavailableError(
            "The report does not contain input assignments to replay"
        )
    if not report.outputs:
        raise ReplayUnavailableError(
            "The report does not contain a model output to compare"
        )

    input_values = report.input_values
    missing = [name for name in schema.features if name not in input_values]
    if missing:
        raise ReplayUnavailableError(
            "The backend assignment does not contain every model feature: "
            + ", ".join(missing)
        )

    ordered_inputs = {name: input_values[name] for name in schema.features}
    frame = pd.DataFrame([ordered_inputs])
    raw_prediction = cast(_Predictor, model).predict(frame)
    prediction = _first_prediction(raw_prediction)

    backend_outputs = report.output_values
    if schema.target not in backend_outputs:
        raise ReplayUnavailableError(
            f"The backend result does not contain target {schema.target!r}"
        )

    model_outputs = {schema.target: python_report_value(prediction)}
    absolute_errors = {
        schema.target: _absolute_error(
            backend_outputs[schema.target],
            model_outputs[schema.target],
        )
    }
    return CounterexampleReplay(
        property_index=report.property_index,
        inputs=ordered_inputs,
        backend_outputs=backend_outputs,
        model_outputs=model_outputs,
        absolute_errors=absolute_errors,
        tolerance=tolerance,
    )


def _first_prediction(value: Any) -> Any:
    iloc = getattr(value, "iloc", None)
    if iloc is not None:
        return value.iloc[0]
    try:
        return value[0]
    except (IndexError, KeyError, TypeError):
        return value


def _absolute_error(left: Any, right: Any) -> float | None:
    try:
        return abs(float(left) - float(right))
    except (TypeError, ValueError):
        return 0.0 if left == right else None
