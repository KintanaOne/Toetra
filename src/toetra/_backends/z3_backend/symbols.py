from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

from toetra._compiler.ir.ir1.model_quantities import EnumModelQuantityKind
from toetra._compiler.ir.ir1.nodes import ModelEvaluationIR, PointBindingIR


@dataclass(frozen=True)
class Z3PointFeatureIdentity:
    """Structured backend identity for one point-qualified input feature."""

    point: PointBindingIR
    feature: str


@dataclass(frozen=True)
class Z3ModelOutputIdentity:
    """Structured backend identity for one point-indexed public model output."""

    evaluation: ModelEvaluationIR


@dataclass(frozen=True)
class Z3ModelQuantityIdentity:
    """Structured identity for one internal model-semantic quantity.

    The identity is deliberately distinct from :class:`Z3ModelOutputIdentity`.
    A latent decision quantity is solver evidence, not a public model output.
    """

    evaluation: ModelEvaluationIR
    quantity_kind: EnumModelQuantityKind
    semantic_profile_id: str


@dataclass(frozen=True)
class Z3LegacyScalarIdentity:
    """Compatibility identity for IR nodes not yet carrying point metadata."""

    entity: str
    feature: str


Z3SymbolIdentity: TypeAlias = (
    Z3PointFeatureIdentity
    | Z3ModelOutputIdentity
    | Z3ModelQuantityIdentity
    | Z3LegacyScalarIdentity
)


def z3_symbol_name(identity: Z3SymbolIdentity) -> str:
    """Return the stable human-readable solver name for one identity.

    Names are only a backend projection. Semantic equality and reverse mapping
    always use the structured identity objects above.
    """

    if isinstance(identity, Z3PointFeatureIdentity):
        return f"{identity.point.name}.{identity.feature}"
    if isinstance(identity, Z3ModelOutputIdentity):
        evaluation = identity.evaluation
        return f"_model.{evaluation.output_name}[{evaluation.point.name}]"
    if isinstance(identity, Z3ModelQuantityIdentity):
        evaluation = identity.evaluation
        return (
            f"_model.{evaluation.output_name}[{evaluation.point.name}]"
            f"::<{identity.quantity_kind.value}>"
        )
    return f"{identity.entity}.{identity.feature}"


def compatibility_assignment_name(
    identity: Z3SymbolIdentity,
    *,
    model_output_count: int,
) -> str:
    """Return the temporary public assignment name used before Patch 15.11.

    Single-output result consumers historically expect ``_model.target``. The
    solver itself always uses the indexed name. Multi-point results keep their
    indexed names because flattening them would be ambiguous. Internal model
    quantities are never flattened into the public output namespace.
    """

    if isinstance(identity, Z3ModelOutputIdentity) and model_output_count == 1:
        return f"_model.{identity.evaluation.output_name}"
    return z3_symbol_name(identity)


def symbol_identity_metadata(identity: Z3SymbolIdentity) -> dict[str, Any]:
    """Serialize a reverse mapping without losing point/evaluation identity."""

    if isinstance(identity, Z3PointFeatureIdentity):
        return {
            "kind": "point_feature",
            "point": _point_metadata(identity.point),
            "feature": identity.feature,
        }
    if isinstance(identity, Z3ModelOutputIdentity):
        evaluation = identity.evaluation
        return {
            "kind": "model_output",
            "model_identity": evaluation.model_identity,
            "point": _point_metadata(evaluation.point),
            "target": evaluation.output_name,
        }
    if isinstance(identity, Z3ModelQuantityIdentity):
        evaluation = identity.evaluation
        return {
            "kind": "model_quantity",
            "model_identity": evaluation.model_identity,
            "point": _point_metadata(evaluation.point),
            "output_name": evaluation.output_name,
            "quantity_kind": identity.quantity_kind.value,
            "semantic_profile_id": identity.semantic_profile_id,
        }
    return {
        "kind": "legacy_scalar",
        "entity": identity.entity,
        "feature": identity.feature,
    }


def _point_metadata(point: PointBindingIR) -> dict[str, Any]:
    return {
        "name": point.name,
        "binding_kind": point.binding_kind,
        "lexical_depth": point.lexical_depth,
        "generated": point.generated,
    }
