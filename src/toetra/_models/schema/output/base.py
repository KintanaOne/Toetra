from abc import ABC, abstractmethod
from dataclasses import dataclass

from toetra._compiler.semantic.types.enums import EnumDataType
from toetra._models.schema.output.enums import (
    EnumModelOutputKind,
    EnumOutputObservable,
)
from toetra._models.schema.value_schema import ValueSchema


@dataclass(frozen=True)
class ModelOutputSchema(ABC):
    """Common immutable contract implemented by typed model outputs."""

    value: ValueSchema

    def __post_init__(self) -> None:
        if not isinstance(self.value, ValueSchema):
            raise TypeError("ModelOutputSchema value must be a ValueSchema.")

    @property
    @abstractmethod
    def kind(self) -> EnumModelOutputKind:
        """Return the semantic output kind."""

    @property
    @abstractmethod
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        """Return public observables exposed by this output."""

    @property
    def name(self) -> str:
        return self.value.name

    @property
    def dtype(self) -> EnumDataType | None:
        return self.value.dtype

    @property
    def source_dtype(self) -> str | None:
        return self.value.source_dtype
