# Numeric Compatibility Registry

> Status: Stabilizing — runtime registry and routing gate implemented in Patch 16.2  
> Normative decision: [ADR-0018](../adr/ADR-0018-numeric-semantics-and-backend-compatibility.md)  
> Scope: framework adapters, model families, source numeric profiles, ModelBridge encoders, backend kinds/profiles, property numeric requirements, and permitted conclusions

## Purpose

FORML must not infer trust from a framework name or a backend name alone.
Numeric compatibility is a property of one complete verification route:

```text
framework adapter + version/opset
× model family
× source execution profile
× ModelBridge encoder + version
× backend kind
× backend adapter + numeric profile
× property numeric requirements
```

The registry is the single runtime source of truth for that route. It is
separate from backend capabilities:

- backend capabilities answer whether an IR2 task can be represented;
- numeric compatibility answers which semantic target is represented and which
  conclusions are justified.

A backend may satisfy every structural IR2 requirement and still be rejected
because no numeric compatibility rule matches.

## Runtime artifacts

Patch 16.2 introduces five backend-neutral artifact families.

| Artifact | Responsibility |
|---|---|
| `FrameworkModelDescriptor` | Identifies the framework adapter, model family, source execution profile, version/opset, and observed dtypes. |
| `ModelEncoderDescriptor` | Identifies the ModelBridge encoder and the semantic target it produces. |
| `BackendProfileDescriptor` | Identifies the backend kind, adapter, concrete numeric profile, version, and non-finite-value policy. |
| `PropertyNumericRequirements` | Summarizes task-local numeric operations derived from IR2 requirements. |
| `NumericCompatibilityAssessment` | Records the matched rule, support status, classification, semantic target, permitted conclusions, evidence, preconditions, and diagnostics. |

The descriptors use strings for extensible adapter, family, profile, and
encoder identities. Backend families and numeric semantic categories use enums
only where FORML needs a stable common vocabulary.

## Rule key

A `CompatibilityRulePattern` can constrain any subset of these dimensions:

| Dimension | Example values |
|---|---|
| Framework adapter | `sklearn`, `onnx`, `pytorch`, `native-exact-affine` |
| Framework version/opset | `1.8.0`, `opset-19`, or wildcard |
| Model family | `affine_regression`, `tree_ensemble`, `relu_network` |
| Source execution profile | `ieee754_binary64`, `integer_exact`, device-specific profile |
| Model encoder | `forml.affine-equation`, tree-path encoder, abstract-network encoder |
| Encoder version | Explicit contract version |
| Backend kind | SMT, MILP, interval analysis, abstract interpretation, concrete search, remote service |
| Backend adapter | `z3`, another solver adapter, a service adapter |
| Backend profile | Exact real arithmetic, IEEE-754 sorts, rational MILP, interval profile, etc. |
| Backend version | Concrete adapter/engine version or wildcard |
| Property tags | Numeric comparisons, affine arithmetic, domains, neighborhoods, scalar sorts, etc. |

`None` is a wildcard for scalar dimensions. Required property tags use subset
matching: a rule requiring `affine_arithmetic` may match a task that also needs
domains and numeric comparisons.

## Deterministic resolution

The registry applies these rules:

1. reject a duplicate normalized pattern at registration time;
2. collect all patterns matching the task;
3. select the highest specificity, measured by constrained scalar dimensions
   plus required property tags;
4. reject equally specific winners as an ambiguous rule set;
5. return `UNKNOWN` and unsupported when no rule matches;
6. reject non-finite contributors before rule matching when the selected backend
   profile does not declare support for them.

The registry never selects a permissive fallback implicitly.

## Support and semantic classification

Support status and semantic compatibility are independent axes.

| Axis | Values |
|---|---|
| Implementation support | `SUPPORTED`, `EXPERIMENTAL`, `PLANNED`, `UNSUPPORTED` |
| Semantic classification | `EXACT`, `SOUND_OVER_APPROXIMATION`, `SOUND_UNDER_APPROXIMATION`, `LOSSY`, `INCOMPATIBLE`, `UNKNOWN` |

