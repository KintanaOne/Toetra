
# Language Evolution Test Matrix

> Status: Accepted implementation gate  
> Scope: `forall <identifier>`, `exists <identifier>`, typed domains and scalar arithmetic  
> Rule: No implementation gate is complete until its mandatory tests pass

## Purpose

This matrix is the executable specification for the documentation-first language evolution.

It defines:

- test identifiers;
- layer ownership;
- expected acceptance or rejection;
- minimum artifact invariants;
- the order in which code should be changed.

---

## Gate G1 — EBNF and Parser

| ID | Case | Expected |
|---|---|---|
| PAR-Q-001 | `forall x0 => ...` | parse |
| PAR-Q-002 | `exists candidate => ...` | parse |
| PAR-Q-003 | `forall => ...` | parser rejection |
| PAR-Q-004 | `exists => ...` | parser rejection |
| PAR-DOM-001 | `with domain(x0.a: [0, 3])` | parse |
| PAR-DOM-002 | `]0, 3]` | parse |
| PAR-DOM-003 | `[0, 3[` | parse |
| PAR-DOM-004 | `]0, 3[` | parse |
| PAR-DOM-005 | `{0, 7}` | parse |
| PAR-DOM-006 | `{EU, US}` | parse |
| PAR-DOM-007 | `domain()` | parser rejection |
| PAR-DOM-008 | `{}` | parser rejection |
| PAR-DOM-009 | `(0, 3]` | parser rejection |
| PAR-ARI-001 | `a + b * 2 <= target` | parse with precedence |
| PAR-ARI-002 | `-a + b <= target` | parse unary sign |
| PAR-ARI-003 | `(a + b) * 2 <= target` | parse parentheses |
| PAR-ARI-004 | `a / b <= target` | parse; support decided later |

### G1 invariant

The CST preserves:

- quantified identifier token;
- interval opening and closing kinds;
- finite-set values and order;
- arithmetic operator hierarchy;
- parenthesized grouping.

---

## Gate G2 — AST and Builder

| ID | Case | Expected AST invariant |
|---|---|---|
| AST-Q-001 | `forall x0` | `QuantifierExprNode(quantifier=FORALL, variable="x0")` |
| AST-Q-002 | `exists candidate` | variable preserved exactly |
| AST-DOM-001 | `[0, 3]` | typed interval, CLOSED/CLOSED |
| AST-DOM-002 | `]0, 3[` | typed interval, OPEN/OPEN |
| AST-DOM-003 | `{EU, US}` | typed finite set with symbolic literals |
| AST-DOM-004 | multiple entries | ordered typed constraints, not raw strings |
| AST-ARI-001 | `a + b * 2` | `ADD(a, MUL(b, 2))` |
| AST-ARI-002 | `a - b - c` | `SUB(SUB(a, b), c)` |
| AST-ARI-003 | `-a` | unary node, not negative string |
| AST-CMP-001 | `a + 1 <= target - 2` | two scalar-expression operands |

### G2 invariant

The builder removes syntax noise but does not bind symbols, infer backend support or flatten expression trees.

---

## Gate G3 — Semantic Binding and Typing

| ID | Case | Expected |
|---|---|---|
| SEM-Q-001 | `forall x0 => x0.a <= 3` | explicit binding succeeds |
| SEM-Q-002 | `forall x0 => a <= 3` | implicit `a → x0.a` |
| SEM-Q-003 | `forall x0 => y.a <= 3` | reject mismatched entity |
| SEM-Q-004 | `forall x0 => target <= 7` | valid target-only assertion |
| SEM-DOM-001 | `x0.a: [0, 3]` | subject binding succeeds |
| SEM-DOM-002 | `a: [0, 3]` | reject implicit subject |
| SEM-DOM-003 | `y.a: [0, 3]` | reject entity mismatch |
| SEM-DOM-004 | duplicate `x0.a` | reject duplicate subject |
| SEM-DOM-005 | `[3, 0]` | reject reversed interval |
| SEM-DOM-006 | `]3, 3[` | reject empty interval |
| SEM-DOM-007 | `[0, target]` | reject target in domain |
| SEM-ARI-001 | numeric affine expression | type and classify affine |
| SEM-ARI-002 | numeric symbolic product | valid, classify nonlinear |
| SEM-ARI-003 | symbolic denominator | valid; classify symbolic-division requirement |
| SEM-ARI-004 | literal division by zero | reject |
| SEM-ARI-005 | string feature plus number | reject type mismatch |

### G3 invariant

Every feature reference is resolved exactly once. Explicit mismatches are errors; no single-variable alias fallback may repair them.

---

## Gate G4 — IR1

