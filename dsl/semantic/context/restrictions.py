from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dsl.ast.nodes.assertion import LogicalNode
    from dsl.ast.nodes.source import SourceSpan


class RestrictionOrigin(Enum):
    """Source form that introduced one canonical semantic restriction."""

    WHERE = "where"
    AT_SUGAR = "at_sugar"


class VerificationSemantics(Enum):
    """Source-level interpretation selected for one restricted property."""

    REFUTATION = "refutation"
    SATISFACTION = "satisfaction"


@dataclass(frozen=True)
class RestrictionProvenance:
    """Trace one generated semantic artifact back to its source surface."""

    origin: RestrictionOrigin
    source_span: SourceSpan | None


@dataclass(frozen=True)
class CanonicalRestrictionSemantics:
    """Canonical language and verification views of one source restriction."""

    quantifier: str
    restriction: LogicalNode
    assertion: LogicalNode
    language_formula: LogicalNode
    verification_body: LogicalNode
    verification_semantics: VerificationSemantics
    provenance: RestrictionProvenance
