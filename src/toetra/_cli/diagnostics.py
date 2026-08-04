"""Process-level diagnostic rendering for the Toetra CLI."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from typing import TextIO

DIAGNOSTIC_SCHEMA = "toetra.cli-diagnostic"
DIAGNOSTIC_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class CliDiagnostic:
    """Stable machine-readable representation of a CLI failure."""

    category: str
    code: str
    message: str
    stage: str | None = None
    hint: str | None = None
    path: str | None = None
    line: int | None = None
    column: int | None = None
    command: str | None = None
    debug_traceback: str | None = None

    def to_json(self) -> str:
        try:
            toetra_version = version("toetra")
        except PackageNotFoundError:
            toetra_version = "unknown"
        payload: dict[str, object] = {
            "schema": DIAGNOSTIC_SCHEMA,
            "schema_version": DIAGNOSTIC_SCHEMA_VERSION,
            "category": self.category,
            "code": self.code,
            "stage": self.stage,
            "message": self.message,
            "hint": self.hint,
            "location": {
                "path": self.path,
                "line": self.line,
                "column": self.column,
            },
            "command": self.command,
            "software": {"toetra_version": toetra_version},
        }
        if self.debug_traceback is not None:
            payload["debug_traceback"] = self.debug_traceback
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
    if diagnostic.path is not None:
        location = diagnostic.path
        if diagnostic.line is not None:
            location += f":{diagnostic.line}"
            if diagnostic.column is not None:
                location += f":{diagnostic.column}"
        print(f"location: {location}", file=target)
    if diagnostic.hint:
        print(f"hint: {diagnostic.hint}", file=target)
    if diagnostic.debug_traceback:
        print(diagnostic.debug_traceback, file=target)
