# Toetra architecture

Toetra is a staged compiler and verification runtime for declarative behavioral
properties of machine-learning models.

```text
.toetra source
→ parser and syntax AST
→ semantic binding and typing
→ declarative IR1
→ model-family semantic lowering
→ NNF and IR2
→ ModelBridge assumptions
→ capability and numeric-compatibility routing
→ backend execution
→ report, provenance, and concrete replay
```

## Responsibilities

| Path | Responsibility |
|---|---|
| `dsl/language` | EBNF source, generated grammar, vocabulary |
| `dsl/ast`, `dsl/builder`, `dsl/parser` | syntax representation |
| `dsl/semantic` | binding, typing, point visibility, validation |
| `dsl/ir/ir1` | backend-neutral declarative intent |
| `model/semantics` | model-family lowering and evidence |
| `dsl/ir/ir2` | normalized verification tasks and assumptions |
| `model/schema`, `model/introspector`, `model/encoder` | ModelBridge |
| `dsl/compatibility`, `dsl/backends` | route qualification and execution |
| `dsl/reporting`, `dsl/provenance`, `dsl/runtime` | reports and replay |
| `toetra` | stable public Python facade |

A `target` is an output port. Regression uses `target[point]`; classification
selects `target[point].label` or `target[point].probability(label)`. Internal
quantities such as the logistic decision value appear only after IR1 and remain
outside the DSL.

Built-in `1.0.0rc3` routes are single-output sklearn `LinearRegression` and
direct fitted binary `LogisticRegression`, both through Z3 with explicit numeric
compatibility and provenance.

Source-of-truth rules:

- edit the EBNF, never the generated Lark file;
- document semantic changes before widening the public profile;
- treat over-declared model/backend support as a soundness defect;
- require CI, release, and review-bundle gates for a release candidate.
