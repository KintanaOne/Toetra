from dataclasses import dataclass

from toetra._models.schema.output.base import ModelOutputSchema
from toetra._models.schema.output.enums import (
    EnumModelOutputKind,
    EnumOutputObservable,
)


@dataclass(frozen=True)
class UnknownOutputSchema(ModelOutputSchema):
    """Model output not yet semantically normalized by Toetra."""

    @property
    def kind(self) -> EnumModelOutputKind:
        return EnumModelOutputKind.UNKNOWN

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        return ()
