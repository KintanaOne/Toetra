# Language Evolution Test Matrix

> Status: Implemented and regression-locked through G7  
> Scope: Explicit quantifiers, typed domains, scalar arithmetic and specification constants  
> Rule: No implementation gate is complete until its mandatory tests pass

## Purpose

This matrix is the executable specification for the documentation-first language evolution.

It defines:

- test identifiers;
- layer ownership;
- expected acceptance or rejection;
- minimum artifact invariants;
- the order in which code should be changed.

## Complete-Program Rule

Every parser, builder-from-source, semantic-from-source and pipeline test must use a complete `.toetra` program containing at least the required `model` and `target` declarations plus one property.

The short expressions shown in matrix tables are case labels, not standalone parser inputs. Fragment tests are limited to lexer, generator and pure helper responsibilities.

---

## Gate G1 — EBNF and Parser

| ID | Case label | Expected |
|---|---|---|
| PAR-Q-001 | `forall x0` | complete program parses |
| PAR-Q-002 | `exists candidate` | complete program parses |
| PAR-Q-003 | missing identifier after `forall` | parser rejection |
| PAR-Q-004 | missing identifier after `exists` | parser rejection |
| PAR-DOM-001 | `[0, 3]` | parse |
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
| PAR-SPC-001 | integer/float/bool/string declarations | parse |
| PAR-SPC-002 | multiple declarations | preserve source order in CST |
| PAR-SPC-003 | bare constant name in assertion | parse without resolution |
| PAR-SPC-004 | constant in domain bound and finite set | parse |
| PAR-SPC-005 | non-literal declaration RHS | parser rejection in initial profile |
| PAR-SPC-006 | missing declaration value | parser rejection |

### G1 invariant

The CST preserves:

- quantified identifier token;
- interval opening and closing kinds;
- finite-set values and order;
- arithmetic operator hierarchy;
- parenthesized grouping;
- specification-constant declaration order, names and literal token families;
- unresolved bare-name occurrences.

---

## Gate G2 — AST and Builder

| ID | Case label | Expected AST invariant |
|---|---|---|
| AST-Q-001 | `forall x0` | `QuantifierExprNode(quantifier=FORALL, variable="x0")` |
| AST-Q-002 | `exists candidate` | variable preserved exactly |
| AST-DOM-001 | `[0, 3]` | typed interval, CLOSED/CLOSED |
| AST-DOM-002 | `]0, 3[` | typed interval, OPEN/OPEN |
| AST-DOM-003 | `{EU, US}` | typed finite set with unresolved symbolic-capable members |
| AST-DOM-004 | multiple entries | ordered typed constraints, not raw strings |
| AST-ARI-001 | `a + b * 2` | `ADD(a, MUL(b, 2))` |
| AST-ARI-002 | `a - b - c` | `SUB(SUB(a, b), c)` |
| AST-ARI-003 | `-a` | unary node, not negative string |
| AST-CMP-001 | `a + 1 <= target - 2` | two scalar-expression operands |
| AST-SPC-001 | declaration list | ordered `SpecificationConstantDeclarationNode` values in header |
| AST-SPC-002 | declaration literal | typed `ConstantNode` |
| AST-SPC-003 | bare scalar name | `NameRefNode`, not implicit feature |
| AST-SPC-004 | `x0.threshold` | explicit `AttributeNode` |

### G2 invariant

The builder removes syntax noise but does not bind symbols, resolve `NameRefNode`, infer backend support or flatten expression trees.

---

## Gate G3 — Semantic Binding and Typing

| ID | Case label | Expected |
|---|---|---|
| SEM-Q-001 | explicit matching entity | binding succeeds |
| SEM-Q-002 | implicit assertion feature | resolves through default entity |
| SEM-Q-003 | explicit mismatched entity | reject |
| SEM-Q-004 | target-only assertion | valid |
| SEM-DOM-001 | explicit matching subject | succeeds |
| SEM-DOM-002 | implicit domain subject | reject |
| SEM-DOM-003 | mismatched domain entity | reject |
| SEM-DOM-004 | duplicate subject | reject |
| SEM-DOM-005 | reversed interval | reject |
| SEM-DOM-006 | empty interval | reject |
| SEM-DOM-007 | target in domain | reject |
| SEM-ARI-001 | numeric affine expression | type and classify affine |
| SEM-ARI-002 | numeric symbolic product | valid, classify nonlinear |
| SEM-ARI-003 | symbolic denominator | valid, classify symbolic division |
| SEM-ARI-004 | literal division by zero | reject |
| SEM-ARI-005 | non-numeric arithmetic | reject |
| SEM-SPC-001 | unique declarations | register globally |
| SEM-SPC-002 | duplicate declaration | reject |
| SEM-SPC-003 | reserved declaration name | reject |
| SEM-SPC-004 | collision with scope variable | reject |
| SEM-SPC-005 | bare name matching constant | resolve constant before implicit feature |
| SEM-SPC-006 | bare name without matching constant in assertion | implicit feature fallback |
| SEM-SPC-007 | explicit qualified feature | always feature |
| SEM-SPC-008 | constant in domain bound | resolve constant |
| SEM-SPC-009 | unknown bare domain-bound name | reject; no implicit feature fallback |
| SEM-SPC-010 | finite-set declared name | resolve constant |
| SEM-SPC-011 | finite-set undeclared identifier | symbolic categorical literal |
| SEM-SPC-012 | incompatible constant use | reject by type validation |

### G3 invariant

Every name is classified exactly once. The semantic layer, not the builder, applies the resolution priority:

```text
specification constant
→ implicit feature where allowed
→ error
```

---

## Gate G4 — IR1

