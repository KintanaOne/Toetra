"""Validate canonical documentation snippets and every declared consumer."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path("docs/snippets/manifest.toml")
SNIPPET_ROOT = Path("docs/snippets")
SUPPORTED_CHECKS = {
    "python": "python-compile",
    "toetra": "toetra-parse",
}
COPY_PATTERN = re.compile(
    r"<!--\s*toetra-doc-snippet:\s*(?P<id>[a-z0-9-]+)\s*-->\s*"
    r"```(?P<language>[a-z0-9-]+)\s*\n(?P<body>.*?)```",
    re.DOTALL,
)
INCLUDE_PATTERN = re.compile(r'--8<--\s+"(?P<path>docs/snippets/[A-Za-z0-9_.-]+)"')


@dataclass(frozen=True)
class Snippet:
    """One canonical snippet and the documents that consume it."""

    identifier: str
    path: Path
    language: str
    check: str
    include_in: tuple[Path, ...]
    copy_in: tuple[Path, ...]


class SnippetContractError(RuntimeError):
    """Raised when the snippet manifest cannot be interpreted."""


def _string_tuple(value: object, *, field: str, identifier: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SnippetContractError(
            f"{identifier}: {field} must be an array of repository-relative paths"
        )
    return tuple(value)


def _load_manifest(root: Path) -> tuple[Snippet, ...]:
    path = root / MANIFEST_PATH
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SnippetContractError(f"{MANIFEST_PATH}: {error}") from error

    if data.get("schema_version") != 1:
        raise SnippetContractError(f"{MANIFEST_PATH}: schema_version must be 1")

    raw_snippets = data.get("snippet")
    if not isinstance(raw_snippets, list) or not raw_snippets:
        raise SnippetContractError(f"{MANIFEST_PATH}: at least one snippet is required")

    snippets: list[Snippet] = []
    identifiers: set[str] = set()
    paths: set[Path] = set()
    for index, raw in enumerate(raw_snippets, start=1):
        if not isinstance(raw, dict):
            raise SnippetContractError(
                f"{MANIFEST_PATH}: snippet {index} must be a table"
            )
        identifier = raw.get("id")
        source = raw.get("path")
        language = raw.get("language")
        check = raw.get("check")
        if not all(
            isinstance(value, str) for value in (identifier, source, language, check)
        ):
            raise SnippetContractError(
                f"{MANIFEST_PATH}: snippet {index} has non-string required fields"
            )
        assert isinstance(identifier, str)
        assert isinstance(source, str)
        assert isinstance(language, str)
        assert isinstance(check, str)

        if not re.fullmatch(r"[a-z0-9-]+", identifier):
            raise SnippetContractError(f"{identifier!r}: invalid snippet id")
        if identifier in identifiers:
            raise SnippetContractError(f"{identifier}: duplicate snippet id")

        source_path = Path(source)
        if source_path.parent != SNIPPET_ROOT:
            raise SnippetContractError(
                f"{identifier}: canonical source must be directly under {SNIPPET_ROOT}"
            )
        if source_path in paths:
            raise SnippetContractError(f"{source_path}: duplicate canonical source")
        if SUPPORTED_CHECKS.get(language) != check:
            raise SnippetContractError(
                f"{identifier}: {language!r} snippets require "
                f"{SUPPORTED_CHECKS.get(language)!r}, found {check!r}"
            )

        include_in = _string_tuple(
            raw.get("include_in", []),
            field="include_in",
            identifier=identifier,
        )
        copy_in = _string_tuple(
            raw.get("copy_in", []),
            field="copy_in",
            identifier=identifier,
        )
        if not include_in and not copy_in:
            raise SnippetContractError(
                f"{identifier}: at least one consumer document is required"
            )

        snippets.append(
            Snippet(
                identifier=identifier,
                path=source_path,
                language=language,
                check=check,
                include_in=tuple(Path(item) for item in include_in),
                copy_in=tuple(Path(item) for item in copy_in),
            )
        )
        identifiers.add(identifier)
        paths.add(source_path)

    return tuple(snippets)


def _normalize_source(source: str) -> str:
    return source.strip("\n") + "\n"


def _check_python(source: str, path: Path) -> str | None:
    try:
        compile(source, path.as_posix(), "exec")
    except SyntaxError as error:
        return f"{path}: Python compilation failed: {error}"
    return None


def _check_toetra(source: str, path: Path, *, root: Path) -> str | None:
    source_root = root / "src"
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

    try:
        from toetra._compiler.builder.program import parse_program
        from toetra._compiler.parser.parser import parse_toetra_code

        parse_program(parse_toetra_code(source))
    except Exception as error:  # pragma: no cover - diagnostic boundary
        return f"{path}: Toetra parsing failed: {error}"
    return None


def _markdown_files(root: Path) -> Iterable[Path]:
    yield root / "README.md"
    yield from sorted((root / "docs").rglob("*.md"))


def snippet_errors(root: Path = ROOT) -> tuple[str, ...]:
    """Return every canonical-snippet contract violation."""

    root = root.resolve()
    try:
        snippets = _load_manifest(root)
    except SnippetContractError as error:
        return (str(error),)

    errors: list[str] = []
    by_identifier = {snippet.identifier: snippet for snippet in snippets}
    by_path = {snippet.path.as_posix(): snippet for snippet in snippets}

    registered_files = {snippet.path for snippet in snippets}
    actual_files = {
        path.relative_to(root)
        for path in (root / SNIPPET_ROOT).iterdir()
        if path.is_file() and path.name != MANIFEST_PATH.name
    }
    for path in sorted(registered_files - actual_files):
        errors.append(f"{path}: registered canonical snippet is missing")
    for path in sorted(actual_files - registered_files):
        errors.append(f"{path}: canonical snippet is not registered")

    document_sources: dict[Path, str] = {}
    observed_copy_ids: dict[str, list[Path]] = {}
    observed_include_paths: dict[str, list[Path]] = {}
    for document in _markdown_files(root):
        if not document.is_file():
            continue
        relative_document = document.relative_to(root)
        source = document.read_text(encoding="utf-8")
        document_sources[relative_document] = source
        for match in COPY_PATTERN.finditer(source):
            observed_copy_ids.setdefault(match.group("id"), []).append(
                relative_document
            )
        for match in INCLUDE_PATTERN.finditer(source):
            observed_include_paths.setdefault(match.group("path"), []).append(
                relative_document
            )

    for snippet in snippets:
        source_path = root / snippet.path
        if not source_path.is_file():
            continue
        source = source_path.read_text(encoding="utf-8")
        if snippet.check == "python-compile":
            error = _check_python(source, snippet.path)
        else:
            error = _check_toetra(source, snippet.path, root=root)
        if error is not None:
            consumers = ", ".join(
                path.as_posix() for path in (*snippet.include_in, *snippet.copy_in)
            )
            errors.append(f"{error}; consumers: {consumers}")

        directive = f'--8<-- "{snippet.path.as_posix()}"'
        for document in snippet.include_in:
            document_source = document_sources.get(document)
            if document_source is None:
                errors.append(
                    f"{snippet.identifier}: owning page is missing: {document}"
                )
                continue
            count = document_source.count(directive)
            if count != 1:
                errors.append(
                    f"{snippet.identifier}: {document} must include {snippet.path} "
                    f"exactly once; found {count}"
                )

        for document in snippet.copy_in:
            document_source = document_sources.get(document)
            if document_source is None:
                errors.append(
                    f"{snippet.identifier}: owning document is missing: {document}"
                )
                continue
            matches = tuple(
                match
                for match in COPY_PATTERN.finditer(document_source)
                if match.group("id") == snippet.identifier
            )
            if len(matches) != 1:
                errors.append(
                    f"{snippet.identifier}: {document} must contain one checked copy; "
                    f"found {len(matches)}"
                )
                continue
            match = matches[0]
            if match.group("language") != snippet.language:
                errors.append(
                    f"{snippet.identifier}: {document} uses fence language "
                    f"{match.group('language')!r}, expected {snippet.language!r}"
                )
            if _normalize_source(match.group("body")) != _normalize_source(source):
                errors.append(
                    f"{snippet.identifier}: checked copy drifted in {document}; "
                    f"canonical source is {snippet.path.as_posix()}"
                )

    expected_copies = {
        (snippet.identifier, document)
        for snippet in snippets
        for document in snippet.copy_in
    }
    for identifier, documents in observed_copy_ids.items():
        if identifier not in by_identifier:
            for document in documents:
                errors.append(
                    f"{document}: unregistered checked-copy marker {identifier!r}"
                )
            continue
        for document in documents:
            if (identifier, document) not in expected_copies:
                errors.append(
                    f"{document}: checked copy {identifier!r} is absent from manifest"
                )

    expected_includes = {
        (snippet.path.as_posix(), document)
        for snippet in snippets
        for document in snippet.include_in
    }
    for path, documents in observed_include_paths.items():
        if path not in by_path:
            for document in documents:
                errors.append(
                    f"{document}: unregistered canonical snippet include {path!r}"
                )
            continue
        for document in documents:
            if (path, document) not in expected_includes:
                errors.append(f"{document}: include {path!r} is absent from manifest")

    return tuple(errors)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical documentation snippets and consumers."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root; defaults to the checkout containing this script.",
    )
    args = parser.parse_args()

    errors = snippet_errors(args.root)
    if errors:
        print("Documentation snippet check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    snippets = _load_manifest(args.root.resolve())
    print(f"Documentation snippets: {len(snippets)} canonical snippet(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
