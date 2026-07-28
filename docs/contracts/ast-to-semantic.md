# AST to SemanticValidatedAST Contract

> Status: Implemented and accepted semantics
> Scope: Scope construction, binding, typing and semantic validation  
> Audience: semantic maintainers, compiler authors and diagnostic authors

## Purpose

This boundary answers:

```text
What does the typed syntax mean in this Toetra scope and model context?
```

---

## Input and Output

```text
Input:  structurally valid ProgramNode / PropertyNode
Output: SemanticValidatedAST + SemanticContext
```

The current implementation may represent the output as AST nodes enriched by semantic annotations. The guarantees remain the same.

---

## Semantic Pass Order

```text
scope validation
→ symbol registration
→ domain binding
→ assertion binding
→ recursive scalar typing
→ domain validity
→ property/scope compatibility
→ model-schema compatibility when available
→ requirement classification
```

A concrete implementation may merge passes, but diagnostic ownership and postconditions remain explicit.

---

## Quantified Binding Algorithm

For:

```toetra
forall x0
```

semantic validation must:

1. create exactly one symbolic scope variable named `x0`;
2. register `x0` in the symbol table;
3. preserve quantifier kind `FORALL`;
4. set `x0` as the default input entity;
5. resolve `x0.feature` to that symbol;
6. resolve unqualified assertion features to `x0.feature`;
7. reject any explicit unknown entity such as `y.feature`;
8. disable single-variable alias fallback for explicit entity names;
9. resolve `target` through the header/model-output namespace;
10. preserve source and resolved paths for diagnostics.

The same rules apply to `exists x0`, with quantifier kind `EXISTS` preserved for later verification semantics.

An assertion is not required to mention the quantified identifier textually:

```toetra
forall x0 => target <= 7
```

remains valid when the model assumptions connect `x0` and `target`.

---

## Domain Semantic Rules

For each domain entry, semantic validation must:

- require an explicitly qualified input subject;
- resolve the subject entity to a variable declared by the scope;
- reject implicit subjects;
- reject unknown or mismatched entities;
- reject `target` as subject;
- reject duplicate resolved subjects;
- recursively bind feature references inside arithmetic bounds;
- require bound references to use declared scope entities;
- reject `target` inside bounds;
- validate finite-set literal compatibility;
- preserve boundary and literal kinds;
- validate constant-foldable interval ordering and emptiness;
- treat entries as simultaneous constraints.

A symbolic interval whose emptiness cannot be decided locally may pass semantic validation and later produce a satisfiability/vacuity diagnostic.

---

## Recursive Scalar Binding

The validator walks both comparison operands recursively.

For every scalar leaf:

- input attributes receive resolved entity/path/symbol metadata;
- `target` receives resolved model-output metadata;
- constants retain scalar type and literal kind.

For every arithmetic node:

- operand types are validated;
- result type is inferred;
- numeric promotion is canonical;
- a literal zero denominator is rejected;
- expression requirements are classified.

---

## Type Rules

### Arithmetic

Arithmetic operators require numeric operands.

The initial canonical promotion is:

```text
INT op INT     → INT, except `/`
INT op REAL    → REAL
REAL op INT    → REAL
REAL op REAL   → REAL
numeric `/`    → REAL unless a future exact rational type is explicit
```

Boolean, string, null and symbolic-category values are not arithmetic operands.

### Comparison

- equality/inequality require compatible scalar categories;
- `<`, `<=`, `>`, `>=` require ordered compatible types;
- numeric comparison uses canonical promotion;
- symbolic categories support equality/inequality only unless an ordering is explicitly declared.

---

## Requirement Classification

Successful semantic validation classifies, without backend choice:

- scalar sorts required;
- affine arithmetic usage;
- nonlinear multiplication usage;
- symbolic division usage;
- finite-set membership;
- categorical symbolic literals;
- interval assumptions;
- model-output references.

Classification is metadata for IR requirements. It is not permission to execute the construct.

---

## Postconditions

After success:

- no input reference is unresolved;
- no target reference is ambiguous;
- all arithmetic nodes have compatible inferred types;
- every domain subject is exactly bound;
- domain structural meaning is preserved;
- quantifier kind and variable identity are preserved;
- IR1 lowering requires no alias guess or type guess.

---

## Semantic-Owned Failures

This boundary owns:

- unbound explicit entity;
- quantified identifier mismatch in assertion/domain;
- implicit domain subject;
- duplicate domain subject;
- target used in input domain;
- incompatible finite-set members;
- non-numeric arithmetic;
- literal division by zero;
- statically empty/reversed interval;
- incompatible comparison types;
- property/scope incompatibility;
- missing model feature when schema-aware validation is active.

Unsupported backend capability is not a semantic error when the expression is otherwise meaningful.

## Specification Constant Resolution Addendum

This boundary additionally guarantees:

- all specification constants are registered before property binding;
- duplicate and reserved declaration names are rejected;
- scope/constant collisions are rejected;
- every `NameRefNode` is resolved according to its syntactic context;
- resolved constants expose value, type, symbol and provenance;
- implicit-feature fallback occurs only where the language contract allows it;
- finite-set symbolic literals are not mistaken for unresolved scalar names.

A valid SemanticValidatedAST contains no semantically unclassified bare scalar reference.


## Patch 21.3 Output-Observable Addendum

The semantic boundary now additionally guarantees:

- `ModelOutputRefNode` binds to the declared output port and exact point;
- `PredictedLabelObservableNode` binds only to classification outputs and receives
  the schema label dtype;
- `ClassProbabilityObservableNode` binds only when class probabilities are
  available and receives `FLOAT` dtype;
- probability label arguments match the schema dtype and one canonical label by
  type-safe value identity;
- one `(model, point, output)` evaluation is interned across all observables;
- bare classification `target` is rejected with the two legal explicit forms;
- predicted-label arithmetic and ordering are rejected before IR1;
- regression bare-target behavior remains unchanged.

The semantic annotation preserves observable kind and resolved label for P21.4.
It does not introduce a logit, decision function, framework class index, affine
quantity, or backend symbol.
