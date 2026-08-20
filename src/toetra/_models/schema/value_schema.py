from dataclasses import dataclass

from toetra._compiler.semantic.types.enums import EnumDataType


@dataclass(frozen=True)
class ValueSchema:
    """Typed named value exposed at a model boundary."""

    name: str
    dtype: EnumDataType | None = None
    source_dtype: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("ValueSchema name must be a string.")

        if not self.name:
            raise ValueError("ValueSchema name cannot be empty.")

        if self.name.strip() != self.name:
            raise ValueError(
                "ValueSchema name cannot have leading or trailing whitespace."
            )

        if self.dtype is not None and not isinstance(self.dtype, EnumDataType):
            raise TypeError("ValueSchema dtype must be an EnumDataType or None.")

        if self.source_dtype is not None:
            if not isinstance(self.source_dtype, str):
                raise TypeError("ValueSchema source_dtype must be a string or None.")

            if not self.source_dtype:
                raise ValueError("ValueSchema source_dtype cannot be empty.")

            if self.source_dtype.strip() != self.source_dtype:
                raise ValueError(
                    "ValueSchema source_dtype cannot have leading or "
                    "trailing whitespace."
                )
