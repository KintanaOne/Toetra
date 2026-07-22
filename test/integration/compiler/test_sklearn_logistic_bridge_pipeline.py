from __future__ import annotations

from dsl.backends.defaults import create_default_backend_registry
from dsl.backends.router import BackendRouter
from dsl.ir.ir2.model.affine import AffineModelQuantityConstraintIR2
from dsl.ir.ir2.run_ir2 import run_ir2_with_model_schema
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import (
    BinaryClassificationDecisionPolicy,
    ClassificationOutputSchema,
)


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={
            "income": FeatureSchema(name="income", dtype=EnumDataType.FLOAT),
        },
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
            decision_policy=BinaryClassificationDecisionPolicy(
                negative_label="rejected",
                positive_label="approved",
            ),
        ),
        metadata={
            "linear": {
                "coef": [[2.0]],
                "intercept": [-1.0],
                "feature_names": ["income"],
            }
        },
    )


def _source() -> str:
    return """\
model := "credit.joblib"
target := decision

[LOGIC]:
forall applicant =>
    target[applicant].label == "approved"
"""


def test_schema_aware_pipeline_injects_latent_affine_equation() -> None:
    task = run_ir2_with_model_schema(_source(), schema=_schema())[0]

    assert len(task.assumptions) == 1
    atom = task.assumptions[0].formula.expression
    assert isinstance(atom, AffineModelQuantityConstraintIR2)
    assert atom.quantity.evaluation == task.model_evaluations[0]
    assert task.requirements.requires_model_semantic_quantities is True
    assert task.requirements.requires_affine_arithmetic is True
    assert task.requirements.requires_model_assertions is True
    assert len(task.lowering_evidence) == 1


def test_z3_profile_routes_model_semantic_quantities() -> None:
    task = run_ir2_with_model_schema(_source(), schema=_schema())[0]

    route = BackendRouter(create_default_backend_registry()).route(task)

    assert route.backend.value == "Z3"
    assert route.capabilities.supports_model_semantic_quantities is True
