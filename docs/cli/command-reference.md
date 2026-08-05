# CLI command reference

> P28.4 implements `validate`, `inspect`, `verify`, and `replay`. The `init`
> section defines the accepted contract for the final P28 handler.

## Shared inputs

```text
SPECIFICATION
--model PATH
--dataset PATH
--anchor-source PATH
--target NAME
```

The header supplies default model, target, and dataset values. Explicit CLI
values are temporary execution overrides for one invocation:

```text
CLI option > .toetra declaration
```

CLI model and dataset paths are relative to the working directory. Header paths
are relative to the specification file. `--target` rebinds the DSL `target`
output for the effective run. Validation, inspection, reports, manifests, and
replay retain both declared and effective values.

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
    [--model PATH]
    [--dataset PATH]
    [--anchor-source PATH]
    [--target NAME]
    [--property INDEX ...]
    [--tolerance NON_NEGATIVE_FLOAT]
    [--format {text,json,html}]
    [--output PATH|-]
```

Replay accepts only a JSON v6 report collection. Model and dataset values
default to the specification header. The archived effective target is reused
when `--target` is omitted. Explicit values may only reconstruct the same
archived effective context. It validates complete input
provenance and each selected property fingerprint, reconstructs matching tasks
without translation or solver execution, and replays all witness and
counterexample evidence by default. Repeated `--property` values preserve first
occurrence order and ignore exact duplicates. A non-replayable selected status
is returned as an inconclusive replay result rather than an empty success.

JSON output uses `toetra.replay-report-collection` schema version 1. Exit status
`0` means all selected evidence is consistent, `1` means at least one concrete
contradiction, and `2` means no contradiction but unavailable or indeterminate
evidence.

## Init

```text
toetra init SPECIFICATION
    --model PATH
    --target NAME
    [--dataset PATH]
    [--force]
```

`init` requires explicit model and target declarations. When `--dataset` is
provided, the generated header also contains `dataset := ...`; model and dataset
references are made relative to the destination when portable. The generated
smoke property is validated at executable depth before an atomic commit, and an
existing destination is preserved unless `--force` is explicitly supplied.

The generated property is an integration check only. Replace it with a meaningful
bound, witness, monotonicity, robustness, fairness, or label/probability
requirement before treating the specification as assurance evidence.

## Global diagnostics

```text
--diagnostic-format {text,json}
--debug
```

Successful primary output belongs to stdout or `--output`. Diagnostics belong
to stderr. `--debug` tracebacks are explicitly not machine-stable.
