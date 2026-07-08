from __future__ import annotations

from dataclasses import dataclass

import pytest

from dsl.ir.ir1.nodes import ComparisonIR, ScopeIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.language.vocabulary.operators import EnumComparisonOperator
from model.detector.model_framework import EnumModelFramework
from model.encoder import (
    InvalidModelAssumptionError,
    ModelEncoderFactory,
    ModelEncoderRegistry,
    UnsupportedModelEncoderError,
    validate_model_assumptions,
)
from model.encoder.context import ModelEncodingContext
from model.schema.model_schema import ModelSchema


@dataclass
class FakeModelEncoder:
    assumptions: tuple[AssumptionIR2, ...] = ()

    def encode(
        self,
        schema: ModelSchema,
        scope: ScopeIR,
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        return self.assumptions


def _schema(model_type: str = "FakeModel") -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type=model_type,
        features={},
        target="target",
        task="classification",
    )


def _scope() -> ScopeIR:
    return ScopeIR(
        kind="pointwise",
        variables={"x": "anchor"},
        neighborhood=None,
        domain=None,
    )


def _model_assumption(
    source: AssumptionSource = AssumptionSource.MODEL,
) -> AssumptionIR2:
    atom = ComparisonIR(
        entity="x",
        feature="a",
        op=EnumComparisonOperator.LTE,
        value=1,
    )
    return AssumptionIR2(
        source=source,
        formula=NNFFormulaIR2(expression=atom),
        description="fake model assumption",
    )


def test_registry_prefers_exact_encoder_over_framework_fallback() -> None:
    fallback = FakeModelEncoder()
    exact = FakeModelEncoder(assumptions=(_model_assumption(),))

    registry = ModelEncoderRegistry()
    registry.register(EnumModelFramework.SKLEARN, fallback)
    registry.register(EnumModelFramework.SKLEARN, exact, model_type="ExactModel")

    assert (
        registry.require(EnumModelFramework.SKLEARN, model_type="ExactModel") is exact
    )
    assert (
        registry.require(EnumModelFramework.SKLEARN, model_type="OtherModel")
        is fallback
    )


def test_factory_encodes_and_validates_model_assumptions() -> None:
    assumption = _model_assumption()
    registry = ModelEncoderRegistry()
    registry.register(
        EnumModelFramework.SKLEARN,
        FakeModelEncoder(assumptions=(assumption,)),
        model_type="FakeModel",
    )

    factory = ModelEncoderFactory(registry)

    assert factory.encode(_schema(), _scope()) == (assumption,)


def test_factory_raises_when_no_encoder_is_registered() -> None:
    factory = ModelEncoderFactory(ModelEncoderRegistry())

    with pytest.raises(UnsupportedModelEncoderError):
        factory.create(_schema())


def test_validate_model_assumptions_rejects_non_model_source() -> None:
    with pytest.raises(InvalidModelAssumptionError):
        validate_model_assumptions((_model_assumption(AssumptionSource.USER),))
