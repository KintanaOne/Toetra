from __future__ import annotations

from toetra._compatibility.enums import CompatibilityClassification, ConclusionKind
from toetra._compiler.ir.ir1.run_ir1 import run_ir
from toetra._models.semantics.evidence import LoweringEvidence
from toetra._models.semantics.lowering import ModelSemanticLowerer
from tests.support.model_semantics import (
    label_property,
    make_binary_logistic_schema,
)


def test_lowering_evidence_is_deterministic_and_complete() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(label_property(), model_schema=schema)[0]
    lowerer = ModelSemanticLowerer()

    first = lowerer.lower_task(task, schema=schema).evidence[0]
    second = lowerer.lower_task(task, schema=schema).evidence[0]

    assert isinstance(first, LoweringEvidence)
    assert isinstance(second, LoweringEvidence)
    assert first == second
    assert first.to_dict() == second.to_dict()
    assert first.compatibility_classification is CompatibilityClassification.EXACT
    assert first.permitted_conclusions == tuple(ConclusionKind)
    assert first.source_intent.label_value == "approved"
    assert first.canonical_constraint.quantity_kind == "oriented_decision_value"
    assert first.canonical_constraint.threshold == "0"
    assert first.boundary_policy.equality_label == "rejected"


def test_evidence_keeps_public_intent_and_canonical_constraint_separate() -> None:
    schema = make_binary_logistic_schema()
    task = run_ir(label_property(operator="!="), model_schema=schema)[0]

    evidence = ModelSemanticLowerer().lower_task(task, schema=schema).evidence[0]
    assert isinstance(evidence, LoweringEvidence)
    payload = evidence.to_dict()

    assert payload["source_intent"] == {
        "observable": "predicted_label",
        "operator": "!=",
        "label_value": "approved",
        "label_dtype": "string",
        "observable_on_left": True,
    }
    assert payload["canonical_constraint"]["operator"] == "<="
    assert payload["semantic_profile_id"] == "binary_logistic_affine_classification"
