# Semantic Layer

> Status: P0 / Implemented / Stabilizing  
> Scope: AST to SemanticValidatedAST  
> Implementation: LHS validation, binding validation, logic validation, compatibility checks  
> Audience: compiler contributors, model integration authors, IR authors

## Purpose

The semantic layer validates the meaning of the AST.

It answers the question:

```text
Is this syntactically valid FORML program meaningful and well-bound?
```

The semantic layer turns an AST into a conceptually richer artifact:

```text
SemanticValidatedAST
```

---

## Position in the Pipeline

```text
AST
    ↓
Semantic Validation
    ↓
SemanticValidatedAST
    ↓
IR1
```

The semantic layer is the bridge between syntax and logical representation.

---

## Responsibilities

The semantic layer is responsible for:

- validating property scopes;
- building a semantic context;
- registering variables in a symbol table;
- resolving explicit and implicit entities;
- validating logical expression structure;
- validating problem/function compatibility;
- validating property/scope compatibility;
- attaching semantic annotations;
- preparing the AST for IR translation.

---

## Semantic Pipeline

The semantic validation of a property follows this sequence:

```text
PropertyNode
    ↓
LHS validation
    ↓
SemanticContext
    ↓
Binding validation
    ↓
Resolved attributes
    ↓
Logic validation
    ↓
Property/scope compatibility
    ↓
Semantic annotations cached on property and attributes
```

---

## Semantic Context

The `SemanticContext` defines the evaluation context produced from the LHS.

It contains:

- scope type;
- variables and roles;
- default entity for implicit feature access;
- optional domain;
- optional neighborhood;
- optional quantifier;
- symbol table.

Example for a local robustness scope:

```text
at x in neighborhood(...)
```

The semantic context may define:

```text
variables = {
    "x": "anchor",
    "x'": "perturbation"
}
default_entity = "x'"
```

This means:

```text
age <= 30
```

can be resolved as:

```text
x'.age <= 30
```

---

## LHS Validation

The LHS defines where the property is evaluated.

| LHS Type | Semantic Scope | Variables |
|---|---|---|
| `check_at x` | pointwise | `x` as anchor |
| `at x` | local | `x` as anchor, `x'` as perturbation |
| `x ~ x'` | pairwise | `x` as anchor, `x'` as perturbation |
| `forall` / `exists` | quantifier | `_x` as symbolic variable |

The LHS validator creates the semantic context used by later passes.

---

## Binding Validation

Binding validation resolves attribute references in RHS assertions.

Resolution priority:

1. symbol table explicit resolution;
2. explicit entity resolution;
3. implicit default entity;
4. single-variable fallback;
5. ambiguity error.

This means the semantic layer can resolve both explicit and concise DSL forms.

---

## Logic Validation

Logic validation checks the semantic validity of the logical tree.

It validates:

- comparison leaves;
- boolean operators;
- implications;
- problem-level predicates;
- resolved attributes;
- operand compatibility.

It assumes binding validation has already run.

---

## Compatibility Validation

The semantic layer validates compatibility between:

- property type and scope;
- problem type and function;
- later: property type and model task;
- later: property type and backend capabilities.

Examples:

| Property | Valid Scopes |
|---|---|
| `ROBUSTNESS` | local, pointwise, quantifier |
| `FAIRNESS` | pairwise |
| `MONOTONICITY` | pairwise, quantifier |
| `BOUND` | pointwise, quantifier |

---

## SemanticValidatedAST

A `SemanticValidatedAST` is an AST with semantic information attached or derivable.

It should provide:

- a validated semantic context;
- a symbol table;
- resolved attribute references;
- a validated logical root;
- validated property/scope compatibility;
- future schema-aware validation results.

---

## Schema-Aware Semantic Validation

The current semantic layer validates syntax-level and scope-level semantics.

The target semantic layer must also integrate `ModelSchema` from ModelBridge.

This enables checks such as:

- feature exists in model schema;
- feature dtype is compatible with comparison value;
- target exists;
- property is compatible with model task;
- problem predicate is compatible with classification/regression;
- model feature metadata is available when required.

---

## Guarantees

The semantic layer must guarantee:

- all RHS attributes are resolved or rejected;
- scope variables are known;
- property/scope compatibility is enforced;
- logical nodes are structurally valid;
- problem functions are compatible with problem types;
- semantic errors are not reported as parser errors in the stabilized architecture;
- IR translation receives resolved semantic information.

---

## Stabilization Requirements

| Topic | Required Action |
|---|---|
| Enum normalization | Validators should handle enum instances and strings robustly. |
| Problem/function validation | Compare enum values consistently. |
| Property/scope validation | Avoid `.upper()` on enum instances. |
| Error boundary | Do not wrap all semantic errors as parser errors. |
| Schema integration | Add ModelSchema-aware validation. |
| Attribute annotations | Ensure all semantic-capable nodes declare semantic fields explicitly. |

---

## Relation to IR1

IR1 must consume semantic resolution.

The IR translator should prefer:

```text
AttributeNode.semantic.resolved_entity
AttributeNode.semantic.resolved_path
```

over raw parsed fields when available.

This is critical for implicit attribute syntax.

---

## Relation to Miova

Miova can challenge the semantic layer by mutating AST artifacts.

Examples:

- unknown variable;
- ambiguous implicit feature;
- invalid pairwise variable;
- unsupported property/scope pair;
- invalid problem/function pair;
- missing neighborhood argument;
- corrupted domain.

The semantic layer should reject invalid mutations with precise semantic diagnostics.
