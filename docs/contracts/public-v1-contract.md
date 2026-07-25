# Public V1 contract

> Status: frozen for `1.0.0rc3`

## Stable public surfaces

The supported Python entry point is `toetra`. Normal user surfaces include
`verify`, sessions/findings/reports, statuses, artifacts, and replay errors.
Internal `dsl.*`, `model.*`, IR, semantic-profile, and backend modules may evolve
unless another contract explicitly marks them public.

The EBNF is the language source of truth; the generated Lark grammar is never
edited directly.

## Built-in executable routes

1. fitted single-output sklearn `LinearRegression` with a scalar numeric output;
2. direct fitted binary sklearn `LogisticRegression` with predicted-label,
   class-probability, and pairwise-label properties.

Both use finite transformed numeric inputs, affine equations, and Z3.

## Compatibility policy

- incompatible public Python changes require a major version;
- incompatible JSON changes require a schema version greater than 6;
- JSON v6 additions are optional and never reinterpret existing fields;
- read-only scalar-target projections remain available through 1.x;
- no route may claim a stronger numeric or semantic conclusion than its policies
  permit.

## Result contract

Logical conclusions and technical execution remain separate. Timeout,
cancellation, resource limits, numeric uncertainty, or lowering uncertainty
cannot be presented as stronger logical conclusions.

## JSON report contract

```text
toetra.verification-report / schema_version 6
toetra.verification-report-collection / schema_version 6
```

Classification adds optional model-evaluation and lowering evidence only.

## Release gates

```bash
make ci
make release-check
make review-bundle-check
git diff --check
```

The clean-installed wheel probe executes a real binary label/probability route
outside the repository.
