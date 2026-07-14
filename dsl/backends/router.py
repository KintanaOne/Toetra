from __future__ import annotations

from dataclasses import dataclass

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.errors import BackendNotRegisteredError, NoCompatibleBackendError
from dsl.backends.registry import BackendRegistry
from dsl.ir.ir2.nodes import VerificationTaskIR2
from dsl.language.vocabulary.backends import EnumBackend


@dataclass(frozen=True)
class BackendRoute:
    """Routing decision produced from an IR2-compatible task."""

    backend: EnumBackend
    capabilities: BackendCapabilities
    reason: str


class BackendRouter:
    """Selects a backend from IR2 requirements and registered capabilities."""

    def __init__(self, registry: BackendRegistry | None = None):
        self.registry = registry or BackendRegistry()

    def route(self, task: VerificationTaskIR2) -> BackendRoute:
        requested_backend = task.backend

        if requested_backend is not None:
            return self._route_requested_backend(task, requested_backend)

        return self._route_any_compatible_backend(task)

    def _route_requested_backend(
        self,
        task: VerificationTaskIR2,
        backend: EnumBackend,
    ) -> BackendRoute:
        capabilities = self.registry.get(backend)

        if capabilities is None:
            raise BackendNotRegisteredError(
                f"Requested backend '{backend.value}' is not registered"
            )

        incompatibilities = capabilities.incompatibilities(task.requirements)
        if incompatibilities:
            details = "; ".join(incompatibilities)
            raise NoCompatibleBackendError(
                f"Requested backend '{backend.value}' does not satisfy IR2 "
                f"requirements: {details}"
            )

        return BackendRoute(
            backend=capabilities.backend,
            capabilities=capabilities,
            reason="requested backend satisfies IR2 requirements",
        )

    def _route_any_compatible_backend(self, task: VerificationTaskIR2) -> BackendRoute:
        for capabilities in self.registry.all():
            if capabilities.supports(task.requirements):
                return BackendRoute(
                    backend=capabilities.backend,
                    capabilities=capabilities,
                    reason="first registered backend satisfying IR2 requirements",
                )

        raise NoCompatibleBackendError(
            "No registered backend satisfies IR2 requirements"
        )
