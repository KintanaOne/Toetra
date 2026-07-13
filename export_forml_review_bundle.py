#!/usr/bin/env python3
"""
Exporte un snapshot textuel, ciblé et auditable du dépôt FORML.

Objectif
--------
Créer une archive ZIP contenant uniquement les sources utiles pour :
- réévaluer la roadmap technique ;
- préparer des patches intégrables ;
- vérifier les contrats EBNF -> Lark -> CST -> AST -> Semantic -> IR -> Backend ;
- comprendre les tests et la configuration de CI.

Le script :
- conserve les chemins relatifs du dépôt ;
- exclut caches, environnements, modèles, jeux de données et anciens agrégats ;
- refuse de suivre les liens symboliques ;
- ajoute un manifeste JSON avec taille et SHA-256 ;
- ajoute un rapport lisible et l'état Git ;
- n'utilise aucune dépendance externe.

Usage recommandé
----------------
Depuis la racine du dépôt :

    python scripts/export_forml_review_bundle.py --strict

Sortie personnalisée :

    python scripts/export_forml_review_bundle.py \
        --output context/forml_review_bundle.zip \
        --strict

Inclure le diff Git non commité, si son partage est souhaité :

    python scripts/export_forml_review_bundle.py \
        --include-git-diff \
        --strict
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


# -----------------------------------------------------------------------------
# Périmètre d'inclusion
# -----------------------------------------------------------------------------
#
# Le choix est volontairement assez large sur les sources textuelles :
# il est préférable d'avoir tout le code actuel d'une couche plutôt qu'un
# agrégat partiel pouvant mélanger plusieurs états historiques.
#
# Le dossier "context/" est volontairement exclu : il contient des snapshots
# concaténés qui peuvent devenir obsolètes et créer de l'ambiguïté.
SOURCE_ROOTS: tuple[str, ...] = (
    "dsl",
    "model",
    "test",
    "docs",
    "demo",
    "scripts",
    ".github",  # Inclus s'il existe : workflows CI, templates, etc.
)

ROOT_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "context_helper.py",
    "mkdocs.yml",
    "pipeline.txt",
    "pyproject.toml",
    "requirements-dev.txt",
)

# Extensions textuelles pertinentes pour les sources, docs, grammaires,
# configurations, cas golden et spécifications FORML.
ALLOWED_SUFFIXES: frozenset[str] = frozenset(
    {
        ".cfg",
        ".ebnf",
        ".forml",
        ".ini",
        ".json",
        ".lark",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)

# Noms de dossiers toujours exclus, quelle que soit leur profondeur.
EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "forml.egg-info",
        "htmlcov",
        "node_modules",
        "site",
        "venv",
    }
)

# Dossiers racine explicitement exclus parce qu'ils contiennent des snapshots
# historiques/concaténés, des données ou des artefacts binaires inutiles ici.
EXCLUDED_ROOTS: frozenset[str] = frozenset(
    {
        "context",
        "examples",  # CSV et modèles d'exemple non requis pour la roadmap.
    }
)

# Extensions binaires ou volumineuses explicitement refusées.
DENIED_SUFFIXES: frozenset[str] = frozenset(
    {
        ".7z",
        ".bin",
        ".csv",
        ".dll",
        ".exe",
        ".joblib",
        ".model",
        ".onnx",
        ".parquet",
        ".pkl",
        ".pickle",
        ".pyc",
        ".so",
        ".tar",
        ".gz",
        ".zip",
    }
)

# Fichiers sensibles à ne jamais exporter automatiquement.
SENSITIVE_FILE_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
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

SENSITIVE_SUFFIXES: frozenset[str] = frozenset(
    {
        ".key",
        ".pem",
        ".p12",
        ".pfx",
    }
)

# Fichiers critiques pour les premiers patches. Leur absence est signalée dans
# le rapport ; avec --strict, elle provoque un échec.
CRITICAL_PATHS: tuple[str, ...] = (
    "pyproject.toml",
    "Makefile",
    "dsl/language/grammar/forml_grammar.ebnf",
    "dsl/language/grammar/forml_grammar.lark",
    "dsl/language/tools/generator.py",
    "dsl/language/tools/registry.py",
    "dsl/language/tools/transforms.py",
    "dsl/language/vocabulary/protected_words.py",
    "dsl/parser/parser.py",
    "dsl/ast/nodes/primitives.py",
    "dsl/ast/nodes/header.py",
    "dsl/builder/scalar.py",
    "dsl/builder/program.py",
    "dsl/semantic/core/binding.py",
    "dsl/semantic/core/validator.py",
    "dsl/ir/ir1/nodes.py",
    "dsl/ir/ir1/query_translator.py",
    "dsl/backends/z3_backend/translator.py",
    "model/schema/model_schema.py",
    "test/unit/parser/test_grammar_generation.py",
    "test/unit/parser/test_arithmetic_expressions.py",
    "test/unit/parser/test_typed_domains.py",
    "test/unit/parser/test_quantified_scopes.py",
    "test/unit/builder/test_scalar_comparisons.py",
    "docs/adr/ADR-0013-explicit-quantified-bindings.md",
    "docs/adr/ADR-0014-scalar-expression-comparisons.md",
    "docs/adr/ADR-0015-typed-domains-as-assumptions.md",
    "docs/adr/ADR-0016-specification-constants-and-name-resolution.md",
    "docs/testing/language-evolution-test-matrix.md",
)


@dataclass(frozen=True)
class FileRecord:
    """Métadonnées d'un fichier exporté."""

    path: str
    size_bytes: int
    sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Créer un bundle textuel auditable du dépôt FORML."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Racine du dépôt. Par défaut : dossier courant.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Chemin du ZIP de sortie. Par défaut : "
            "forml_review_bundle_<timestamp>.zip à la racine du dépôt."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Échouer si un fichier critique est absent.",
    )
    parser.add_argument(
        "--include-git-diff",
        action="store_true",
        help=(
            "Inclure le diff Git non commité dans _meta/git_diff.patch. "
            "À activer seulement si ce contenu peut être partagé."
        ),
    )
    parser.add_argument(
        "--include-pip-freeze",
        action="store_true",
        help=(
            "Inclure la sortie de 'python -m pip freeze'. "
            "Utile pour diagnostiquer l'environnement, mais souvent volumineux."
        ),
    )
    return parser.parse_args()


