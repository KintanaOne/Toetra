from __future__ import annotations

from dsl.ast.nodes.assertion import AndNode, ComparisonNode
from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_toetra_code
from dsl.semantic.core.validator import ToetraValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema, EnumOutputObservable


def _schema() -> ModelSchema:
    return ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"age": FeatureSchema("age", EnumDataType.INT)},
        output_name="MyTarget",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )


def _validate(assertion: str):
    program = parse_program(parse_toetra_code(f"""
        model := "model.pkl"
        target := MyTarget

        [LOGIC]:
        forall x0 => {assertion}
        """))
    ToetraValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=_schema(),
    )
    return program


def test_sem_obs_001_binds_predicted_label_to_output_and_point() -> None:
    program = _validate('target[x0].label == "approved"')
    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, PredictedLabelObservableNode)
    observable = comparison.left.semantic
    output = comparison.left.output.semantic
    assert observable is not None
    assert output is not None
    assert observable.resolved_entity == "_model"
    assert observable.resolved_path == ["_model", "MyTarget", "predicted_label"]
    assert observable.resolved_point is not None
    assert observable.resolved_point.name == "x0"
    assert observable.resolved_output_observable is EnumOutputObservable.PREDICTED_LABEL
    assert observable.resolved_evaluation is output.resolved_evaluation
    assert output.resolved_type == "model_output_port"


def test_sem_obs_002_binds_probability_to_canonical_label() -> None:
    program = _validate('target[x0].probability("approved") >= 0.80')
    comparison = program.body[0].rule.assertion.root
    assert isinstance(comparison, ComparisonNode)
    assert isinstance(comparison.left, ClassProbabilityObservableNode)
    semantic = comparison.left.semantic
    assert semantic is not None
    assert semantic.resolved_output_observable is EnumOutputObservable.CLASS_PROBABILITY
    assert semantic.resolved_label == "approved"
    assert semantic.resolved_path == [
        "_model",
        "MyTarget",
        "class_probability",
        "'approved'",
    ]


def test_sem_obs_008_reuses_one_evaluation_for_multiple_observables() -> None:
    program = _validate(
        'target[x0].label == "approved" '
        'and target[x0].probability("approved") >= 0.80'
    )
    root = program.body[0].rule.assertion.root
    assert isinstance(root, AndNode)
    left, right = root.operands
    assert isinstance(left, ComparisonNode)
    assert isinstance(right, ComparisonNode)
    assert isinstance(left.left, PredictedLabelObservableNode)
    assert isinstance(right.left, ClassProbabilityObservableNode)
    label_semantic = left.left.semantic
    probability_semantic = right.left.semantic
    assert label_semantic is not None
    assert probability_semantic is not None
    label_evaluation = label_semantic.resolved_evaluation
    probability_evaluation = probability_semantic.resolved_evaluation
    property_semantic = program.body[0].semantic
    assert property_semantic is not None
    context = property_semantic.context
    assert label_evaluation is probability_evaluation
    assert context is not None
    assert context.evaluation_registry.all() == (label_evaluation,)
