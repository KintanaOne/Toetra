from toetra._compiler.ir.ir2.context import IR2BuildContext
from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._compiler.ir.ir2.guardrails.model_output import (
    IR2_MODEL_OUTPUT_NOT_REFERENCED,
)
from toetra._compiler.ir.ir2.run_ir2 import run_ir2, run_ir2_with_model_schema
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema


def _linear_regression_schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={
            "a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT),
        },
        target="MyTarget",
        task="regression",
        metadata={
            "linear": {
                "coef": [2.0],
                "intercept": 1.0,
                "feature_names": ["a"],
            }
        },
    )


def _diagnostic_codes(task) -> set[str]:
    return {diagnostic.code for diagnostic in task.diagnostics}


def test_evaluation_driven_modelbridge_skips_point_only_property():
    code = """
    model := "model.pkl"
    target := MyTarget

    [BOUND]:
    forall x0 => x0.a <= 10 using Z3
    """

    task = run_ir2_with_model_schema(
        code,
        schema=_linear_regression_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )[0]

    assert task.assumptions == ()
    assert task.model_evaluations == ()
    assert IR2_MODEL_OUTPUT_NOT_REFERENCED not in _diagnostic_codes(task)


def test_does_not_warn_when_spec_references_model_output():
    code = """
    model := "model.pkl"
    target := MyTarget

    [BOUND]:
    forall x0 => target <= 10 using Z3
    """

    tasks = run_ir2_with_model_schema(
        code,
        schema=_linear_regression_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    task = tasks[0]

    assert IR2_MODEL_OUTPUT_NOT_REFERENCED not in _diagnostic_codes(task)


def test_does_not_warn_without_model_assumptions():
    code = """
    model := "model.onnx"
    target := MyTarget

    [BOUND]:
    forall x0 => x0.a <= 10 using Z3
    """

    tasks = run_ir2(
        code,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    task = tasks[0]

    assert task.assumptions == ()
    assert IR2_MODEL_OUTPUT_NOT_REFERENCED not in _diagnostic_codes(task)
