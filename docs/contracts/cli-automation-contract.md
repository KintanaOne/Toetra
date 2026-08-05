# CLI and Automation Contract

> **Status:** Accepted design; P28.4 replay implemented, init pending
>
> **Compatibility surface:** installed process interface, machine-readable output,
> diagnostics, artifacts, and exit codes
>
> **Implementation target:** the first Toetra release candidate that ships the
> `toetra` entry point

## Purpose

The CLI exposes Toetra as a deterministic operating-system process for terminal
use, CI/CD, container jobs, and higher-level orchestration.

It is not a second verification engine. Command handlers adapt process inputs to
shared application services and adapt their results to streams, files, and exit
codes.

```text
argv + working directory + environment
→ CLI parsing and path resolution
→ shared Toetra application workflow
→ result or structured failure
→ stdout / stderr / artifacts / process status
```

No parser, compiler, model, routing, backend, reporting, or replay semantics may
be reimplemented beneath `toetra._cli`.

## Command surface

The initial accepted command grammar is:

```text
toetra [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]

COMMAND := validate | inspect | verify | replay | init
```

The following process-level conveniences are also required:

```text
toetra --help
toetra --version
python -m toetra --help
python -m toetra --version
```

The installed entry point and `python -m toetra` are behaviorally equivalent.

`compile` and `serve` are reserved command names but are not implemented by
P28. Reserving them does not create a support promise.

## Global options

| Option | Meaning |
|---|---|
| `--help` | Show help for the selected command or the command index. |
| `--version` | Print the installed Toetra distribution version and exit. |
| `--diagnostic-format {text,json}` | Select stderr diagnostic rendering. Default: `text`. |
| `--debug` | Include internal traceback information on stderr. Not a machine-stable format. |

Help and version output must not load a model, dataset, anchor source, or invoke
a backend. `--version` is read from installed distribution metadata rather than
a duplicated CLI constant.

## Shared verification inputs

`validate`, `inspect`, and `verify` share this input surface:

```text
SPECIFICATION
[--model PATH]
[--dataset PATH]
[--anchor-source PATH]
[--target NAME]
```

### `SPECIFICATION`

- exactly one `.toetra` file is accepted per invocation;
- the path is required and interpreted relative to the process working
  directory;
- stdin (`-`) and inline source are not accepted by the first CLI contract;
- the source must be readable UTF-8;
- retired specification extensions are rejected by the existing public error
  boundary.

One specification per process keeps provenance, cancellation, output ownership,
and exit status unambiguous. Pipeline-level fan-out belongs to the orchestrator.

The header values are reusable defaults, not immutable run parameters. Explicit
`--model`, `--target`, and `--dataset` values form one temporary execution
overlay with precedence over the header. The source AST remains unchanged; the
shared runtime resolves and records the effective context before compilation.

### Model precedence

When `--model` is supplied, it replaces the model reference declared in the
specification header. The CLI path is interpreted relative to the process
working directory.

When `--model` is omitted, the model reference from the specification header is
interpreted relative to the specification file, matching `toetra.verify(...)`.

### Dataset, anchors, and target

- `--dataset` overrides the optional dataset reference declared in the
  specification header; when omitted, the header dataset is resolved relative
  to the specification file and is used by model introspection and, when
  eligible, the existing anchor-source fallback;
- `--anchor-source` supplies a CSV anchor source explicitly;
- `--target` temporarily rebinds the effective DSL output name before semantic
  validation and IR construction; the runtime rebuilds or aliases the effective
  schema to the same name and records both declared and effective targets;
- providing both an explicit anchor source and another future resolver form is
  rejected rather than guessed.

The first CLI accepts file-backed artifacts only. In-memory schemas, pandas
objects, custom registries, custom encoders, and custom anchor resolvers remain
Python integration concerns.

## Shared execution policy options

`validate --level executable`, `inspect`, and `verify` share this
backend-neutral policy surface:

```text
[--timeout-ms POSITIVE_INTEGER | --no-timeout]
[--max-backend-units POSITIVE_INTEGER]
[--max-memory-mb POSITIVE_INTEGER]
[--seed NON_NEGATIVE_INTEGER]
```