| ID | Case label | Expected IR1 invariant |
|---|---|---|
| IR1-Q-001 | quantified scope | quantifier and variable preserved |
| IR1-DOM-001 | interval | typed boundary kinds preserved |
| IR1-DOM-002 | finite set | members and dtypes preserved |
| IR1-ARI-001 | arithmetic assertion | recursive scalar IR preserved |
| IR1-ARI-002 | arithmetic bound | recursive scalar IR in DomainIR |
| IR1-CMP-001 | expression comparison | symmetric scalar operands |
| IR1-TGT-001 | `target` | resolved `_model.<header target>` |
| IR1-SPC-001 | resolved constant reference | constant-valued scalar IR |
| IR1-SPC-002 | constant provenance | value, dtype and source name preserved |
| IR1-SPC-003 | unresolved name | forbidden in IR1 |

### G4 invariant

IR1 contains no unresolved DSL entity, no `NameRefNode` and no backend-native object.

---

## Gate G5 — IR2 and Aggregation

| ID | Case label | Expected |
|---|---|---|
| IR2-DOM-001 | `[0, 3]` | `x >= 0 ∧ x <= 3`, source=DOMAIN |
| IR2-DOM-002 | `]0, 3[` | `x > 0 ∧ x < 3`, source=DOMAIN |
| IR2-DOM-003 | `{0, 7}` | membership disjunction, source=DOMAIN |
| IR2-DOM-004 | `{EU, US}` | categorical requirement |
| IR2-ARI-001 | arithmetic comparison | remains one logical atom |
| IR2-REQ-001 | affine expression | affine requirement |
| IR2-REQ-002 | symbolic product | nonlinear requirement |
| IR2-REQ-003 | symbolic categories | categorical requirement |
| IR2-SPC-001 | constant in assertion | remains constant in atom |
| IR2-SPC-002 | constant in domain bound | domain and declaration provenance retained |
| AGG-Q-001 | `forall` | `Γdomain ∧ Γmodel ∧ ¬P` |
| AGG-Q-002 | `exists` | `Γdomain ∧ Γmodel ∧ P` |
| AGG-PROV-001 | expanded interval | atoms trace to domain entry |

### G5 invariant

Logical normalization may change boolean grouping and polarity, but it must not lose scalar or specification-constant provenance.

---

## Gate G6 — Backend Boundary

| ID | Requirement | Initial Z3 profile expectation |
|---|---|---|
| BE-001 | affine numeric arithmetic | accept |
| BE-002 | numeric open/closed bounds | accept |
| BE-003 | numeric finite-set membership | accept |
| BE-004 | nonlinear symbolic product | reject explicitly if unsupported |
| BE-005 | symbolic division | reject explicitly if unsupported |
| BE-006 | symbolic categories | reject explicitly until encoding exists |
| BE-SPC-001 | numeric specification constant | encode as literal, not solver variable |
| BE-SPC-002 | bool/string constant | capability-aware encoding or explicit rejection |
| BE-007 | unsupported request | no silent approximation or fallback |

### G6 invariant

Capability mismatch is reported before solver execution, and immutable specification constants never become unconstrained solver variables.

---

## Gate G7 — End-to-End Solver Semantics

| ID | Semantics | Solver result | Expected FORML result |
|---|---|---|---|
| E2E-FORALL-001 | universal refutation | UNSAT | PROVED |
| E2E-FORALL-002 | universal refutation | SAT | COUNTEREXAMPLE with valuation |
| E2E-FORALL-003 | universal refutation | UNKNOWN | UNKNOWN |
| E2E-EXISTS-001 | existential witness | SAT | WITNESS with valuation |
| E2E-EXISTS-002 | existential witness | UNSAT | NO_WITNESS |
| E2E-EXISTS-003 | existential witness | UNKNOWN | UNKNOWN |
| E2E-SPC-001 | universal property using numeric threshold constant | UNSAT/SAT | result matches substituted literal semantics |
| E2E-SPC-002 | same constant reused across properties | per property | same global value and provenance |
| E2E-VAC-001 | universal + empty admissible set | UNSAT | structured vacuity warning |

## Mandatory Initial End-to-End Fixture with Constants

```toetra
model := "linear.joblib"
target := score

max_score := 7.0
minimum_a := 0.0
maximum_a := 3.0

[BOUND]:
forall x0
    with domain(
        x0.a: [minimum_a, maximum_a]
    )
    => target <= max_score
    using Z3
```

The fixture must prove that `minimum_a`, `maximum_a` and `max_score` are substituted as typed literals while retaining declaration provenance.

## Implementation Order

```text
1. G1 baseline: explicit quantifiers, typed domains and arithmetic parser tests.
2. G1.1: specification-constant EBNF/parser tests in a dedicated file.
3. G2: unified AST and builder changes, including declarations and NameRefNode.
4. G3: registration, contextual name resolution, binding and typing.
5. G4: IR1 scalar/domain lowering plus constant provenance.
6. G5: domain assumptions, requirements and aggregation.
7. G6: backend capabilities and initial numeric affine encoding.
8. G7: universal/existential result interpretation and end-to-end tests.
```

At every step, previous suites remain green. Exact specification-constant file organization is defined in [Specification Constants Test Plan](specification-constants-tests.md).

## Completion Record

Patches 01 through 08 implement and test all gates in this matrix for the initial numeric-affine Z3 profile. `UNKNOWN` interpretation is tested through the runner contract because a deterministic end-to-end source fixture cannot force Z3 to return `unknown` without backend resource controls. Vacuity is tested with inconsistent aggregated assumptions and produces the structured `Z3_VACUOUS_PROOF` warning.

The mandatory affine fixture is frozen as a golden contract under:

```text
test/fixtures/end_to_end/cases/affine_specification_constants.toetra
test/fixtures/end_to_end/expected/affine_specification_constants.json
```
