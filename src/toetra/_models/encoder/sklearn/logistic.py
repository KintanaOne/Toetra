from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, cast

from toetra._compatibility.descriptors import ModelEncoderDescriptor
from toetra._compiler.ir.ir1.model_quantities import (
    EnumModelQuantityKind,
    ModelQuantityExpressionIR,
)
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineModelQuantityConstraintIR2,
    AffineTermIR2,
)
from toetra._compiler.ir.ir2.nodes import AssumptionIR2, NNFFormulaIR2
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.encoder.context import ModelEncodingContext
from toetra._models.encoder.errors import (
    MissingModelParameterError,
    UnsupportedModelParameterError,
)
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema
from toetra._models.families import (
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)


class SklearnLogisticRegressionEncoder:
    """Encode the latent affine quantity of direct binary LogisticRegression.

    The encoder does not define label or probability semantics. P21.5 already
    lowered public label intent to an oriented decision quantity. This bridge
    only materializes the model equation that defines that quantity per point.
    """

    supported_model_types = frozenset({"LogisticRegression"})
    compatibility = ModelEncoderDescriptor(
        encoder_id="toetra.binary-logistic-affine-equation",
        version="1",
        semantic_target="toetra.oriented-decision-value",
    )

    def encode(
        self,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        context = context or ModelEncodingContext()
        if (
            not context.include_model_constraints
            or not context.include_output_constraints
        ):
            return ()

        self._validate_schema(schema)
        unique_evaluations = tuple(dict.fromkeys(evaluations))
        if not unique_evaluations:
            return ()

        linear = self._linear_metadata(schema)
        feature_names = self._feature_names(schema, linear)
        coefficients = self._binary_coefficients(linear)
        intercept = self._binary_intercept(linear)
        self._validate_finite(coefficients=coefficients, intercept=intercept)

        if len(coefficients) != len(feature_names):
            raise UnsupportedModelParameterError(
                "Logistic coefficient count does not match schema feature count: "
                f"{len(coefficients)} coefficients for {len(feature_names)} features."
            )

        assumptions: list[AssumptionIR2] = []
        for evaluation in unique_evaluations:
            self._validate_evaluation(schema, evaluation)
            point = evaluation.point
            quantity = ModelQuantityExpressionIR(
                evaluation=evaluation,
                quantity_kind=EnumModelQuantityKind.ORIENTED_DECISION_VALUE,
                semantic_profile_id=BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
            )
            expression = AffineExpressionIR2(
                terms=tuple(
                    AffineTermIR2(
                        entity=point.name,
                        feature=feature_name,
                        coefficient=coefficient,
                        point=point,
                    )
                    for feature_name, coefficient in zip(feature_names, coefficients)
                ),
                bias=intercept,
            )
            atom = AffineModelQuantityConstraintIR2(
                quantity=quantity,
                op=EnumComparisonOperator.EQ,
                expression=expression,
                evaluation=evaluation,
                metadata={
                    "framework": schema.framework.value,
                    "model_type": schema.model_type,
                    "task": schema.task,
                    "model_family": BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
                    "semantic_profile_id": (BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID),
                    "model_identity": evaluation.model_identity,
                    "point": point.name,
                    "output_name": evaluation.output_name,
                    "native_probability_threshold": "0.5",
                    "native_decision_threshold": "0",
                    "threshold_source": "recognized_model_profile",
                },
            )
            assumptions.append(
                AssumptionIR2(
                    source=AssumptionSource.MODEL,
                    formula=NNFFormulaIR2(expression=atom),
                    description=(
                        "sklearn binary logistic oriented decision equation "
                        f"for point {point.name}"
                    ),
                    metadata={
                        "encoder": self.__class__.__name__,
                        "model_type": schema.model_type,
                        "model_family": BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
                        "model_identity": evaluation.model_identity,
                        "point": point.name,
                        "point_binding_kind": point.binding_kind,
                        "output_name": schema.output_name,
                    },
                )
            )
        return tuple(assumptions)

    @staticmethod
    def _validate_schema(schema: ModelSchema) -> None:
        if schema.model_type != "LogisticRegression":
            raise UnsupportedModelParameterError(
                "SklearnLogisticRegressionEncoder supports only direct "
                "LogisticRegression schemas."
            )
        if schema.task != "classification":
            raise UnsupportedModelParameterError(
                "SklearnLogisticRegressionEncoder requires classification."
            )
        output = schema.output_schema
        if not isinstance(output, ClassificationOutputSchema):
            raise UnsupportedModelParameterError(
                "Binary logistic encoding requires a classification output schema."
            )
        if len(output.labels) != 2:
            raise UnsupportedModelParameterError(
                "Binary logistic encoding requires exactly two ordered labels."
            )
        if not output.probability_available:
            raise UnsupportedModelParameterError(
                "Binary logistic encoding requires class probability observability."
            )
        if output.decision_policy is None:
            raise UnsupportedModelParameterError(
                "Binary logistic encoding requires the recognized native decision "
                "policy; custom or wrapped threshold policies are unsupported."
            )
        if (
            framework_model_descriptor(schema).model_family
            != BINARY_LOGISTIC_AFFINE_MODEL_FAMILY
        ):
            raise UnsupportedModelParameterError(
                "Model schema is not classified as the binary logistic affine "
                "model family."
            )

    @staticmethod
    def _validate_evaluation(
        schema: ModelSchema,
        evaluation: ModelEvaluationIR,
    ) -> None:
        if evaluation.output_name != schema.output_name:
            raise UnsupportedModelParameterError(
                "Requested evaluation output does not match ModelSchema.output_name: "
                f"{evaluation.output_name!r} != {schema.output_name!r}."
            )
        if not evaluation.model_identity:
            raise UnsupportedModelParameterError(
                "Requested model evaluation is missing its model identity."
            )

    @staticmethod
    def _linear_metadata(schema: ModelSchema) -> dict[str, Any]:
        raw = schema.metadata.get("linear")
        if not isinstance(raw, dict):
            raise MissingModelParameterError(
                "A fitted direct LogisticRegression must expose learned "
                "coef_ and intercept_ metadata."
            )
        if "coef" not in raw or "intercept" not in raw:
            raise MissingModelParameterError(
                "Logistic linear metadata must contain 'coef' and 'intercept'."
            )
        return raw

    @staticmethod
    def _feature_names(
        schema: ModelSchema,
        linear: dict[str, Any],
    ) -> tuple[str, ...]:
        raw = linear.get("feature_names")
        if raw is None:
            return tuple(schema.features.keys())
        if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
            raise UnsupportedModelParameterError(
                "linear.feature_names must be a sequence of strings."
            )
        names = tuple(str(value) for value in raw)
        if len(set(names)) != len(names):
            raise UnsupportedModelParameterError(
                "Logistic feature names must be unique."
            )
        if names != tuple(schema.features.keys()):
            raise UnsupportedModelParameterError(
                "Logistic feature order must match the normalized schema order."
            )
        return names

    @staticmethod
    def _binary_coefficients(linear: dict[str, Any]) -> tuple[float, ...]:
        coef = linear["coef"]
        if not isinstance(coef, Sequence) or isinstance(coef, (str, bytes)):
            raise UnsupportedModelParameterError(
                "linear.coef must be a one-row sequence."
            )
        rows = cast(Sequence[Any], coef)
        if len(rows) != 1:
            raise UnsupportedModelParameterError(
                "Multiclass or multi-output logistic coefficients are unsupported."
            )
        row = rows[0]
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)):
            raise UnsupportedModelParameterError(
                "Binary logistic coefficients must contain exactly one row."
            )
        return tuple(float(value) for value in cast(Sequence[Any], row))

    @staticmethod
    def _binary_intercept(linear: dict[str, Any]) -> float:
        intercept = linear["intercept"]
        if not isinstance(intercept, Sequence) or isinstance(intercept, (str, bytes)):
            raise UnsupportedModelParameterError(
                "Binary logistic intercept must be a one-item sequence."
            )
        if len(intercept) != 1:
            raise UnsupportedModelParameterError(
                "Multiclass or multi-output logistic intercepts are unsupported."
            )
        return float(intercept[0])

    @staticmethod
    def _validate_finite(
        *,
        coefficients: tuple[float, ...],
        intercept: float,
    ) -> None:
        if not all(math.isfinite(value) for value in coefficients):
            raise UnsupportedModelParameterError(
                "Logistic coefficients must all be finite."
            )
        if not math.isfinite(intercept):
            raise UnsupportedModelParameterError("Logistic intercept must be finite.")
