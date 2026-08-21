from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ModelLoweringContext:
    """Backend-independent controls for model-to-IR2 lowering."""

    strict: bool = True
    include_feature_domains: bool = True
    include_model_constraints: bool = True
    include_output_constraints: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)
