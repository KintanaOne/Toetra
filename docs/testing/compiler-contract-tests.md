# Compiler Contract Tests

> Status: P0 — required  
> Implementation: planned / partially implemented  
> Scope: compiler and model pipeline boundaries

## Purpose

Compiler contract tests validate the boundaries between FORML layers.

A contract test does not only ask whether a function returns something. It asks whether
a layer accepts the right input, produces the right output, preserves the required
information, and rejects invalid artifacts at the expected boundary.

## Contract Testing Philosophy

FORML is a progressive formalization pipeline. Each layer strengthens or transforms the
artifact it receives.

```text
Source
→ CST
→ AST
→ SemanticValidatedAST
→ IR1
→ IR2
→ AggregatedAssertionSet
→ LoweredQuery
→ BackendQuery
```

Contract tests ensure that each arrow is meaningful and stable.

## Contract Test Template

Each contract test should define:

| Field | Meaning |
|---|---|
| contract | Name of the boundary |
| input artifact | Artifact accepted by the layer |
| output artifact | Artifact produced by the layer |
| preconditions | What must be true before transformation |
| postconditions | What must be true after transformation |
| preserved information | What must survive the transformation |
| rejected cases | What must fail |
| expected error | Error class/category expected on failure |
| mutation targets | Miova artifacts relevant to this boundary |

## Source → CST

### Input

```text
.forml source string
```

### Output

```text
Lark CST
```

### Guarantees

- valid syntax produces a CST;
- invalid syntax fails at parser boundary;
- comments and whitespace are ignored according to grammar;
- no AST construction occurs here.

### Tests

```text
valid source → CST
invalid missing header → parser failure
invalid property syntax → parser failure
multiple properties → one program CST
comments do not alter structure
```

## CST → AST

### Input

```text
Lark CST
```

### Output

```text
ProgramNode
```

### Guarantees

- header is converted into `HeaderNode`;
- property sections become `PropertyNode`;
- LHS scope is explicit;
- RHS assertion is a logical AST;
- backend declaration is parsed when present;
- missing required CST nodes fail early.

### Tests

```text
valid CST → ProgramNode
missing model declaration → build failure
missing target declaration → build failure
valid at expression → AtExprNode
valid pairwise expression → PairwiseExprNode
valid check_at expression → CheckAtExprNode
valid `forall x0` expression → QuantifierExprNode(variable="x0")
valid RHS comparison → ComparisonNode
valid arithmetic comparison → symmetric expression tree
arithmetic precedence → expected unary/binary AST shape
valid problem expression → ProblemNode
```

## AST Contract

### Artifact

```text
ProgramNode
```

### Guarantees

- AST is syntax-oriented, not backend-oriented;
- AST preserves user-level structure;
- AST does not perform solver encoding;
- semantic annotations may be absent before semantic validation;
- AST nodes are stable inputs for semantic validation.

### Tests

```text
AST contains header and body
each property has type, rule, backend
each rule has scope and assertion
logical tree preserves parentheses/precedence
primitive values have inferred dtype
scalar-expression nodes preserve operator precedence and operand order
comparison nodes contain two scalar-expression operands
```

## AST → SemanticValidatedAST

### Input

```text
ProgramNode
```

### Output

```text
ProgramNode enriched with SemanticAnnotations
```

### Guarantees

- LHS produces `SemanticContext`;
- variables are registered in `SymbolTable`;
- implicit attributes are resolved;
- property/scope compatibility is checked;
- invalid binding fails here;
- invalid problem/function compatibility fails here.

### Tests

```text
at scope introduces x and x'
check_at uses x as default entity
pairwise requires x ~ x'
forall x0 introduces x0 as symbolic variable
implicit attribute resolves to quantified default entity
matching explicit quantified variable succeeds
mismatched explicit quantified variable fails
typed domain subjects bind to declared scope variables
implicit domain subject fails
interval boundaries and finite-set literals are preserved
duplicate/reversed/empty domains fail at documented boundaries
target-only quantified assertion remains valid
arithmetic feature references are recursively bound
non-numeric arithmetic fails type validation
literal-zero division fails semantic validation
target inside domain bounds fails semantic validation
unsupported property/scope combination fails
```

## SemanticValidatedAST → IR1

### Input

```text
SemanticValidatedAST
```

### Output

```text
IR1 VerificationTask
```

### Guarantees

- semantic bindings are preserved;
- LHS scope becomes `ScopeIR`;
- RHS expression becomes `QueryIR`;
- logical structure becomes backend-independent `LogicalIR`;
- IR1 applies or prepares early normalization such as implication handling, De Morgan, and NNF;
- no backend-specific encoding is performed.

### Tests

```text
local scope → ScopeIR(kind="local")
pointwise scope → ScopeIR(kind="pointwise")
pairwise scope → ScopeIR(kind="pairwise")
quantifier scope → ScopeIR(kind="quantifier")
typed domain → DomainIR with resolved constraints
comparison → ComparisonIR(left expression, operator, right expression)
arithmetic AST → recursive scalar IR
arithmetic domain bound → typed DomainIR expression
AND/OR/NOT/IMPLY → corresponding IR nodes or normalized forms
problem predicate → ProblemIR
```

## IR1 → IR2

### Input

```text
IR1 logical task
```

### Output

```text
IR2 normal-form artifact
```

### Target Guarantees

- CNF or DNF is selected according to verification need;
- semantic equivalence is preserved when possible;
- equisatisfiability is explicitly tracked when strict equivalence is not preserved;
- traceability to source assertions is preserved;
- no backend-specific query is emitted yet;
- arithmetic capability requirements remain explicit and traceable.

### Tests

