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
| `src/toetra/_language` | EBNF source, generated grammar, vocabulary |
| `src/toetra/_compiler/ast`, `src/toetra/_compiler/builder`, `src/toetra/_compiler/parser` | syntax representation |
| `src/toetra/_compiler/semantic` | binding, typing, point visibility, validation |
| `src/toetra/_compiler/ir/ir1` | backend-neutral declarative intent |
| `src/toetra/_models/semantics` | model-family lowering and evidence |
| `src/toetra/_compiler/ir/ir2` | normalized verification tasks and assumptions |
| `src/toetra/_models/schema`, `src/toetra/_models/introspector`, `src/toetra/_models/encoder` | ModelBridge |
| `src/toetra/_compatibility`, `src/toetra/_backends` | route qualification and execution |
| `src/toetra/_reporting`, `src/toetra/_provenance`, `src/toetra/_runtime` | reports and replay |
| `src/toetra` | stable public facade and private implementation packages |

Only `src/toetra/__init__.py` and the installed `toetra.examples` resource helper
intentionally aggregate names. Private `toetra._*` package initializers do not
re-export implementation symbols; internal code imports concrete modules.

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
