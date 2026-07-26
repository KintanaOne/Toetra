from __future__ import annotations

from dataclasses import dataclass, field

from toetra._compiler.ir.ir1.nodes import (
    ModelEvaluationIR,
    PointBindingIR,
    ScalarExpressionIR,
)
from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.schema.output_schema import EnumOutputObservable, ModelLabel


@dataclass(frozen=True)
class ClassLabelIR:
    """Canonical class label retained as selector metadata in IR1."""

    value: ModelLabel
    dtype: EnumDataType
    source_lexeme: str | None = field(default=None, compare=False)


@dataclass
class OutputObservableExpressionIR(ScalarExpressionIR):
    """One declarative scalar observable projected from a model evaluation.

    The evaluation identifies the model invocation. ``observable`` and ``label``
    retain the user-facing view selected from that invocation. This node does
    not contain model-family lowering or backend-specific quantities.
    """

    evaluation: ModelEvaluationIR
    observable: EnumOutputObservable
    dtype: EnumDataType | None = None
    label: ClassLabelIR | None = None

    @property
    def point(self) -> PointBindingIR:
        """Return the exact point selected by this observable."""

        return self.evaluation.point

    @property
    def model_identity(self) -> str:
        """Return the declared model identity of the shared evaluation."""

        return self.evaluation.model_identity

    @property
    def output_name(self) -> str:
        """Return the declared output-port name of the shared evaluation."""

        return self.evaluation.output_name
