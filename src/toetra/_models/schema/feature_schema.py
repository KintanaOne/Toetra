from dataclasses import dataclass

from toetra._compiler.semantic.types.enums import EnumDataType


@dataclass
class FeatureSchema:

    name: str
    dtype: EnumDataType
    nullable: bool = False
    source_dtype: str | None = None
