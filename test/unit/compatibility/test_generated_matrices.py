from __future__ import annotations

from pathlib import Path

from dsl.compatibility.defaults import create_default_numeric_compatibility_registry
from dsl.compatibility.matrix import (
    compatibility_matrix_rows,
    render_compatibility_matrices_markdown,
)


def test_default_registry_generates_deterministic_support_and_guarantee_matrices() -> (
    None
):
    registry = create_default_numeric_compatibility_registry()

    first = render_compatibility_matrices_markdown(registry)
    second = render_compatibility_matrices_markdown(registry)

    assert first == second
    assert "## Support matrix" in first
    assert "## Semantic guarantee matrix" in first
    assert "sklearn" in first
    assert "z3 / smt_real_affine_exact" in first
    assert "lossy" in first
    assert "semantic_target_only" in first


def test_default_matrix_rows_are_sorted_by_rule_id() -> None:
    rows = compatibility_matrix_rows(create_default_numeric_compatibility_registry())

    assert [row.rule_id for row in rows] == sorted(row.rule_id for row in rows)


def test_checked_in_matrix_matches_the_default_registry() -> None:
    path = (
        Path(__file__).parents[3]
        / "docs"
        / "generated"
        / "numeric-compatibility-matrices.md"
    )

    assert path.read_text(encoding="utf-8") == render_compatibility_matrices_markdown(
        create_default_numeric_compatibility_registry()
    )


def test_generated_matrix_accepts_non_sklearn_non_smt_rows() -> None:
    from dsl.compatibility.enums import (
        CompatibilityClassification,
        ConclusionKind,
        ConclusionScope,
        SupportStatus,
    )
    from dsl.compatibility.model import CompatibilityRule, CompatibilityRulePattern
    from dsl.compatibility.registry import NumericCompatibilityRegistry

    registry = NumericCompatibilityRegistry()
    registry.register(
        CompatibilityRule(
            rule_id="pytorch-relu-abstract-interpretation",
            pattern=CompatibilityRulePattern(
                framework_adapter_id="pytorch",
                model_family="relu_network",
                model_encoder_id="forml.relu-network",
                model_encoder_version="2",
                backend_kind="abstract_interpretation",
                backend_adapter_id="eran",
                backend_profile_id="deeppoly",
            ),
            support_status=SupportStatus.EXPERIMENTAL,
            classification=CompatibilityClassification.SOUND_OVER_APPROXIMATION,
            semantic_target="pytorch.relu.source-semantics",
            evidence_id="paper:deeppoly",
            permitted_conclusions=frozenset({ConclusionKind.UNIVERSAL_PROOF}),
            conclusion_scope=ConclusionScope.SOURCE_ARTIFACT,
        )
    )

    rendered = render_compatibility_matrices_markdown(registry)

    assert "pytorch" in rendered
    assert "relu_network" in rendered
    assert "abstract_interpretation" in rendered
    assert "eran / deeppoly" in rendered
    assert "sound_over_approximation" in rendered
    assert "source_artifact" in rendered
