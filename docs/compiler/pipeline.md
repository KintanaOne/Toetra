# Compiler pipeline

> **Status:** Implemented for `1.0.0rc4`
>
> **Scope:** source text through backend-neutral IR2
>
> **Audience:** compiler, model-integration, and backend contributors

The compiler converts `.toetra` source into validated backend-neutral
verification tasks. Backend selection, solver translation, execution, and
reporting occur after the compiler boundary.

## Implemented chain

```text
source text
→ Lark CST
→ ProgramNode AST
→ semantic validation in place
→ VerificationTask IR1
→ model-semantic lowering
→ NNF-normalized IR1
→ VerificationTaskIR2
```

The model-aware entry point additionally supplies:

```text
ModelSchema + Model IR
→ schema-aware validation
→ semantic profile selection
→ requested model evaluations
→ compiler model lowering
→ model assumptions
→ VerificationTaskIR2
```

The runtime constructs Model IR from the concrete model artifact before calling
the compiler. Schema-only execution uses the documented compatibility builder.
Supplying an explicit legacy `model_encoder_factory` remains an opt-in advanced
integration path and is not the built-in affine default.

## Stage contract

| Stage | Input | Output | Does not own |
|---|---|---|---|
| parser | UTF-8 source | Lark CST | semantic meaning |
| builder | CST | typed AST | name binding or model compatibility |
| semantic validator | AST, optional schema/anchors | validated AST state | logical normal forms |
| IR1 translator | validated AST | `VerificationTask` | model-family observable meaning |
| semantic lowerer | IR1 + schema | canonical IR1 + evidence | fitted coefficient extraction |
| NNF normalizer | lowered IR1 | NNF IR1 | CNF/DNF selection |
| IR2 builder | NNF IR1 + assumptions + policy | `VerificationTaskIR2` | backend-native objects |

## Source, CST, and AST

The EBNF under `src/toetra/_language/grammar` is the syntax source of truth. The
generated Lark grammar is derived and must not be edited manually.

`parse_toetra_code(...)` rejects invalid grammar and returns a CST.
`parse_program(...)` fully translates that CST into nodes beneath
`toetra._compiler.ast`. No Lark `Tree` should survive in the AST. Every
information-bearing accepted construct must either be represented by AST or be
rejected explicitly under the
[DSL information preservation contract](../contracts/dsl-information-preservation.md).

## Semantic validation

`ToetraValidator.validate(...)` establishes:

- scope and binder correctness;
- point visibility and anchor resolution;
- symbol and specification-constant resolution;
- feature and output-observable typing;
- schema-aware target and feature compatibility;
- valid property, restriction, and logical structure.

Validation enriches the AST and semantic contexts used by IR translation. The
code does not define a separate `SemanticValidatedAST` class.

## IR1

`IRTranslator` emits one `VerificationTask` per property. Each task retains:

- property type and optional backend requirement;
- `ScopeIR`, ordered binders, points, domains, and restrictions;
- backend-neutral scalar/logical query;
- public output-observable intent when model-family meaning is still required.

IR1 contains no Z3 object and no raw framework estimator.

## Model-semantic lowering

`ModelSemanticLowerer` selects a profile from `ModelSchema.model_family`.
Regression scalar output is already canonical. Binary classification label and
probability observables lower into oriented-decision constraints with structured
evidence.

A supported task cannot retain unresolved model-dependent observables. The
generic no-schema path rejects them instead of guessing.

Lowering occurs before final NNF because a rewrite may introduce Boolean
structure.

## NNF and IR2

`NNFNormalizer` eliminates implication, applies De Morgan rules, and confines
negation to atomic predicates.

`IR2Builder` then:

1. encodes domain and anchor assumptions;
2. collects supplied model assumptions;
3. constructs the verification condition;
4. selects or preserves NNF/CNF/DNF under guardrails;
5. records point mappings, evaluation identities, and quantifier structure;
6. derives `IR2Requirements`;
7. validates and diagnoses the completed task.

The output `VerificationTaskIR2` contains both the source property formula and
the executable condition. There is no later compiler object named
`AggregatedAssertionSet` or `LoweredQuery`.

## Compiler outputs

The high-level compiler output is a list of `VerificationTaskIR2` objects, one
per property. Each task is ready for capability and numeric qualification, but
not yet tied to a backend implementation.

The backend creates its native translation after routing. For Z3 this is a
private `Z3Translation`, not a generic compiler `BackendQuery`.

## Preservation and failure

Every transition must either preserve the declared semantics or fail at its
own boundary. In particular:

- open/closed domain bounds remain exact;
- ordered point identities remain distinct;
- universal and existential semantics are explicit;
- approximate logistic thresholds retain directed bounds and permitted
  conclusions;
- unsupported arithmetic, model meaning, or backend capability is rejected,
  never silently approximated.

## Related contracts

- [Compiler pipeline](../contracts/compiler-pipeline.md)
- [AST contract](../contracts/ast-contract.md)
- [AST to semantic](../contracts/ast-to-semantic.md)
- [Semantic to IR1](../contracts/semantic-to-ir1.md)
- [Model semantic lowering](../contracts/model-semantic-lowering.md)
- [IR1 to IR2](../contracts/ir1-to-ir2.md)
