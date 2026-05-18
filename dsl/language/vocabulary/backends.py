# /forml/grammar/official_contents/backends.py

from enum import Enum
from dsl.language.vocabulary.utils import EnumMixin

official_backends = {
    "eran": '"eran"',
    "ERAN": '"ERAN"',
    "zonotope": '"zonotope"',
    "ZONOTOPE": '"ZONOTOPE"',
    "box": '"box"',
    "BOX": '"BOX"',
    "z3": '"z3"',
    "Z3": '"Z3"',
}


class EnumBackend(EnumMixin, Enum):
    ERAN = "ERAN"
    zonotope = "zonotope"
    ZONOTOPE = "ZONOTOPE"
    box = "box"
    BOX = "BOX"
    z3 = "z3"
    Z3 = "Z3"
