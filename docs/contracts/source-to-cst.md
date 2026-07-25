# Source to CST Contract

> Status: P0 / Accepted target syntax
> Scope: Raw Toetra source to Concrete Syntax Tree
> Implementation: Lark parser
> Audience: grammar authors, parser maintainers and parser-test authors

## Purpose

This boundary decides only whether source text conforms to Toetra syntax.

It does not decide what the program means.

---

## Input and Output

```text
Input:  SourceText: str
Output: CST rooted at `program`
```

The CST preserves tokens and grammar structure required by the builder.

---

## Normative Quantifier Syntax

```text
quantifier_scope ::= ("forall" | "exists" | "∀" | "∃") identifier [domain]
```

The identifier is mandatory.

Valid:

```toetra
forall x0 => target <= 7
exists candidate => candidate.score > 0
```

Invalid at this boundary:

```toetra
forall => target <= 7
exists with domain(...) => target <= 7
```

The parser preserves the identifier spelling. It does not register or resolve the symbol.

---

## Normative Domain Syntax

Conceptually:

```text
domain          ::= "with" "domain" "(" domain_entry ("," domain_entry)* [","] ")"
domain_entry    ::= qualified_attribute ":" domain_constraint
domain_constraint ::= interval | finite_set
```

The grammar distinguishes:

```text
[a, b]
]a, b]
[a, b[
]a, b[
```

and:

```text
{v1, v2, ...}
```

Curly braces always represent finite sets.

The parser preserves delimiter orientation and member boundaries. It does not validate interval order, duplicate subjects, binding or feature types.

---

## Normative Scalar Syntax

A comparison relates two scalar expressions:

```text
comparison ::= scalar_expression comparison_operator scalar_expression
```

Precedence is:

```text
parentheses
unary + -
* /
+ -
comparison
NOT
AND
OR
logical implication
```

Comparisons are non-associative. Chained comparisons are rejected by the grammar or an immediately adjacent structural parser rule.

---

## Parser Guarantees

If parsing succeeds:

- the quantified identifier is present;
- interval and set delimiters are structurally valid;
- scalar precedence is represented in the CST;
- comparison operands are syntactically present;
- the result contains no semantic annotations or solver objects.

---

## Parser Non-Goals

The parser does not:

- verify that `x0` matches references in the assertion;
- distinguish a valid feature from an unknown feature;
- decide whether `obj1` is compatible with a categorical feature;
- infer scalar types;
- classify affine/nonlinear arithmetic;
- reject duplicate domain subjects;
- build verification conditions.

---

## Parser-Owned Failures

The parser rejects:

- missing quantified identifier;
- malformed domain parentheses;
- malformed interval delimiters;
- missing interval bound;
- malformed finite-set separators;
- missing comparison operand;
- malformed arithmetic grouping;
- chained comparison syntax;
- unsupported tokens.

Semantically invalid but syntactically valid programs must reach later boundaries.
