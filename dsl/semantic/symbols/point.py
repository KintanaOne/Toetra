from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping, TypeVar

from dsl.semantic.types.enums import EnumDataType

if TYPE_CHECKING:
    from dsl.ast.nodes.anchors import AnchorDeclarationNode
    from dsl.ast.nodes.primitives import PrimitiveValue


class PointBindingKind(Enum):
    """Semantic origin of one model-input point."""

    INLINE_ANCHOR = "inline_anchor"
    REFERENCED_ANCHOR = "referenced_anchor"
    UNIVERSAL = "universal"
    EXISTENTIAL = "existential"
    PERTURBATION = "perturbation"
    # Diagnostic/compatibility-only: new source programs never register these.
    LEGACY_ANCHOR = "legacy_anchor"


@dataclass(frozen=True)
class PointLiteral:
    """Immutable literal snapshot retained by a semantic point binding."""

    value: PrimitiveValue
    dtype: EnumDataType
    source_lexeme: str | None = field(default=None, compare=False)
    source_dtype: str | None = field(default=None, compare=False)


@dataclass(frozen=True)
class PointFeatureSchema:
    """Immutable model-input feature schema snapshot for one point."""

    name: str
    dtype: EnumDataType
    nullable: bool


@dataclass(frozen=True)
class AnchorReference:
    """Validated single-source lookup metadata for a referenced anchor."""

    key: str
    value: PointLiteral


@dataclass(frozen=True)
class AnchorResolutionProvenance:
    """Runtime provenance retained for one resolved referenced anchor."""

    key: str
    lookup_value: PointLiteral
    source_kind: str
    source_reference: str | None
    row_index: str


@dataclass(frozen=True)
class ResolvedAnchorBinding:
    """Concrete values and lookup provenance supplied by the runtime."""

    concrete_values: Mapping[str, PointLiteral]
    provenance: AnchorResolutionProvenance


@dataclass(frozen=True)
class PointSymbol:
    """Immutable semantic identity for one concrete or symbolic input point."""

    name: str
    binding_kind: PointBindingKind
    declaration: AnchorDeclarationNode | object
    lexical_depth: int = 0
    feature_schema: Mapping[str, PointFeatureSchema] | None = None
    concrete_values: Mapping[str, PointLiteral] | None = None
    reference: AnchorReference | None = None
    resolution: AnchorResolutionProvenance | None = None

    @property
    def kind(self) -> str:
        """Backward-compatible symbol role consumed by existing binders."""
        if self.binding_kind in {
            PointBindingKind.INLINE_ANCHOR,
            PointBindingKind.REFERENCED_ANCHOR,
            PointBindingKind.LEGACY_ANCHOR,
        }:
            return "anchor"
        return "symbolic"

    @property
    def dtype(self) -> EnumDataType | None:
        """Points are structured entities rather than scalar-typed symbols."""
        return None

    @property
    def origin(self) -> object:
        """Compatibility alias shared with the historical ``Symbol`` type."""
        return self.declaration

    @property
    def is_anchor(self) -> bool:
        return self.binding_kind in {
            PointBindingKind.INLINE_ANCHOR,
            PointBindingKind.REFERENCED_ANCHOR,
            PointBindingKind.LEGACY_ANCHOR,
        }


_T = TypeVar("_T")


def frozen_mapping(values: Mapping[str, _T]) -> Mapping[str, _T]:
    """Copy a mapping into a read-only deterministic semantic payload."""
    return MappingProxyType(dict(values))
