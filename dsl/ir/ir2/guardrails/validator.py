from __future__ import annotations

from typing import Any

from dsl.ir.ir2.guardrails.diagnostics import IR2Diagnostic
from dsl.ir.ir2.guardrails.model_output import (
    diagnose_model_evaluation_connectivity,
    diagnose_model_output_not_referenced,
)


def collect_ir2_diagnostics(task: Any) -> tuple[IR2Diagnostic, ...]:
    diagnostics: list[IR2Diagnostic] = []
    diagnostics.extend(diagnose_model_output_not_referenced(task))
    diagnostics.extend(diagnose_model_evaluation_connectivity(task))
    return tuple(diagnostics)
