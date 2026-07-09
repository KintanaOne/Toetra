from dsl.ir.ir1.nodes import ComparisonIR
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind
from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema


def test_target_ref_connects_to_model_output_assumption():
    code = """
    model := "model.pkl"
    target := MyTarget

    [BOUND]:
    check_at x0 => target <= 10 using Z3
    """

    schema = ModelSchema(
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

    tasks = run_ir2_with_model_schema(
        code,
        schema=schema,
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    assert len(tasks) == 1

    task = tasks[0]

    spec = task.spec_formula.expression

    assert isinstance(spec, ComparisonIR)
    assert spec.entity == "_model"
    assert spec.feature == "MyTarget"
    assert spec.op == EnumComparisonOperator.LTE
    assert spec.value == 10

    assert len(task.assumptions) == 1

    assumption = task.assumptions[0]

    assert assumption.source is AssumptionSource.MODEL
    assert isinstance(assumption.formula.expression, AffineOutputConstraintIR2)

    model_constraint = assumption.formula.expression

    assert model_constraint.output_entity == "_model"
    assert model_constraint.output_feature == "MyTarget"

    assert model_constraint.output_entity == spec.entity
    assert model_constraint.output_feature == spec.feature

    assert len(model_constraint.expression.terms) == 1

    term = model_constraint.expression.terms[0]

    assert term.entity == "x0"
    assert term.feature == "a"
    assert term.coefficient == 2.0
    assert model_constraint.expression.bias == 1.0

    assert task.requirements.requires_model_assertions is True
    assert task.normal_form is NormalFormKind.NNF
