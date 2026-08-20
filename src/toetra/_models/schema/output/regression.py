from dataclasses import dataclass

from toetra._models.schema.output.base import ModelOutputSchema
from toetra._models.schema.output.enums import (
    EnumModelOutputKind,
    EnumOutputObservable,
)


@dataclass(frozen=True)
class RegressionOutputSchema(ModelOutputSchema):
    """One directly observable scalar regression output."""

    @property
    def kind(self) -> EnumModelOutputKind:
        return EnumModelOutputKind.REGRESSION

    @property
    def available_observables(self) -> tuple[EnumOutputObservable, ...]:
        return (EnumOutputObservable.REGRESSION_VALUE,)
