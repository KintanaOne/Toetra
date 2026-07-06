from __future__ import annotations

from dataclasses import dataclass, field

from dsl.backends.capabilities import BackendCapabilities
from dsl.language.vocabulary.backends import EnumBackend


@dataclass
class BackendRegistry:
    """Registry of backend capabilities.

    Concrete backend packages can register themselves here later. The registry
    stores capabilities only; translator instances can be added in a future
    extension without changing IR2.
    """

    _capabilities: dict[EnumBackend, BackendCapabilities] = field(default_factory=dict)

    def register(self, capabilities: BackendCapabilities) -> None:
        self._capabilities[capabilities.backend] = capabilities

    def get(self, backend: EnumBackend) -> BackendCapabilities | None:
        return self._capabilities.get(backend)

    def all(self) -> tuple[BackendCapabilities, ...]:
        return tuple(self._capabilities.values())

    def clear(self) -> None:
        self._capabilities.clear()
