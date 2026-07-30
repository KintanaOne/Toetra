"""Audit the public source snapshot or every object reachable from Git refs."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Iterator

MAX_TEXT_BYTES = 5 * 1024 * 1024

SENSITIVE_NAMES = frozenset(
    {
        ".env",
        ".npmrc",
        ".pypirc",
        "credentials",
        "credentials.json",
        "id_dsa",
        "id_ed25519",
        "id_rsa",
        "secrets.json",
    }
)
SENSITIVE_SUFFIXES = frozenset(
    {".der", ".jks", ".key", ".keystore", ".p12", ".pem", ".pfx"}
)
FORBIDDEN_PUBLIC_SUFFIXES = frozenset(
    {".joblib", ".patch", ".pickle", ".pkl", ".sqlite", ".sqlite3"}
)
ALLOWED_PUBLIC_EMAILS = frozenset({"KintanaOne@proton.me"})

CONTENT_RULES = (
    (
        "private-key",
        re.compile(rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    (
        "github-token",
        re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})\b"),
    ),
    ("aws-access-key", re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("google-api-key", re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("slack-token", re.compile(rb"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    (
        "openai-token",
        re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "credential-in-url",
        re.compile(rb"https?://[^/\s:@]+:[^/\s@]+@"),
    ),
)
LOCAL_PATH_RULES = (
    re.compile(rb"(?i)\b[A-Z]:\\Users\\[^\\\r\n]+\\"),
    re.compile(rb"(?i)/(?:Users|home)/[^/\s]+/"),
)
EMAIL_PATTERN = re.compile(
    rb"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    rb"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    rb"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+\b"
)

CLEVELAND_PATH = PurePosixPath(
    "demo/classification/cleveland/data/heart-disease-cleveland.csv"
)
CLEVELAND_SHA256 = "bc9bd5b0af3c54a0ca87cae80799fbf24a670de839d97f97b3f55a754bc84615"
THIRD_PARTY_MARKERS = (
    "10.24432/C52P4X",
    "Creative Commons Attribution 4.0 International",
    CLEVELAND_SHA256,
    "a74b7efa387bc9d108d7d0115d831fe9b414b29ae7124f331b622b4efa0427c8",
)


@dataclass(frozen=True, slots=True)
class AuditFinding:
    rule: str
    location: str

    def render(self) -> str:
        return f"{self.rule}: {self.location}"


class PublicExposureAuditError(RuntimeError):
    """Raised when automated public-exposure checks find a blocker."""


def _path_findings(path: PurePosixPath, *, location: str) -> list[AuditFinding]:
    lowered_name = path.name.lower()
    findings: list[AuditFinding] = []
    if lowered_name in SENSITIVE_NAMES or lowered_name.startswith(".env."):
        findings.append(AuditFinding("sensitive-filename", location))
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        findings.append(AuditFinding("sensitive-file-type", location))
    if path.suffix.lower() in FORBIDDEN_PUBLIC_SUFFIXES:
        findings.append(AuditFinding("forbidden-public-artifact", location))
    if any(part in {"build", "dist", "site"} for part in path.parts):
        findings.append(AuditFinding("generated-output", location))
    return findings


def _content_findings(payload: bytes, *, location: str) -> list[AuditFinding]:
    findings = [
        AuditFinding(rule, location)
        for rule, pattern in CONTENT_RULES
        if pattern.search(payload)
    ]
    if any(pattern.search(payload) for pattern in LOCAL_PATH_RULES):
        findings.append(AuditFinding("local-absolute-path", location))
    for match in EMAIL_PATTERN.finditer(payload):
        email = match.group().decode("ascii")
        if email not in ALLOWED_PUBLIC_EMAILS and not email.endswith(
            (".example", ".invalid")
        ):
            findings.append(AuditFinding("unreviewed-email", location))
            break
    return findings


def _git(
    repository: Path,
    *arguments: str,
    input_payload: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repository,
        input=input_payload,
        check=True,
        capture_output=True,
    )


def _tracked_paths(repository: Path) -> tuple[PurePosixPath, ...]:
    completed = _git(repository, "ls-files", "-z")
    return tuple(
        PurePosixPath(raw.decode("utf-8", errors="surrogateescape"))
        for raw in completed.stdout.split(b"\0")
        if raw
    )


def _provenance_findings(repository: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    dataset = repository / CLEVELAND_PATH
    notice = repository / "THIRD_PARTY.md"
    readme = repository / "demo" / "classification" / "cleveland" / "README.md"

    if not dataset.is_file():
        findings.append(AuditFinding("missing-third-party-asset", str(CLEVELAND_PATH)))
    elif (
        hashlib.sha256(dataset.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        != CLEVELAND_SHA256
    ):
        findings.append(
            AuditFinding("third-party-digest-mismatch", str(CLEVELAND_PATH))
        )

    if not notice.is_file():
        findings.append(AuditFinding("missing-third-party-notice", "THIRD_PARTY.md"))
    else:
        notice_text = notice.read_text(encoding="utf-8")
        for marker in THIRD_PARTY_MARKERS:
            if marker not in notice_text:
                findings.append(
                    AuditFinding("incomplete-third-party-notice", "THIRD_PARTY.md")
                )
                break

    if not readme.is_file() or "../../../THIRD_PARTY.md" not in readme.read_text(
        encoding="utf-8"
    ):
        findings.append(
            AuditFinding(
                "unlinked-third-party-notice",
                "demo/classification/cleveland/README.md",
            )
        )
    return findings


def audit_snapshot(repository: Path) -> tuple[AuditFinding, ...]:
    """Audit tracked files in the commit/worktree selected for exposure."""

    repository = repository.resolve()
    findings: list[AuditFinding] = []
    for relative in _tracked_paths(repository):
        location = relative.as_posix()
        findings.extend(_path_findings(relative, location=location))
        path = repository / relative
        if not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
            if path.is_file():
                findings.append(AuditFinding("large-file-review", location))
            continue
        payload = path.read_bytes()
        if b"\0" not in payload:
            findings.extend(_content_findings(payload, location=location))
    findings.extend(_provenance_findings(repository))
    return tuple(sorted(set(findings), key=lambda item: (item.location, item.rule)))


def _reachable_objects(repository: Path) -> dict[str, set[PurePosixPath]]:
    completed = _git(repository, "rev-list", "--objects", "--all")
    objects: dict[str, set[PurePosixPath]] = {}
    for raw_line in completed.stdout.splitlines():
        object_id_raw, separator, path_raw = raw_line.partition(b" ")
        object_id = object_id_raw.decode("ascii")
        objects.setdefault(object_id, set())
        if separator:
            objects[object_id].add(
                PurePosixPath(path_raw.decode("utf-8", errors="surrogateescape"))
            )
    return objects


def _blob_payloads(
    repository: Path,
    object_ids: Iterable[str],
) -> Iterator[tuple[str, bytes]]:
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=repository,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        for object_id in object_ids:
            process.stdin.write(object_id.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").strip()
            parts = header.split()
            if len(parts) != 3 or parts[1] != "blob":
                if len(parts) == 3:
                    size = int(parts[2])
                    process.stdout.read(size)
                    process.stdout.read(1)
                continue
            size = int(parts[2])
            payload = process.stdout.read(size)
            process.stdout.read(1)
            yield object_id, payload
    finally:
        process.stdin.close()
        process.stdout.close()
        stderr = process.stderr.read() if process.stderr is not None else b""
        return_code = process.wait()
        if return_code:
            raise PublicExposureAuditError(
                "git cat-file failed during history audit: "
                + stderr.decode("utf-8", errors="replace").strip()
            )


def _history_location(object_id: str, paths: set[PurePosixPath]) -> str:
    if not paths:
        return object_id[:12]
    rendered = ",".join(sorted(path.as_posix() for path in paths))
    return f"{object_id[:12]} ({rendered})"


def audit_history(repository: Path) -> tuple[AuditFinding, ...]:
    """Audit every blob reachable from local branches, remote refs, and tags."""

    repository = repository.resolve()
    shallow = _git(repository, "rev-parse", "--is-shallow-repository").stdout.strip()
    if shallow != b"false":
        return (AuditFinding("shallow-history", ".git"),)

    objects = _reachable_objects(repository)
    findings: list[AuditFinding] = []
    for object_id, paths in objects.items():
        for path in paths:
            findings.extend(
                _path_findings(
                    path,
                    location=_history_location(object_id, {path}),
                )
            )

    for object_id, payload in _blob_payloads(repository, objects):
        paths = objects[object_id]
        location = _history_location(object_id, paths)
        if len(payload) > MAX_TEXT_BYTES:
            findings.append(AuditFinding("large-history-blob-review", location))
            continue
        if b"\0" in payload:
            findings.append(AuditFinding("binary-history-blob-review", location))
            continue
        findings.extend(_content_findings(payload, location=location))

    return tuple(sorted(set(findings), key=lambda item: (item.location, item.rule)))


def history_review_summary(repository: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return reachable refs and author identities for explicit human review."""

    raw_refs = _git(
        repository,
        "for-each-ref",
        "--format=%(refname)",
        "refs/heads",
        "refs/remotes",
        "refs/tags",
    ).stdout
    refs = tuple(sorted(line.decode("utf-8") for line in raw_refs.splitlines()))
    raw_authors = _git(
        repository,
        "log",
        "--all",
        "--format=%aN <%aE>%n%cN <%cE>",
    ).stdout
    authors = tuple(
        sorted(
            {
                line.decode("utf-8", errors="replace")
                for line in raw_authors.splitlines()
                if line
            }
        )
    )
    return refs, authors


def _repository_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def _render_findings(findings: tuple[AuditFinding, ...], *, scope: str) -> None:
    if not findings:
        print(f"Public {scope} audit: no automated blocker found.")
        return
    details = "\n".join(f"- {finding.render()}" for finding in findings)
    raise PublicExposureAuditError(
        f"Public {scope} audit found {len(findings)} blocker(s):\n{details}\n"
        "Findings contain rule and location only; inspect values without copying "
        "secrets into reports."
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--snapshot", action="store_true")
    scope.add_argument("--history", action="store_true")
    parser.add_argument(
        "repository",
        nargs="?",
        type=Path,
        default=_repository_from_script(),
    )
    arguments = parser.parse_args(argv)

    if arguments.snapshot:
        _render_findings(audit_snapshot(arguments.repository), scope="snapshot")
        return 0

    refs, authors = history_review_summary(arguments.repository)
    print("Reachable refs requiring owner review:")
    for ref in refs:
        print(f"- {ref}")
    print("Author/committer identities requiring owner review:")
    for author in authors:
        print(f"- {author}")
    _render_findings(audit_history(arguments.repository), scope="history")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
