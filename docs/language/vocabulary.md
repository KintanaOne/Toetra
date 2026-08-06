# Vocabulary

> Status: Current vocabulary for `1.0.0rc4`
> Scope: Recognized language words and their support level
> Audience: users, semantic maintainers, and language contributors

## Interpretation

Vocabulary recognition is not an execution promise. The tables distinguish:

- **recognized**: represented by the grammar and AST builder;
- **defined**: accepted semantic rules exist for the relevant use;
- **public V1**: an end-to-end route in the public profile supports it.

See [Language support levels](support-levels.md).

## Property labels

| Label | User intent | Current meaning |
|---|---|---|
| `ROBUSTNESS` | behavior under bounded perturbation | recognized and defined by its explicit scope/assertion |
| `STABILITY` | controlled output stability | recognized and defined by its explicit scope/assertion |
| `FAIRNESS` | relational behavior between points | requires at least two visible points |
| `MONOTONICITY` | ordered behavior between points | recognized and defined by its explicit restriction/assertion |
| `BOUND` | upper, lower, or interval constraint | recognized and defined by its assertion |
| `LOGIC` | general logical property | recognized and defined by its assertion |

The label classifies intent; it does not insert an undocumented formula.
Unknown uppercase labels may parse for diagnostic purposes but fail semantic
normalization.

## Point vocabulary

| Word | Meaning | V1 boundary |
|---|---|---|
| `forall`, `∀` | universal symbolic point binder | homogeneous chains executable |
| `exists`, `∃` | existential symbolic point binder | homogeneous chains executable |
| `anchor` | concrete named point declaration | executable for supported numeric schemas |
| `ref` | external-row anchor binding | requires runtime resolution |
| `check_at` | select one declared anchor | executable when the anchor resolves |
| `at ... with ... in neighborhood` | local universal-candidate sugar | executable for the supported neighborhood profile |
| `where` | relation restricting a quantified context | executable when its requirements are supported |
| `domain` | admissible input constraints | numeric-affine V1 subset |

Ordered alternating quantifiers are recognized and represented but
capability-rejected by the built-in V1 route.

## Problem and function vocabulary

Recognized problem names:

```text
CLASSIFICATION
PREDICTION
REGRESSION
CLUSTERING
ANOMALY_DETECTION
REINFORCEMENT_LEARNING
```

Recognized function names:

```text
EQUAL
EQUITY
BETWEEN
INCREASING
DECREASING
```

Grammar recognition does not make every Cartesian product meaningful. Semantic
compatibility rejects unknown combinations. In the public V1 profile,
`CLASSIFICATION.EQUAL()` is the supported problem predicate: it denotes
predicted-label equality over exactly two visible binary model evaluations.
Other problem/function spellings must not be presented as executable unless the
public profile is extended.

## Model output vocabulary

| Form | Meaning | Public V1 route |
|---|---|---|
| `target[point]` | scalar regression evaluation | single-output `LinearRegression` |
| `target[point].label` | predicted classification label | direct binary `LogisticRegression` |
| `target[point].probability(label)` | class probability estimate for one label | direct binary `LogisticRegression` |

`target` names the output declared in the header. The bracket selects an input
point, not an output index.

These are intentionally not DSL observables:

```text
logit
decision_function
predict
predict_proba
classes_
score
Z3 symbol
```

Technical evidence may mention internal quantities without making them writable
language constructs.

## Domain vocabulary

| Form | Meaning |
|---|---|
| `[a, b]` | closed lower and upper endpoints |
| `]a, b]` | open lower, closed upper |
| `[a, b[` | closed lower, open upper |
| `]a, b[` | open lower and upper |
| `{a, b}` | finite discrete set |
| `EU` in a finite set | symbolic categorical literal |
| `"EU"` | string literal |

Domain subjects are explicitly qualified features. Bare names in interval
bounds may resolve to specification constants; feature references in bounds
remain explicit.

## Metrics

The grammar recognizes:

```text
L1
L2
Linf
```

Recognition preserves user intent. The public built-in neighborhood route is
the numeric-affine `Linf` profile documented by the public profile and point
contracts. `L1` and `L2` must not be inferred to be executable from their
presence in the grammar.

## Operators

### Comparison

```text
==  !=  <  <=  >  >=
```

Ordering requires numeric operands. Equality requires compatible scalar types.
Predicted labels accept equality and inequality, not ordering.

### Arithmetic

```text
+  -  *  /
unary +  unary -
```

All operators build structured scalar trees. Semantic analysis classifies them
as affine, nonlinear, or symbolic division. The built-in V1 route supports the
affine class only.

### Boolean

```text
and / AND
or  / OR
not / NOT
->
```

The internal canonical values are lowercase `and`, `or`, `not`, and `->`.
Although `xor` exists in a low-level token map, it is not part of the supported
Boolean AST/IR contract and must not be used in user examples.

## Literal vocabulary

| Family | Examples |
|---|---|
| integer or real | `7`, `-0.1`, `2.5` |
| Boolean | `true`, `false`, `True`, `False` |
| quoted string | `"approved"`, `"EU"` |
| symbolic finite-set member | `EU`, `US` |

Specification-constant and anchor declarations accept scalar literals, not
arbitrary expressions.

## Backend vocabulary

| Spelling | Recognition | Meaning |
|---|---|---|
| `Z3`, `z3` | accepted | public built-in backend |
| `ERAN`, `eran` | reserved | rejected as a V1 backend |
| `ZONOTOPE`, `zonotope` | reserved | rejected as a V1 backend |
| `BOX`, `box` | reserved | rejected as a V1 backend |

An explicit backend is required. Omitting `using ...` permits capability-based
selection from the registered runtime backends; the built-in V1 registry
contains only Z3.

## Protected words

The language reserves words that introduce declarations, scopes, domains,
restrictions, neighborhoods, and backends, including:

```text
model target dataset anchor ref
forall exists at check_at
with domain where in neighborhood
using true false
```

Protected-word matching uses token boundaries. A longer identifier such as
`target_score` remains an identifier.

## Normalization boundary

The lexer and builder normalize equivalent spellings into enum-like internal
values while preserving source locations and declared point names. Normalizing
a token never authorizes a semantic combination or a backend route.

## Related pages

- [Syntax](syntax.md)
- [Properties](properties.md)
- [Model output observables](model-output-observables.md)
- [Backends syntax](backends.md)
- [Public V1 profile](../public-v1-profile.md)
