"""Top-level process contract for the Toetra command-line interface."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import NoReturn, Sequence, cast

from toetra._cli.diagnostics import CliDiagnostic, render_diagnostic

EXIT_OK = 0
EXIT_USAGE = 3

_COMMANDS: tuple[tuple[str, str], ...] = (
    ("validate", "Validate a verification request without solving."),
    ("inspect", "Describe the resolved executable verification plan."),
    ("verify", "Run formal verification and emit reports."),
    ("replay", "Replay archived witness and counterexample evidence."),
    ("init", "Create a model-aware smoke specification."),
)


def _distribution_version() -> str:
    try:
        return version("toetra")
    except PackageNotFoundError:
        return "unknown"


def _requested_diagnostic_format(argv: Sequence[str]) -> str:
    for index, argument in enumerate(argv):
        if argument == "--diagnostic-format" and index + 1 < len(argv):
            candidate = argv[index + 1]
            if candidate in {"text", "json"}:
                return candidate
        if argument.startswith("--diagnostic-format="):
            candidate = argument.partition("=")[2]
            if candidate in {"text", "json"}:
                return candidate
    return "text"


class ToetraArgumentParser(argparse.ArgumentParser):
    """Argument parser that preserves Toetra's reserved exit-code contract."""

    _diagnostic_format: str = "text"

    def use_diagnostic_format(self, output_format: str) -> None:
        """Configure diagnostics without widening ``ArgumentParser.__init__``."""

        self._diagnostic_format = output_format

    def error(self, message: str) -> NoReturn:
        render_diagnostic(
            CliDiagnostic(
                category="usage",
                code="INVALID_ARGUMENTS",
                message=message,
                hint=f"Run '{self.prog} --help' for usage.",
            ),
            output_format=self._diagnostic_format,
        )
        raise SystemExit(EXIT_USAGE)


def _build_parser(*, diagnostic_format: str) -> ToetraArgumentParser:
    parser = ToetraArgumentParser(
        prog="toetra",
        description=(
            "Declarative behavioral specification and formal verification "
            "for machine-learning models."
        ),
    )
    parser.use_diagnostic_format(diagnostic_format)
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_distribution_version()}",
    )
    parser.add_argument(
        "--diagnostic-format",
        choices=("text", "json"),
        default="text",
        help="Select stderr diagnostic rendering (default: text).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Include internal traceback information for unexpected failures.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    for name, help_text in _COMMANDS:
        command = cast(
            ToetraArgumentParser,
            subparsers.add_parser(name, help=help_text, description=help_text),
        )
        command.use_diagnostic_format(diagnostic_format)
        command.set_defaults(_command_name=name)

    return parser


def _pending_command(command: str, *, diagnostic_format: str) -> int:
    render_diagnostic(
        CliDiagnostic(
            category="usage",
            code="COMMAND_NOT_IMPLEMENTED",
            message=f"Command '{command}' is not implemented in this build.",
            hint="This P28.1 increment provides the CLI foundation only.",
        ),
        output_format=diagnostic_format,
    )
    return EXIT_USAGE


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the Toetra CLI and return its process status."""

    arguments = tuple(sys.argv[1:] if argv is None else argv)
    diagnostic_format = _requested_diagnostic_format(arguments)
    parser = _build_parser(diagnostic_format=diagnostic_format)

    if not arguments:
        parser.print_help()
        return EXIT_OK

    namespace = parser.parse_args(arguments)
    command = getattr(namespace, "_command_name", None)
    if command is None:
        parser.print_help()
        return EXIT_OK

    return _pending_command(
        command,
        diagnostic_format=namespace.diagnostic_format,
    )


if __name__ == "__main__":  # pragma: no cover - module execution guard
    raise SystemExit(main())
