from __future__ import annotations

from typing import Any, Protocol

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.results import VerificationResult
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.language.vocabulary.backends import EnumBackend


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

    def run(self, task: VerificationTaskIR2) -> VerificationResult: ...
