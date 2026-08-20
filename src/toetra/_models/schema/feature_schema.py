from dataclasses import dataclass

from toetra._compiler.semantic.types.enums import EnumDataType


@dataclass(frozen=True, slots=True)
class FeatureSchema:
    name: str
    dtype: EnumDataType
    nullable: bool = False
    source_dtype: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("FeatureSchema name must be a string.")
        if not self.name:
            raise ValueError("FeatureSchema name cannot be empty.")
        if self.name.strip() != self.name:
            raise ValueError(
                "FeatureSchema name cannot have leading or trailing whitespace."
            )
        if not isinstance(self.dtype, EnumDataType):
            raise TypeError("FeatureSchema dtype must be an EnumDataType.")
        if type(self.nullable) is not bool:
            raise TypeError("FeatureSchema nullable must be a bool.")
        if self.source_dtype is not None:
            if not isinstance(self.source_dtype, str):
                raise TypeError("FeatureSchema source_dtype must be a string or None.")
            if not self.source_dtype:
                raise ValueError("FeatureSchema source_dtype cannot be empty.")
            if self.source_dtype.strip() != self.source_dtype:
                raise ValueError(
                    "FeatureSchema source_dtype cannot have leading or "
                    "trailing whitespace."
                )
