"""Install the built wheel outside the checkout and probe the public API."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

PROBE = r"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import forml
from forml import VerificationSession, verify

module_path = Path(forml.__file__).resolve()
assert "site-packages" in module_path.parts, module_path
assert callable(verify)
assert VerificationSession is not None

spec = importlib.util.find_spec("dsl.language.grammar")
assert spec is not None and spec.submodule_search_locations
root = Path(next(iter(spec.submodule_search_locations)))
assert (root / "forml_grammar.ebnf").is_file()
assert (root / "forml_grammar.lark").is_file()
print(f"Installed FORML probe passed from {module_path}")
"""


def _venv_python(directory: Path) -> Path:
    if os.name == "nt":
        return directory / "Scripts" / "python.exe"
    return directory / "bin" / "python"


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    if str(repository_root) not in sys.path:
        sys.path.insert(0, str(repository_root))
    from scripts.release.distribution import check_distribution_directory

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    arguments = parser.parse_args()
    artifacts = check_distribution_directory(arguments.directory.resolve())

    with tempfile.TemporaryDirectory(prefix="forml-install-check-") as raw_directory:
        root = Path(raw_directory)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = _venv_python(environment)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                str(artifacts.wheel),
            ],
            check=True,
            cwd=root,
        )
        subprocess.run([str(python), "-m", "pip", "check"], check=True, cwd=root)
        clean_environment = os.environ.copy()
        clean_environment.pop("PYTHONPATH", None)
        clean_environment["PYTHONSAFEPATH"] = "1"
        subprocess.run(
            [str(python), "-I", "-c", PROBE],
            check=True,
            cwd=root,
            env=clean_environment,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