def is_within(path: Path, root: Path) -> bool:
    """Vérifie qu'un chemin résolu reste dans la racine du dépôt."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def is_sensitive(path: Path) -> bool:
    """Détecte les noms et extensions potentiellement sensibles."""
    name_lower = path.name.lower()
    return (
        name_lower in SENSITIVE_FILE_NAMES
        or path.suffix.lower() in SENSITIVE_SUFFIXES
    )


def should_include(path: Path, repo_root: Path) -> bool:
    """Décide si un fichier doit entrer dans le bundle."""
    if not path.is_file():
        return False

    # Ne jamais suivre un lien symbolique : sa cible pourrait être hors dépôt.
    if path.is_symlink():
        return False

    if not is_within(path, repo_root):
        return False

    relative = path.relative_to(repo_root)
    parts = relative.parts

    if not parts:
        return False

    if parts[0] in EXCLUDED_ROOTS:
        return False

    if any(part in EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return False

    if is_sensitive(relative):
        return False

    suffix = path.suffix.lower()

    if suffix in DENIED_SUFFIXES:
        return False

    # Les fichiers racine explicitement listés sont acceptés même sans suffixe.
    if relative.as_posix() in ROOT_FILES:
        return True

    return suffix in ALLOWED_SUFFIXES


def iter_candidate_files(repo_root: Path) -> Iterable[Path]:
    """Énumère les fichiers candidats dans un ordre déterministe."""
    candidates: list[Path] = []

    for relative_name in ROOT_FILES:
        candidate = repo_root / relative_name
        if should_include(candidate, repo_root):
            candidates.append(candidate)

    for root_name in SOURCE_ROOTS:
        source_root = repo_root / root_name
        if not source_root.exists():
            continue

        for current_root, dir_names, file_names in os.walk(source_root):
            # Élagage en place : os.walk ne descendra pas dans ces dossiers.
            dir_names[:] = sorted(
                name
                for name in dir_names
                if name not in EXCLUDED_DIR_NAMES
            )

            current_path = Path(current_root)

            for file_name in sorted(file_names):
                candidate = current_path / file_name
                if should_include(candidate, repo_root):
                    candidates.append(candidate)

    # Déduplication et tri par chemin relatif.
    unique = {
        path.relative_to(repo_root).as_posix(): path
        for path in candidates
    }
    for relative_name in sorted(unique):
        yield unique[relative_name]


def sha256_file(path: Path) -> str:
    """Calcule l'empreinte SHA-256 d'un fichier sans le charger entièrement."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(
    args: list[str],
    cwd: Path,
    *,
    timeout_seconds: int = 20,
) -> str:
    """Exécute une commande de diagnostic sans faire échouer l'export."""
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"[commande indisponible] {exc}\n"

    output = completed.stdout
    if completed.stderr:
        output += "\n[stderr]\n" + completed.stderr

    return output.strip() + "\n"


