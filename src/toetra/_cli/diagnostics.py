"""Process-level diagnostic rendering for the Toetra CLI."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import TextIO

DIAGNOSTIC_SCHEMA = "toetra.cli-diagnostic"
DIAGNOSTIC_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class CliDiagnostic:
    """Stable machine-readable representation of a CLI failure."""

    category: str
    code: str
    message: str
    hint: str | None = None

    def to_json(self) -> str:
        payload = {
            "schema": DIAGNOSTIC_SCHEMA,
            "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
            **asdict(self),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def render_diagnostic(
    diagnostic: CliDiagnostic,
    *,
    output_format: str,
    stream: TextIO | None = None,
) -> None:
    """Render one diagnostic to stderr without touching primary output."""

    target = sys.stderr if stream is None else stream

    if output_format == "json":
        print(diagnostic.to_json(), file=target)
        return

    print(f"toetra: {diagnostic.message}", file=target)
    if diagnostic.hint:
        print(f"hint: {diagnostic.hint}", file=target)
