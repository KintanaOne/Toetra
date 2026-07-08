from dsl.ir.ir1.nodes import AndIR
from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import AssumptionSource, NormalFormKind
from dsl.ir.ir2.model.affine import AffineOutputConstraintIR2
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

SOURCE = """
model := "model.pkl"
target := MyTarget

[LOGIC]:
check_at x0 => x0.a <= 10 using Z3
"""


def test_run_ir2_with_model_schema_injects_scope_dependent_model_assumption():
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LinearRegression",
        features={"a": FeatureSchema(name="a", dtype=EnumDataType.FLOAT)},
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
        SOURCE,
        schema=schema,
        ir2_context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )

    assert len(tasks) == 1

    task = tasks[0]
    assert task.requirements.requires_model_assertions is True
    assert len(task.assumptions) == 1

    assumption = task.assumptions[0]
    assert assumption.source is AssumptionSource.MODEL
    assert isinstance(assumption.formula.expression, AffineOutputConstraintIR2)

    atom = assumption.formula.expression
    assert atom.output_entity == "_model"
    assert atom.output_feature == "MyTarget"
    assert atom.expression.terms[0].entity == "x0"
    assert atom.expression.terms[0].feature == "a"
    assert atom.expression.terms[0].coefficient == 2.0
    assert atom.expression.bias == 1.0

    assert task.normal_form is NormalFormKind.NNF
    assert isinstance(task.verification_condition.expression, AndIR)
