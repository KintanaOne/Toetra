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

The target quantified-scope grammar is:

```ebnf
quantifier_expr = quantifier, identifier, [ domain ] ;
quantifier      = "forall" | "exists" | "∀" | "∃" ;
```

The identifier is syntactically mandatory. The grammar only preserves it in the CST; matching explicit references against that declaration is a semantic responsibility.

Target AST shape:

```text
QuantifierExprNode(quantifier, variable, domain)
```

The current implementation does not yet satisfy this target contract and must be updated only after the documentation patches are accepted.

| Scope | Example | Meaning |
|---|---|---|
| `at` | `at x in neighborhood(metric=L2, eps=0.1)` | Local evaluation around an anchor. |
| `check_at` | `check_at x` | Pointwise evaluation. |
| `pairwise` | `x ~ x' in neighborhood(metric=L2, eps=0.1)` | Relation between anchor and perturbation. |
| quantifier | `forall x0 with domain(...)` | Symbolic evaluation over an explicitly named variable. |

---

## Domain Grammar

The target typed-domain grammar is:

```ebnf
domain = "with", "domain", "(", domain_entry,
         { ",", domain_entry }, [ "," ], ")" ;

domain_entry = domain_subject, ":", domain_constraint ;
domain_subject = qualified_attribute ;
domain_constraint = interval_domain | finite_set_domain ;

interval_domain = closed_closed_interval
                | open_closed_interval
                | closed_open_interval
                | open_open_interval ;

closed_closed_interval = "[", arithmetic_expression, ",", arithmetic_expression, "]" ;
open_closed_interval   = "]", arithmetic_expression, ",", arithmetic_expression, "]" ;
closed_open_interval   = "[", arithmetic_expression, ",", arithmetic_expression, "[" ;
open_open_interval     = "]", arithmetic_expression, ",", arithmetic_expression, "[" ;

finite_set_domain = "{", domain_literal,
                    { ",", domain_literal }, "}" ;

domain_literal = numeric_literal
               | boolean_literal
               | string_literal
               | symbolic_literal ;
```

Grammar-level decisions:

- `domain` is a protected keyword, not a generic identifier;
- a domain contains at least one entry;
- domain subjects are explicitly qualified attributes;
- input references inside arithmetic bounds are also explicitly qualified;
- a trailing comma is accepted;
- empty finite sets are rejected syntactically;
- interval boundaries preserve all four bracket combinations;
- interval bounds may contain arithmetic expressions;
- finite-set members remain literals in this language slice.

The grammar preserves syntax. It does not validate entity binding, numeric typing, interval satisfiability, division by zero, target usage in a domain, or backend capability.

## Assertion Grammar

The target assertion grammar separates scalar expressions from boolean expressions.

```ebnf
comparison_expr = scalar_expression,
                  comparison_operation,
                  scalar_expression ;

scalar_expression = additive_expression ;

additive_expression = multiplicative_expression,
                      { ("+" | "-"), multiplicative_expression } ;

multiplicative_expression = unary_expression,
                            { ("*" | "/"), unary_expression } ;

unary_expression = [ "+" | "-" ], scalar_primary ;

scalar_primary = numeric_literal
               | boolean_literal
               | string_literal
               | attribute
               | "target"
               | "(", scalar_expression, ")" ;

assertion = logic_imply ;
logic_imply = logic_or | logic_or, "->", logic_imply ;
logic_or = logic_and, { "OR", logic_and } ;
logic_and = logic_not, { "AND", logic_not } ;
logic_not = [ "NOT" ], logical_atom ;
logical_atom = comparison_expr
             | problem_expr
             | "(", assertion, ")" ;
```

Normative consequences:

- comparisons accept expressions on both sides;
- `target` is a scalar leaf distinct from an input attribute;
- arithmetic precedence is encoded structurally;
- comparison operators are non-associative;
- chained comparisons are invalid;
- boolean operators compose predicates, not numeric values;
- problem predicates remain boolean leaves and are not arithmetic operands.

The grammar may represent multiplication or division that exceeds the initial affine verification profile. Semantic requirement analysis and backend routing decide whether such an expression is supported.

The previous `logic_expr = attribute logic_operation value` form is superseded. Boolean operators belong only to the logical assertion tree.

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

Recommended P1 decision:

```text
Accept case-insensitive logical operators, normalize internally to uppercase enum names.
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
| Operator precedence samples | Validate logical and arithmetic tree structure. |
| Arithmetic samples | Cover unary/binary precedence, symmetric comparisons, interval bounds, and chained-comparison rejection. |
| Scope samples | Cover `at`, `check_at`, `pairwise`, `forall <identifier>`, and `exists <identifier>`. |
| Domain samples | Cover four interval forms, finite sets, symbolic literals, trailing commas, and malformed domains. |
| Backend samples | Cover backend names and arguments. |
| Hypothesis-generated syntax | Discover grammar edge cases. |
| Fuzzed syntax | Challenge parser robustness. |

---

## Related Documents

- [Syntax](syntax.md)
- [Vocabulary](vocabulary.md)
- [Assertions](assertions.md)
- [Scopes](scopes.md)
- [Quantified Variable Bindings](quantified-bindings.md)
- [Domains](domains.md)
- [Arithmetic Expressions](arithmetic-expressions.md)
- [Examples](examples.md)
