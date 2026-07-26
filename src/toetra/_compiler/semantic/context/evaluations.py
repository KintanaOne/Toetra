from __future__ import annotations

from dataclasses import dataclass, field

from toetra._compiler.semantic.symbols.point import PointSymbol


@dataclass(frozen=True, init=False)
class ModelEvaluationIdentity:
    """Stable identity for one model-output invocation at one point.

    Identity is the triple ``(model, point, output port)``. Observable kind is
    intentionally not part of this identity. ``target_name`` remains a
    read-only compatibility projection during Patch 21.
    """

    model_identity: str
    point: PointSymbol
    output_name: str

    def __init__(
        self,
        model_identity: str,
        point: PointSymbol,
        output_name: str | None = None,
        *,
        target_name: str | None = None,
    ) -> None:
        resolved_output_name = _resolve_output_name(output_name, target_name)
        object.__setattr__(self, "model_identity", model_identity)
        object.__setattr__(self, "point", point)
        object.__setattr__(self, "output_name", resolved_output_name)

    @property
    def target_name(self) -> str:
        """Compatibility projection for pre-Patch-21 consumers."""

        return self.output_name


@dataclass
class ModelEvaluationRegistry:
    """Intern evaluations so all observables reuse one model invocation."""

    _evaluations: dict[tuple[str, str, str], ModelEvaluationIdentity] = field(
        default_factory=dict
    )

    def intern(
        self,
        *,
        model_identity: str,
        point: PointSymbol,
        output_name: str | None = None,
        target_name: str | None = None,
    ) -> ModelEvaluationIdentity:
        resolved_output_name = _resolve_output_name(output_name, target_name)
        key = (model_identity, point.name, resolved_output_name)
        existing = self._evaluations.get(key)

        if existing is not None:
            return existing

        evaluation = ModelEvaluationIdentity(
            model_identity=model_identity,
            point=point,
            output_name=resolved_output_name,
        )
        self._evaluations[key] = evaluation
        return evaluation

    def all(self) -> tuple[ModelEvaluationIdentity, ...]:
        return tuple(self._evaluations.values())


def _resolve_output_name(
    output_name: str | None,
    target_name: str | None,
) -> str:
    if (
        output_name is not None
        and target_name is not None
        and output_name != target_name
    ):
        raise ValueError(
            "Model evaluation output_name and compatibility target_name must match"
        )

    resolved = output_name if output_name is not None else target_name
    if resolved is None or not resolved.strip():
        raise ValueError("Model evaluation requires a non-empty output name")
    return resolved
