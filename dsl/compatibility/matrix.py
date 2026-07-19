from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from dsl.compatibility.model import CompatibilityRule
from dsl.compatibility.registry import NumericCompatibilityRegistry

_WILDCARD = "*"
_NONE = "—"


@dataclass(frozen=True)
class CompatibilityMatrixRow:
    """Stable flattened view of one registry rule for public matrices."""

    rule_id: str
    framework: str
    model_family: str
    source_profile: str
    encoder: str
    backend_kind: str
    backend: str
    property_requirements: str
    support_status: str
    classification: str
    semantic_target: str
    conclusion_scope: str
    permitted_conclusions: str
    replay_required_for: str
    evidence_id: str

    @classmethod
    def from_rule(cls, rule: CompatibilityRule) -> CompatibilityMatrixRow:
        pattern = rule.pattern
        return cls(
            rule_id=rule.rule_id,
            framework=_versioned(
                pattern.framework_adapter_id,
                pattern.framework_version,
            ),
            model_family=_value(pattern.model_family),
            source_profile=_value(pattern.source_execution_profile_id),
            encoder=_versioned(
                pattern.model_encoder_id,
                pattern.model_encoder_version,
            ),
            backend_kind=_value(pattern.backend_kind),
            backend=_backend(pattern.backend_adapter_id, pattern.backend_profile_id),
            property_requirements=_items(pattern.required_property_tags),
            support_status=rule.support_status.value,
            classification=rule.classification.value,
            semantic_target=rule.semantic_target,
            conclusion_scope=rule.conclusion_scope.value,
            permitted_conclusions=_items(
                conclusion.value for conclusion in rule.permitted_conclusions
            ),
            replay_required_for=_items(
                conclusion.value for conclusion in rule.replay_required_for
            ),
            evidence_id=rule.evidence_id,
        )


def compatibility_matrix_rows(
    registry: NumericCompatibilityRegistry,
) -> tuple[CompatibilityMatrixRow, ...]:
    """Return deterministic public rows from the normative registry."""

    return tuple(
        CompatibilityMatrixRow.from_rule(rule)
        for rule in sorted(registry.all(), key=lambda item: item.rule_id)
    )


def render_compatibility_matrices_markdown(
    registry: NumericCompatibilityRegistry,
    *,
    title: str = "Numeric compatibility matrices",
) -> str:
    """Render support and semantic-guarantee matrices from one registry."""

    rows = compatibility_matrix_rows(registry)
    lines = [
        f"# {title}",
        "",
        "This page is generated from the normative numeric compatibility registry. ",
        "Do not edit the tables manually.",
        "",
        "## Support matrix",
        "",
        _table(
            (
                "Rule",
                "Framework",
                "Model family",
                "Source profile",
                "Encoder",
                "Backend kind",
                "Backend profile",
                "Property requirements",
                "Support",
            ),
            (
                (
                    row.rule_id,
                    row.framework,
                    row.model_family,
                    row.source_profile,
                    row.encoder,
                    row.backend_kind,
                    row.backend,
                    row.property_requirements,
                    row.support_status,
                )
                for row in rows
            ),
        ),
        "",
        "## Semantic guarantee matrix",
        "",
        _table(
            (
                "Rule",
                "Classification",
                "Semantic target",
                "Conclusion scope",
                "Permitted conclusions",
                "Replay required for",
                "Evidence",
            ),
            (
                (
                    row.rule_id,
                    row.classification,
                    row.semantic_target,
                    row.conclusion_scope,
                    row.permitted_conclusions,
                    row.replay_required_for,
                    row.evidence_id,
                )
                for row in rows
            ),
        ),
        "",
        "## Reading the matrices",
        "",
        "- `*` means that the rule intentionally matches any value on that axis.",
        "- Support describes implementation availability; it does not imply an exact guarantee.",
        "- The semantic target and conclusion scope define what a result is allowed to claim.",
        "- A route classified as `lossy` may still be executable when conclusions are explicitly limited to the declared semantic target.",
        "",
    ]
    return "\n".join(lines)


def write_compatibility_matrices_markdown(
    registry: NumericCompatibilityRegistry,
    path: str | Path,
) -> Path:
    """Write generated matrices and return the resolved output path."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_compatibility_matrices_markdown(registry),
        encoding="utf-8",
    )
    return output


def _versioned(identifier: str | None, version: str | None) -> str:
    base = _value(identifier)
    if version is None:
        return base
    return f"{base}@{version}"


def _backend(adapter: str | None, profile: str | None) -> str:
    if adapter is None and profile is None:
        return _WILDCARD
    return f"{_value(adapter)} / {_value(profile)}"


def _value(value: str | None) -> str:
    return value if value is not None else _WILDCARD


def _items(values: Iterable[object]) -> str:
    items = sorted(str(value) for value in values)
    return ", ".join(items) if items else _NONE


def _table(
    headers: tuple[str, ...],
    rows: Iterable[tuple[object, ...]],
) -> str:
    rendered_rows = [tuple(_escape_cell(value) for value in row) for row in rows]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rendered_rows)
    if not rendered_rows:
        lines.append("| " + " | ".join(_NONE for _ in headers) + " |")
    return "\n".join(lines)


def _escape_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
