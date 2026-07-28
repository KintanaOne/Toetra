# IR2 normal forms

> **Status:** Implemented
>
> **Scope:** NNF, CNF, and DNF representations inside `VerificationTaskIR2`

IR2 stores the executable verification condition in one of three explicit
backend-neutral representations.

## Formula types

| Type | Shape |
|---|---|
| `NNFFormulaIR2` | logical tree with implication removed and negation confined to atoms |
| `CNFFormulaIR2` | conjunction of `ClauseIR2`, each a disjunction of signed literals |
| `DNFFormulaIR2` | disjunction of `TermIR2`, each a conjunction of signed literals |

`LiteralIR2` stores an atom plus `Polarity`; CNF/DNF do not wrap leaves in
arbitrary `NotIR` nodes.

## Construction order

```text
lowered VerificationTask
→ NNFNormalizer
→ NNFGuard
→ NNFFormulaIR2 property
→ assumptions + verification semantics
→ NNF verification condition
→ form selection
→ optional CNF/DNF conversion
→ VerificationTaskIR2
```

The source property and executable condition are intentionally distinct. Under
universal refutation the executable condition negates the property; under
existential witness semantics it does not.

## Selection

`NormalFormSelector` uses `IR2BuildContext` to determine the preferred form.
`IR2Builder` records the form actually produced, which may remain NNF when that
is the configured or safe choice.

CNF and DNF conversion can expand exponentially. Cost estimation and configured
limits prevent uncontrolled distribution. A form is never claimed unless the
corresponding representation was actually produced.

## Semantic preservation

Conversion must preserve:

- atomic comparison identity;
- literal polarity;
- open/closed boundary meaning;
- point and model-evaluation identity;
- assumption provenance;
- universal or existential verification semantics.

The converters transform Boolean structure only. They do not simplify scalar
algebra, coerce sorts, or approximate model equations.

## Requirements

`RequirementsAnalyzer` derives the backend requirements from:

- the selected verification condition;
- property and assumption atoms;
- scalar expression families and sorts;
- normal form;
- model and domain assumptions;
- quantifier structure and verification semantics;
- model-semantic quantities.

These requirements are consumed by routing. Normal-form conversion does not
select a backend.

## Validation

`IR2Validator` and guardrails reject or diagnose:

- invalid NNF input;
- malformed formulas;
- inconsistent point/evaluation identities;
- missing, duplicate, or unrequested model equations;
- requirement/task disagreement;
- unsupported normal-form expansion.

## Contracts

- [IR1 to IR2](../contracts/ir1-to-ir2.md)
- [Lowering and minimization](../contracts/lowering-minimization.md)
- [IR to backend](../contracts/ir-to-backend.md)
