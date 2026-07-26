from __future__ import annotations

from toetra._compiler.ast.nodes.assertion import AndNode, ComparisonNode
from toetra._compiler.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    PredictedLabelObservableNode,
)
from toetra._compiler.builder.program import parse_program
from toetra._compiler.parser.parser import parse_toetra_code
from toetra._compiler.semantic.core.validator import ToetraValidator
from toetra._compiler.semantic.runtime.tracer import ValidationTracer
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.detector.model_framework import EnumModelFramework
from toetra._models.schema.feature_schema import FeatureSchema
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import (
    ClassificationOutputSchema,
    EnumOutputObservable,
)


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
    program = parse_program(parse_toetra_code(source))
    assert ToetraValidator().validate(
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
