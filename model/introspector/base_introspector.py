from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema

class BaseIntrospector(ABC):
    """
    Base class for model introspection.

    Responsibilities
    ----------------
    - expose a unified introspection API
    - provide shared utilities
    - normalize metadata extraction
    - enforce implementation contracts

    Subclasses are responsible for:
    - framework-specific introspection
    - task detection
    - metadata extraction
    """

    def __init__(
        self,
        model,
        source_path: str | Path | None = None,
        schema=None,
        serialization_format: str | None = None,
    ):
        self.model = model
        self.source_path = Path(source_path) if source_path is not None else None
        self.input_schema = schema
        self.serialization_format = serialization_format

    @abstractmethod
    def introspect(self) -> ModelSchema:
        """
        Produce a normalized ModelSchema.
        """
        raise NotImplementedError

    def _safe_getattr(self, name, default=None):
        """
        Safe attribute access helper.
        """
        return getattr(self.model, name, default)

    def _has_attr(self, name) -> bool:
        """
        Check whether the model exposes an attribute.
        """
        return hasattr(self.model, name)

    def _build_base_metadata(self) -> dict:
        """
        Common metadata shared across frameworks.
        """
        return {
            "serialization_format": self.serialization_format,
            "model_class": type(self.model).__name__,
            "module": type(self.model).__module__,
        }