# Public V1 contract

> Status: frozen for `1.0.0rc1`

## Stable public surfaces

The supported Python entry point is the `forml` package. The normal user surface
includes `verify`, verification sessions/findings/reports, result statuses, and
replay errors. Internal `dsl.*`, `model.*`, IR, and backend modules may evolve
unless another contract explicitly marks them public.

The supported source language is generated from the repository EBNF. The EBNF is
the source of truth; the generated Lark grammar must never be edited directly.

## Compatibility policy

For the FORML 1.x line:

- incompatible public Python changes require a major version;
- incompatible JSON report changes require a schema version greater than 5;
- additions to JSON v5 must be optional and must not reinterpret existing fields;
- diagnostic text may improve, but stable diagnostic codes must retain meaning;
- new framework/model/backend routes do not alter the guarantee of existing rules;
- a route must never claim a stronger numeric conclusion than its rule permits.

## Result contract

Logical conclusions and technical execution are separate:

- logical: proved, counterexample, witness, no witness, unknown;
- technical: SAT, UNSAT, UNKNOWN, TIMEOUT, RESOURCE_LIMIT, CANCELLED, ERROR.

A timeout, cancellation, or resource limit cannot be presented as a proof or a
counterexample. Technical errors raise structured execution errors rather than
being disguised as logical unknowns.

## JSON report contract

The stable identifiers are:

```text
forml.verification-report / schema_version 5
forml.verification-report-collection / schema_version 5
```

JSON v5 includes property and scope identity, logical and backend execution
status, assignments grouped by points, diagnostics, numeric compatibility, and
verification provenance. Any incompatible restructuring requires JSON v6.

## Release gates

A V1 release candidate is acceptable only when all of these pass from a clean
checkout:

```bash
make ci
make release-check
make review-bundle-check
git diff --check
```

The wheel must install and import outside the repository. The review bundle must
contain the public package, grammar sources/generated grammar, demos, notebooks,
and test fixtures declared critical by the bundle contract.
