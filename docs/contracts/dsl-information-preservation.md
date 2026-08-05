# DSL Information Preservation Contract

> **Status:** Implemented and accepted
>
> **Scope:** information-bearing Toetra syntax from CST construction through
> runtime planning
>
> **Audience:** grammar, builder, semantic, IR, runtime, and CLI maintainers

## Purpose

Every information-bearing construct accepted by the Toetra grammar must follow
one of two explicit paths:

1. it is represented by the owning AST node and preserved through every later
   boundary that requires its meaning; or
2. the first boundary that owns its validity rejects it with a deliberate
   diagnostic.

A builder, semantic pass, IR translator, runtime adapter, or CLI handler must
never accept a value and then silently discard it.

## Preservation matrix

| DSL information | AST ownership | Later ownership | Required outcome |
|---|---|---|---|
| `model := ...` | `HeaderNode.model` | model resolution, semantic model identity, model evaluations, provenance | preserved; a runtime artifact override may replace only the effective path |
| `target := ...` | `HeaderNode.target` | schema contract, semantic output identity, model-evaluation IR, reporting | preserved; mismatches fail closed |
| `dataset := ...` | `HeaderNode.dataset` | dataset resolution, schema construction, anchor fallback, provenance, inspection | preserved; an explicit runtime dataset may replace only the effective path |
| specification constants | ordered header declarations | semantic constant registry and scalar IR | preserved with literal type and spelling evidence |
| inline and referenced anchors | ordered `ProgramNode.anchors` | point environment, concrete resolution, assumptions, provenance, replay | preserved; malformed or unresolved bindings fail explicitly |
| property type | `PropertyNode.type` | compatibility rules, IR1, IR2, routing, reporting | preserved |
| scope, binders, domains, and restrictions | typed scope AST | semantic point environment, IR1 scope, IR2 assumptions/quantifiers | preserved in source order and with boundary kinds |
| logical/scalar expressions and output observables | typed assertion AST | semantic binding/typing, IR1 query, lowering, IR2 formula | preserved until an owning lowering deliberately rewrites them |
| backend name | `BackendNode.name` | semantic compatibility, IR1/IR2 backend requirement, routing | preserved |
| backend arguments | ordered typed `BackendNode.args` | semantic backend profile | preserved in AST, then rejected in public V1 because no argument semantics are defined |
| problem/function arguments | grammar CST | builder | rejected when non-empty because public problem predicates define no argument contract |
| legacy neighborhood arguments | ordered typed `NeighborhoodNode.args` | migration/semantic boundary and IR1 when eligible | preserved; positional or duplicate arguments are rejected |

This matrix is normative. More detailed contracts may impose additional
validation, lowering, or execution requirements.

## Header artifact semantics

A file-backed specification resolves quoted or identifier artifact references
as follows:

```text
model/dataset declared in the header
    → relative to the directory containing the .toetra file

explicit runtime model/dataset override
    → relative to the caller's working directory
```

Absolute paths remain absolute. The runtime records both the declared reference
and the effective consumed artifact. An override changes the artifact selected
for one run; it does not rewrite the specification or alter its target or
properties.

For inline source, header artifact references are resolved from the caller's
working directory because no specification directory exists.

The optional header dataset participates in:

- model-schema construction when a model artifact is loaded;
- referenced-anchor lookup when no dedicated anchor source or resolver is
  supplied;
- provenance and inspection as the effective dataset artifact.

A declared dataset that does not exist is an input error. It is part of the
declarative input contract and is never ignored.

## Argument ownership

The generic grammar-level `args` rule does not create generic execution
semantics.

- Backend arguments must use unique `name=value` entries. The builder retains
  their typed primitive values. Public V1 semantic validation rejects every
  non-empty backend argument list until a backend contract defines those names.
- `CLASSIFICATION.EQUAL()` and other problem predicates accept no arguments in
  the public profile. A non-empty list is rejected by the builder.
- Legacy neighborhood arguments must use unique `name=value` entries and retain
  typed primitive values. Unsupported legacy scopes are still rejected by the
  migration/semantic boundary rather than being partially lowered.
- Anchor `ref(...)` arguments retain order and values in AST. Semantic
  validation owns required names, uniqueness, and types.

## Boundary rules

### Parser

The parser preserves the complete accepted CST shape and source locations. It
does not decide whether an accepted optional construct is publicly executable.

### Builder

The builder creates a typed representation for every supported syntactic value.
It rejects structurally representable-but-unsupported argument forms before
returning a partial AST.

### Semantic validation

Semantic validation resolves declarations and rejects constructs whose meaning
is not defined by the active public profile. It must not erase a construct to
make a property appear supported.

### IR lowering

Only semantically accepted meaning reaches IR1. IR1 and IR2 preserve every
field required by later lowering, routing, reporting, or replay. A construct
rejected by semantics does not need a placeholder IR representation.

### Runtime and CLI

Runtime planning distinguishes declared artifacts from effective artifacts.
CLI options may override supported artifact locations or execution policy, but
must not create a second source of truth for DSL semantics.

## Regression requirements

Tests must cover at least:

- model, target, dataset, constants, and anchors retained from CST to AST;
- header dataset resolution relative to a specification;
- explicit dataset override precedence;
- inspection of declared and effective artifact identities;
- typed backend argument retention followed by explicit semantic rejection;
- explicit rejection of problem-function arguments;
- typed legacy-neighborhood argument retention and duplicate rejection;
- no change to model/property fingerprints merely because this contract was
  introduced.
