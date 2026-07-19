from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dsl.compatibility.defaults import (  # noqa: E402
    create_default_numeric_compatibility_registry,
)
from dsl.compatibility.matrix import (  # noqa: E402
    render_compatibility_matrices_markdown,
)

DEFAULT_OUTPUT = Path("docs/generated/numeric-compatibility-matrices.md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate public numeric compatibility matrices from the registry."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output Markdown path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when the checked-in matrix differs from generated content",
    )
    args = parser.parse_args()

    content = render_compatibility_matrices_markdown(
        create_default_numeric_compatibility_registry()
    )
    output = args.output

    if args.check:
        if not output.is_file():
            raise SystemExit(f"Generated matrix is missing: {output}")
        current = output.read_text(encoding="utf-8")
        if current != content:
            raise SystemExit(
                "Numeric compatibility matrices are stale. Run "
                "python scripts/generate_numeric_compatibility_matrices.py"
            )
        print(f"Numeric compatibility matrices are current: {output}")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Generated numeric compatibility matrices: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
