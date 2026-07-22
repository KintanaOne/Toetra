from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

from dsl.compatibility.enums import CompatibilityClassification, ConclusionKind
from dsl.ir.ir1.nodes import ModelEvaluationIR
from dsl.language.vocabulary.operators import EnumComparisonOperator
from dsl.semantic.types.enums import EnumDataType
from model.schema.output_schema import EnumOutputObservable, ModelLabel


@dataclass(frozen=True)
class ObservableIntentEvidence:
    """Serializable copy of one user-visible observable comparison."""

    observable: EnumOutputObservable
    operator: EnumComparisonOperator
    label_value: ModelLabel
    label_dtype: EnumDataType
    observable_on_left: bool
    property_threshold: str | None = None
    property_threshold_dtype: EnumDataType | None = None
    logical_polarity: str = "positive"


@dataclass(frozen=True)
class CanonicalConstraintEvidence:
    """Serializable description of one generated canonical constraint."""

    quantity_kind: str
    operator: EnumComparisonOperator
    threshold: str
    threshold_dtype: EnumDataType
    exact_threshold_expression: str | None = None
    threshold_lower_bound: str | None = None
    threshold_upper_bound: str | None = None
    selected_bound: str = "exact"
    precision_digits: int | None = None
    working_precision_digits: int | None = None
    guard_digits: int | None = None


@dataclass(frozen=True)
class BoundaryPolicyEvidence:
    """Decision-boundary behavior used by a semantic rewrite."""

    positive_operator: EnumComparisonOperator
    positive_threshold: str
    equality_label: ModelLabel


