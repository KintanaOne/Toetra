"""Top-level process contract for the Toetra command-line interface."""

from __future__ import annotations

import argparse
import math
import signal
import sys
import traceback
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from types import FrameType
from typing import NoReturn, Sequence, cast

from toetra._cli.diagnostics import CliDiagnostic, render_diagnostic

EXIT_OK = 0
EXIT_LOGICAL_FAILURE = 1
EXIT_INCONCLUSIVE = 2
EXIT_USAGE = 3
EXIT_RUNTIME = 4
EXIT_INTERNAL = 5
EXIT_INTERRUPTED = 130
EXIT_TERMINATED = 143

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
        self._diagnostic_format = output_format

    def error(self, message: str) -> NoReturn:
        render_diagnostic(
            CliDiagnostic(
                category="usage",
                code="INVALID_ARGUMENTS",
                stage="usage",
                message=message,
                hint=f"Run '{self.prog} --help' for usage.",
            ),
            output_format=self._diagnostic_format,
        )
        raise SystemExit(EXIT_USAGE)


class _TerminationRequested(Exception):
    """Internal control flow raised by the temporary SIGTERM handler."""


def _raise_termination(_signum: int, _frame: FrameType | None) -> NoReturn:
    raise _TerminationRequested


@contextmanager
def _sigterm_boundary() -> Iterator[None]:
    sigterm = getattr(signal, "SIGTERM", None)
    if sigterm is None:
        yield
        return

    try:
        previous = signal.getsignal(sigterm)
        signal.signal(sigterm, _raise_termination)
    except (OSError, ValueError):
        yield
        return

    try:
        yield
    finally:
        try:
            signal.signal(sigterm, previous)
        except (OSError, ValueError):
            pass


def _positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a strictly positive integer")
    return parsed


def _non_negative_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def _non_negative_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("must be a finite non-negative number")
    return parsed


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
    parsers: dict[str, ToetraArgumentParser] = {}
    for name, help_text in _COMMANDS:
        command = cast(
            ToetraArgumentParser,
            subparsers.add_parser(name, help=help_text, description=help_text),
        )
        command.use_diagnostic_format(diagnostic_format)
        command.set_defaults(_command_name=name)
        parsers[name] = command

    _configure_validate_parser(parsers["validate"])
    _configure_inspect_parser(parsers["inspect"])
    _configure_verify_parser(parsers["verify"])
    _configure_replay_parser(parsers["replay"])
    return parser


def _configure_validate_parser(parser: ToetraArgumentParser) -> None:
    _add_shared_inputs(parser)
    _add_execution_policy(parser)
    parser.add_argument(
        "--level",
        choices=("syntax", "semantic", "executable"),
        default="executable",
        help="Validation depth (default: executable).",
    )
    _add_primary_output(parser)


def _configure_inspect_parser(parser: ToetraArgumentParser) -> None:
    _add_shared_inputs(parser)
    _add_execution_policy(parser)
    _add_primary_output(parser)


def _configure_verify_parser(parser: ToetraArgumentParser) -> None:
    _add_shared_inputs(parser)
    _add_execution_policy(parser)
    _add_primary_output(parser, formats=("text", "json", "html"))
    parser.add_argument(
        "--artifacts-dir",
        metavar="DIRECTORY",
        help="Write JSON, HTML, and a completion manifest into this directory.",
    )
    parser.add_argument(
        "--artifact-stem",
        metavar="NAME",
        help="Portable filename stem for --artifacts-dir outputs.",
    )


def _configure_replay_parser(parser: ToetraArgumentParser) -> None:
    parser.add_argument("report", metavar="REPORT_JSON")
    parser.add_argument(
        "--specification",
        required=True,
        metavar="SPECIFICATION",
    )
    parser.add_argument("--model", metavar="PATH")
    parser.add_argument("--dataset", metavar="PATH")
    parser.add_argument("--anchor-source", metavar="PATH")
    parser.add_argument("--target", metavar="NAME")
    parser.add_argument(
        "--property",
        dest="properties",
        action="append",
        type=_non_negative_integer,
        default=[],
        metavar="INDEX",
        help="Replay one zero-based property index; may be repeated.",
    )
    parser.add_argument(
        "--tolerance",
        type=_non_negative_float,
        default=1e-9,
        metavar="FLOAT",
        help="Finite non-negative replay tolerance (default: 1e-9).",
    )
    _add_primary_output(parser, formats=("text", "json", "html"))


