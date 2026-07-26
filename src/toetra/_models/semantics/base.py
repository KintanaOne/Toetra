from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from toetra._compiler.ir.ir1.nodes import LogicalIR, VerificationTask
from toetra._models.schema.model_schema import ModelSchema
from toetra._models.semantics.evidence import SemanticLoweringEvidence


@dataclass(frozen=True)
class LoweredVerificationTask:
    """One task after model-semantic rewriting and before final NNF."""

    task: VerificationTask
    evidence: tuple[SemanticLoweringEvidence, ...] = ()


class ModelSemanticProfile(Protocol):
    """Framework- and backend-neutral observable lowering contract."""

    profile_id: str
    version: str

    def lower_task(
        self,
        task: VerificationTask,
        *,
        schema: ModelSchema,
    ) -> LoweredVerificationTask:
        """Lower every supported public observable in one task."""
        ...


class LogicalLoweringResult(Protocol):
    expression: LogicalIR
    evidence: tuple[SemanticLoweringEvidence, ...]
