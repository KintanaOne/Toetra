from __future__ import annotations

from dataclasses import dataclass

from toetra._compiler.ir.ir2.enums import NormalFormKind
from toetra._language.vocabulary.backends import EnumBackend


@dataclass(frozen=True)
class IR2BuildContext:
    """Internal construction options for IR2.

    These options are compiler concerns. They must not leak into the Toetra Specification Language.
    """

    preferred_normal_form: NormalFormKind | None = None
    max_distribution_size: int = 128
    allow_nnf_fallback: bool = True
    backend_hint: EnumBackend | None = None
    strict: bool = True

    def with_preferred_form(self, form: NormalFormKind | None) -> "IR2BuildContext":
        return IR2BuildContext(
            preferred_normal_form=form,
            max_distribution_size=self.max_distribution_size,
            allow_nnf_fallback=self.allow_nnf_fallback,
            backend_hint=self.backend_hint,
            strict=self.strict,
        )
