import pytest

from dsl.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR
from dsl.semantic.context.evaluations import (
    ModelEvaluationIdentity,
    ModelEvaluationRegistry,
)
from dsl.semantic.symbols.point import PointBindingKind, PointSymbol


def _point(name: str = "x0") -> PointSymbol:
    return PointSymbol(
        name=name,
        binding_kind=PointBindingKind.UNIVERSAL,
        declaration=object(),
    )


def _point_ir(name: str = "x0") -> PointBindingIR:
    return PointBindingIR(name=name, binding_kind="quantified")


def test_semantic_evaluation_uses_output_name_as_source_of_truth() -> None:
    evaluation = ModelEvaluationIdentity(
        model_identity="model",
        point=_point(),
        output_name="decision",
    )

    assert evaluation.output_name == "decision"
    assert evaluation.target_name == "decision"


def test_semantic_evaluation_accepts_legacy_target_name_projection() -> None:
    evaluation = ModelEvaluationIdentity(
        model_identity="model",
        point=_point(),
        target_name="score",
    )

    assert evaluation.output_name == "score"


def test_registry_reuses_same_model_point_and_output_port() -> None:
    registry = ModelEvaluationRegistry()
    point = _point()

    first = registry.intern(
        model_identity="model",
        point=point,
        output_name="decision",
    )
    second = registry.intern(
        model_identity="model",
        point=point,
        target_name="decision",
    )

    assert first is second
    assert registry.all() == (first,)


def test_registry_keeps_output_port_in_evaluation_identity() -> None:
    registry = ModelEvaluationRegistry()
    point = _point()

    first = registry.intern(
        model_identity="model",
        point=point,
        output_name="decision",
    )
    second = registry.intern(
        model_identity="model",
        point=point,
        output_name="auxiliary",
    )

    assert first is not second
    assert registry.all() == (first, second)


def test_ir1_evaluation_exposes_legacy_target_name_projection() -> None:
    evaluation = ModelEvaluationIR(
        model_identity="model",
        point=_point_ir(),
        output_name="decision",
    )

    assert evaluation.output_name == "decision"
    assert evaluation.target_name == "decision"


def test_evaluation_rejects_conflicting_compatibility_names() -> None:
    with pytest.raises(ValueError, match="must match"):
        ModelEvaluationIdentity(
            model_identity="model",
            point=_point(),
            output_name="decision",
            target_name="score",
        )
