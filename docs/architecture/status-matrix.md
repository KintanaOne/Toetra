# FORML Implementation Status Matrix

> Status date: July 2026  
> Purpose: Separate implemented behavior from stabilizing or future work

## Status vocabulary

| Status | Meaning |
|---|---|
| `implemented` | Executable behavior exists and is covered by tests. |
| `implemented / stabilizing` | Executable behavior exists; contracts and ergonomics may still evolve. |
| `partial` | A useful subset exists, but the subsystem is intentionally incomplete. |
| `planned` | Documented direction without an executable implementation. |
| `research direction` | Long-term investigation, not a committed V1 capability. |

## Compiler and verification pipeline

| Component | Status | Current guarantee | Remaining boundary |
|---|---|---|---|
| EBNF and generated Lark grammar | implemented | Explicit quantifiers, typed domains, scalar arithmetic and specification constants parse from complete programs. | Future syntax must remain generator-driven. |
| CST → AST builder | implemented | Structured scalar trees, ordered declarations and typed domain nodes are produced without semantic binding. | Additional property families may require new AST nodes. |
| Semantic binding | implemented / stabilizing | Constants, implicit features, explicit features and target references are resolved deterministically. | Public error taxonomy still wraps several semantic failures as `ParserError`. |
| Schema-aware typing | implemented | Input and target dtypes are read from `ModelSchema`; arithmetic is typed and classified. | Richer categorical and tensor types are future work. |
| IR1 | implemented | Symmetric scalar comparisons, recursive arithmetic, typed domains and constant provenance are preserved. | Optional affine canonicalization is not implemented. |
| NNF normalization | implemented | De Morgan and implication normalization preserve scalar atoms. | Additional simplification passes are optional future work. |
| IR2 NNF/CNF/DNF | implemented / stabilizing | Normal-form selection, conversion, guardrails and task validation exist. | Explosion-control and optimization policies can be enriched. |
| Assertion aggregation | implemented | DSL domains, model assumptions and user properties are combined into `Γ ∧ ¬P` or `Γ ∧ P`. | Additional assumption sources may be added. |
| Domain lowering | implemented | Open/closed intervals and numeric finite sets become provenanced IR2 assumptions. | Symbolic categories are represented but not encoded by Z3. |
| Backend capability routing | implemented | Unsupported arithmetic, sorts and domain features are rejected before execution. | Multi-backend policy and fallback remain future work. |
| Z3 numeric-affine backend | implemented / stabilizing | Numeric comparisons, affine arithmetic, numeric domains, finite sets, model equations and result interpretation execute end to end. | Nonlinear arithmetic, symbolic division and categorical encoding are explicitly unsupported. |
| Result interpretation | implemented | Universal and existential SAT/UNSAT/UNKNOWN outcomes map to FORML statuses with messages. | Timeouts and resource limits need a dedicated configuration contract. |
| Vacuity diagnostics | implemented | Inconsistent assumptions are detected after UNSAT and reported as a structured warning. | More advanced vacuity and redundancy analysis is future work. |

## Runtime and user-facing output

| Component | Status | Current guarantee | Remaining boundary |
|---|---|---|---|
| Public `forml.verify(...)` API | implemented | Model loading or supplied schema, compilation, routing, execution and report construction are exposed through a stable top-level facade. | Timeout and execution-policy configuration remain future work. |
| `VerificationSession` | implemented | Multiple properties expose filtered findings, records/data frames, grouped artifact export and CI-friendly exit codes. | Persistence and cross-run comparison are post-V1 concerns. |
| Text reporting | implemented | Backend-neutral terminal output groups inputs, outputs and diagnostics. | Optional localization and richer explanations may be added later. |
| JSON reporting | implemented | Versioned report and collection schemas preserve exact rational values. | Schema evolution requires explicit future versions. |
| HTML/Jupyter reporting | implemented | Escaped, dependency-free status cards and standalone HTML documents are generated from the same report model. | Interactive widgets are intentionally outside the current V1. |
| Notebook workflow | implemented | A credit-risk example uses only the `forml` facade, rich sessions and automatic estimator replay. | The example uses transformed numerical features; preprocessing is not encoded. |
| Counterexample replay | implemented | Numeric backend assignments are normalized, reconstructed in schema feature order and compared with the original estimator output. | V1 expects an estimator exposing `predict(...)`; preprocessing remains external. |

## ModelBridge

| Component | Status | Current guarantee | Remaining boundary |
|---|---|---|---|
| Loading and framework detection | implemented / stabilizing | Existing sklearn/XGBoost foundations remain available. | Unsupported frameworks require continued diagnostic cleanup. |
| `ModelSchema` | implemented | Feature dtypes, target name and optional target dtype cross the compiler boundary. | Preprocessing remains explicitly outside V1. |
| Schema-aware semantic validation | implemented | Unknown features are rejected and scalar dtypes reach IR1 when a schema is supplied. | Structured shapes and richer target schemas are future work. |
| LinearRegression encoder | implemented | A single-output affine output equation is emitted as a backend-neutral MODEL assumption. | Other linear/classification families and preprocessing are not encoded. |
| Rich model encoders | planned | Trees, ensembles and neural encodings have architectural placeholders only. | Implement per-family sound encoders and tests. |

## Testing

| Testing layer | Status | Evidence |
|---|---|---|
| Parser, AST, builder and semantic unit tests | implemented | Gate-specific acceptance, rejection and invariant tests. |
| IR1 and IR2 contract tests | implemented | Recursive scalar IR, domains, provenance, normal forms and requirements. |
| Backend capability tests | implemented | Accepted affine profile and explicit rejection paths. |
| Z3 execution tests | implemented | Universal proof/counterexample, existential witness/no-witness and UNKNOWN interpretation. |
| Golden samples | implemented / stabilizing | Parser/IR/normalization/model and final affine end-to-end contracts. |
| Vacuity tests | implemented | Contradictory assumptions emit structured result diagnostics. |
| Miova mutation campaigns | planned integration | Mutation boundaries are documented but not part of this language-evolution chantier. |

## Current end-to-end profile

```text
.forml source
    → CST
    → AST
    → semantic binding and schema-aware typing
    → IR1 recursive scalar logic
    → NNF
    → IR2 + domain/model assumptions
    → capability routing
    → Z3 numeric-affine translation
    → PROVED / COUNTEREXAMPLE / WITNESS / NO_WITNESS / UNKNOWN
```

The profile is intentionally narrow but real. It supports numeric affine properties over a supported model encoding. It does not imply support for arbitrary ML models, preprocessing pipelines, nonlinear formulas or symbolic categories.

## Immediate next engineering priorities

1. Stabilize public error boundaries instead of wrapping semantic failures as parser failures.
2. Define the next scope semantics for `at`, `check_at`, explicit anchors and nested/multiple quantified entities.
3. Add model encoders beyond single-output `LinearRegression`.
4. Decide the V1 policy for preprocessing and transformed-feature contracts.
5. Add timeout/resource controls and richer backend execution diagnostics.
6. Connect Miova mutation campaigns to the now-stable layer contracts.
