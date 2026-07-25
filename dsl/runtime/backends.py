from __future__ import annotations

from dataclasses import dataclass, field

from dsl.backends.base import BackendRunner
from dsl.backends.z3_backend.runner import Z3Runner
from dsl.language.vocabulary.backends import EnumBackend
from dsl.runtime.errors import BackendRunnerNotRegisteredError


@dataclass
class BackendRunnerRegistry:
    """Runtime registry mapping routed backends to concrete executors."""

    _runners: dict[EnumBackend, BackendRunner] = field(default_factory=dict)

    def register(self, backend: EnumBackend, runner: BackendRunner) -> None:
        self._runners[backend] = runner

    def get(self, backend: EnumBackend) -> BackendRunner | None:
        return self._runners.get(backend)

    def require(self, backend: EnumBackend) -> BackendRunner:
        runner = self.get(backend)
        if runner is None:
            raise BackendRunnerNotRegisteredError(
                f"No runtime runner is registered for backend '{backend.value}'"
            )
        return runner

    def clear(self) -> None:
        self._runners.clear()


def create_default_backend_runner_registry() -> BackendRunnerRegistry:
    """Create the runner registry shipped with the current Toetra runtime."""

    registry = BackendRunnerRegistry()
    registry.register(EnumBackend.Z3, Z3Runner())
    return registry
