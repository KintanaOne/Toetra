# ADR-0014 — Represent Comparisons as Relations Between Scalar Expressions

> Status: Accepted  
> Date: 2026-07  
> Scope: DSL assertions, arithmetic AST, IR1, requirements, and backend lowering

## Context

The initial comparison shape in FORML is asymmetric:

```text
attribute comparison_operator constant
```

This representation is sufficient for simple predicates such as:

```forml
x0.age >= 18
```

but it cannot express important behavioral relations such as:

```forml
x0.revenue - x0.cost >= 0
x0.a <= x0.b
2 * x0.a + x0.b <= target
```

Special-casing `target` on the left-hand side also duplicates grammar and builder logic while preventing target arithmetic or expression-to-expression comparisons.

FORML needs a language-level expression model that remains independent from a concrete solver and allows semantic and backend capability checks to occur at explicit boundaries.

## Decision

A comparison is represented as a relation between two scalar expressions:

```text
scalar_expression comparison_operator scalar_expression
```

The target AST family is conceptually:

```text
ScalarExpressionNode
├── ConstantNode
├── AttributeNode
├── TargetRefNode
├── UnaryArithmeticNode
└── BinaryArithmeticNode
```

and a comparison becomes:

```text
ComparisonNode(
    left: ScalarExpressionNode,
    op: EnumComparisonOperator,
    right: ScalarExpressionNode,
)
```

The corresponding IR1 representation must preserve the expression tree in a backend-independent form.

### Scalar-expression leaves

The initial scalar leaves are:

- numeric, boolean, string, and null constants where semantically valid;
- explicit or implicit input-feature references;
- the model output reference `target`;
- parenthesized scalar expressions.

Only numeric expressions may participate in arithmetic operators.

### Arithmetic operators

The target language recognizes:

```text
unary +
unary -
+
-
*
/
```

Precedence from strongest to weakest is:

```text
parentheses
unary arithmetic
multiplication and division
addition and subtraction
comparison
NOT
AND
OR
logical implication
```

Arithmetic operators are structurally represented even when a selected backend cannot execute every expression family.

### Comparison rules

Comparisons are non-associative. Chained comparisons such as:

```forml
0 <= x0.a <= 3
```

are rejected. They must be expressed with boolean conjunction:

```forml
0 <= x0.a AND x0.a <= 3
```

Equality and inequality may compare compatible scalar types. Ordering comparisons require compatible ordered types.

### Initial end-to-end profile

The first end-to-end verification profile is affine.

Initially supported arithmetic is:

- addition and subtraction;
- unary numeric signs;
- multiplication by a numeric constant;
- division by a non-zero numeric constant.

Examples inside the initial profile:

```forml
x0.a + x0.b <= 7
2 * x0.a - x0.b >= target
x0.a / 2 <= 3
```

Expressions such as:

```forml
x0.a * x0.b
x0.a / x0.b
```

remain structurally representable by the language model but require explicit nonlinear or symbolic-division capabilities. They must be rejected at a capability or lowering boundary when unsupported. FORML must never replace them with a silent approximation.

### Logical normalization

A complete comparison remains one logical atom for NNF, CNF, and DNF transformations.

Logical normalizers may change boolean structure and literal polarity, but they do not rewrite inside scalar arithmetic expressions.

## Rationale

A symmetric comparison model removes artificial distinctions between attributes, constants, and model outputs.

It also establishes a clean separation:

```text
Grammar and AST describe the expression requested by the user.
Semantic validation determines whether it is typed and meaningful.
IR requirements classify the expression family.
Backend capabilities determine whether it can be executed soundly.
```

This avoids contaminating the language with Z3-specific syntax or restricting the AST to the first minimal backend implementation.

## Consequences

### Positive

- Feature-to-feature and expression-to-expression comparisons become first-class.
- `target` no longer needs a separate comparison grammar branch.
- Arithmetic can be reused in assertions and interval bounds.
- Semantic validation can infer and check expression types recursively.
- IR requirements can distinguish affine and nonlinear arithmetic.
- Backends can reject unsupported expression families explicitly.
- NNF/CNF/DNF remain focused on boolean structure.

### Negative

- AST and IR comparison nodes become recursive rather than flat.
- Builder and translator logic require recursive expression visitors.
- Binding and type validation must traverse both sides of every comparison.
- Pretty printers and diagnostics must preserve precedence and parentheses.
- Backend capability declarations need finer arithmetic distinctions.
- Constant folding and division-by-zero checks require dedicated passes.

## Alternatives considered

### Add arithmetic only to the right-hand side

Rejected because it preserves the asymmetric model and still prevents natural relations such as `x0.a + x0.b <= target` or `target - x0.baseline <= 3`.

### Add special comparison nodes for target expressions

Rejected because `target` is a scalar reference, not a separate logical category. Special-casing it would duplicate grammar, AST, builder, and lowering paths.

### Normalize every comparison immediately to `expression op 0`

Rejected at the AST boundary because it loses the user's original syntactic structure too early and weakens diagnostics and traceability. Such canonicalization may be introduced later as an explicit IR transformation.

### Restrict the grammar itself to affine arithmetic

Rejected because the language representation and backend execution profile are distinct concerns. The parser should preserve user intent, while semantic requirements and backend capabilities decide whether a property is currently executable.

### Translate expressions directly to Z3 during parsing

Rejected because it violates the staged compiler pipeline and creates backend leakage before semantic validation and IR construction.

## Impact on FORML

### Grammar

Arithmetic requires explicit precedence levels, and comparison operands become scalar expressions.

### AST

`ComparisonNode.left` and `ComparisonNode.right` become scalar-expression nodes. Recursive unary and binary arithmetic nodes are introduced.

### Semantic validation

Binding recursively resolves every attribute reference. Type validation infers expression types, enforces numeric arithmetic, checks comparison compatibility, and rejects literal division by zero.

### IR1

IR1 preserves scalar expression trees. Comparisons remain logical leaves containing two scalar operands and one comparison operator.

### IR2

NNF/CNF/DNF treat the complete comparison as an atom. Requirements analysis classifies arithmetic families without rewriting them silently.

### Backends

Backend capabilities must distinguish at least:

- scalar comparisons;
- affine arithmetic;
- nonlinear arithmetic;
- symbolic division;
- compatible scalar data types.

The minimal Z3 translator is extended recursively only for capabilities it declares.

### Tests

Required tests include:

- operator precedence and associativity;
- parenthesized expressions;
- unary arithmetic;
- symmetric comparison operands;
- target arithmetic;
- recursive binding;
- numeric type promotion;
- incompatible arithmetic rejection;
- chained comparison rejection;
- literal division-by-zero rejection;
- affine capability acceptance;
- nonlinear capability rejection without approximation;
- preservation of comparison atoms through NNF/CNF/DNF.

### Related documentation

- `language/arithmetic-expressions.md`
- `language/assertions.md`
- `contracts/cst-to-ast.md`
- `contracts/ast-to-semantic.md`
- `contracts/semantic-to-ir1.md`
- `ir/ir1-nnf.md`
- `backends/capabilities.md`
- `backends/z3.md`
