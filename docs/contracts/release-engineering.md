# Release engineering contract

## Scope

This contract defines how a Toetra source state becomes a reviewable and installable V1 artifact.

## Required gates

A release candidate must satisfy all of the following:

1. `make ci` passes without modifying any source file.
2. the release source is a clean Git checkout with no tracked or untracked changes;
3. Python 3.11 and Python 3.12 pass the same quality gate;
4. two distribution builds made with the same source epoch have identical SHA-256 hashes;
5. the wheel and sdist identify the same project and version;
6. the wheel contains `toetra` as its only top-level package, both generated/source grammar files and the packaged public example policy;
7. wheel and sdist package inventories match the current files under `src/toetra/`;
8. the wheel contains no repository-only `tests`, `docs`, `demo` or workflow trees;
9. the wheel installs in a clean virtual environment outside the checkout;
10. the exact `toetra.__all__` V1 facade imports successfully and obsolete top-level namespaces are absent;
11. the review bundle contains every critical V1 artifact;
12. two review-bundle builds produce identical bytes.

## Commands

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

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
- the canonical notebook;
- classification and regression CSV fixtures used by ModelBridge tests.

The generator may exclude caches, build outputs, virtual environments and serialized model binaries. It must never claim completeness when a critical path is absent.

## Failure semantics

Release tooling failures are build failures, not verification results. They must stop publication and must not be represented as `UNKNOWN`, `PROVED` or any other logical status.

## Final repository gate

`make p24-check` aggregates CI, public demonstrations, release validation, and
review-bundle reproducibility from a clean committed checkout. The underlying
layout is defined by the [repository contract](repository-contract.md).
