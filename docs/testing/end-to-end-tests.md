# End-to-End Tests

> Status: Patch 15 canonical suite implemented

The end-to-end suite protects the complete path:

```text
source → CST → AST → semantic points → IR1 → IR2
→ ModelBridge → routing → Z3 → grouped report → real-model replay
```

## Canonical Patch 15 fixtures

| ID | Scenario | Required outcome |
|---|---|---|
| E2E-01 | inline anchor direct assertion | point evidence and consistent replay |
| E2E-02 | referenced anchor with `check_at` | unique lookup, provenance, no metadata leakage |
| E2E-03 | two-point universal monotonicity | proof and counterexample variants, grouped evidence |
| E2E-04 | `at` sugar vs explicit neighborhood | equivalent canonical query/result except provenance |
| E2E-05 | existential adversarial search | witness terminology and replay of both points |
| E2E-06 | alternating quantifiers | preserved order and capability rejection before solver |

Fixtures live under `tests/fixtures/point_binding/`; tests are split by anchor, multi-point, and sugar-equivalence concerns under `tests/e2e/point_binding/`.

## Regression obligations

Every change must keep green:

- EBNF → generated Lark synchronization;
- parser/AST/semantic contracts;
- typed domains and specification constants;
- IR1/IR2 point ownership and quantifier structure;
- exactly one model equation per requested evaluation;
- Z3 symbol mapping and result semantics;
- JSON schema v2 and renderer goldens;
- grouped replay against the real sklearn model;
- stable legacy migration diagnostics;
- notebook hygiene and both public notebook workflows from the repository root
  and each notebook directory;
- a quickstart copied and executed outside the repository with an isolated
  Python path.

## CI

The authoritative local gate is:

```bash
make ci
```

It runs notebook hygiene, Ruff, Black, Pyright, and Pytest. A patch is not complete until this gate is green in the full repository.
## Reproducible CLI smoke scenario

The complete five-command process contract is exercised by one reusable
cross-platform scenario:

```bash
make cli-smoke-check
```

`scripts/ci/check_cli_smoke.py` creates all models, datasets, policies, and
outputs in a temporary directory outside the checkout. It verifies the
active distribution version, both `python -m toetra` and the installed
`toetra` script, then runs `init`, `validate`, `inspect`, `verify`, and
`replay`, including declared/effective overrides and report artifacts.

The same Python scenario is invoked by the isolated-wheel installation
probe. Checkout CI and release CI therefore share assertions rather than
maintaining separate manual command lists. A failure retains its temporary
workspace and prints the exact command, status, stdout, and stderr.
