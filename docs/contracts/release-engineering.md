# Release engineering contract

## Scope

This contract defines how a FORML source state becomes a reviewable and installable V1 artifact.

## Required gates

A release candidate must satisfy all of the following:

1. `make ci` passes without modifying any source file.
2. Python 3.11 and Python 3.12 pass the same quality gate.
3. two distribution builds made with the same source epoch have identical SHA-256 hashes;
4. the wheel and sdist identify the same project and version;
5. the wheel contains `forml`, `dsl`, `model` and both generated/source grammar files;
6. the wheel contains no repository-only `test`, `docs`, `demo` or workflow trees;
7. the wheel installs in a clean virtual environment outside the checkout;
8. `from forml import verify, VerificationSession` succeeds from that environment;
9. the review bundle contains every critical V1 artifact;
10. two review-bundle builds produce identical bytes.

## Commands

```bash
make ci
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

Package inventory is checked structurally rather than inferred from a successful build command.

## Review bundle contents

Critical paths include:

- the public `forml` package;
- the CI workflow and packaging metadata;
- the EBNF source and generated Lark grammar;
- the canonical notebook;
- classification and regression CSV fixtures used by ModelBridge tests.

The generator may exclude caches, build outputs, virtual environments and serialized model binaries. It must never claim completeness when a critical path is absent.

## Failure semantics

Release tooling failures are build failures, not verification results. They must stop publication and must not be represented as `UNKNOWN`, `PROVED` or any other logical status.
