from dataclasses import dataclass

from dsl.semantic.types.enums import EnumDataType


@dataclass
class FeatureSchema:

    name: str
    dtype: EnumDataType
    nullable: bool = False
