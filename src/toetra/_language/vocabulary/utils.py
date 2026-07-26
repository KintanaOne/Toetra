from __future__ import annotations

from enum import Enum
from typing import Self, cast


class EnumMixin:
    @classmethod
    def from_str(cls: type[Self], name: str) -> Self:
        normalized = name.strip().strip('"').upper()

        members = getattr(cls, "__members__", None)
        if members is None:
            raise TypeError(f"{cls.__name__} must be used with an Enum class")

        for member in members.values():
            enum_member = cast(Enum, member)

            member_name = enum_member.name.strip().strip('"').upper()
            member_value = str(enum_member.value).strip().strip('"').upper()

            if member_name == normalized or member_value == normalized:
                return cast(Self, enum_member)

        raise ValueError(f"{cls.__name__} inconnu : {name}")
