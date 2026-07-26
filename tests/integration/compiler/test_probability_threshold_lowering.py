from __future__ import annotations

from toetra._compatibility.descriptors import PropertyNumericRequirements
from toetra._compiler.ir.ir2.run_ir2 import run_ir2_with_model_schema
from tests.support.binary_classification import (
    binary_probability_property,
    make_sklearn_logistic_schema,
)


def test_non_exact_probability_threshold_sets_ir2_requirements() -> None:
    task = run_ir2_with_model_schema(
        binary_probability_property(threshold="0.8", backend=None),
        schema=make_sklearn_logistic_schema(),
    )[0]

    assert task.requirements.requires_logistic_probability_threshold is True
    assert task.requirements.requires_transcendental_threshold_lowering is True
    tags = PropertyNumericRequirements.from_ir2(task.requirements).tags
    assert "logistic_probability_threshold" in tags
    assert "transcendental_threshold_lowering" in tags
    assert len(task.lowering_evidence) == 1


def test_exact_half_threshold_does_not_require_transcendental_lowering() -> None:
    task = run_ir2_with_model_schema(
        binary_probability_property(threshold="0.5", backend=None),
        schema=make_sklearn_logistic_schema(),
    )[0]

    assert task.requirements.requires_logistic_probability_threshold is True
    assert task.requirements.requires_transcendental_threshold_lowering is False
