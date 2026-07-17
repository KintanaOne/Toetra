from __future__ import annotations

from dsl.ir.ir2.context import IR2BuildContext
from dsl.ir.ir2.enums import NormalFormKind
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.ir.ir2.run_ir2 import run_ir2


def compile_ir2(source: str) -> VerificationTaskIR2:
    return run_ir2(
        source,
        context=IR2BuildContext(preferred_normal_form=NormalFormKind.NNF),
    )[0]
