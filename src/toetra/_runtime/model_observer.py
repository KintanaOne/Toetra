from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from toetra._models.schema.model_schema import ModelSchema
from toetra._models.schema.output_schema import ModelLabel


@dataclass(frozen=True)
class ModelObservation:
    """Framework-neutral concrete views of one model evaluation."""

    output_name: str
    regression_value: Any | None = None
    predicted_label: ModelLabel | None = None
    class_probabilities: Mapping[ModelLabel, float] = field(
        default_factory=lambda: MappingProxyType({})
    )
    model_quantities: Mapping[str, float] = field(
        default_factory=lambda: MappingProxyType({})
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "class_probabilities",
            MappingProxyType(dict(self.class_probabilities)),
        )
        object.__setattr__(
            self,
            "model_quantities",
            MappingProxyType(dict(self.model_quantities)),
        )


class ModelRuntimeObserver(Protocol):
    """Concrete runtime observation contract used by replay."""

    observer_id: str

    def supports(self, *, schema: ModelSchema, model: object) -> bool:
        """Return whether this observer can evaluate the supplied model."""
        ...

    def observe(
        self,
        *,
        schema: ModelSchema,
        model: object,
        inputs: Mapping[str, Any],
    ) -> ModelObservation:
        """Evaluate one point and expose normalized public/internal views."""
        ...


class ModelObserverRegistry:
    """Ordered registry of framework-specific runtime observers."""

    def __init__(self, observers: tuple[ModelRuntimeObserver, ...] = ()) -> None:
        self._observers = list(observers)

    def register(self, observer: ModelRuntimeObserver) -> None:
        self._observers.append(observer)

    def require(self, *, schema: ModelSchema, model: object) -> ModelRuntimeObserver:
        for observer in self._observers:
            if observer.supports(schema=schema, model=model):
                return observer
        from toetra._runtime.errors import ReplayUnavailableError

        raise ReplayUnavailableError(
            "No model runtime observer supports the supplied framework/model schema"
        )
