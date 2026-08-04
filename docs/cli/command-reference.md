# CLI command reference

> P28.3 implements `validate`, `inspect`, and `verify`. The remaining command
> sections define accepted contracts for handlers delivered in later P28
> increments.

## Shared inputs

```text
SPECIFICATION
--model PATH
--dataset PATH
--anchor-source PATH
--target NAME
```

CLI model paths are relative to the working directory. A model declared inside
the specification is relative to the specification file.

The executable commands share:

```text
--timeout-ms POSITIVE_INTEGER | --no-timeout
--max-backend-units POSITIVE_INTEGER
--max-memory-mb POSITIVE_INTEGER
--seed NON_NEGATIVE_INTEGER
```

`validate` accepts these options only with `--level executable`; `inspect` and
`verify` always accept them.

## Validate

```text
toetra validate SPECIFICATION
    [--model PATH]
    [--dataset PATH]
    [--anchor-source PATH]
    [--target NAME]
    [--timeout-ms POSITIVE_INTEGER | --no-timeout]
    [--max-backend-units POSITIVE_INTEGER]
    [--max-memory-mb POSITIVE_INTEGER]
    [--seed NON_NEGATIVE_INTEGER]
    [--level {syntax,semantic,executable}]
    [--format {text,json}]
    [--output PATH|-]
```

Default level: `executable`.

- `syntax` stops after AST construction;
- `semantic` stops after model-aware IR1 construction;
- `executable` proves routing and backend translation readiness without solving.

## Inspect

```text
toetra inspect SPECIFICATION
    [--model PATH]
    [--dataset PATH]
    [--anchor-source PATH]
    [--target NAME]
    [--timeout-ms POSITIVE_INTEGER | --no-timeout]
    [--max-backend-units POSITIVE_INTEGER]
    [--max-memory-mb POSITIVE_INTEGER]
    [--seed NON_NEGATIVE_INTEGER]
    [--format {text,json}]
    [--output PATH|-]
```

Inspection always requires a complete executable plan and deliberately excludes
private compiler IR and backend-native formulas.

## Verify

```text
toetra verify SPECIFICATION
    [--model PATH]
    [--dataset PATH]
    [--anchor-source PATH]
    [--target NAME]
    [--timeout-ms POSITIVE_INTEGER | --no-timeout]
    [--max-backend-units POSITIVE_INTEGER]
    [--max-memory-mb POSITIVE_INTEGER]
    [--seed NON_NEGATIVE_INTEGER]
    [--format {text,json,html}]
    [--output PATH|-]
    [--artifacts-dir DIRECTORY]
    [--artifact-stem NAME]
```

JSON primary output remains the existing verification-report collection schema
v6. `--artifacts-dir` commits each JSON and HTML file atomically, then commits
the run manifest last.
`--artifact-stem` is a portable ASCII filename stem, not a path; leading dots or
hyphens, trailing dots, separators, and Windows reserved device names are
rejected.

## Replay

```text
toetra replay REPORT_JSON
    --specification SPECIFICATION
    --model PATH
    [--dataset PATH]
    [--anchor-source PATH]
    [--target NAME]
    [--property INDEX ...]
    [--tolerance NON_NEGATIVE_FLOAT]
    [--format {text,json,html}]
    [--output PATH|-]
```

Replay accepts only a JSON v6 report collection. It validates provenance,
reconstructs matching tasks without solving, and replays all witness and
counterexample evidence by default.

## Init

```text
toetra init SPECIFICATION
    --model PATH
    [--dataset PATH]
    [--target NAME]
    [--force]
```

`init` writes a model-aware smoke specification, validates it at executable
depth, and refuses to overwrite an existing destination without `--force`.

## Global diagnostics

```text
--diagnostic-format {text,json}
--debug
```

Successful primary output belongs to stdout or `--output`. Diagnostics belong
to stderr. `--debug` tracebacks are explicitly not machine-stable.