def collect_git_metadata(repo_root: Path, include_diff: bool) -> dict[str, str]:
    """Collecte des informations Git utiles pour identifier le snapshot."""
    metadata = {
        "root": run_command(
            ["git", "rev-parse", "--show-toplevel"],
            repo_root,
        ),
        "branch": run_command(
            ["git", "branch", "--show-current"],
            repo_root,
        ),
        "commit": run_command(
            ["git", "rev-parse", "HEAD"],
            repo_root,
        ),
        "status": run_command(
            ["git", "status", "--short", "--branch"],
            repo_root,
        ),
        "diff_stat": run_command(
            ["git", "diff", "--stat"],
            repo_root,
        ),
    }

    if include_diff:
        metadata["diff"] = run_command(
            ["git", "diff", "--binary", "--no-ext-diff"],
            repo_root,
            timeout_seconds=60,
        )

    return metadata


def build_report(
    records: list[FileRecord],
    missing_critical: list[str],
    git_metadata: dict[str, str],
) -> str:
    """Produit un rapport Markdown lisible sans ouvrir le manifeste JSON."""
    total_size = sum(record.size_bytes for record in records)

    lines = [
        "# FORML review bundle",
        "",
        "## Résumé",
        "",
        f"- Fichiers exportés : **{len(records)}**",
        f"- Taille textuelle totale : **{total_size:,} octets**",
        "- Chemins conservés relativement à la racine du dépôt.",
        "- Liens symboliques, caches, binaires, modèles et données exclus.",
        "- Le dossier `context/` est exclu pour éviter les snapshots historiques.",
        "",
        "## État Git",
        "",
        "```text",
        git_metadata.get("status", "[indisponible]").rstrip(),
        "```",
        "",
        "## Fichiers critiques absents",
        "",
    ]

    if missing_critical:
        lines.extend(f"- `{path}`" for path in missing_critical)
    else:
        lines.append("- Aucun.")

    lines.extend(
        [
            "",
            "## Contenu",
            "",
            "```text",
            *(record.path for record in records),
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def write_text_to_zip(
    archive: zipfile.ZipFile,
    archive_path: str,
    content: str,
) -> None:
    """Ajoute proprement un contenu texte UTF-8 dans le ZIP."""
    archive.writestr(archive_path, content.encode("utf-8"))


def main() -> int:
    args = parse_args()

    repo_root = args.repo_root.expanduser().resolve()

    if not repo_root.is_dir():
        print(f"Erreur : racine de dépôt introuvable : {repo_root}", file=sys.stderr)
        return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = (
        args.output.expanduser()
        if args.output is not None
        else repo_root / f"forml_review_bundle_{timestamp}.zip"
    )
    if not output.is_absolute():
        output = repo_root / output
    output = output.resolve()

    if not is_within(output, repo_root) and args.output is None:
        print("Erreur interne : sortie par défaut hors dépôt.", file=sys.stderr)
        return 2

    files = list(iter_candidate_files(repo_root))
    missing_critical = [
        relative_path
        for relative_path in CRITICAL_PATHS
        if not (repo_root / relative_path).is_file()
    ]

    if args.strict and missing_critical:
        print(
            "Erreur : fichiers critiques absents :\n  - "
            + "\n  - ".join(missing_critical),
            file=sys.stderr,
        )
        return 3

    records = [
        FileRecord(
            path=path.relative_to(repo_root).as_posix(),
            size_bytes=path.stat().st_size,
            sha256=sha256_file(path),
        )
        for path in files
    ]

    git_metadata = collect_git_metadata(
        repo_root,
        include_diff=args.include_git_diff,
    )

    environment = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
    }

    manifest = {
        "schema_version": 1,
        "bundle_kind": "forml_review_source_snapshot",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root_name": repo_root.name,
        "file_count": len(records),
        "total_size_bytes": sum(record.size_bytes for record in records),
        "missing_critical_paths": missing_critical,
        "files": [
            {
                "path": record.path,
                "size_bytes": record.size_bytes,
                "sha256": record.sha256,
            }
            for record in records
        ],
    }

    report = build_report(records, missing_critical, git_metadata)

    output.parent.mkdir(parents=True, exist_ok=True)

    # Écriture dans un fichier temporaire puis remplacement atomique, afin de ne
    # pas laisser un ZIP partiel si le processus est interrompu.
    with tempfile.NamedTemporaryFile(
        prefix=f".{output.stem}_",
        suffix=".tmp",
        dir=output.parent,
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for path in files:
                relative_path = path.relative_to(repo_root).as_posix()
                archive.write(path, arcname=relative_path)

            write_text_to_zip(
                archive,
                "_meta/manifest.json",
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            )
            write_text_to_zip(
                archive,
                "_meta/report.md",
                report,
            )
            write_text_to_zip(
                archive,
                "_meta/environment.json",
                json.dumps(environment, indent=2, ensure_ascii=False) + "\n",
            )
            write_text_to_zip(
                archive,
                "_meta/git_branch.txt",
                git_metadata.get("branch", ""),
            )
            write_text_to_zip(
                archive,
                "_meta/git_commit.txt",
                git_metadata.get("commit", ""),
            )
            write_text_to_zip(
                archive,
                "_meta/git_status.txt",
                git_metadata.get("status", ""),
            )
            write_text_to_zip(
                archive,
                "_meta/git_diff_stat.txt",
                git_metadata.get("diff_stat", ""),
            )

            if args.include_git_diff:
                write_text_to_zip(
                    archive,
                    "_meta/git_diff.patch",
                    git_metadata.get("diff", ""),
                )

            if args.include_pip_freeze:
                write_text_to_zip(
                    archive,
                    "_meta/pip_freeze.txt",
                    run_command(
                        [sys.executable, "-m", "pip", "freeze"],
                        repo_root,
                        timeout_seconds=60,
                    ),
                )

        temporary_path.replace(output)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    print(f"Bundle créé : {output}")
    print(f"Fichiers : {len(records)}")
    print(
        "Taille source : "
        f"{sum(record.size_bytes for record in records):,} octets"
    )

    if missing_critical:
        print("Attention : fichiers critiques absents :")
        for path in missing_critical:
            print(f"  - {path}")

    print("Commande de contrôle :")
    print(f'  python -m zipfile -l "{output}"')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
