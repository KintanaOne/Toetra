from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from toetra._runtime.replay import (
        CounterexampleReplay,
        EvaluationReplay,
        PointReplay,
    )


def render_replay_text(replay: CounterexampleReplay) -> str:
    lines = [
        "Toetra Counterexample Replay",
        f"Property      : {replay.property_index + 1}",
        f"Consistent    : {'yes' if replay.is_consistent else 'no'}",
        f"Tolerance     : {replay.tolerance:g}",
    ]
    for name, point in replay.points.items():
        lines.append(f"Point {name}")
        lines.extend(f"  {field} = {value}" for field, value in point.inputs.items())
        for target in point.backend_outputs:
            lines.append(f"  {target} (Toetra) = {point.backend_outputs[target]}")
            lines.append(f"  {target} (model) = {point.model_outputs.get(target)}")
            lines.append(f"  absolute error = {point.absolute_errors.get(target)}")
        for evaluation in point.evaluations:
            lines.append(f"  Evaluation {evaluation.output_name}")
            if evaluation.formal_label is not None:
                lines.append(
                    f"    label: Toetra={evaluation.formal_label}, "
                    f"model={evaluation.model_label}, "
                    f"match={evaluation.label_matches}"
                )
            for label, formal in evaluation.formal_probabilities.items():
                lines.append(
                    f"    probability({label!r}): Toetra={formal}, "
                    f"model={evaluation.model_probabilities.get(label)}, "
                    f"error={evaluation.probability_errors.get(label)}"
                )
            for quantity, formal in evaluation.formal_quantities.items():
                lines.append(
                    f"    {quantity}: Toetra={formal}, "
                    f"model={evaluation.model_quantities.get(quantity)}, "
                    f"error={evaluation.quantity_errors.get(quantity)}"
                )
    lines.append(f"Relation      : {replay.relation_satisfied}")
    lines.append(f"Assertion     : {replay.assertion_satisfied}")
    return "\n".join(lines)


def render_replay_html(replay: CounterexampleReplay) -> str:
    status = "consistent" if replay.is_consistent else "mismatch"
    sections = "".join(_point_html(point) for point in replay.points.values())
    return (
        '<div class="toetra-replay" style="font-family:system-ui;'
        'border:1px solid #dbe3ee;border-radius:12px;padding:1rem">'
        f'<h3 style="margin-top:0">Counterexample replay · {status}</h3>'
        f"<p>Tolerance: <code>{replay.tolerance:g}</code></p>"
        f"{sections}"
        f"<p>Relation: <code>{replay.relation_satisfied}</code> · "
        f"Assertion: <code>{replay.assertion_satisfied}</code></p></div>"
    )


def _point_html(point: PointReplay) -> str:
    inputs = "".join(
        f"<li><code>{escape(name)}</code> = {escape(str(value))}</li>"
        for name, value in point.inputs.items()
    )
    rows = "".join(
        "<tr>"
        f"<td>{escape(name)}</td>"
        f"<td>{escape(str(point.backend_outputs[name]))}</td>"
        f"<td>{escape(str(point.model_outputs.get(name)))}</td>"
        f"<td>{escape(str(point.absolute_errors.get(name)))}</td>"
        "</tr>"
        for name in point.backend_outputs
    )
    evaluation_html = "".join(_evaluation_html(item) for item in point.evaluations)
    return (
        f"<h4>Point {escape(point.name)}</h4><ul>{inputs}</ul>"
        '<table style="border-collapse:collapse;width:100%">'
        "<thead><tr><th>Output</th><th>Toetra</th><th>Model</th>"
        f"<th>Absolute error</th></tr></thead><tbody>{rows}</tbody></table>"
        f"{evaluation_html}"
    )


def _evaluation_html(evaluation: EvaluationReplay) -> str:
    rows: list[str] = []
    if evaluation.formal_label is not None:
        rows.append(
            "<tr><td>label</td>"
            f"<td>{escape(str(evaluation.formal_label))}</td>"
            f"<td>{escape(str(evaluation.model_label))}</td>"
            f"<td>{escape(str(evaluation.label_matches))}</td></tr>"
        )
    for label, formal in evaluation.formal_probabilities.items():
        rows.append(
            f"<tr><td>probability({escape(str(label))})</td>"
            f"<td>{escape(str(formal))}</td>"
            f"<td>{escape(str(evaluation.model_probabilities.get(label)))}</td>"
            f"<td>{escape(str(evaluation.probability_errors.get(label)))}</td></tr>"
        )
    for kind, formal in evaluation.formal_quantities.items():
        rows.append(
            f"<tr><td>{escape(kind)}</td>"
            f"<td>{escape(str(formal))}</td>"
            f"<td>{escape(str(evaluation.model_quantities.get(kind)))}</td>"
            f"<td>{escape(str(evaluation.quantity_errors.get(kind)))}</td></tr>"
        )
    return (
        f"<h5>Evaluation {escape(evaluation.output_name)}</h5>"
        '<table style="border-collapse:collapse;width:100%">'
        "<thead><tr><th>View</th><th>Toetra</th><th>Model</th><th>Match/error</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )


def evaluation_record(evaluation: EvaluationReplay) -> dict[str, Any]:
    return {
        "output_name": evaluation.output_name,
        "formal_label": evaluation.formal_label,
        "model_label": evaluation.model_label,
        "label_matches": evaluation.label_matches,
        "formal_probabilities": dict(evaluation.formal_probabilities),
        "model_probabilities": dict(evaluation.model_probabilities),
        "probability_errors": dict(evaluation.probability_errors),
        "formal_quantities": dict(evaluation.formal_quantities),
        "model_quantities": dict(evaluation.model_quantities),
        "quantity_errors": dict(evaluation.quantity_errors),
    }
