from dataclasses import dataclass

from toetra._compatibility.descriptors import FrameworkModelDescriptor
from toetra._models.detector.model_framework import EnumModelFramework


@dataclass(frozen=True)
class ModelDescriptor:
    """Identity and source-execution description of a model."""

    framework: EnumModelFramework
    model_type: str
    compatibility: FrameworkModelDescriptor | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.framework, EnumModelFramework):
            raise TypeError(
                "ModelDescriptor framework must be an EnumModelFramework."
            )

        if not isinstance(self.model_type, str):
            raise TypeError("ModelDescriptor model_type must be a string.")

        if not self.model_type:
            raise ValueError("ModelDescriptor model_type cannot be empty.")

        if self.model_type.strip() != self.model_type:
            raise ValueError(
                "ModelDescriptor model_type cannot have leading or trailing whitespace."
            )

        if (
            self.compatibility is not None
            and not isinstance(self.compatibility, FrameworkModelDescriptor)
        ):
            raise TypeError(
                "ModelDescriptor compatibility must be a "
                "FrameworkModelDescriptor or None."
            )
