"""Declared and effective header values for one runtime invocation."""

from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from toetra._compiler.ast.nodes.program import ProgramNode
from toetra._language.vocabulary.protected_words import EnumProtectedWord
from toetra._runtime.errors import VerificationConfigurationError

_TARGET_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_PROTECTED_TARGETS = frozenset(item.value for item in EnumProtectedWord)


@dataclass(frozen=True)
class ExecutionContext:
    """Declared defaults and temporary effective values for one run."""

    declared_model_reference: str
    declared_target: str
    declared_dataset_reference: str | None
    effective_model_reference: str
    effective_target: str
    effective_dataset_reference: str | None
    model_overridden: bool
    target_overridden: bool
    dataset_overridden: bool

    def apply_to(self, program: ProgramNode) -> ProgramNode:
        """Return an isolated AST view with this invocation's effective header."""

        effective = deepcopy(program)
        effective.header.model = self.effective_model_reference
        effective.header.target = self.effective_target
        effective.header.dataset = self.effective_dataset_reference
        return effective

    def to_dict(self) -> dict[str, object]:
        return {
            "declared": {
                "model": self.declared_model_reference,
                "target": self.declared_target,
                "dataset": self.declared_dataset_reference,
            },
            "effective": {
                "model": self.effective_model_reference,
                "target": self.effective_target,
                "dataset": self.effective_dataset_reference,
            },
            "overrides": {
                "model": self.model_overridden,
                "target": self.target_overridden,
                "dataset": self.dataset_overridden,
            },
        }


def resolve_execution_context(
    *,
    declared_model_reference: str,
    declared_target: str,
    declared_dataset_reference: str | None,
    model: str | Path | None,
    target: str | None,
    dataset: str | Path | None,
) -> ExecutionContext:
    """Resolve temporary CLI/API overrides without mutating the specification."""

    effective_target = declared_target if target is None else _validated_target(target)
    return ExecutionContext(
        declared_model_reference=declared_model_reference,
        declared_target=declared_target,
        declared_dataset_reference=declared_dataset_reference,
        effective_model_reference=(
            declared_model_reference if model is None else os.fspath(model)
        ),
        effective_target=effective_target,
        effective_dataset_reference=(
            declared_dataset_reference if dataset is None else os.fspath(dataset)
        ),
        model_overridden=model is not None,
        target_overridden=target is not None,
        dataset_overridden=dataset is not None,
    )


def _validated_target(value: str) -> str:
    candidate = value.strip()
    if (
        candidate != value
        or _TARGET_IDENTIFIER.fullmatch(candidate) is None
        or candidate.lower() in _PROTECTED_TARGETS
    ):
        raise VerificationConfigurationError(
            f"Invalid target override: {value!r}",
            code="TARGET_OVERRIDE_INVALID",
            stage="configuration",
            hint=(
                "Use one non-reserved Toetra identifier such as 'score' or "
                "'risk_probability'."
            ),
        )
    return candidate