Omitted values use the existing Toetra defaults. `--timeout-ms` and
`--no-timeout` are mutually exclusive. Positive resource values fail closed when
the selected backend cannot enforce them.

Execution options supplied to `validate --level syntax` or
`validate --level semantic` are rejected with status `3`; they are never
silently ignored.

Backend-native option passthrough is intentionally absent from the initial
stable CLI.

## Path resolution

For every CLI path:

1. the user-home prefix is expanded;
2. a relative path is interpreted against the process working directory unless
   a command-specific rule says otherwise;
3. the resolved path is normalized before input/output collision checks;
4. operating-system symlink behavior is preserved;
5. content fingerprints, not presentation paths, remain the provenance
   authority.

Toetra does not perform environment-variable interpolation inside argument
values. Shell or orchestrator expansion occurs before process invocation.

Paths with spaces and Unicode characters are part of the acceptance matrix on
Windows and Linux.

## `validate`

### Intent

`validate` answers:

> Can Toetra accept this verification request at the requested pipeline depth
> without running the backend solver?

```text
toetra validate SPECIFICATION [SHARED_INPUTS]
    [EXECUTION_POLICY_OPTIONS]
    [--level {syntax,semantic,executable}]
    [--format {text,json}]
    [--output PATH|-]
```

The default level is `executable`. The default format is `text`. The default
output is stdout (`-`).

### Validation levels

| Level | Required successful boundary | Explicitly excluded |
|---|---|---|
| `syntax` | source loading, parsing, and CST-to-AST construction | model loading, semantic validation, routing, backend work |
| `semantic` | `syntax` plus model/schema resolution, target and anchor validation, semantic validation, and IR1 construction | model encoding, IR2, routing, translation, solver execution |
| `executable` | `semantic` plus model-semantic lowering, model encoding, IR2, numeric compatibility, backend routing, runner lookup, execution-policy compatibility, and backend-private translation | solver execution |

`executable` is a dry run of every pre-execution boundary. It may allocate and
translate backend objects but must not call the backend solver.

`executable` validates the exact execution policy supplied to the command, or
the default policy when no execution option is present.

### Validation JSON

Text and JSON validation results are emitted for both accepted and rejected
requests whenever the validation workflow completes normally. A rejected
request therefore keeps a machine-readable result while returning status `3`
or `4`. Unexpected internal failures and output-write failures produce only the
selected stderr diagnostic.

JSON output uses:

```text
toetra.validation-result / schema_version 1
```

It contains at minimum:

- requested and completed validation level;
- `valid` boolean;
- resolved specification/model/dataset/anchor identities when consumed;
- completed boundary checks;
- property count when available;
- normalized structured diagnostics;
- Toetra software identity.

It must not expose CST, AST, IR1, IR2, backend-native formulas, or private Python
class names.

### Exit status

| Status | Meaning |
|---:|---|
| `0` | valid at the requested level |
| `3` | invalid usage, source, artifact, or configuration |
| `4` | meaningful but unsupported route, translation failure, or technical runtime failure |
| `5` | unexpected internal failure |
| `130` | interrupted by SIGINT |
| `143` | terminated by SIGTERM where supported |

Logical verification exit statuses `1` and `2` are impossible because no solver
result is produced.

## `inspect`

### Intent

`inspect` answers:

> What verification request has Toetra resolved, and what would it execute?

```text
toetra inspect SPECIFICATION [SHARED_INPUTS]
    [EXECUTION_POLICY_OPTIONS]
    [--format {text,json}]
    [--output PATH|-]
```

`inspect` performs the same pre-execution work as
`validate --level executable`. It fails closed if no complete executable plan
can be built.

### Inspection content

The inspection contains public, normalized descriptions of:

- specification identity, target, constants, anchors, and property count;
- model framework, model family, task type, input schema, output schema, and
  consumed artifact identities;
- each property index, source type, verification semantics, requested
  observables, capability requirements, numeric trust classification, selected
  backend, route reason, and execution-policy compatibility;
