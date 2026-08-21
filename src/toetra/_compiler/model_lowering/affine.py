from __future__ import annotations

from toetra._compatibility.descriptors import ModelEncoderDescriptor
from toetra._compiler.ir.ir1.model_quantities import (
    EnumModelQuantityKind,
    ModelQuantityExpressionIR,
)
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR
from toetra._compiler.ir.ir2.enums import AssumptionSource
from toetra._compiler.ir.ir2.dsl.nodes import AssumptionIR2, NNFFormulaIR2
from toetra._compiler.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineModelQuantityConstraintIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
)
from toetra._compiler.model_lowering.errors import (
    InvalidModelIRLoweringError,
    UnsupportedModelIRLoweringError,
)
from toetra._compiler.model_lowering.context import ModelLoweringContext
from toetra._language.vocabulary.operators import EnumComparisonOperator
from toetra._models.compatibility import framework_model_descriptor
from toetra._models.families import (
    AFFINE_REGRESSION_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
    BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
)
from toetra._models.ir.affine import AffineModelIR
from toetra._models.ir.base import ModelIR
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ClassificationOutputSchema


class AffineModelIRLowerer:
    """Lower one reusable affine computation for requested model evaluations."""

    def descriptor(self, schema: ModelSchema) -> ModelEncoderDescriptor:
        if self._is_affine_regression(schema):
            return ModelEncoderDescriptor(
                encoder_id="toetra.affine-equation",
                version="1",
                semantic_target="toetra.real_affine_extracted_model",
            )
        if self._is_binary_logistic(schema):
            return ModelEncoderDescriptor(
                encoder_id="toetra.binary-logistic-affine-equation",
                version="1",
                semantic_target="toetra.oriented-decision-value",
            )
        raise UnsupportedModelIRLoweringError(
            "Affine Model IR has no lowering profile for "
            f"task={schema.task!r}, model_type={schema.model_type!r}."
        )

    def lower(
        self,
        model_ir: ModelIR,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
        *,
        context: ModelLoweringContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        if not isinstance(model_ir, AffineModelIR):
            raise TypeError("AffineModelIRLowerer requires an AffineModelIR.")
        affine_ir = model_ir
        context = context or ModelLoweringContext()
        if (
            not context.include_model_constraints
            or not context.include_output_constraints
        ):
            return ()

        unique_evaluations = tuple(dict.fromkeys(evaluations))
        if not unique_evaluations:
            return ()
        self._validate_alignment(affine_ir, schema)

        if self._is_affine_regression(schema):
            return self._lower_regression(affine_ir, schema, unique_evaluations)
        if self._is_binary_logistic(schema):
            self._validate_binary_logistic_schema(schema)
            return self._lower_binary_logistic(
                affine_ir,
                schema,
                unique_evaluations,
            )
        raise UnsupportedModelIRLoweringError(
            "Affine Model IR has no supported semantic lowering for "
            f"task={schema.task!r}, model_type={schema.model_type!r}."
        )

    @staticmethod
    def _validate_alignment(model_ir: AffineModelIR, schema: ModelSchema) -> None:
        names = tuple(feature for feature, _coefficient in model_ir.terms)
        if names != schema.feature_names:
            raise InvalidModelIRLoweringError(
                "Affine Model IR term order must match ModelSchema.feature_names."
            )

    def _lower_regression(
        self,
        model_ir: AffineModelIR,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
    ) -> tuple[AssumptionIR2, ...]:
        assumptions: list[AssumptionIR2] = []
        for evaluation in evaluations:
            self._validate_evaluation(schema, evaluation)
            point = evaluation.point
            atom = AffineOutputConstraintIR2(
                output_entity="_model",
                output_feature=schema.output_name,
                op=EnumComparisonOperator.EQ,
                expression=self._expression(model_ir, evaluation),
                evaluation=evaluation,
                metadata={
                    "framework": schema.framework.value,
                    "model_type": schema.model_type,
                    "task": schema.task,
                    "model_identity": evaluation.model_identity,
                    "point": point.name,
                    "target": evaluation.output_name,
                },
            )
            assumptions.append(
                AssumptionIR2(
                    source=AssumptionSource.MODEL,
                    formula=NNFFormulaIR2(expression=atom),
                    description=(
                        "sklearn linear regression output equation "
                        f"for point {point.name}"
                    ),
                    metadata={
                        "encoder": "SklearnLinearRegressorEncoder",
                        "model_type": schema.model_type,
                        "model_identity": evaluation.model_identity,
                        "point": point.name,
                        "point_binding_kind": point.binding_kind,
                        "target": schema.output_name,
                    },
                )
            )
        return tuple(assumptions)

    def _lower_binary_logistic(
        self,
        model_ir: AffineModelIR,
        schema: ModelSchema,
        evaluations: tuple[ModelEvaluationIR, ...],
    ) -> tuple[AssumptionIR2, ...]:
        assumptions: list[AssumptionIR2] = []
        for evaluation in evaluations:
            self._validate_evaluation(schema, evaluation)
            point = evaluation.point
            quantity = ModelQuantityExpressionIR(
                evaluation=evaluation,
                quantity_kind=EnumModelQuantityKind.ORIENTED_DECISION_VALUE,
                semantic_profile_id=BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
            )
            atom = AffineModelQuantityConstraintIR2(
                quantity=quantity,
                op=EnumComparisonOperator.EQ,
                expression=self._expression(model_ir, evaluation),
                evaluation=evaluation,
                metadata={
                    "framework": schema.framework.value,
                    "model_type": schema.model_type,
                    "task": schema.task,
                    "model_family": BINARY_LOGISTIC_AFFINE_MODEL_FAMILY,
                    "semantic_profile_id": BINARY_LOGISTIC_AFFINE_SEMANTIC_PROFILE_ID,
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
                        "encoder": "SklearnLogisticRegressionEncoder",
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
    def _expression(
        model_ir: AffineModelIR,
        evaluation: ModelEvaluationIR,
    ) -> AffineExpressionIR2:
        return AffineExpressionIR2(
            terms=tuple(
                AffineTermIR2(
                    entity=evaluation.point.name,
                    feature=feature,
                    coefficient=coefficient,
                    point=evaluation.point,
                )
                for feature, coefficient in model_ir.terms
            ),
            bias=model_ir.bias,
        )

    @staticmethod
    def _validate_evaluation(
        schema: ModelSchema,
        evaluation: ModelEvaluationIR,
    ) -> None:
        if evaluation.output_name != schema.output_name:
            raise InvalidModelIRLoweringError(
                "Requested evaluation output does not match ModelSchema.output_name: "
                f"{evaluation.output_name!r} != {schema.output_name!r}."
            )
        if not evaluation.model_identity:
            raise InvalidModelIRLoweringError(
                "Requested model evaluation is missing its model identity."
            )

    @staticmethod
    def _is_affine_regression(schema: ModelSchema) -> bool:
        return (
            schema.task == "regression"
            and framework_model_descriptor(schema).model_family
            == AFFINE_REGRESSION_MODEL_FAMILY
        )

    @staticmethod
    def _is_binary_logistic(schema: ModelSchema) -> bool:
        return (
            schema.task == "classification"
            and framework_model_descriptor(schema).model_family
            == BINARY_LOGISTIC_AFFINE_MODEL_FAMILY
        )

    @staticmethod
    def _validate_binary_logistic_schema(schema: ModelSchema) -> None:
        output = schema.output_schema
        if not isinstance(output, ClassificationOutputSchema):
            raise UnsupportedModelIRLoweringError(
                "Binary logistic lowering requires a classification output schema."
            )
        if len(output.labels) != 2:
            raise UnsupportedModelIRLoweringError(
                "Binary logistic lowering requires exactly two ordered labels."
            )
        if not output.probability_available:
            raise UnsupportedModelIRLoweringError(
                "Binary logistic lowering requires probability observability."
            )
        if output.decision_policy is None:
            raise UnsupportedModelIRLoweringError(
                "Binary logistic lowering requires a recognized decision policy."
            )
