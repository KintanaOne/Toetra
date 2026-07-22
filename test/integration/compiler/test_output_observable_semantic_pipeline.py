from __future__ import annotations

from dsl.ast.nodes.assertion import AndNode, ComparisonNode
from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from dsl.builder.program import parse_program
from dsl.parser.parser import parse_forml_code
from dsl.semantic.core.validator import FORMLValidator
from dsl.semantic.runtime.tracer import ValidationTracer
from dsl.semantic.types.enums import EnumDataType
from model.detector.model_framework import EnumModelFramework
from model.schema.feature_schema import FeatureSchema
from model.schema.model_schema import ModelSchema
from model.schema.output_schema import ClassificationOutputSchema, EnumOutputObservable


def test_output_observables_survive_source_to_schema_aware_semantics() -> None:
    source = """
    model := "credit.pkl"
    target := decision

    [LOGIC]:
    forall applicant =>
        target[applicant].label == "approved"
        and target[applicant].probability("approved") >= 0.80
    """
    schema = ModelSchema(
        framework=EnumModelFramework.SKLEARN,
        model_type="LogisticRegression",
        features={"income": FeatureSchema("income", EnumDataType.FLOAT)},
        output_name="decision",
        task="classification",
        output_schema=ClassificationOutputSchema(
            label_dtype=EnumDataType.STRING,
            labels=("rejected", "approved"),
            probability_available=True,
        ),
    )
    program = parse_program(parse_forml_code(source))
    assert FORMLValidator().validate(
        program,
        tracer=ValidationTracer(enabled=False),
        model_schema=schema,
    )
    root = program.body[0].rule.assertion.root
    assert isinstance(root, AndNode)
    label_comparison, probability_comparison = root.operands
    assert isinstance(label_comparison, ComparisonNode)
    assert isinstance(probability_comparison, ComparisonNode)
    assert isinstance(label_comparison.left, PredictedLabelObservableNode)
    assert isinstance(probability_comparison.left, ClassProbabilityObservableNode)
    label_semantic = label_comparison.left.semantic
    probability_semantic = probability_comparison.left.semantic
    assert label_semantic is not None
    assert probability_semantic is not None
    assert (
        label_semantic.resolved_output_observable
        is EnumOutputObservable.PREDICTED_LABEL
    )
    assert (
        probability_semantic.resolved_output_observable
        is EnumOutputObservable.CLASS_PROBABILITY
    )
    assert probability_semantic.resolved_label == "approved"
    assert (
        label_semantic.resolved_evaluation is probability_semantic.resolved_evaluation
    )
