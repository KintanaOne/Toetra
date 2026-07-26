from enum import Enum

from toetra._language.vocabulary.utils import EnumMixin

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
