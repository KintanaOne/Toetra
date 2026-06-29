# Documentation Review Corrections

> Date: 2026-06-29  
> Scope: `docs.zip` documentation pass  
> Goal: remove overclaims, freeze V1 boundaries, and align examples with the current compiler contracts.

## Corrections Applied

### 1. Z3-only V1 backend scope

The documentation now states that Z3 is the minimal and only intended backend for the first functional V1 path. ERAN, zonotope, box, AutoFORML, and general multi-backend orchestration are documented as post-V1 or reserved syntax only.

### 2. IR1 implementation status

The docs previously risked implying that IR1 already enforced De Morgan / NNF normalization. This pass clarifies the distinction:

```text
Structural IR1 translator: implemented / stabilizing
IR1 NNF + De Morgan pass: planned / critical
IR2 CNF-DNF: planned / critical
```

### 3. Semantic-to-IR1 contract

The docs now emphasize that IR1 must consume semantic annotations, especially resolved entities, instead of relying on raw unresolved AST attributes.

### 4. Pairwise contract

The pairwise syntax contract is now explicit:

```text
x ~ x'
```

The separator is `~`, and the right variable must be the primed version of the left variable. IR translation must not split pairwise tokens on commas.

### 5. Attribute-to-attribute comparisons

Examples that implied current support for right-hand-side attributes such as:

```forml
x'.score >= x.score
```

were replaced or marked as planned. The current comparison contract remains:

```text
AttributeNode op ConstantNode
```

### 6. Logical operator casing

The documentation now recommends uppercase `AND`, `OR`, and `NOT` as the canonical V1 public DSL spelling. Lowercase aliases can be added later only if grammar and golden tests explicitly support them.

## Remaining Implementation Fixes Suggested

These are code-level items surfaced by the documentation review, not changes made inside this docs-only zip:

1. Make the IR translator use `AttributeNode.semantic.resolved_entity` / `resolved_path` when building `ComparisonIR`.
2. Fix pairwise IR translation to split `scope.pair` on `~`, not comma.
3. Implement the explicit IR1 NNF/De Morgan pass or downgrade all runtime claims to structural IR1 only.
4. Align grammar logical operator tokens with the V1 casing decision.
5. Keep non-Z3 backend names as reserved/post-V1 until the Z3 path works.
6. Remove or quarantine production imports from `test.fixtures.*` in runtime scripts.
7. Avoid claiming attribute-to-attribute comparisons until AST and semantic contracts support them.

## Recommended Next Pass

The next useful pass is not more prose. It is an executable contract freeze:

```text
Source → CST
CST → AST
AST → SemanticValidatedAST
SemanticValidatedAST → structural IR1
structural IR1 → IR1-NNF
```

Each boundary should receive golden samples and expected artifacts before continuing toward Z3 lowering.
