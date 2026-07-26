from __future__ import annotations

from typing import Any, Protocol

from toetra._backends.capabilities import BackendCapabilities
from toetra._backends.execution import BackendExecutionPolicy
from toetra._backends.results import VerificationResult
from toetra._compiler.ir.ir2.dsl.nodes import VerificationTaskIR2
from toetra._language.vocabulary.backends import EnumBackend


class BackendTranslator(Protocol):
    """Protocol for concrete backend translators.

    A translator consumes VerificationTaskIR2 and produces a backend-specific
    artifact, such as a Z3 expression graph. IR2 itself must never import a
    concrete translator.
    """

    backend: EnumBackend
    capabilities: BackendCapabilities

    def translate(self, task: VerificationTaskIR2) -> Any: ...


class BackendRunner(Protocol):
    """Protocol implemented by backend executors exposed to the runtime."""

    def run(
        self,
        task: VerificationTaskIR2,
        *,
        policy: BackendExecutionPolicy | None = None,
    ) -> VerificationResult: ...
