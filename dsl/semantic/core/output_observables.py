from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dsl.ast.nodes.outputs import (
    ClassProbabilityObservableNode,
    OutputObservableNode,
    PredictedLabelObservableNode,
)
from dsl.semantic.errors.errors import InvalidOutputObservableError
from dsl.semantic.types.enums import EnumDataType
from model.schema.output_schema import (
    ClassificationOutputSchema,
    EnumModelOutputKind,
    EnumOutputObservable,
    ModelLabel,
)

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema


@dataclass(frozen=True)
class ResolvedOutputObservable:
    """Schema-aware semantic description of one public output observable."""

    kind: EnumOutputObservable
    dtype: EnumDataType | None
    label: ModelLabel | None = None
    arithmetic_allowed: bool = True
    ordering_allowed: bool = True


class OutputObservableResolver:
    """Resolve public output observables without choosing model lowering or backend."""

    def __init__(self, model_schema: ModelSchema | None):
        self.model_schema = model_schema

    def validate_bare_target(self) -> None:
        """Reject an ambiguous bare target when the schema is classification."""

        if self.model_schema is None:
            return
        if self.model_schema.output_schema.kind is EnumModelOutputKind.CLASSIFICATION:
            raise InvalidOutputObservableError(
                "A classification output requires an explicit observable: "
                "use 'target[point].label' or "
                "'target[point].probability(label)'"
            )

    def resolve(self, node: OutputObservableNode) -> ResolvedOutputObservable:
        if isinstance(node, PredictedLabelObservableNode):
            return self._resolve_predicted_label()
        if isinstance(node, ClassProbabilityObservableNode):
            return self._resolve_probability(node)
        raise InvalidOutputObservableError(
            f"Unsupported model output observable '{type(node).__name__}'"
        )

    def _resolve_predicted_label(self) -> ResolvedOutputObservable:
        if self.model_schema is None:
            return ResolvedOutputObservable(
                kind=EnumOutputObservable.PREDICTED_LABEL,
                dtype=None,
                arithmetic_allowed=False,
                ordering_allowed=False,
            )

        output = self._classification_output(requested="predicted label")
        if EnumOutputObservable.PREDICTED_LABEL not in output.available_observables:
            raise InvalidOutputObservableError(
                "The selected classification output does not expose a predicted label"
            )

        return ResolvedOutputObservable(
            kind=EnumOutputObservable.PREDICTED_LABEL,
            dtype=output.label_dtype,
            arithmetic_allowed=False,
            ordering_allowed=False,
        )

    def _resolve_probability(
        self,
        node: ClassProbabilityObservableNode,
    ) -> ResolvedOutputObservable:
        label = node.label.value
        if label is None:
            raise InvalidOutputObservableError(
                "Class probability requires a non-null class label"
            )

        if self.model_schema is None:
            return ResolvedOutputObservable(
                kind=EnumOutputObservable.CLASS_PROBABILITY,
                dtype=EnumDataType.FLOAT,
                label=label,
            )

        output = self._classification_output(requested="class probability")
        if EnumOutputObservable.CLASS_PROBABILITY not in output.available_observables:
            raise InvalidOutputObservableError(
                "The selected classification output does not expose class probabilities"
            )

        if (
            output.label_dtype is not None
            and node.label.dtype is not output.label_dtype
        ):
            raise InvalidOutputObservableError(
                "Probability label has incompatible type: expected "
                f"{output.label_dtype.value}, got {node.label.dtype.value}"
            )

        if output.labels and not any(
            _same_canonical_label(label, candidate) for candidate in output.labels
        ):
            available = ", ".join(repr(candidate) for candidate in output.labels)
            raise InvalidOutputObservableError(
                f"Unknown classification label {label!r}. "
                f"Available labels: [{available}]"
            )

        return ResolvedOutputObservable(
            kind=EnumOutputObservable.CLASS_PROBABILITY,
            dtype=EnumDataType.FLOAT,
            label=label,
        )

    def _classification_output(
        self,
        *,
        requested: str,
    ) -> ClassificationOutputSchema:
        assert self.model_schema is not None
        output = self.model_schema.output_schema
        if not isinstance(output, ClassificationOutputSchema):
            raise InvalidOutputObservableError(
                f"Cannot access {requested} on a " f"{output.kind.value} model output"
            )
        return output


def _same_canonical_label(left: ModelLabel, right: ModelLabel) -> bool:
    """Compare labels without Python's bool/int or int/float coercion."""

    return type(left) is type(right) and left == right
