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


def normalize_output_text(text: str) -> str:
    """Return one UTF-8-friendly representation with exactly one final newline."""

    return text.rstrip("\r\n") + "\n"


def validate_output_paths(
    destinations: Iterable[str | Path],
    *,
    consumed_paths: Iterable[Path] = (),
) -> tuple[Path, ...]:
    """Resolve and validate a complete set of file outputs before writing."""

    consumed = {path.expanduser().resolve() for path in consumed_paths}
    resolved: list[Path] = []
    seen: set[Path] = set()
    for destination in destinations:
        output = Path(destination).expanduser().resolve()
        if output in consumed:
            raise VerificationConfigurationError(
                f"Output path collides with a consumed input artifact: {output}",
                code="CLI_OUTPUT_INPUT_COLLISION",
                stage="output",
                hint=(
                    "Choose output paths distinct from the specification and "
                    "input artifacts."
                ),
                path=str(output),
            )
        if output in seen:
            raise VerificationConfigurationError(
                f"Output path collides with another CLI output artifact: {output}",
                code="CLI_OUTPUT_OUTPUT_COLLISION",
                stage="output",
                hint="Choose distinct primary-output and artifact destinations.",
                path=str(output),
            )
        seen.add(output)
        resolved.append(output)
    return tuple(resolved)


def write_atomic_text(
    text: str,
    destination: str | Path,
    *,
    consumed_paths: Iterable[Path] = (),
    reserved_paths: Iterable[Path] = (),
) -> Path:
    """Commit normalized UTF-8 text atomically after collision validation."""

    output = Path(destination).expanduser().resolve()
    consumed = {path.expanduser().resolve() for path in consumed_paths}
    reserved = {path.expanduser().resolve() for path in reserved_paths}
    if output in consumed:
        raise VerificationConfigurationError(
            f"Output path collides with a consumed input artifact: {output}",
            code="CLI_OUTPUT_INPUT_COLLISION",
            stage="output",
            hint="Choose an output path distinct from the specification and artifacts.",
            path=str(output),
        )
    if output in reserved:
        raise VerificationConfigurationError(
            f"Output path collides with another CLI output artifact: {output}",
            code="CLI_OUTPUT_OUTPUT_COLLISION",
            stage="output",
            hint="Choose distinct primary-output and artifact destinations.",
            path=str(output),
        )

    normalized = normalize_output_text(text)
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
        except BaseException:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
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


def emit_primary_output(
    text: str,
    *,
    destination: str | Path,
    consumed_paths: Iterable[Path] = (),
    reserved_paths: Iterable[Path] = (),
    stream: TextIO,
) -> Path | None:
    """Write one normalized primary representation to stdout or atomically to disk."""

    normalized = normalize_output_text(text)
    if str(destination) == "-":
        try:
            stream.write(normalized)
            stream.flush()
        except UnicodeEncodeError:
            encoding = stream.encoding or "utf-8"
            escaped = normalized.encode(encoding, errors="backslashreplace").decode(
                encoding
            )
            stream.write(escaped)
            stream.flush()
        except OSError as error:
            raise VerificationRuntimeError(
                "Failed to write CLI output to stdout.",
                code="CLI_STDOUT_WRITE_FAILED",
                stage="output",
                hint="Check the receiving process or redirect output to a file.",
            ) from error
        return None

    return write_atomic_text(
        normalized,
        destination,
        consumed_paths=consumed_paths,
        reserved_paths=reserved_paths,
    )
