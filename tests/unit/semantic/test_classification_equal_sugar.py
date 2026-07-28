from __future__ import annotations

import pytest

from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, ProblemIR
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._language.vocabulary.functions import EnumFunction
from toetra._language.vocabulary.problems import EnumProblem
from toetra._compiler.semantic.errors.errors import SemanticError
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import RegressionOutputSchema
from tests.support.model_semantics import make_binary_logistic_schema


def _source(scope: str) -> str:
    return f"""\
model := "credit.joblib"
target := decision

[LOGIC]:
{scope} => CLASSIFICATION.EQUAL()
"""


def test_pair_bc_003_sugar_resolves_two_ordered_model_evaluations() -> None:
    task = run_ir(
        _source("forall left, right"), model_schema=make_binary_logistic_schema()
    )[0]
    problem = task.query.expression
    assert isinstance(problem, ProblemIR)
    assert problem.problem is EnumProblem.CLASSIFICATION
    assert problem.function is EnumFunction.EQUAL
    assert problem.args is not None
    evaluations = problem.args["evaluations"]
    assert isinstance(evaluations, tuple)
    assert all(isinstance(item, ModelEvaluationIR) for item in evaluations)
    assert tuple(item.point.name for item in evaluations) == ("left", "right")
    assert all(item.output_name == "decision" for item in evaluations)


@pytest.mark.parametrize(
    ("scope", "count"), [("forall only", 1), ("forall first, second, third", 3)]
)
def test_pair_bc_004_sugar_rejects_contexts_without_exactly_two_points(
    scope: str, count: int
) -> None:
    with pytest.raises(
        SemanticError,
        match=rf"requires exactly two visible model-input points, got {count}",
    ):
        run_ir(_source(scope), model_schema=make_binary_logistic_schema())


def test_pair_bc_004_sugar_rejects_non_classification_output_schema() -> None:
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "income": FeatureSchema(
                name="income", dtype=EnumDataType.FLOAT, nullable=False
            )
        },
        output_name="decision",
        task="regression",
        output_schema=RegressionOutputSchema(value_dtype=EnumDataType.FLOAT),
    )
    with pytest.raises(SemanticError, match="requires a classification output schema"):
        run_ir(_source("forall left, right"), model_schema=schema)