A rule is executable only when it is supported or experimental and its
classification is neither incompatible nor unknown.

Each rule also declares a conclusion scope:

- `SOURCE_ARTIFACT`: the conclusion applies to the concrete source semantics;
- `SEMANTIC_TARGET_ONLY`: the conclusion applies only to the explicitly named
  abstraction or encoding.

A lossy, unknown, or under-approximating source-artifact rule cannot register a
universal proof or an existential no-witness conclusion. Rule construction
fails immediately if it attempts to do so.

## Conclusion interpretation

Backend statuses are interpreted through the matched assessment. The registry
uses four logical conclusion kinds:

| Verification status | Conclusion kind |
|---|---|
| `PROVED` | Universal proof |
| `COUNTEREXAMPLE` | Universal counterexample candidate |
| `WITNESS` | Existential witness candidate |
| `NO_WITNESS` | Existential no-witness conclusion |

If a backend produces a conclusion not permitted by the rule, FORML downgrades
the result to `UNKNOWN` and records the backend-interpreted status in metadata.

Patch 16.3 exposes the complete route in public reports and generates the public support and semantic-guarantee matrices from this registry.

## Initial built-in rule

The V1 registry currently contains one built-in implementation row. It is an
instantiation of the generic contract, not the architecture itself.

| Framework | Model family | Source profile | Encoder | Backend kind | Adapter/profile | Classification | Semantic target | Scope |
|---|---|---|---|---|---|---|---|---|
| sklearn | affine regression | discovered binary float or unknown | `forml.affine-equation@1` | SMT | `z3 / smt_real_affine_exact` | `LOSSY` | `forml.real_affine_extracted_model` | semantic target only |

The pattern deliberately does not require a specific sklearn version or binary
float width. Those values are preserved in the query and report provenance,
while the rule remains conservatively `LOSSY` for concrete source execution.

Potential future rows may target ONNX tree ensembles with MILP, PyTorch ReLU
networks with abstract interpretation, exact native affine artifacts with SMT,
or concrete runtime search. They must be registered through the same rule
model.

## Numeric information preservation

Patch 16.2 preserves information required by later compatibility decisions:

- numeric source lexemes remain available from AST to IR1 without changing
  semantic equality;
- sklearn introspection records framework version, source parameter dtypes,
  reference-data dtypes, model family, and a conservative source profile;
- manual schemas receive an explicit conservative descriptor rather than an
  inferred exact profile;
- every selected model encoder supplies a descriptor or receives an `unknown`
  fallback;
- every backend participating in compatibility-aware routing must declare a
  numeric profile.

The current descriptor does not claim to reconstruct every device kernel,
operation order, or intermediate rounding. Missing knowledge remains explicit.

## Routing order

```text
IR2 requirements
→ structural backend capability check
→ build task-local numeric query
→ compatibility registry resolution
→ reject unsupported/incompatible/unknown route
→ backend execution
→ conclusion policy
→ reporting
```

The registry is evaluated after model assumptions have been encoded, so the
non-finite scan includes the complete pre-backend task rather than only source
metadata.

## Extension contract

A new framework/model/backend route must provide:

1. a framework/model descriptor from introspection or explicit schema metadata;
2. a model-encoder descriptor naming its semantic target;
3. a backend profile descriptor naming its numeric semantics;
4. one or more evidence-backed compatibility rules;
5. tests for matching, wildcard precedence, conflicts, no-match behavior,
   non-finite handling, and permitted conclusions.

Framework- or backend-specific conditionals must not be scattered through the
router or result interpreter.

## Reporting and generated views

Patch 16.3 implements:

- generated public support and semantic-guarantee matrices;
- full report serialization of source, encoder, backend, evidence, assumptions,
  permitted conclusions and replay requirements;
- decimal-boundary tests that keep abstraction conclusions visibly scoped;
- fail-closed tests for exact, over-approximating and under-approximating routes.

See [Numeric Compatibility Reporting](numeric-compatibility-reporting.md).

Deferred beyond Patch 16.3:

- replay dtype preservation and promotion rules;
- broader property-operation compatibility rules;
- framework-specific execution-kernel evidence beyond registered descriptors.