- backend runner availability and successful translation readiness;
- software and compiler-policy identity.

It must not expose:

- raw CST, AST, IR1, or IR2;
- backend-native formulas or mutable solver objects;
- private module/class names;
- learned model parameters unless a later explicit inspection contract accepts
  them.

### Inspection JSON

JSON output uses:

```text
toetra.inspection / schema_version 1
```

The top-level groups are:

```text
specification
model
properties
execution
provenance
software
```

Field ordering is presentation-only. Callers branch on schema identity, schema
version, stable enum values, and diagnostic codes rather than prose.

### Exit status

`inspect` uses the same process statuses as `validate`.

## `verify`

### Intent

`verify` answers:

> What is the formal conclusion for every property in this specification?

```text
toetra verify SPECIFICATION [SHARED_INPUTS]
    [EXECUTION_POLICY_OPTIONS]
    [--format {text,json,html}]
    [--output PATH|-]
    [--artifacts-dir DIRECTORY]
    [--artifact-stem NAME]
```

Defaults:

- timeout: the existing Toetra default of 30,000 ms;
- format: `text`;
- output: stdout (`-`);
- artifact stem: `toetra-verification-report`.

`--artifact-stem` accepts one portable ASCII filename stem, not a path. It
must contain 1-128 letters, digits, dots, underscores, or hyphens; begin with a
letter, digit, or underscore; and not end with a dot. Directory separators,
`.`/`..`, leading dots or hyphens, and Windows reserved device names are
rejected.

The execution controls construct the existing backend-neutral execution policy.

### Primary output

| Format | Contract |
|---|---|
| `text` | shared terminal rendering from `VerificationSession.to_text()` |
| `json` | exact `toetra.verification-report-collection` JSON v6 produced by `VerificationSession.to_json()` |
| `html` | shared self-contained HTML rendering produced by `VerificationSession.to_html()` |

The CLI does not wrap JSON v6 in a CLI-specific success envelope.

### Artifact directory

When `--artifacts-dir` is supplied, the CLI writes, at minimum:

```text
ARTIFACTS_DIR/
├── ARTIFACT_STEM.json
├── ARTIFACT_STEM.html
└── ARTIFACT_STEM.manifest.json
```

The JSON and HTML files come from the same `VerificationSession`. Each file is
committed atomically, and the manifest is committed last. Before replacing an
existing artifact set under the same stem, the previous manifest is removed
immediately before the first report write. A valid final manifest is therefore
the completion marker for the current artifact set.

The manifest uses:

```text
toetra.run-manifest / schema_version 1
```

and records:

- command and terminal process status;
- relative artifact names and SHA-256 digests;
- verification collection schema identity/version;
- shared input fingerprint and provenance completeness;
- Toetra version/build identity;
- start/completion timestamps and duration;
- whether primary output was stdout or a file.

The manifest does not replace report provenance.

### Logical exit status

| Status | Meaning |
|---:|---|
| `0` | every property is `PROVED` or `WITNESS` |
| `1` | at least one property is `COUNTEREXAMPLE` or `NO_WITNESS` |
| `2` | no logical failure exists, but at least one property is `UNKNOWN` |

The precedence is:

```text
process failure > logical failure > inconclusive > success
```

A timeout, backend resource limit, or native solver `unknown` remains a reportable
`UNKNOWN` and therefore status `2`, not a process error.

After verification, output and artifact writes are part of the command. If they
fail, the final process status is `4` even when the logical session had status
`0`, `1`, or `2`.

### Process failure status

| Status | Meaning |
|---:|---|
| `3` | invalid CLI usage, source, artifact, or configuration |
| `4` | unsupported route, technical runtime failure, serialization, or filesystem failure |
| `5` | unexpected internal failure |
| `130` | interrupted by SIGINT |
| `143` | terminated by SIGTERM where supported |

## `replay`

### Intent

`replay` answers:

> Does concrete execution of the supplied model remain consistent with the
> formal witness or counterexample archived in a JSON v6 report?

It does not invoke the solver or silently perform a new verification.

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

Defaults:

- model and dataset use the specification declarations when no override is
  supplied;
