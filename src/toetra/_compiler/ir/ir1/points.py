from __future__ import annotations

from toetra._compiler.ast.nodes.source import SourceSpan
from toetra._compiler.ir.ir1.nodes import (
    AnchorReferenceIR,
    AnchorResolutionIR,
    ModelEvaluationIR,
    PointBindingIR,
    PointConcreteValueIR,
    PointFeatureIR,
    PointLiteralIR,
    SourceSpanIR,
)
from toetra._compiler.semantic.context.evaluations import ModelEvaluationIdentity
from toetra._compiler.semantic.context.points import LexicalPointFrame
from toetra._compiler.semantic.symbols.point import PointSymbol


class PointIRRegistry:
    """Intern semantic points and evaluations for one IR1 property.

    One registry instance is shared by scope, domain and query translation so
    every reference to the same semantic point reuses the same immutable IR1
    identity object.
    """

    def __init__(self) -> None:
        self._points: dict[int, PointBindingIR] = {}
        self._evaluations: dict[int, ModelEvaluationIR] = {}
        self._frames: dict[int, LexicalPointFrame] = {}

    def clear(self) -> None:
        """Start translation of a new property."""
        self._points.clear()
        self._evaluations.clear()
        self._frames.clear()

    def register_frame(self, frame: LexicalPointFrame) -> None:
        self._frames[id(frame.point)] = frame

    def point(self, symbol: PointSymbol) -> PointBindingIR:
        key = id(symbol)
        existing = self._points.get(key)
        if existing is not None:
            return existing

        frame = self._frames.get(key)
        declaration_span = getattr(symbol.declaration, "source_span", None)
        source_span = frame.source_span if frame is not None else declaration_span
        point = PointBindingIR(
            name=symbol.name,
            binding_kind=symbol.binding_kind.value,
            lexical_depth=symbol.lexical_depth,
            source_span=_copy_source_span(source_span),
            generated=frame.generated if frame is not None else False,
            feature_schema=tuple(
                PointFeatureIR(
                    name=feature.name,
                    dtype=feature.dtype,
                    nullable=feature.nullable,
                )
                for feature in (symbol.feature_schema or {}).values()
            ),
            concrete_values=tuple(
                PointConcreteValueIR(
                    feature=name,
                    literal=PointLiteralIR(
                        value=literal.value,
                        dtype=literal.dtype,
                        source_lexeme=literal.source_lexeme,
                        source_dtype=literal.source_dtype,
                    ),
                )
                for name, literal in (symbol.concrete_values or {}).items()
            ),
            reference=(
                AnchorReferenceIR(
                    key=symbol.reference.key,
                    value=PointLiteralIR(
                        value=symbol.reference.value.value,
                        dtype=symbol.reference.value.dtype,
                        source_lexeme=symbol.reference.value.source_lexeme,
                        source_dtype=symbol.reference.value.source_dtype,
                    ),
                )
                if symbol.reference is not None
                else None
            ),
            resolution=(
                AnchorResolutionIR(
                    key=symbol.resolution.key,
                    lookup_value=PointLiteralIR(
                        value=symbol.resolution.lookup_value.value,
                        dtype=symbol.resolution.lookup_value.dtype,
                        source_lexeme=symbol.resolution.lookup_value.source_lexeme,
                        source_dtype=symbol.resolution.lookup_value.source_dtype,
                    ),
                    source_kind=symbol.resolution.source_kind,
                    source_reference=symbol.resolution.source_reference,
                    row_index=symbol.resolution.row_index,
                )
                if symbol.resolution is not None
                else None
            ),
        )
        self._points[key] = point
        return point

    def evaluation(self, identity: ModelEvaluationIdentity) -> ModelEvaluationIR:
        key = id(identity)
        existing = self._evaluations.get(key)
        if existing is not None:
            return existing

        evaluation = ModelEvaluationIR(
            model_identity=identity.model_identity,
            point=self.point(identity.point),
            output_name=identity.output_name,
        )
        self._evaluations[key] = evaluation
        return evaluation


def copy_source_span(source_span: SourceSpan | None) -> SourceSpanIR | None:
    """Expose source-span conversion to IR1 translators."""
    return _copy_source_span(source_span)


def _copy_source_span(source_span: SourceSpan | None) -> SourceSpanIR | None:
    if source_span is None:
        return None
    return SourceSpanIR(
        line=source_span.line,
        column=source_span.column,
        end_line=source_span.end_line,
        end_column=source_span.end_column,
    )
