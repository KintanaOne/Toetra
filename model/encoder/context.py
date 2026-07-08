from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ModelEncodingContext:
    """Options controlling model-to-IR2 assumption encoding.

    This context is backend-independent. It controls which families of model
    assumptions should be emitted, but it must never mention a concrete solver
    such as Z3.
    """

    strict: bool = True
    include_feature_domains: bool = True
    include_model_constraints: bool = True
    include_output_constraints: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)