| ID | Case | Expected IR1 invariant |
|---|---|---|
| IR1-Q-001 | `forall x0` | quantifier and variable preserved |
| IR1-DOM-001 | open/closed interval | typed boundary kinds preserved |
| IR1-DOM-002 | finite set | member values and dtypes preserved |
| IR1-ARI-001 | arithmetic assertion | recursive scalar IR preserved |
| IR1-ARI-002 | arithmetic bound | recursive scalar IR in DomainIR |
| IR1-CMP-001 | expression comparison | left/right symmetric scalar IR |
| IR1-TGT-001 | `target` | resolved `_model.<header target>` |

### G4 invariant

IR1 contains no unresolved DSL entity and no backend-native object.

---

## Gate G5 — IR2 and Aggregation

| ID | Case | Expected |
|---|---|---|
| IR2-DOM-001 | `[0, 3]` | `x >= 0 ∧ x <= 3`, source=DOMAIN |
| IR2-DOM-002 | `]0, 3[` | `x > 0 ∧ x < 3`, source=DOMAIN |
| IR2-DOM-003 | `{0, 7}` | `x == 0 ∨ x == 7`, source=DOMAIN |
| IR2-DOM-004 | `{EU, US}` | finite-set atom/disjunction plus categorical requirement |
| IR2-ARI-001 | arithmetic comparison | remains one logical atom during CNF/DNF |
| IR2-REQ-001 | affine expression | `requires_affine_arithmetic` |
| IR2-REQ-002 | symbolic product | `requires_nonlinear_arithmetic` |
| IR2-REQ-003 | symbolic categories | categorical capability requirement |
| AGG-Q-001 | `forall` | `Γdomain ∧ Γmodel ∧ ¬P` |
| AGG-Q-002 | `exists` | `Γdomain ∧ Γmodel ∧ P` |
| AGG-PROV-001 | expanded interval | lower/upper atoms trace to one domain entry |

### G5 invariant

Logical normalization may change boolean grouping and polarity, but it must not decompose or algebraically rewrite scalar expressions without a dedicated sound transformation.

---

## Gate G6 — Backend Boundary

| ID | Requirement | Initial Z3 profile expectation |
|---|---|---|
| BE-001 | affine numeric arithmetic | accept |
| BE-002 | numeric open/closed bounds | accept |
| BE-003 | numeric finite-set membership | accept |
| BE-004 | nonlinear symbolic product | reject explicitly if unsupported |
| BE-005 | symbolic division | reject explicitly if unsupported |
| BE-006 | symbolic categories | reject explicitly until categorical encoding exists |
| BE-007 | unsupported request | no silent approximation or fallback |

### G6 invariant

Capability mismatch is reported before solver execution.

---

## Gate G7 — End-to-End Solver Semantics

| ID | Semantics | Solver result | Expected FORML result |
|---|---|---|---|
| E2E-FORALL-001 | universal refutation | UNSAT | VERIFIED |
| E2E-FORALL-002 | universal refutation | SAT | COUNTEREXAMPLE with valuation |
| E2E-FORALL-003 | universal refutation | UNKNOWN | UNKNOWN |
| E2E-EXISTS-001 | existential witness | SAT | WITNESS with valuation |
| E2E-EXISTS-002 | existential witness | UNSAT | NO_WITNESS |
| E2E-EXISTS-003 | existential witness | UNKNOWN | UNKNOWN |
| E2E-VAC-001 | universal + empty admissible set | UNSAT | VERIFIED_WITH_VACUITY_WARNING or equivalent structured warning |

---

## Mandatory Initial End-to-End Fixtures

### Numeric universal proof

```forml
model := "linear.joblib"
target := score

[BOUND]:
forall x0
    with domain(
        x0.a: [0.0, 3.0],
        x0.b: ]0.0, 2.0]
    )
    => target <= 7
    using Z3
```

### Numeric universal counterexample

Same model/domain with a deliberately false target bound.

### Numeric existential witness

```forml
model := "linear.joblib"
target := score

[LOGIC]:
exists x0
    with domain(x0.a: [0.0, 3.0])
    => target >= 2
    using Z3
```

### Numeric existential absence

Same model/domain with an impossible target threshold.

### Capability rejection

A valid nonlinear or categorical request reaching backend routing and receiving a structured unsupported diagnostic.

---

## Implementation Order

```text
1. Update EBNF and Lark grammar; add G1 tests.
2. Update AST node model and builder; add G2 tests.
3. Update semantic scope, binding, domain and type validation; add G3 tests.
4. Generalize IR1 scalar and domain representations; add G4 tests.
5. Expand domains to IR2 assumptions and requirements; add G5 tests.
6. Extend backend capabilities and Z3 translation for the initial numeric affine profile; add G6 tests.
7. Add universal/existential result interpretation and G7 end-to-end tests.
```

At every step, the existing suite must remain green or failures must be explicitly migrated with a documented compatibility decision.
