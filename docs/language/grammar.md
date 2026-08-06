# Grammar

> Status: Implemented and generation-checked in `1.0.0rc4`
> Scope: Source recognition and CST structure
> Audience: language and parser contributors

## Authoritative files

The maintained grammar source is:

```text
src/toetra/_language/grammar/toetra_grammar.ebnf
```

The parser consumes the generated Lark grammar:

```text
src/toetra/_language/grammar/toetra_grammar.lark
```

`tests/unit/parser/test_grammar_generation.py` regenerates the Lark text from
the EBNF and requires byte-for-byte equality with the committed file. Edit the
EBNF and vocabulary sources, regenerate, and commit both files together.

## Grammar boundary

The grammar establishes only that source text has a recognized structure. It
does not establish:

- exact point binding;
- model feature existence or type;
- interval satisfiability;
- specification-constant name resolution;
- output-observable compatibility;
- arithmetic capability;
- model encoder availability;
- backend support.

Those decisions belong to semantic validation and route qualification. Grammar
acceptance still creates a preservation obligation: an information-bearing CST
value must reach its owning AST/semantic boundary or fail explicitly under the
[DSL information preservation contract](../contracts/dsl-information-preservation.md).
See [Language support levels](support-levels.md).

## Program structure

The current structural shape is:

```text
program
  = header property+

header
  = model_declaration
    target_declaration
    dataset_declaration?
    specification_constant_declaration*
    anchor_declaration*

property
  = "[" property_type "]" ":"
    (property_scope "=>")?
    assertion
    backend?
```

This notation is explanatory. The committed EBNF is the exact source.

## Declarations

```text
model_declaration   = "model" ":=" quoted_identifier
target_declaration  = "target" ":=" identifier
dataset_declaration = "dataset" ":=" quoted_identifier

specification_constant_declaration
  = identifier ":=" signed_number_or_boolean_or_string

anchor_declaration
  = "anchor" identifier ":=" (inline_anchor | anchor_ref)
```

Specification constants accept literals only. Anchor blocks require at least
one entry. Reference argument presence and uniqueness are semantic concerns.

## Point scopes

```text
property_scope
  = quantifier_expr
  | at_expr
  | check_expr
  | legacy_pairwise_expr

quantifier_expr
  = quantifier identifier ("," identifier)*
    (quantifier_clause)*
    domain?
    where_clause?
```

The grammar preserves ordered quantifier clauses. It does not decide whether a
backend supports alternation.

Legacy `at` and pairwise shapes remain parseable only so semantic validation can
emit stable migration diagnostics. They are not part of the supported core.

## Domains

```text
domain
  = "with" "domain" "(" domain_entry ("," domain_entry)* ","? ")"

domain_entry
  = attribute ":" (interval_domain | finite_set_domain)
```

Intervals use the four bracket combinations `[a,b]`, `]a,b]`, `[a,b[`, and
`]a,b[`. Bounds are scalar expressions. Finite sets contain one or more values
or symbolic literals.

The parser preserves delimiters and tree structure. Semantic validation decides
whether subjects are explicitly bound, bounds are numeric and non-empty, and
set members match the feature type.

## Scalar and Boolean grammar

```text
scalar_expression
  = additive_expression

additive_expression
  = multiplicative_expression (("+" | "-") multiplicative_expression)*

multiplicative_expression
  = unary_expression (("*" | "/") unary_expression)*

unary_expression
  = ("+" | "-") unary_expression
  | scalar_primary

comparison
  = scalar_expression comparison_operator scalar_expression
```

Boolean precedence is encoded by separate recursive rules:

```text
atom
→ not
→ and
→ or
→ implication
```

Implication is right-associative. Comparisons are atoms and cannot be chained.
Arithmetic capability is deliberately not enforced by the grammar.

## Output references

```text
model_output_ref
  = "target" ("[" identifier "]")?

output_observable
  = model_output_ref "." (
      "label"
      | "probability" "(" class_label_literal ")"
    )
```

The parser distinguishes a model-output reference from a feature attribute.
Schema-aware semantic validation later distinguishes regression and
classification meaning.

## Lexical rules

### Identifiers

Identifiers use the common-name shape:

```text
[A-Za-z_][A-Za-z0-9_]*
```

Reserved words have lexer priority and use word boundaries so names such as
`target_score` are not split into `target` plus a suffix.

### Casing

- property, problem, and function vocabulary is uppercase;
- `forall`, `exists`, protected words, and `using` are lowercase;
- Boolean operators accept lowercase and uppercase forms;
- `Z3` and `z3` are both accepted;
- the metric spelling is `Linf`, not `LINF`.

### Comments

```text
# line comment
''' block comment '''
```

Both are discarded before CST construction.

## Regeneration

From the repository root:

```bash
python -m toetra._language.tools.generator
python -m pytest tests/unit/parser/test_grammar_generation.py
```

The generator and grammar package are private implementation surfaces. The
commands are contributor workflows, not public Python API.

## Required test layers

A grammar change is incomplete without:

1. positive and negative parser tests;
2. AST-builder coverage for every new tree shape;
3. semantic tests proving accepted and rejected meanings;
4. IR and backend capability tests when execution changes;
5. language reference and public-profile updates when support changes.

Parser tests alone may establish accepted syntax, never public execution.

## Related pages

- [Syntax](syntax.md)
- [Vocabulary](vocabulary.md)
- [Language support levels](support-levels.md)
- [Parser layer](../compiler/parser-layer.md)
- [CST to AST contract](../contracts/cst-to-ast.md)
