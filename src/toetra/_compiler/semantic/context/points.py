from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from toetra._compiler.semantic.errors.errors import InvalidPropertyError
from toetra._compiler.semantic.symbols.point import PointSymbol

if TYPE_CHECKING:
    from toetra._compiler.ast.nodes.source import SourceSpan


@dataclass(frozen=True)
class LexicalPointFrame:
    """One canonical left-to-right point binder frame."""

    depth: int
    quantifier: str
    point: PointSymbol
    source_span: SourceSpan | None = None
    generated: bool = False


@dataclass
class PointEnvironment:
    """Composed semantic registry for global anchors and lexical points."""

    _points: OrderedDict[str, PointSymbol] = field(default_factory=OrderedDict)
    _global_anchor_names: tuple[str, ...] = ()
    _lexical_frames: list[LexicalPointFrame] = field(default_factory=list)

    @classmethod
    def from_global_anchors(
        cls,
        anchors: Iterable[PointSymbol],
    ) -> PointEnvironment:
        environment = cls()
        names: list[str] = []

        for anchor in anchors:
            environment.register(anchor)
            names.append(anchor.name)

        environment._global_anchor_names = tuple(names)
        return environment

    def fork_for_property(self) -> PointEnvironment:
        """Create an isolated property view retaining immutable global points."""
        return PointEnvironment(
            _points=OrderedDict(self._points.items()),
            _global_anchor_names=self._global_anchor_names,
            _lexical_frames=[],
        )

    def register(self, point: PointSymbol) -> None:
        if point.name in self._points:
            raise InvalidPropertyError(f"Point '{point.name}' is already declared")
        self._points[point.name] = point

    def register_lexical(
        self,
        point: PointSymbol,
        *,
        quantifier: str,
        source_span: SourceSpan | None = None,
        generated: bool = False,
    ) -> LexicalPointFrame:
        """Register one canonical binder frame in source expansion order."""
        self.register(point)
        frame = LexicalPointFrame(
            depth=len(self._lexical_frames) + 1,
            quantifier=quantifier,
            point=point,
            source_span=source_span,
            generated=generated,
        )
        self._lexical_frames.append(frame)
        return frame

    def resolve(self, name: str) -> PointSymbol | None:
        return self._points.get(name)

    def exists(self, name: str) -> bool:
        return name in self._points

    def all(self) -> tuple[PointSymbol, ...]:
        return tuple(self._points.values())

    def global_anchors(self) -> tuple[PointSymbol, ...]:
        return tuple(self._points[name] for name in self._global_anchor_names)

    def lexical_frames(self) -> tuple[LexicalPointFrame, ...]:
        return tuple(self._lexical_frames)

    def names(self) -> tuple[str, ...]:
        return tuple(self._points)

    def compatibility_variables(self) -> dict[str, str]:
        """Project exact point symbols to the legacy role mapping."""
        return {point.name: point.kind for point in self._points.values()}
