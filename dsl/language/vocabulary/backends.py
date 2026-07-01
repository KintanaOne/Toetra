from enum import Enum

from dsl.language.vocabulary.utils import EnumMixin


official_backends = {
    "z3": '"z3"',
    "Z3": '"Z3"',
    "eran": '"eran"',
    "ERAN": '"ERAN"',
    "zonotope": '"zonotope"',
    "ZONOTOPE": '"ZONOTOPE"',
    "box": '"box"',
    "BOX": '"BOX"',
}


class EnumBackend(EnumMixin, Enum):
    Z3 = "Z3"
    ERAN = "ERAN"
    ZONOTOPE = "ZONOTOPE"
    BOX = "BOX"

    @classmethod
    def from_str(cls, value: str) -> "EnumBackend":
        normalized = value.strip().strip('"').upper()

        aliases = {
            "Z3": cls.Z3,
            "ERAN": cls.ERAN,
            "ZONOTOPE": cls.ZONOTOPE,
            "BOX": cls.BOX,
        }

        try:
            return aliases[normalized]
        except KeyError as e:
            raise ValueError(f"Unknown backend: {value}") from e