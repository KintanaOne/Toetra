from __future__ import annotations

from dataclasses import dataclass, field

from dsl.semantic.symbols.point import PointSymbol


@dataclass(frozen=True)
class ModelEvaluationIdentity:
    """Stable semantic identity for one model invocation at one point.

    FORML V1 exposes one scalar target per model header. The target name is
    retained as metadata, while identity itself is the pair ``(model, point)``.
    """

    model_identity: str
    point: PointSymbol
    target_name: str


@dataclass
class ModelEvaluationRegistry:
    """Intern model evaluations so repeated target references share identity."""

    _evaluations: dict[tuple[str, str], ModelEvaluationIdentity] = field(
        default_factory=dict
    )

    def intern(
        self,
        *,
        model_identity: str,
        point: PointSymbol,
        target_name: str,
    ) -> ModelEvaluationIdentity:
        key = (model_identity, point.name)
        existing = self._evaluations.get(key)

        if existing is not None:
            if existing.target_name != target_name:
                raise ValueError(
                    "One model-point evaluation cannot be associated with "
                    "several target names"
                )
            return existing

        evaluation = ModelEvaluationIdentity(
            model_identity=model_identity,
            point=point,
            target_name=target_name,
        )
        self._evaluations[key] = evaluation
        return evaluation

    def all(self) -> tuple[ModelEvaluationIdentity, ...]:
        return tuple(self._evaluations.values())
