from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema

SOURCE = """
model := "model.pkl"
target := MyTarget

[LOGIC]:
forall x0 => x0.a <= 10 using Z3
"""


def test_run_ir2_with_model_schema_skips_unreferenced_model_evaluation() -> None:
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
    assert task.requirements.requires_model_assertions is False
    assert task.requirements.model_evaluation_count == 0
    assert task.model_evaluations == ()
    assert task.assumptions == ()
    assert task.normal_form is NormalFormKind.NNF
