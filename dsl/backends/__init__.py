"""Backend routing primitives.

This package is intentionally backend-neutral at the top level. Concrete
backends such as Z3 should live in subpackages and register capabilities here.
"""

from dsl.backends.capabilities import BackendCapabilities
from dsl.backends.registry import BackendRegistry
from dsl.backends.router import BackendRoute, BackendRouter

__all__ = [
    "BackendCapabilities",
    "BackendRegistry",
    "BackendRoute",
    "BackendRouter",
]
