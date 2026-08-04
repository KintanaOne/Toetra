from __future__ import annotations

from toetra._backends.registry import BackendRegistry


def create_default_backend_registry() -> BackendRegistry:
    from toetra._backends.z3_backend.capabilities import Z3_CAPABILITIES

    registry = BackendRegistry()
    registry.register(Z3_CAPABILITIES)
    return registry