- target uses the archived effective target when available, otherwise the
  specification declaration;
- all replayable `COUNTEREXAMPLE` and `WITNESS` reports are selected;
- repeated `--property` values select zero-based report property indices,
  preserve first occurrence order, and ignore exact duplicates;
- tolerance: `1e-9`;
- format: `text`;
- output: stdout (`-`).

### Replay reconstruction

The command:

1. loads a `toetra.verification-report-collection` schema v6 document;
2. validates its structure before using any evidence;
3. resolves the header defaults plus any explicit model, target, or dataset
   overrides and fingerprints the effective artifacts;
4. verifies those fingerprints against archived provenance;
5. recompiles the exact specification through the pre-execution pipeline
   without invoking the solver;
6. matches selected reports to reconstructed tasks by property index and
   property fingerprint;
7. applies the existing concrete replay semantics.

A provenance, schema, property, or artifact mismatch is a configuration failure.
There is no initial `--ignore-provenance` escape hatch.

### Replay JSON

JSON output uses:

```text
toetra.replay-report-collection / schema_version 1
```

It records each selected property, formal status, replay availability,
per-point comparisons, tolerance, assertion/restriction consistency, maximum
absolute error, and final replay conclusion.

### Replay exit status

| Status | Meaning |
|---:|---|
| `0` | every selected replay is available and consistent |
| `1` | at least one selected replay contradicts or exceeds the accepted tolerance |
| `2` | no contradiction exists, but at least one selected replay is unavailable or indeterminate |
| `3` | invalid report, arguments, provenance mismatch, or artifact configuration |
| `4` | technical replay, observer, serialization, or filesystem failure |
| `5` | unexpected internal failure |
| `130` | interrupted by SIGINT |
| `143` | terminated by SIGTERM where supported |

No replayable finding is an inconclusive status `2`, not a successful empty run.

## `init`

### Intent

`init` creates a model-aware starter specification without guessing a meaningful
business property.

```text
toetra init SPECIFICATION
    --model PATH
    --target NAME
    [--dataset PATH]
    [--force]
```

The command:

- requires a destination ending in `.toetra`;
- refuses to overwrite an existing file unless `--force` is present;
- loads and introspects the supplied model using the accepted built-in route;
- writes the explicitly supplied `--target` as the default output declaration;
- writes a relative model reference when a portable relative path can be
  represented;
- includes comments listing normalized input features and model/task identity;
- generates exactly one clearly labelled smoke property:
  - regression compares the selected output with itself;
  - classification compares the selected predicted label with itself;
- adds commented guidance for replacing the smoke property with a meaningful
  bound, witness, monotonicity, robustness, or label/probability property;
- validates the generated source at `executable` depth before committing it.

The smoke property proves integration only. It is not presented as model
quality, safety, robustness, or business evidence.

Successful `init` returns `0`, writes the generated destination path as one
UTF-8 line on stdout, and leaves stderr empty. Invalid inputs return `3`;
unsupported or technical model-route failures return `4`; unexpected failures
return `5`.

## Output ownership

### Stdout

Stdout contains only the selected primary representation for a completed
command. This includes formal status `1` or `2`, replay status `1` or `2`, and a
completed negative validation result. A process failure that cannot produce its
command result leaves stdout empty.

Stdout must not contain progress messages, log prefixes, artifact
announcements, dependency warnings, or debug output.

This guarantee permits:

```bash
toetra verify policy.toetra --format json > verification.json
```

without corrupting JSON.

### Stderr

Stderr contains only diagnostics, warnings that materially affect trust, and
optional debug tracebacks.

Human diagnostics are concise and actionable. With
`--diagnostic-format json --debug`, traceback content is carried in an optional
`debug_traceback` string inside the single JSON diagnostic rather than emitted
as additional non-JSON text.

JSON diagnostics use:

```text
toetra.cli-diagnostic / schema_version 1
```

with at least:

