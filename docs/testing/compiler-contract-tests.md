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
valid quantifier expression → QuantifierExprNode
valid RHS comparison → ComparisonNode
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
forall introduces _x
implicit attribute resolves to default entity
unknown explicit variable fails
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
comparison → ComparisonIR
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
- no backend-specific query is emitted yet.

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
