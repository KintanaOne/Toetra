# Compiler pipeline contract

> **Status:** Implemented and accepted
>
> **Scope:** source text through backend-neutral result preparation

## Official artifact chain

```text
SourceText
→ Lark CST
→ ProgramNode AST
→ semantically validated AST state
→ VerificationTask (IR1)
→ model-semantically lowered VerificationTask
→ NNF VerificationTask
→ VerificationTaskIR2
→ BackendRoute
→ backend-private translation
→ VerificationResult
```

The model path contributes:

```text
ModelArtifact
→ ModelSchema
→ Model IR construction
→ semantic profile + compiler model lowering
→ typed model AssumptionIR2 values
→ VerificationTaskIR2
```

Labels such as `SemanticValidatedAST`, `AggregatedAssertionSet`,
`LoweredQuery`, and `BackendQuery` may appear in historical design records.
They are not runtime classes in `1.0.0rc4` and must not be required by current
extensions.

## Artifact ownership

| Artifact/state | Producer | Must contain | Must exclude |
|---|---|---|---|
| source | caller/filesystem | public DSL text | compiler objects |
| CST | parser | grammar tree and tokens | resolved symbols, model/backend objects |
| AST | builder | typed source nodes | assumed binding, solver objects |
| validated AST state | semantic validator | resolved contexts, symbols, points, types | backend expressions |
| IR1 | IR translator | backend-neutral scope, scalar/logical intent, observable identity | Lark nodes, Z3 objects |
| lowered IR1 | model semantic profile | canonical constraints and evidence | unresolved supported observables |
| NNF IR1 | NNF normalizer | implication-free logical tree | non-leaf negation |
| IR2 | IR2 builder | property, assumptions, condition, semantics, requirements, diagnostics | raw source syntax, backend API objects |
| route | backend router | selected capabilities, reason, numeric assessment | native query objects |
| native translation | backend adapter | exact backend representation and reverse mappings | unchecked requirements |
| result | backend runner | logical status, assignments, execution evidence | public rendering policy |

## Global guarantees

1. Each layer consumes only its declared inputs.
2. Each transition returns a valid next artifact/state or fails explicitly.
3. Source identifiers, point identities, and model evaluations remain traceable.
4. No backend object leaks into IR1 or IR2.
5. No unresolved source/model reference enters IR1.
6. Model-dependent public observables are lowered before final NNF.
7. Domain, anchor, and model assumptions remain distinguishable.
8. Requirement, numeric, and execution-policy checks precede backend
   translation.
9. Unsupported expressions are rejected, never silently approximated.
10. Universal and existential semantics govern both condition construction and
    result interpretation.

## Verification-condition branch

Homogeneous binders are represented by symbolic variables and explicit
verification semantics:

```text
universal:  Γdomain ∧ Γanchor ∧ Γmodel ∧ ¬P
existential: Γdomain ∧ Γanchor ∧ Γmodel ∧ P
```

Alternating quantifiers are represented in requirements and rejected by the V1
route. They are not flattened unsoundly.

## Expected failure boundaries

| Failure | Boundary |
|---|---|
| malformed syntax | source → CST |
| unsupported CST shape | CST → AST |
| invalid binding/type/model reference | AST → semantic state |
| missing semantic resolution | semantic state → IR1 |
| unsupported model-family observable | model-semantic lowering |
| invalid NNF or normal-form expansion | IR1 → IR2 |
| missing/duplicate/unrequested model equation | IR2 guardrails |
| unsupported structural/numeric/operational capability | routing |
| invalid native translation | backend adapter |
| backend technical failure | backend runner |

## Forbidden shortcuts

```text
Source → Z3
AST → Z3
Raw framework estimator → semantic validator
Unvalidated AST → IR2
IR2 → native translation without routing
Renderer → solver-status reinterpretation
```

## Specification-constant invariant

```text
header declaration
→ typed declaration AST
→ registered semantic symbol
→ resolved bare-name occurrence
→ typed constant IR with provenance
→ backend literal
```

No layer may reinterpret a specification constant as a model feature or
unconstrained backend variable.
