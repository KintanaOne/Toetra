# Grammar

> Status: Implemented / needs cleanup  
> Scope: Source language grammar  
> Priority: P1  
> Audience: compiler contributors, DSL maintainers, test authors

## Purpose

The grammar defines the accepted surface syntax of FORML programs.

It is the first formal boundary of the compiler pipeline:

```text
.forml source
→ parser
→ CST
```

The grammar is currently expressed in EBNF and generated or maintained as a Lark grammar.

The grammar is responsible for syntax only. It must not perform semantic interpretation such as feature existence checks, model compatibility, scope compatibility, or backend capability matching.

---

## Program Structure

A FORML program contains:

```text
header body
```

The header declares the model and target:

```forml
model := "model.joblib"
target := prediction
```

The body contains one or more property sections:

```forml
[ROBUSTNESS]: at x in neighborhood(metric=L2, eps=0.1) => CLASSIFICATION.EQUAL()
```

---

## Header Grammar

The intended header shape is:

```ebnf
header = padding,
         model_declaration,
         padding,
         target_declaration,
         padding,
         [ dataset_declaration, padding ],
         [ variables_declaration, padding ] ;
```

### Required declarations

| Declaration | Example | Status |
|---|---|---|
| `model` | `model := "model.joblib"` | implemented |
| `target` | `target := prediction` | implemented |

### Optional declarations

| Declaration | Example | Status |
|---|---|---|
| `dataset` | `dataset := "data.csv"` | grammar-level support |
| variables | `eps := 0.1` | grammar-level support |

---

## Property Grammar

A property section has the following shape:

```ebnf
property_section = property, [ backend ] ;
property = "[", property_type, "]", ":", property_expr, property_imply, assertion ;
property_imply = "=>" ;
```

Example:

```forml
[BOUND]: check_at x => score >= 0
```

Each property contains:

| Part | Example | Meaning |
|---|---|---|
| Property type | `[ROBUSTNESS]` | High-level verification intent. |
| Scope | `at x ...` | Where the property is evaluated. |
| Implication | `=>` | Separates scope from assertion. |
| Assertion | `score >= 0` | What must hold. |
| Backend | `using z3` | Optional backend hint or selection. |

---

## Scope Grammar

The current grammar supports four major scope forms:

```ebnf
property_expr = quantifier_expr | at_expr | check_expr | pairwise_expr ;
```

| Scope | Example | Meaning |
|---|---|---|
| `at` | `at x in neighborhood(metric=L2, eps=0.1)` | Local evaluation around an anchor. |
| `check_at` | `check_at x` | Pointwise evaluation. |
| `pairwise` | `x ~ x' in neighborhood(metric=L2, eps=0.1)` | Relation between anchor and perturbation. |
| quantifier | `forall with age(18, 65)` | Symbolic or domain-wide evaluation. |

---

## Assertion Grammar

The intended assertion grammar supports:

- comparisons,
- boolean composition,
- implication,
- negation,
- problem-level predicates,
- parentheses.

Examples:

```forml
age <= 30
score >= 0 AND score <= 1
NOT age < 18
CLASSIFICATION.EQUAL()
(age >= 18 AND age <= 65) -> score >= 0.5
```

### Current Stabilization Point

The grammar currently contains two overlapping concepts:

```ebnf
logic_expr = attribute, logic_operation, value ;
comparison_expr = attribute, comparison_operation, value ;
```

`comparison_expr` is the proper representation for assertions such as:

```forml
age <= 30
```

`logic_expr` should be reviewed because boolean operators normally compose logical expressions, not attribute/value leaves directly.

Recommended decision:

```text
Keep comparison_expr as the atomic predicate form.
Use AND/OR/NOT/IMPLY only at assertion-tree level.
Remove or repurpose logic_expr if it creates ambiguity.
```

---

## Operator Casing

The grammar currently mixes:

```text
AND : "and"
OR  : "or"
NOT : "not"
```

with assertion rules using uppercase literals:

```ebnf
logic_or  = logic_or "OR" logic_and ;
logic_and = logic_and "AND" logic_not ;
logic_not = "NOT" atom ;
```

This must be stabilized before public DSL freeze.

Recommended options:

| Option | Description | Recommendation |
|---|---|---|
| Uppercase canonical | Users write `AND`, `OR`, `NOT`. | Good for formal DSL style. |
| Lowercase canonical | Users write `and`, `or`, `not`. | Good for Python-like readability. |
| Case-insensitive | Both are accepted. | Flexible but must be tested carefully. |

Recommended V1 freeze decision:

```text
Use uppercase `AND`, `OR`, and `NOT` as the canonical public DSL spelling.
Normalize internally to enum names. Lowercase aliases may be added later only if the grammar and golden tests explicitly cover both forms.
```

---

## Grammar Responsibilities

The grammar should guarantee:

- source can be parsed or rejected deterministically;
- parse tree contains enough structure for AST building;
- operator precedence is syntactically encoded;
- comments and whitespace do not affect meaning;
- property sections are separable;
- optional backend syntax is attached to the relevant property.

The grammar should not guarantee:

- feature existence;
- model compatibility;
- property/scope compatibility;
- backend support;
- type compatibility;
- logical satisfiability.

Those belong to later compiler stages.

---

## Grammar Testing

Grammar tests should include:

| Test Category | Purpose |
|---|---|
| Minimal valid programs | Ensure basic parseability. |
| Full valid programs | Cover all syntax branches. |
| Invalid syntax samples | Ensure correct parse failure. |
| Operator precedence samples | Validate assertion tree structure. |
| Scope samples | Cover `at`, `check_at`, `pairwise`, quantifiers. |
| Backend samples | Cover backend names and arguments. |
| Hypothesis-generated syntax | Discover grammar edge cases. |
| Fuzzed syntax | Challenge parser robustness. |

---

## Related Documents

- [Syntax](syntax.md)
- [Vocabulary](vocabulary.md)
- [Assertions](assertions.md)
- [Scopes](scopes.md)
- [Examples](examples.md)
