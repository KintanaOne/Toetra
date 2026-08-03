"""Supported public Python API for Toetra model verification.

Only names listed in :data:`__all__` belong to the stable V1 Python contract.
Modules beneath ``toetra._*`` are private implementation details.

The facade resolves public symbols lazily so process-level operations such as
``toetra --help`` and ``python -m toetra --version`` do not import compiler,
model, backend, or solver implementations.
"""

from importlib import import_module as _import_module
from typing import TYPE_CHECKING as _TYPE_CHECKING
from typing import Any as _Any

if _TYPE_CHECKING:
    from toetra._backends.results import VerificationStatus
    from toetra._reporting.model import VerificationReport
    from toetra._runtime.api import verify
    from toetra._runtime.errors import (
        ReplayUnavailableError,
        VerificationConfigurationError,
        VerificationRuntimeError,
    )
    from toetra._runtime.replay import CounterexampleReplay
    from toetra._runtime.session import VerificationFinding, VerificationSession

__all__ = (
    "CounterexampleReplay",
    "ReplayUnavailableError",
    "VerificationConfigurationError",
    "VerificationFinding",
    "VerificationReport",
    "VerificationRuntimeError",
    "VerificationSession",
    "VerificationStatus",
    "verify",
)

_PUBLIC_IMPORTS = {
    "CounterexampleReplay": ("toetra._runtime.replay", "CounterexampleReplay"),
    "ReplayUnavailableError": (
        "toetra._runtime.errors",
        "ReplayUnavailableError",
    ),
    "VerificationConfigurationError": (
        "toetra._runtime.errors",
        "VerificationConfigurationError",
    ),
    "VerificationFinding": ("toetra._runtime.session", "VerificationFinding"),
    "VerificationReport": ("toetra._reporting.model", "VerificationReport"),
    "VerificationRuntimeError": (
        "toetra._runtime.errors",
        "VerificationRuntimeError",
    ),
    "VerificationSession": ("toetra._runtime.session", "VerificationSession"),
    "VerificationStatus": ("toetra._backends.results", "VerificationStatus"),
    "verify": ("toetra._runtime.api", "verify"),
}


def __getattr__(name: str) -> _Any:
    try:
        module_name, attribute_name = _PUBLIC_IMPORTS[name]
    except KeyError as error:
        message = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(message) from error

    value = getattr(_import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