```json
{
  "schema": "toetra.cli-diagnostic",
  "schema_version": 1,
  "category": "configuration",
  "code": "SPECIFICATION_NOT_FOUND",
  "stage": "configuration",
  "message": "...",
  "hint": "...",
  "location": {
    "path": "...",
    "line": null,
    "column": null
  },
  "command": "verify",
  "software": {
    "toetra_version": "..."
  }
}
```

Message and hint prose may improve. Automation branches on schema identity,
`category`, `code`, `stage`, and process status.

Argument-parser failures must use status `3`; the parser must not reuse the
usual argparse status `2`, because Toetra reserves `2` for an inconclusive
logical or replay outcome.

## File-write behavior

- output files are UTF-8 without a byte-order mark;
- JSON and text files end with one newline;
- writes are atomic within the destination filesystem;
- parent directories are created for explicit output and artifact paths;
- an existing output file may be replaced atomically for repeatable CI runs;
- no output may overwrite a consumed specification, model, dataset, anchor
  source, or report input;
- the primary output and generated artifact destinations must be distinct;
- a failed command leaves no temporary or partially written final artifact;
- an existing artifact directory retains unrelated files and replaces only the
  known Toetra-owned names for the selected stem.

`init` is the exception: it refuses an existing destination unless `--force` is
explicit.

## Signals and cancellation

- SIGINT triggers best-effort backend cancellation, cleanup, and status `130`;
- SIGTERM, where available, triggers best-effort cancellation, cleanup, and
  status `143`;
- no Python traceback is emitted unless `--debug` is present;
- a signal-triggered termination is not rewritten as logical `UNKNOWN`.

The process may still be force-killed by the host before cleanup completes.
Callers must treat atomic final artifacts and their manifest as the completion
boundary.

## Security boundary

Serialized `.pkl` and `.joblib` models may execute code during deserialization.
The CLI documentation must state that such artifacts are accepted only from a
trusted source.

The initial CLI:

- does not download remote models or specifications;
- does not evaluate shell fragments;
- does not interpolate environment variables itself;
- does not expose arbitrary backend-native options;
- does not start a network listener;
- does not deserialize a CLI-private pickle cache or compiled artifact.

## Compatibility rules

The following are public compatibility surfaces once shipped:

- command and option names;
- required/optional argument relationships;
- path precedence and output ownership;
- exit-code meanings;
- stdout/stderr separation;
- JSON schema identities and versions;
- artifact filenames when default stems are used.

Additive options and additive optional JSON fields are backward-compatible.
Removing or reinterpreting a command, option, status, stable enum, or required
field requires an explicit compatibility decision and release note.

Text wording and layout may improve provided they preserve meaning. `--debug`
traceback output is never machine-stable.

## Explicit non-goals

P28 does not:

- expose private compiler IRs;
- serialize an executable compiled plan;
- add a backend override outside the DSL;
- accept multiple specifications in one process;
- provide a configuration file or Toetra-specific environment-variable layer;
- provide a daemon, HTTP API, authentication, queue, multi-tenancy, or remote
  model upload;
- promise third-party plugin discovery through the CLI.

## Acceptance gates

The CLI is not releasable until tests prove:

1. source-tree, wheel-installed, and `python -m toetra` equivalence;
2. `--help` and `--version` from an external working directory;
3. every documented exit status and its precedence;
4. byte-parseable JSON on stdout with no contamination;
5. JSON diagnostics on stderr with no stdout contamination;
6. atomic output and artifact writes, including logical statuses `1` and `2`;
7. input/output collision rejection;
8. path resolution outside the checkout, with spaces and Unicode;
9. Windows and Linux behavior for the accepted Python matrix;
10. validation stopping at the documented boundary without solver execution;
11. inspection containing no private IR or backend-native formula;
12. verification JSON remaining exactly the existing JSON v6 collection;
13. replay rejecting provenance mismatch and never invoking the solver;
14. `init` producing an executable, model-aware smoke specification;
15. SIGINT and supported SIGTERM cancellation behavior;
16. no direct CLI dependency on parser, compiler, model encoder, router, backend,
    or renderer implementation modules beyond accepted application adapters;
17. clean-install MLOps examples that archive artifacts and gate on statuses
    `0`, `1`, and `2` deliberately.
