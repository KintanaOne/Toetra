from __future__ import annotations

from typing import Any, Sequence, cast

from dsl.ir.ir1.nodes import ScopeIR
from dsl.ir.ir2.enums import AssumptionSource
from dsl.ir.ir2.dsl.nodes import AssumptionIR2, NNFFormulaIR2
from dsl.ir.ir2.model.affine import (
    AffineExpressionIR2,
    AffineOutputConstraintIR2,
    AffineTermIR2,
)
from dsl.language.vocabulary.operators import EnumComparisonOperator
from model.encoder.context import ModelEncodingContext
from model.encoder.errors import (
    MissingModelParameterError,
    UnsupportedModelParameterError,
)
from model.schema.model_schema import ModelSchema


class SklearnLinearRegressorEncoder:
    """Encode a simple single-output sklearn LinearRegression schema.

    The encoder emits one backend-independent MODEL assumption:

        _model.<target> == w1*x.f1 + ... + wn*x.fn + b

    It deliberately does not build solver expressions. The returned assumption is
    NNF and can be aggregated by IR2 before CNF/DNF/NNF adaptation.
    """

    supported_model_types = frozenset({"LinearRegression"})

    def encode(
        self,
        schema: ModelSchema,
        scope: ScopeIR,
        *,
        context: ModelEncodingContext | None = None,
    ) -> tuple[AssumptionIR2, ...]:
        context = context or ModelEncodingContext()

        if (
            not context.include_model_constraints
            or not context.include_output_constraints
        ):
            return ()

        if schema.model_type not in self.supported_model_types:
            raise UnsupportedModelParameterError(
                f"SklearnLinearRegressorEncoder does not support model_type="
                f"{schema.model_type!r}."
            )

        if schema.task != "regression":
            raise UnsupportedModelParameterError(
                "SklearnLinearRegressorEncoder only supports regression schemas."
            )

        linear_metadata = self._linear_metadata(schema)
        feature_names = self._feature_names(schema, linear_metadata)
        coefficients = self._single_output_coefficients(linear_metadata)
        intercept = self._single_output_intercept(linear_metadata)

        if len(coefficients) != len(feature_names):
            raise UnsupportedModelParameterError(
                "Linear coefficient count does not match schema feature count: "
                f"{len(coefficients)} coefficients for {len(feature_names)} features."
            )

        input_entity = self._select_input_entity(scope)

        terms = tuple(
            AffineTermIR2(
                entity=input_entity,
                feature=feature_name,
                coefficient=float(coefficient),
            )
            for feature_name, coefficient in zip(feature_names, coefficients)
        )

        expression = AffineExpressionIR2(
            terms=terms,
            bias=float(intercept),
        )

        atom = AffineOutputConstraintIR2(
            output_entity="_model",
            output_feature=schema.target,
            op=EnumComparisonOperator.EQ,
            expression=expression,
            metadata={
                "framework": schema.framework.value,
                "model_type": schema.model_type,
                "task": schema.task,
            },
        )

        return (
            AssumptionIR2(
                source=AssumptionSource.MODEL,
                formula=NNFFormulaIR2(expression=atom),
                description="sklearn linear regression output equation",
                metadata={
                    "encoder": self.__class__.__name__,
                    "model_type": schema.model_type,
                    "target": schema.target,
                },
            ),
        )

    def _linear_metadata(self, schema: ModelSchema) -> dict[str, Any]:
        raw = schema.metadata.get("linear")

        if not isinstance(raw, dict):
            raise MissingModelParameterError(
                "ModelSchema.metadata['linear'] is required for linear encoding."
            )

        if "coef" not in raw or "intercept" not in raw:
            raise MissingModelParameterError(
                "Linear metadata must contain 'coef' and 'intercept'."
            )

        return raw

    def _feature_names(
        self,
        schema: ModelSchema,
        linear_metadata: dict[str, Any],
    ) -> tuple[str, ...]:
        raw_feature_names = linear_metadata.get("feature_names")

        if raw_feature_names is not None:
            if not isinstance(raw_feature_names, Sequence) or isinstance(
                raw_feature_names, str
            ):
                raise UnsupportedModelParameterError(
                    "linear.feature_names must be a sequence of strings."
                )

            return tuple(str(name) for name in raw_feature_names)

        return tuple(schema.features.keys())

    def _single_output_coefficients(
        self,
        linear_metadata: dict[str, Any],
    ) -> tuple[float, ...]:
        coef = linear_metadata["coef"]

        if not isinstance(coef, Sequence) or isinstance(coef, (str, bytes)):
            raise UnsupportedModelParameterError("linear.coef must be a sequence.")

        if (
            coef
            and isinstance(coef[0], Sequence)
            and not isinstance(coef[0], (str, bytes))
        ):
            rows = cast(Sequence[Sequence[Any]], coef)
            if len(rows) != 1:
                raise UnsupportedModelParameterError(
                    "Only single-output linear regression is supported for now."
                )
            coef = rows[0]

        return tuple(float(value) for value in cast(Sequence[Any], coef))

    def _single_output_intercept(self, linear_metadata: dict[str, Any]) -> float:
        intercept = linear_metadata["intercept"]

        if isinstance(intercept, Sequence) and not isinstance(intercept, (str, bytes)):
            if len(intercept) != 1:
                raise UnsupportedModelParameterError(
                    "Only single-output intercepts are supported for now."
                )
            intercept = intercept[0]

        return float(intercept)

    def _select_input_entity(self, scope: ScopeIR) -> str:
        for variable, role in scope.variables.items():
            if role == "perturbation":
                return variable

        for variable, role in scope.variables.items():
            if role in {"anchor", "symbolic"}:
                return variable

        if scope.variables:
            return next(iter(scope.variables.keys()))

        raise UnsupportedModelParameterError(
            "Cannot encode model without scope variables."
        )
