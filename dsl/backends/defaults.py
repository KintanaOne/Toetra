from __future__ import annotations

from dsl.backends.registry import BackendRegistry
from dsl.backends.z3_backend.capabilities import Z3_CAPABILITIES


def create_default_backend_registry() -> BackendRegistry:
    registry = BackendRegistry()
    registry.register(Z3_CAPABILITIES)
    return registry