@dataclass(frozen=True)
class LoweringEvidence:
    """Deterministic trace from a public intent to a canonical constraint."""

    evaluation: ModelEvaluationIR
    source_intent: ObservableIntentEvidence
    semantic_profile_id: str
    semantic_profile_version: str
    transformation_id: str
    transformation_version: str
    canonical_constraint: CanonicalConstraintEvidence
    boundary_policy: BoundaryPolicyEvidence
    compatibility_classification: CompatibilityClassification
    permitted_conclusions: tuple[ConclusionKind, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible representation."""

        source_intent = {
            "observable": self.source_intent.observable.value,
            "operator": self.source_intent.operator.value,
            "label_value": self.source_intent.label_value,
            "label_dtype": self.source_intent.label_dtype.value,
            "observable_on_left": self.source_intent.observable_on_left,
        }
        if self.source_intent.property_threshold is not None:
            source_intent["property_threshold"] = self.source_intent.property_threshold
        if self.source_intent.property_threshold_dtype is not None:
            source_intent["property_threshold_dtype"] = (
                self.source_intent.property_threshold_dtype.value
            )
        if self.source_intent.logical_polarity != "positive":
            source_intent["logical_polarity"] = self.source_intent.logical_polarity

        canonical_constraint = {
            "quantity_kind": self.canonical_constraint.quantity_kind,
            "operator": self.canonical_constraint.operator.value,
            "threshold": self.canonical_constraint.threshold,
            "threshold_dtype": self.canonical_constraint.threshold_dtype.value,
        }
        optional_canonical = {
            "exact_threshold_expression": (
                self.canonical_constraint.exact_threshold_expression
            ),
            "threshold_lower_bound": (self.canonical_constraint.threshold_lower_bound),
            "threshold_upper_bound": (self.canonical_constraint.threshold_upper_bound),
            "precision_digits": self.canonical_constraint.precision_digits,
            "working_precision_digits": (
                self.canonical_constraint.working_precision_digits
            ),
            "guard_digits": self.canonical_constraint.guard_digits,
        }
        canonical_constraint.update(
            {
                key: value
                for key, value in optional_canonical.items()
                if value is not None
            }
        )
        if self.canonical_constraint.selected_bound != "exact":
            canonical_constraint["selected_bound"] = (
                self.canonical_constraint.selected_bound
            )

        return {
            "evaluation": {
                "model_identity": self.evaluation.model_identity,
                "point": {
                    "name": self.evaluation.point.name,
                    "binding_kind": self.evaluation.point.binding_kind,
                    "lexical_depth": self.evaluation.point.lexical_depth,
                    "generated": self.evaluation.point.generated,
                },
                "output_name": self.evaluation.output_name,
            },
            "source_intent": source_intent,
            "semantic_profile_id": self.semantic_profile_id,
            "semantic_profile_version": self.semantic_profile_version,
            "transformation_id": self.transformation_id,
            "transformation_version": self.transformation_version,
            "canonical_constraint": canonical_constraint,
            "boundary_policy": {
                "positive_operator": self.boundary_policy.positive_operator.value,
                "positive_threshold": self.boundary_policy.positive_threshold,
                "equality_label": self.boundary_policy.equality_label,
            },
            "compatibility_classification": (self.compatibility_classification.value),
            "permitted_conclusions": tuple(
                conclusion.value for conclusion in self.permitted_conclusions
            ),
        }


@dataclass(frozen=True)
class PairwiseObservableIntentEvidence:
    """Serializable copy of one relation between two public observables."""

    observable: EnumOutputObservable
    operator: EnumComparisonOperator
    related_observable: EnumOutputObservable
    logical_polarity: str = "positive"


@dataclass(frozen=True)
class PairwiseCanonicalFormulaEvidence:
    """Deterministic description of one binary decision-region relation."""

    quantity_kind: str
    relation: str
    positive_operator: EnumComparisonOperator
    negative_operator: EnumComparisonOperator
    threshold: str
    threshold_dtype: EnumDataType


@dataclass(frozen=True)
class PairwiseLoweringEvidence:
    """Trace from a two-evaluation label relation to a canonical formula."""

    evaluations: tuple[ModelEvaluationIR, ModelEvaluationIR]
    source_intent: PairwiseObservableIntentEvidence
    semantic_profile_id: str
    semantic_profile_version: str
    transformation_id: str
    transformation_version: str
    canonical_formula: PairwiseCanonicalFormulaEvidence
    boundary_policy: BoundaryPolicyEvidence
    compatibility_classification: CompatibilityClassification
    permitted_conclusions: tuple[ConclusionKind, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluations": tuple(
                {
                    "model_identity": evaluation.model_identity,
                    "point": {
                        "name": evaluation.point.name,
                        "binding_kind": evaluation.point.binding_kind,
                        "lexical_depth": evaluation.point.lexical_depth,
                        "generated": evaluation.point.generated,
                    },
                    "output_name": evaluation.output_name,
                }
                for evaluation in self.evaluations
            ),
            "source_intent": {
                "observable": self.source_intent.observable.value,
                "operator": self.source_intent.operator.value,
                "related_observable": self.source_intent.related_observable.value,
                "logical_polarity": self.source_intent.logical_polarity,
            },
            "semantic_profile_id": self.semantic_profile_id,
            "semantic_profile_version": self.semantic_profile_version,
            "transformation_id": self.transformation_id,
            "transformation_version": self.transformation_version,
            "canonical_formula": {
                "quantity_kind": self.canonical_formula.quantity_kind,
                "relation": self.canonical_formula.relation,
                "positive_operator": self.canonical_formula.positive_operator.value,
                "negative_operator": self.canonical_formula.negative_operator.value,
                "threshold": self.canonical_formula.threshold,
                "threshold_dtype": self.canonical_formula.threshold_dtype.value,
            },
            "boundary_policy": {
                "positive_operator": self.boundary_policy.positive_operator.value,
                "positive_threshold": self.boundary_policy.positive_threshold,
                "equality_label": self.boundary_policy.equality_label,
            },
            "compatibility_classification": self.compatibility_classification.value,
            "permitted_conclusions": tuple(
                conclusion.value for conclusion in self.permitted_conclusions
            ),
        }


SemanticLoweringEvidence: TypeAlias = LoweringEvidence | PairwiseLoweringEvidence
