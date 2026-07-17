# FORML Implementation Status Matrix

> Status date: 2026-07-17  
> Purpose: Record the closed Patch 15 architecture and the remaining V1 boundary

## Patch 15 closure

The points, scopes, quantifiers, anchors, multiple-evaluation, backend, reporting, and replay chantier is **implemented end to end** for the numeric-affine V1 profile.

| Layer | Status | Guarantee |
|---|---|---|
| EBNF and generated Lark | implemented | Natural anchors, ordered binders, indexed targets, `where`, `neighborhood`, `check_at`, and new `at` syntax; generated grammar remains source-controlled output. |
| CST → AST | implemented | Ordered anchors/binders, direct properties, restrictions, neighborhoods, source spans, and sugar provenance. |
| Semantic layer | implemented | First-class point environment, lexical visibility, exact default-point rules, anchor validation/resolution, indexed evaluation registry, and stable legacy diagnostics. |
| IR1 | implemented | Point bindings, ordered binders, point-owned domains, restrictions, and `(model, point, target)` references survive normalization. |
| IR2 | implemented | Point mappings, evaluation set, quantifier profile, provenance, capability requirements, and universal/existential verification semantics. |
| ModelBridge | implemented | One affine equation per distinct requested evaluation; no scope guessing. |
| Z3 | implemented | Distinct point-feature/output symbols, homogeneous multi-point proof/counterexample/witness execution, reverse symbol mappings. |
| Runtime anchors | implemented | Inline anchors plus `ref(...)` from resolver, source, or dataset fallback; lookup metadata excluded from model inputs. |
| Reporting | implemented | Grouped point evidence, JSON schema v2, text/HTML/Jupyter rendering. |
| Replay | implemented | Every referenced point is reconstructed and evaluated against the real estimator; restrictions and assertions are reevaluated. |
| Migration | implemented | Provisional legacy forms are diagnostic-only and never silently reinterpreted. |
| Canonical E2E suite | implemented | E2E-01 through E2E-06 and full `make ci` baseline. |

## Executable V1 profile

```text
numeric transformed features
+ scalar sklearn LinearRegression output
+ inline/referenced anchors
+ homogeneous forall or exists chains
+ typed numeric domains and scalar arithmetic
+ Linf restrictions
+ Z3
→ PROVED / COUNTEREXAMPLE / WITNESS / NO_WITNESS / UNKNOWN
→ grouped evidence and real-model replay
```

## Explicitly unsupported or deferred

- execution of alternating quantifiers;
- arbitrary preprocessing reconstruction;
- categorical/string backend reasoning;
- multi-output or multi-model properties;
- trees, ensembles, neural and nonlinear encoders;
- neighborhood metrics outside the implemented numeric-affine profile;
- additional solver backends.

## Remaining V1 engineering work

Patch 15 is no longer the critical path. Remaining work is product stabilization:

1. public error-boundary cleanup and diagnostics consistency;
2. solver timeout/resource controls;
3. documentation/demo polish and packaging/release checks;
4. Miova mutation campaigns and broader golden coverage;
5. final V1 release checklist and versioning.

Richer model families and preprocessing remain post-V1 unless the release scope is deliberately reopened.
