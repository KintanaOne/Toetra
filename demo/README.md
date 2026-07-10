# FORML Z3 End-to-End Demo

This demo validates the first complete FORML verification path using the minimal
Z3 backend.

## Pipeline

```text
.forml DSL
→ Lark parser
→ AST builder
→ semantic validation
→ IR1
→ NNF normalization
→ IR2 verification task
→ backend router
→ Z3 translation
→ Z3 solver execution
→ FORML verification result
```
## RUN
```python
python -m demo.end_to_end_z3
```
## Demo cases
### Case 1 — Tautological property
```forml
model := "demo.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => x0.a <= 1 OR NOT x0.a <= 1 using Z3
```
Expected result:
```text
Solver status : unsat
FORML status  : proved
```
Why?

FORML verifies properties by refutation. It checks whether the negation of the
property is satisfiable.
```text
Γ ∧ ¬P
```
If this verification condition is UNSAT, then no counterexample exists and the
property is proved.

### Case 2 — Violable property
```forml
model := "demo.onnx"
target := MyTarget

[LOGIC]:
check_at x0 => x0.a <= 1 using Z3
```
Expected result:
```text
Solver status : sat
FORML status  : counterexample
```
Example counterexample:
```text
x0.a = 2
```
Why?

The property x0.a <= 1 is not always true. Z3 can find an assignment where the
property is false, so the verification condition is SAT.

## Current backend scope

The minimal Z3 backend currently targets:

- boolean logic;
- numeric comparisons;
- NNF / CNF / DNF formulas;
- affine model-output constraints;
- refutation-based verification.

The following are intentionally not part of the minimal backend yet:

- quantifier syntax;
- domain constraints;
- neighborhood constraints;
- problem predicates such as CLASSIFICATION.EQUAL();
- robustness-specific encodings.

---