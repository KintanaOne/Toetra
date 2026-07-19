from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from dsl.ast.nodes.anchors import (
    AnchorDeclarationNode,
    AnchorReferenceBindingNode,
    InlineAnchorBindingNode,
)
from dsl.ast.nodes.primitives import ConstantNode
from dsl.semantic.context.points import PointEnvironment
from dsl.semantic.errors.errors import InvalidPropertyError, TypeMismatchError
from dsl.semantic.symbols.point import (
    AnchorReference,
    PointBindingKind,
    PointFeatureSchema,
    PointLiteral,
    PointSymbol,
    ResolvedAnchorBinding,
    frozen_mapping,
)
from dsl.semantic.types.enums import EnumDataType

if TYPE_CHECKING:
    from model.schema.model_schema import ModelSchema


class AnchorValidator:
    """Validate global anchor declarations and build immutable point symbols."""

    def __init__(
        self,
        model_schema: ModelSchema | None = None,
        resolved_anchors: Mapping[str, ResolvedAnchorBinding] | None = None,
    ):
        self.model_schema = model_schema
        self.resolved_anchors = resolved_anchors or {}

    def validate(
        self,
        declarations: Sequence[AnchorDeclarationNode],
    ) -> PointEnvironment:
        symbols: list[PointSymbol] = []
        names: set[str] = set()

        for declaration in declarations:
            if declaration.name in names:
                raise InvalidPropertyError(
                    f"Duplicate anchor identifier '{declaration.name}'",
                    node=declaration,
                    context="AnchorValidator",
                )
            names.add(declaration.name)
            symbols.append(self._build_symbol(declaration))

        return PointEnvironment.from_global_anchors(symbols)

    def _build_symbol(self, declaration: AnchorDeclarationNode) -> PointSymbol:
        binding = declaration.binding

        if isinstance(binding, InlineAnchorBindingNode):
            return self._build_inline_symbol(declaration, binding)

        if isinstance(binding, AnchorReferenceBindingNode):
            return self._build_reference_symbol(declaration, binding)

        raise InvalidPropertyError(
            f"Unsupported anchor binding '{type(binding).__name__}'",
            node=declaration,
            context="AnchorValidator",
        )

    def _build_inline_symbol(
        self,
        declaration: AnchorDeclarationNode,
        binding: InlineAnchorBindingNode,
    ) -> PointSymbol:
        values: dict[str, ConstantNode] = {}

        for entry in binding.entries:
            if entry.feature in values:
                raise InvalidPropertyError(
                    f"Duplicate feature '{entry.feature}' in anchor "
                    f"'{declaration.name}'",
                    node=entry,
                    context="AnchorValidator",
                )
            values[entry.feature] = entry.value

        schema_features = self._validate_inline_schema(declaration, values)

        return PointSymbol(
            name=declaration.name,
            binding_kind=PointBindingKind.INLINE_ANCHOR,
            declaration=declaration,
            feature_schema=frozen_mapping(schema_features),
            concrete_values=frozen_mapping(
                {
                    name: PointLiteral(
                        value=value.value,
                        dtype=value.dtype,
                        source_lexeme=value.source_lexeme,
                        source_dtype=f"dsl:{value.dtype.value}",
                    )
                    for name, value in values.items()
                }
            ),
        )

    def _validate_inline_schema(
        self,
        declaration: AnchorDeclarationNode,
        values: dict[str, ConstantNode],
    ) -> dict[str, PointFeatureSchema]:
        if self.model_schema is None:
            return {}

        expected = self.model_schema.features
        unknown = [name for name in values if name not in expected]
        if unknown:
            available = ", ".join(sorted(expected))
            raise InvalidPropertyError(
                f"Unknown model feature '{unknown[0]}' in anchor "
                f"'{declaration.name}'. Available transformed features: {available}",
                node=declaration,
                context="AnchorValidator",
            )

        missing = [name for name in expected if name not in values]
        if missing:
            missing_text = ", ".join(missing)
            raise InvalidPropertyError(
                f"Incomplete anchor '{declaration.name}': missing transformed "
                f"model feature(s): {missing_text}",
                node=declaration,
                context="AnchorValidator",
            )

        for name, value in values.items():
            expected_dtype = expected[name].dtype
            if not _anchor_literal_compatible(expected_dtype, value.dtype):
                raise TypeMismatchError(
                    f"Anchor '{declaration.name}' feature '{name}' expects "
                    f"{expected_dtype.value}, got {value.dtype.value}",
                    node=value,
                    context="AnchorValidator",
                )

        return {
            name: PointFeatureSchema(
                name=feature.name,
                dtype=feature.dtype,
                nullable=feature.nullable,
            )
            for name, feature in expected.items()
        }

    def _build_reference_symbol(
        self,
        declaration: AnchorDeclarationNode,
        binding: AnchorReferenceBindingNode,
    ) -> PointSymbol:
        arguments: dict[str, ConstantNode] = {}

        for argument in binding.arguments:
            if argument.name in arguments:
                raise InvalidPropertyError(
                    f"Duplicate ref argument '{argument.name}' in anchor "
                    f"'{declaration.name}'",
                    node=argument,
                    context="AnchorValidator",
                )
            arguments[argument.name] = argument.value

        missing = [name for name in ("key", "value") if name not in arguments]
        if missing:
            raise InvalidPropertyError(
                f"Anchor '{declaration.name}' ref(...) is missing argument(s): "
                f"{', '.join(missing)}",
                node=declaration,
                context="AnchorValidator",
            )

        key = arguments["key"]
        if key.dtype is not EnumDataType.STRING or not isinstance(key.value, str):
            raise TypeMismatchError(
                f"Anchor '{declaration.name}' ref key must be a string literal",
                node=key,
                context="AnchorValidator",
            )
        if not key.value:
            raise InvalidPropertyError(
                f"Anchor '{declaration.name}' ref key cannot be empty",
                node=key,
                context="AnchorValidator",
            )

        feature_schema = (
            {
                name: PointFeatureSchema(
                    name=feature.name,
                    dtype=feature.dtype,
                    nullable=feature.nullable,
                )
                for name, feature in self.model_schema.features.items()
            }
            if self.model_schema is not None
            else {}
        )

        reference = AnchorReference(
            key=key.value,
            value=PointLiteral(
                value=arguments["value"].value,
                dtype=arguments["value"].dtype,
                source_lexeme=arguments["value"].source_lexeme,
                source_dtype=f"dsl:{arguments['value'].dtype.value}",
            ),
        )
        resolved = self.resolved_anchors.get(declaration.name)
        if resolved is not None:
            self._validate_resolved_reference(
                declaration,
                reference=reference,
                resolved=resolved,
            )

        concrete_values = None
        if resolved is not None:
            ordered_names = tuple(feature_schema) or tuple(resolved.concrete_values)
            concrete_values = frozen_mapping(
                {name: resolved.concrete_values[name] for name in ordered_names}
            )

        return PointSymbol(
            name=declaration.name,
            binding_kind=PointBindingKind.REFERENCED_ANCHOR,
            declaration=declaration,
            feature_schema=frozen_mapping(feature_schema),
            concrete_values=concrete_values,
            reference=reference,
            resolution=resolved.provenance if resolved is not None else None,
        )

    def _validate_resolved_reference(
        self,
        declaration: AnchorDeclarationNode,
        *,
        reference: AnchorReference,
        resolved: ResolvedAnchorBinding,
    ) -> None:
        provenance = resolved.provenance
        if (
            provenance.key != reference.key
            or provenance.lookup_value != reference.value
        ):
            raise InvalidPropertyError(
                f"Resolved anchor '{declaration.name}' provenance does not match "
                "its ref(...) declaration",
                node=declaration,
                context="AnchorValidator",
            )

        if self.model_schema is None:
            return

        expected = self.model_schema.features
        actual = resolved.concrete_values
        unknown = [name for name in actual if name not in expected]
        if unknown:
            raise InvalidPropertyError(
                f"Resolved anchor '{declaration.name}' contains unknown model "
                f"feature '{unknown[0]}'",
                node=declaration,
                context="AnchorValidator",
            )
        missing = [name for name in expected if name not in actual]
        if missing:
            raise InvalidPropertyError(
                f"Resolved anchor '{declaration.name}' is missing transformed "
                f"model feature(s): {', '.join(missing)}",
                node=declaration,
                context="AnchorValidator",
            )
        for name, literal in actual.items():
            if not _anchor_literal_compatible(expected[name].dtype, literal.dtype):
                raise TypeMismatchError(
                    f"Resolved anchor '{declaration.name}' feature '{name}' expects "
                    f"{expected[name].dtype.value}, got {literal.dtype.value}",
                    node=declaration,
                    context="AnchorValidator",
                )


def _anchor_literal_compatible(
    expected: EnumDataType,
    actual: EnumDataType,
) -> bool:
    if expected is actual:
        return True

    # Safe widening from an integer literal to a floating-point model feature.
    return expected is EnumDataType.FLOAT and actual is EnumDataType.INT