```text
NNF input → CNF output
NNF input → DNF output
equivalence metadata is preserved
source assertion ids are retained
unsupported transformation fails explicitly
```

## Model → Schema

### Input

```text
model path + optional dataset/schema
```

### Output

```text
ModelSchema
```

### Guarantees

- loader is selected by model format;
- model is loaded;
- framework is detected;
- introspector produces normalized schema;
- unsupported formats/models fail at model boundary.

### Tests

```text
joblib model → ModelSchema
pkl model → ModelSchema
unsupported extension → model loading failure
unsupported framework → model detection failure
missing feature metadata → introspection failure
```

## Schema → Semantic

### Input

```text
ModelSchema + SemanticValidatedAST
```

### Output

```text
Schema-aware semantic artifact
```

### Target Guarantees

- referenced features exist in model schema;
- feature dtypes are compatible with constants/operators;
- target/task compatibility is checked;
- property/problem compatibility can use model task metadata.

### Tests

```text
property references existing feature → pass
property references missing feature → schema semantic failure
numeric comparison on string feature → type failure
classification predicate on regression model → compatibility failure
```

## Assertion Aggregation

### Input

```text
IR2 + semantic constraints + model constraints
```

### Output

```text
AggregatedAssertionSet
```

### Target Guarantees

- all constraints are composed into a coherent verification problem;
- constraint origins are preserved;
- contradictory constraints are detected when possible;
- aggregation remains backend-independent.

### Tests

```text
single property aggregation
multiple property aggregation
model constraints added
semantic constraints added
domain assumptions expanded with source=DOMAIN
open/closed interval operators preserved
finite-set disjunction preserved
origin metadata preserved
contradiction detected
```

## Lowering / Minimization

### Input

```text
AggregatedAssertionSet
```

### Output

```text
LoweredQuery
```

### Target Guarantees

- redundant assertions are simplified;
- equivalent constraints can be merged;
- backend-relevant shape is prepared;
- removed constraints are traceable;
- logical meaning is preserved or approximation is explicit.

### Tests

```text
duplicate assertion removed
tautology removed
contradiction retained as unsat diagnostic
simplification preserves traceability
```

## IR → Backend

### Input

```text
LoweredQuery + backend configuration
```

### Output

```text
BackendQuery
```

### Target Guarantees

- backend capabilities are checked;
- unsupported features fail before execution;
- backend query is deterministic;
- backend query preserves logical intent.

### Tests

```text
valid lowered query → Z3 query
unsupported property/backend pair → capability failure
unsupported operator → backend boundary failure
```

## Miova Contract Testing

Miova should be used to mutate artifacts at each boundary and verify that:

- valid mutations are accepted when contracts allow them;
- invalid mutations are rejected at the right layer;
- unexpected failures are classified;
- invariants hold across transformations.

## Success Criteria

Compiler contract tests are sufficient when every FORML boundary has:

- at least one valid path;
- at least one invalid path;
- one expected error case;
- one preservation check;
- one mutation scenario.

---

## Mandatory Quantified-Domain-Arithmetic Contract Suite

The implementation must include the stable test families defined below.

```text
test_parser_requires_quantified_identifier
test_parser_accepts_all_interval_boundary_combinations
test_parser_accepts_numeric_and_symbolic_finite_sets
test_parser_preserves_arithmetic_precedence

test_builder_preserves_quantified_identifier
test_builder_builds_typed_interval_boundaries
test_builder_builds_typed_finite_set
test_builder_builds_symmetric_scalar_comparison

test_semantic_binds_matching_quantified_entity
test_semantic_resolves_implicit_assertion_feature
test_semantic_rejects_mismatched_quantified_entity
test_semantic_requires_explicit_domain_subject
test_semantic_rejects_duplicate_domain_subject
test_semantic_rejects_invalid_or_empty_interval
test_semantic_rejects_target_in_domain
test_semantic_classifies_affine_and_nonlinear_arithmetic

test_ir1_preserves_scalar_expression_tree
test_ir1_preserves_typed_domain
test_ir2_expands_domain_with_domain_provenance
test_ir2_keeps_arithmetic_comparison_atomic

test_aggregation_builds_universal_refutation
test_aggregation_builds_existential_witness_search
test_router_rejects_unsupported_nonlinear_requirement
test_router_rejects_unsupported_categorical_requirement
```

Exact cases and acceptance boundaries are defined in [Language Evolution Test Matrix](language-evolution-test-matrix.md).


## Mandatory Specification-Constant Contract Suite

```text
test_parser_accepts_scalar_specification_constant_literals
test_parser_preserves_specification_constant_declaration_order
test_parser_rejects_non_literal_specification_constant_rhs

test_builder_builds_specification_constant_declarations
test_builder_builds_bare_scalar_name_as_name_ref
test_builder_keeps_qualified_feature_as_attribute_ref

test_semantic_registers_unique_specification_constants
test_semantic_rejects_duplicate_specification_constant
test_semantic_rejects_scope_variable_collision
test_semantic_resolves_constant_before_implicit_feature
test_semantic_falls_back_to_implicit_feature_in_assertion
test_semantic_requires_explicit_feature_in_domain_bound
test_semantic_distinguishes_constant_from_symbolic_finite_set_member
test_semantic_rejects_incompatible_specification_constant_use

test_ir1_substitutes_constant_value_with_provenance
test_ir1_contains_no_unresolved_name_ref
test_ir2_preserves_domain_and_constant_provenance
test_backend_encodes_specification_constant_as_literal
test_backend_does_not_create_variable_for_specification_constant
```

Every source-driven case uses a complete `.forml` program. The detailed split and fixture catalog are defined in [Specification Constants Test Plan](specification-constants-tests.md).
