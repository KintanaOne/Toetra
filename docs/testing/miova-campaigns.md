# Miova Campaigns

> Status: P0 — planned / critical  
> Implementation: external integration planned  
> Scope: mutation-driven validation of Toetra artifacts

## Purpose

Miova campaigns challenge Toetra by mutating artifacts across the pipeline.

The purpose is not to replace unit tests or contract tests. Miova is used to explore
whether Toetra remains robust when artifacts are modified, corrupted, simplified, or
semantically challenged.

## Position in the Testing Strategy

Miova is a transversal testing layer.

```text
Source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ ModelSchema
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

Miova can mutate artifacts at several points, but it is not part of the normal runtime
verification path.

## Campaign Goals

Miova campaigns should answer questions such as:

- Does the parser reject malformed source mutations?
- Does the builder reject structurally invalid CST mutations?
- Does the semantic layer reject invalid bindings?
- Does IR1 preserve semantic resolution under valid transformations?
- Does IR2 maintain normal-form invariants?
- Does the schema-semantic boundary detect feature mismatch?
- Does aggregation detect incompatible constraints?
- Does lowering preserve or explicitly track logical meaning?
- Does backend boundary reject unsupported encodings?

## Artifact Kinds

Recommended Toetra artifact kinds for Miova:

| Artifact Kind | Layer |
|---|---|
| `toetra.source` | source string |
| `toetra.cst` | parsed CST |
| `toetra.ast` | syntax AST |
| `toetra.semantic_ast` | semantic-validated AST |
| `toetra.ir1` | IR1 logical representation |
| `toetra.ir2` | IR2 normal form |
| `toetra.model_schema` | normalized model schema |
| `toetra.model_constraints` | model-derived constraints |
| `toetra.aggregated_assertions` | aggregated verification problem |
| `toetra.lowered_query` | minimized/lowered query |
| `toetra.backend_query` | backend-specific query |

## Campaign Types

### 1. Syntax Mutation Campaigns

Target:

```text
toetra.source
```

Examples:

- remove `model :=`;
- corrupt property brackets;
- replace `=>` with another operator;
- remove a closing parenthesis;
- mutate backend syntax.

Expected result:

```text
Parser rejects invalid syntax.
Valid syntax-preserving mutations continue to next layer.
```

### 2. AST Mutation Campaigns

Target:

```text
toetra.ast
```

Examples:

- remove `PropertyRuleNode`;
- replace `AtExprNode` with incompatible scope;
- remove assertion root;
- flip property type;
- corrupt backend name.

Expected result:

```text
Builder or semantic contracts detect invalid structure or incompatibility.
```

### 3. Semantic Mutation Campaigns

Target:

```text
toetra.semantic_ast
```

Examples:

- remove semantic annotations;
- corrupt resolved entity;
- remove symbol table entry;
- change scope type;
- change default entity.

Expected result:

```text
Semantic-to-IR contract rejects unresolved or inconsistent artifacts.
```

### 4. IR1 Mutation Campaigns

Target:

```text
toetra.ir1
```

Examples:

- flip comparison operator;
- introduce nested negation;
- replace `AndIR` with `OrIR`;
- remove scope variables;
- remove query expression.

Expected result:

```text
IR1 invariants or IR1-to-IR2 contracts detect invalid logical structure.
```

### 5. IR2 Mutation Campaigns

Target:

```text
toetra.ir2
```

Examples:

- break CNF clause structure;
- break DNF case structure;
- introduce backend-specific constructs too early;
- remove equivalence/equisatisfiability metadata.

Expected result:

```text
IR2 normal-form invariants fail.
```

### 6. ModelSchema Mutation Campaigns

Target:

```text
toetra.model_schema
```

Examples:

- remove a feature;
- change feature dtype;
- change task from classification to regression;
- remove target;
- corrupt framework metadata.

Expected result:

```text
Schema-semantic validation detects mismatch.
```

### 7. Aggregation Mutation Campaigns

Target:

```text
toetra.aggregated_assertions
```

Examples:

- remove model constraints;
- duplicate contradictory constraints;
- erase origin metadata;
- mix constraints from incompatible scopes.

Expected result:

```text
Aggregation or lowering detects inconsistency or traceability violation.
```

### 8. Backend Boundary Campaigns

Target:

```text
toetra.backend_query
```

Examples:

- use unsupported backend operator;
- use unsupported property/backend pair;
- remove required backend metadata;
- corrupt solver-specific expression.

Expected result:

```text
Backend boundary rejects the query before execution.
```

## Campaign Output

Each Miova campaign should produce:

| Output | Meaning |
|---|---|
| success count | mutations accepted as valid |
| skipped count | mutations not applicable |
| rejected count | mutations correctly rejected |
| failed count | unexpected failures |
| rejection layer | layer that rejected mutation |
| invariant failures | violated invariants |
| contract failures | violated contracts |
| examples | representative mutated artifacts |

## Expected Failure Classification

Miova should distinguish:

```text
SUCCESS
SKIPPED
REJECTED
FAILED
```

In Toetra context:

| Status | Meaning |
|---|---|
| SUCCESS | mutation produced a valid artifact accepted by pipeline |
| SKIPPED | mutation was not applicable |
| REJECTED | mutation violated a known contract or invariant |
| FAILED | mutation produced an unexpected runtime or unclassified error |

## Campaign Seeds

Campaigns should start from golden samples.

Recommended seed types:

- minimal valid property;
- local robustness;
- pointwise bound;
- pairwise monotonicity;
- quantifier property;
- logical composition;
- model-backed source;
- invalid known examples.

## Campaign Depth

Initial campaigns should use shallow mutations:

```text
depth = 1
```

Later campaigns can explore pipelines:

```text
source mutation → parse → AST mutation → semantic mutation → IR mutation
```

## Success Criteria

Miova campaigns are useful when:

- they find real weaknesses in layer boundaries;
- they classify expected rejections cleanly;
- they do not produce noise by mutating impossible artifacts;
- they can reproduce failures;
- they improve confidence in compiler evolution;
- they make Toetra robust against future refactors.

---

## Language Evolution Mutation Seeds

Miova campaigns should seed from the normative examples and apply mutations such as:

| Mutation | Expected classification |
|---|---|
| remove quantified identifier | REJECTED at parser |
| rename declaration but not references | REJECTED at semantic binding |
| remove entity qualifier from domain subject | REJECTED at semantic domain validation |
| flip one interval boundary | SUCCESS with changed domain semantics |
| reverse interval endpoints | REJECTED at semantic domain validation |
| duplicate domain entry | REJECTED at semantic domain validation |
| replace numeric finite member with symbolic member | SUCCESS with changed capability requirements |
| replace constant multiplier with feature reference | SUCCESS, reclassified nonlinear |
| replace constant denominator with zero | REJECTED semantically |
| erase DOMAIN provenance after expansion | REJECTED by IR2/aggregation invariant |
| change universal semantics to existential without changing task metadata | REJECTED by aggregation invariant |

Successful semantics-changing mutations must record lineage and changed requirements; they must not be reported as equivalent transformations.
