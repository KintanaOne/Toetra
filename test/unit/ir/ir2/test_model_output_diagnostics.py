from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.guardrails.diagnostics import DiagnosticSeverity
from dsl.ir.ir2.guardrails.model_output import IR2_MODEL_OUTPUT_NOT_REFERENCED
from dsl.ir.ir2.run_ir2 import run_ir2, run_ir2_with_model_schema
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


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


def test_warns_when_model_assumption_is_injected_but_spec_does_not_reference_model_output():
    code = """
    model := "model.pkl"
    target := MyTarget

    [BOUND]:
    check_at x0 => x0.a <= 10 using Z3
    """

    tasks = run_ir2_with_model_schema(
        code,
        schema=_linear_regression_schema(),
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    task = tasks[0]

    assert IR2_MODEL_OUTPUT_NOT_REFERENCED in _diagnostic_codes(task)

    diagnostic = task.diagnostics[0]

    assert diagnostic.code == IR2_MODEL_OUTPUT_NOT_REFERENCED
    assert diagnostic.severity is DiagnosticSeverity.WARNING
    assert "does not reference any model output symbol" in diagnostic.message


def test_does_not_warn_when_spec_references_model_output():
    code = """
    model := "model.pkl"
    target := MyTarget

    [BOUND]:
    check_at x0 => target <= 10 using Z3
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
    check_at x0 => x0.a <= 10 using Z3
    """

    tasks = run_ir2(
        code,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    task = tasks[0]

    assert task.assumptions == ()
    assert IR2_MODEL_OUTPUT_NOT_REFERENCED not in _diagnostic_codes(task)
