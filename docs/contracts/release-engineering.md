# Release engineering contract

## Scope

This contract defines how a Toetra source state becomes a reviewable and installable V1 artifact.

## Required gates

A release source state, including stable `1.0.0`, must satisfy all of the following:

1. `make ci` passes without modifying any source file.
2. the release source is a clean Git checkout with no tracked or untracked changes;
3. Python 3.11 and Python 3.12 pass the same quality gate;
4. two distribution builds made with the same source epoch have identical SHA-256 hashes;
5. the wheel and sdist identify the same project and version;
6. the wheel contains `toetra` as its only top-level package, both generated/source grammar files and the packaged public example policy;
7. wheel and sdist package inventories match the current files under `src/toetra/`;
8. the wheel contains no repository-only `tests`, `docs`, `demo` or workflow trees;
9. wheel and sdist each install in their own clean virtual environment outside the checkout on Ubuntu and native Windows, with Python 3.11 and 3.12;
10. the exact `toetra.__all__` V1 facade imports successfully and obsolete top-level namespaces are absent;
11. the standalone public quickstart runs after being copied into that clean environment;
12. the review bundle contains every critical V1 artifact;
13. two review-bundle builds produce identical bytes.
14. wheel and sdist include `toetra/py.typed` (under `src/` in the sdist),
    and the marker exists in the installed package;
15. a strict Pyright consumer using the public facade passes outside the checkout
    with source search paths disabled, and `pyright --verifytypes toetra
    --ignoreexternal` reports 100% type completeness from that clean installation.

## Commands

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

`make release-check` runs both archive formats. The installation script retains
wheel-only behavior by default; `--format sdist` selects the source distribution
and `--format both` runs the same journey twice in separate fresh environments.

## Automatic installation matrix

On every push to `main` and every pull request, `.github/workflows/ci.yml` runs
the Linux quality job on Python 3.11 and 3.12. One Ubuntu/Python 3.12 release job
then builds and validates reproducible distributions from the clean checkout,
runs the public demonstrations, and verifies the reproducible review bundle.
It uploads the wheel, sdist, and `SHA256SUMS` together as one Actions artifact.

Eight dependent installation jobs consume these same archives:

| Runner | Python | Archive formats |
|---|---|---|
| Ubuntu | 3.11 | wheel, sdist |
| Ubuntu | 3.12 | wheel, sdist |
| Native Windows | 3.11 | wheel, sdist |
| Native Windows | 3.12 | wheel, sdist |

Each cell installs only the archive-validation tooling in the host interpreter,
then installs the selected archive into a new temporary venv outside the checkout.
There is no editable installation or checkout build in an installation job.
Pip builds the sdist normally with isolated build dependencies. Both formats use
the same import, nine-name facade, resource, PEP 561, strict consumer, type
completeness, regression/classification, replay, CLI, and copied-quickstart checks.
The imported module and the package analyzed by Pyright must both resolve inside
the exact new venv's `site-packages`; source `PYTHONPATH`/`PYTHONHOME` are removed.

Artifact digest mismatches and failing combinations fail their jobs. Matrix
fail-fast is disabled so other combinations can report their results. Jobs retain
read-only permissions, bounded timeouts, immutable action references, and checkout
mutation checks. No job publishes packages or creates a release or tag. Acceptance
requires every cell to pass; the configured matrix is not evidence that a pending
workflow run has already succeeded. No macOS or additional Python version is
claimed. WSL exercises Linux, not native Windows.

See [installation and availability](../getting-started/installation.md#reproduce-an-installation-check)
for local reproduction commands on Linux/WSL and native Windows.

To create a review bundle:

```bash
make review-bundle
```

## Source date epoch

Release commands use `SOURCE_DATE_EPOCH` when provided. Otherwise they use the timestamp of the current Git commit and fall back to a fixed timestamp only outside a Git checkout.

The epoch controls archive metadata. It does not alter verification timestamps stored in runtime reports.

## Distribution contents

The installed wheel must contain runtime code and package data only. The source distribution also contains project metadata and legal/readme files.

Package inventory is checked exactly against `src/toetra/`, rather than inferred from a successful build command. Unexpected or missing package files fail the distribution gate.

## Review bundle contents

Critical paths include:

- the public `toetra` package and packaged example policy;
- the CI workflow and packaging metadata;
- the EBNF source and generated Lark grammar;
- the canonical public notebooks and their supported launch locations;
- classification and regression CSV fixtures used by ModelBridge tests.

The generator may exclude caches, build outputs, virtual environments and serialized model binaries. It must never claim completeness when a critical path is absent.

## Failure semantics

Release tooling failures are build failures, not verification results. They must stop publication and must not be represented as `UNKNOWN`, `PROVED` or any other logical status.

## Gate composition

CI, public demonstrations, distribution validation, and review-bundle
reproducibility remain separate durable gates. Run all four commands listed
above from a clean committed checkout when validating a release for publication. The
underlying layout is defined by the
[repository contract](repository-contract.md).
