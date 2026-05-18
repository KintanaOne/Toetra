from abc import ABC, abstractmethod
from pathlib import Path


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

        # Optional dataset path
        self.source_path = Path(source_path) if source_path is not None else None

        # Optional external schema
        self.input_schema = schema

        # Serialization metadata
        self.serialization_format = serialization_format

    # ======================================================
    # Public API
    # ======================================================

    @abstractmethod
    def introspect(self):
        """
        Produce a normalized ModelSchema.
        """
        pass

    # ======================================================
    # Shared helpers
    # ======================================================

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

    # ======================================================
    # Metadata helpers
    # ======================================================

    def _build_base_metadata(self) -> dict:
        """
        Common metadata shared across frameworks.
        """

        return {
            "serialization_format": self.serialization_format,
            "model_class": type(self.model).__name__,
            "module": type(self.model).__module__,
        }
