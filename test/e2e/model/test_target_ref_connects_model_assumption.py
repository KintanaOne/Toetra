from dsl.ir.ir1.nodes import (
    AndIR,
    ComparisonIR,
    ConstantExpressionIR,
    NotIR,
    TargetExpressionIR,
)
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind
from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.nodes import NNFFormulaIR2
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.language.vocabulary.operators import EnumComparisonOperator
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


def test_target_ref_connects_to_model_output_assumption():
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

    assert len(tasks) == 1

    task = tasks[0]

    spec = task.spec_formula.expression

    assert isinstance(spec, ComparisonIR)
    assert isinstance(spec.left, TargetExpressionIR)
    assert spec.left.entity == "_model"
    assert spec.left.feature == "MyTarget"
    assert spec.op == EnumComparisonOperator.LTE
    assert isinstance(spec.right, ConstantExpressionIR)
    assert spec.right.value == 10

    assert len(task.assumptions) == 1

    assumption = task.assumptions[0]

    assert assumption.source is AssumptionSource.MODEL
    assert isinstance(assumption.formula.expression, AffineOutputConstraintIR2)

    model_constraint = assumption.formula.expression

    assert model_constraint.output_entity == "_model"
    assert model_constraint.output_feature == "MyTarget"

    assert model_constraint.output_entity == spec.left.entity
    assert model_constraint.output_feature == spec.left.feature

    assert len(model_constraint.expression.terms) == 1

    term = model_constraint.expression.terms[0]

    assert term.entity == "x0"
    assert term.feature == "a"
    assert term.coefficient == 2.0
    assert model_constraint.expression.bias == 1.0

    assert task.requirements.requires_model_assertions is True
    assert task.normal_form is NormalFormKind.NNF


def test_target_ref_and_model_assumption_build_refutation_vc():
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

    assert len(tasks) == 1

    task = tasks[0]

    vc = task.verification_condition

    assert isinstance(vc, NNFFormulaIR2)

    expr = vc.expression

    assert isinstance(expr, AndIR)

    model_constraints = [
        operand
        for operand in expr.operands
        if isinstance(operand, AffineOutputConstraintIR2)
    ]

    negated_specs = [operand for operand in expr.operands if isinstance(operand, NotIR)]

    assert len(model_constraints) == 1
    assert len(negated_specs) == 1

    model_constraint = model_constraints[0]

    assert model_constraint.output_entity == "_model"
    assert model_constraint.output_feature == "MyTarget"
    assert model_constraint.op == EnumComparisonOperator.EQ

    assert len(model_constraint.expression.terms) == 1

    term = model_constraint.expression.terms[0]

    assert term.entity == "x0"
    assert term.feature == "a"
    assert term.coefficient == 2.0
    assert model_constraint.expression.bias == 1.0

    negated_spec = negated_specs[0]

    assert isinstance(negated_spec.operand, ComparisonIR)

    spec = negated_spec.operand

    assert isinstance(spec.left, TargetExpressionIR)
    assert spec.left.entity == "_model"
    assert spec.left.feature == "MyTarget"
    assert spec.op == EnumComparisonOperator.LTE
    assert isinstance(spec.right, ConstantExpressionIR)
    assert spec.right.value == 10