def _add_shared_inputs(parser: ToetraArgumentParser) -> None:
    parser.add_argument("specification", metavar="SPECIFICATION")
    parser.add_argument("--model", metavar="PATH")
    parser.add_argument("--dataset", metavar="PATH")
    parser.add_argument("--anchor-source", metavar="PATH")
    parser.add_argument("--target", metavar="NAME")


def _add_execution_policy(parser: ToetraArgumentParser) -> None:
    timeout = parser.add_mutually_exclusive_group()
    timeout.add_argument("--timeout-ms", type=_positive_integer, default=None)
    timeout.add_argument("--no-timeout", action="store_true")
    parser.add_argument("--max-backend-units", type=_positive_integer)
    parser.add_argument("--max-memory-mb", type=_positive_integer)
    parser.add_argument("--seed", type=_non_negative_integer)


def _add_primary_output(
    parser: ToetraArgumentParser,
    *,
    formats: tuple[str, ...] = ("text", "json"),
) -> None:
    parser.add_argument(
        "--format",
        choices=formats,
        default="text",
        help="Primary output representation (default: text).",
    )
    parser.add_argument(
        "--output",
        metavar="PATH|-",
        default="-",
        help="Primary output destination (default: stdout).",
    )


def _pending_command(command: str, *, diagnostic_format: str) -> int:
    render_diagnostic(
        CliDiagnostic(
            category="usage",
            code="COMMAND_NOT_IMPLEMENTED",
            stage="usage",
            command=command,
            message=f"Command '{command}' is not implemented in this build.",
            hint="This command is planned for a later P28 increment.",
        ),
        output_format=diagnostic_format,
    )
    return EXIT_USAGE


def _dispatch(namespace: argparse.Namespace) -> int:
    command = cast(str, namespace._command_name)
    if command == "validate":
        from toetra._cli.commands import run_validate

        return run_validate(namespace)
    if command == "inspect":
        from toetra._cli.commands import run_inspect

        return run_inspect(namespace)
    if command == "verify":
        from toetra._cli.commands import run_verify

        return run_verify(namespace)
    if command == "replay":
        from toetra._cli.commands import run_replay

        return run_replay(namespace)
    return _pending_command(command, diagnostic_format=namespace.diagnostic_format)


def _render_failure(
    error: Exception,
    *,
    command: str | None,
    diagnostic_format: str,
    debug: bool,
) -> int:
    from toetra._runtime.errors import (
        VerificationConfigurationError,
        VerificationRuntimeError,
    )

    if isinstance(error, VerificationConfigurationError):
        status = EXIT_USAGE
        category = "configuration"
        code = error.code
        stage = error.stage
        hint = error.hint
        path = error.path
        line = error.line
        column = error.column
    elif isinstance(error, VerificationRuntimeError):
        status = EXIT_RUNTIME
        category = "runtime"
        code = error.code
        stage = error.stage
        hint = error.hint
        path = error.path
        line = error.line
        column = error.column
    else:
        status = EXIT_INTERNAL
        category = "internal"
        code = "INTERNAL_ERROR"
        stage = "internal"
        hint = "Re-run with --debug and report the traceback if the failure persists."
        path = None
        line = None
        column = None

    render_diagnostic(
        CliDiagnostic(
            category=category,
            code=code,
            stage=stage,
            message=str(error),
            hint=hint,
            path=path,
            line=line,
            column=column,
            command=command,
            debug_traceback=(
                traceback.format_exc() if debug and status == EXIT_INTERNAL else None
            ),
        ),
        output_format=diagnostic_format,
    )
    return status


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

    try:
        with _sigterm_boundary():
            return _dispatch(namespace)
    except _TerminationRequested:
        render_diagnostic(
            CliDiagnostic(
                category="signal",
                code="TERMINATED",
                stage="process",
                command=command,
                message="Command terminated by SIGTERM.",
            ),
            output_format=namespace.diagnostic_format,
        )
        return EXIT_TERMINATED
    except KeyboardInterrupt:
        render_diagnostic(
            CliDiagnostic(
                category="signal",
                code="INTERRUPTED",
                stage="process",
                command=command,
                message="Command interrupted by the user.",
            ),
            output_format=namespace.diagnostic_format,
        )
        return EXIT_INTERRUPTED
    except Exception as error:
        return _render_failure(
            error,
            command=command,
            diagnostic_format=namespace.diagnostic_format,
            debug=namespace.debug,
        )


if __name__ == "__main__":  # pragma: no cover - module execution guard
    raise SystemExit(main())
