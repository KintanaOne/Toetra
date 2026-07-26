from __future__ import annotations

import inspect

import pytest

from toetra._backends.defaults import create_default_backend_registry
from toetra._backends.router import BackendRouter
from toetra._backends.z3_backend.translator import Z3Translator
from toetra._compiler.ir.ir1.model_quantities import ModelQuantityExpressionIR
from toetra._compiler.ir.ir1.nodes import ComparisonIR
from toetra._compiler.ir.ir2.run_ir2 import run_ir2, run_ir2_with_model_schema
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.semantics.errors import (
    MissingModelSemanticsError,
    UnsupportedModelSemanticProfileError,
)
from tests.support.model_semantics import (
    label_property,
    make_binary_logistic_schema,
)


class _NoopEncoderFactory:
    def encode(self, schema, evaluations, *, context=None):  # noqa: ANN001, ANN201
        del schema, evaluations, context
        return ()


def test_schema_aware_pipeline_lowers_before_ir2_and_retains_evidence() -> None:
    schema = make_binary_logistic_schema()

    task = run_ir2_with_model_schema(
        label_property(),
        schema=schema,
        model_context=ModelEncodingContext(include_model_constraints=False),
        encoder_factory=_NoopEncoderFactory(),  # type: ignore[arg-type]
    )[0]

    comparison = task.spec_formula.expression
    assert isinstance(comparison, ComparisonIR)
    assert isinstance(comparison.left, ModelQuantityExpressionIR)
    assert task.requirements.requires_model_semantic_quantities is True
    assert len(task.model_evaluations) == 1
    assert len(task.lowering_evidence) == 1
    assert task.lowering_evidence[0].source_intent.label_value == "approved"


def test_generic_ir2_route_rejects_unlowered_observable_properties() -> None:
    with pytest.raises(MissingModelSemanticsError, match="model schema"):
        run_ir2(label_property())


def test_unknown_model_family_is_rejected_before_encoder_or_backend() -> None:
    schema = make_binary_logistic_schema(model_family="unknown_binary_family")

    with pytest.raises(
        UnsupportedModelSemanticProfileError, match="unknown_binary_family"
    ):
        run_ir2_with_model_schema(
            label_property(),
            schema=schema,
            model_context=ModelEncodingContext(include_model_constraints=False),
            encoder_factory=_NoopEncoderFactory(),  # type: ignore[arg-type]
        )


def test_z3_profile_accepts_lowered_model_semantic_quantities() -> None:
    schema = make_binary_logistic_schema()
    source = label_property().rstrip() + " using Z3\n"
    task = run_ir2_with_model_schema(
        source,
        schema=schema,
        model_context=ModelEncodingContext(include_model_constraints=False),
        encoder_factory=_NoopEncoderFactory(),  # type: ignore[arg-type]
    )[0]

    route = BackendRouter(create_default_backend_registry()).route(task)

    assert route.backend.value == "Z3"
    assert route.capabilities.supports_model_semantic_quantities is True


def test_z3_translator_contains_no_classification_framework_semantics() -> None:
    source = inspect.getsource(Z3Translator)
    forbidden = (
        "LogisticRegression",
        "predicted_label",
        "class_probability",
        "predict_proba",
        "decision_function",
    )
    assert not any(token in source for token in forbidden)
