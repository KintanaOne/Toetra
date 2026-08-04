"""Atomic primary-output handling for Toetra CLI commands."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable, TextIO

from toetra._runtime.errors import (
    VerificationConfigurationError,
    VerificationRuntimeError,
)


def emit_primary_output(
    text: str,
    *,
    destination: str | Path,
    consumed_paths: Iterable[Path] = (),
    stream: TextIO,
) -> Path | None:
    """Write one normalized primary representation to stdout or atomically to disk."""

    normalized = text.rstrip("\n") + "\n"
    if str(destination) == "-":
        stream.write(normalized)
        return None

    output = Path(destination).expanduser().resolve()
    consumed = {path.expanduser().resolve() for path in consumed_paths}
    if output in consumed:
        raise VerificationConfigurationError(
            f"Output path collides with a consumed input artifact: {output}",
            code="CLI_OUTPUT_INPUT_COLLISION",
            stage="output",
            hint="Choose an output path distinct from the specification and artifacts.",
            path=str(output),
        )

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
            text=True,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(normalized)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(output)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
    except OSError as error:
        raise VerificationRuntimeError(
            f"Failed to write CLI output: {output}",
            code="CLI_OUTPUT_WRITE_FAILED",
            stage="output",
            hint="Check the destination path, permissions, and available storage.",
            path=str(output),
        ) from error
    return output
