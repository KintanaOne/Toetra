# P25 documentation roadmap

> **Status:** Active
>
> **Baseline:** `1.0.0rc3` after P24 repository freeze
>
> **Scope:** public and contributor documentation

## Purpose

P25 makes the documentation describe the product that is implemented and
supported today. It establishes a public Python reference, replaces prospective
architecture descriptions with as-built views, documents extension paths, and
prevents examples from drifting away from executable behavior.

P25 does not add a model, property, framework, backend, public symbol, or result
status. User-facing error and report redesign belongs to P26. Further release
automation belongs to P27.

## Sources of authority

When documents disagree, resolve the conflict in this order:

1. [`public-v1-profile.md`](../public-v1-profile.md) defines the executable
   routes and exclusions exposed as Toetra V1.
2. `src/toetra/__init__.py` and the
   [public V1 contract](../contracts/public-v1-contract.md) define the supported
   Python facade.
3. Accepted contracts and ADRs define normative guarantees and architectural
   decisions. They cannot silently widen the public V1 profile.
4. As-built architecture pages describe the current implementation behind those
   boundaries. If implementation and description disagree, P25 corrects the
   description or records the discrepancy; it does not invent a guarantee.
5. Completed roadmaps and historical documents provide context only. They do
   not define current support or pending work.

For language syntax specifically, the EBNF source is authoritative and the
generated Lark grammar is derived. Language pages must still distinguish
parseable syntax, accepted semantics, and the smaller end-to-end public V1
profile.

## Documentation rules

Every current page must make its audience and status clear enough to answer:

- is this a public guarantee, an internal implementation description, or future
  direction;
- what inputs and outputs cross the documented boundary;
- what is implemented in `1.0.0rc3`;
- where the behavior is tested or otherwise validated.

Current documentation must not present planned types as implemented, private
modules as supported imports, or post-V1 routes as available. Code examples use
the public `toetra` facade unless a page is explicitly an internal contributor
guide.

## Delivery sequence

### P25.0 — Documentation truth reset

Remove the retired P24 aggregate gate, establish this authority order, and
define the remaining P25 exit criteria.

Exit criteria:

- no reference to the retired P24 aggregate target remains;
- release documentation names only durable Make targets;
- this roadmap identifies public, normative, as-built, and historical sources;
- identity, repository, public-contract, documentation, and CI checks remain
  green.

### P25.1 — Public Python API reference

Document the nine names exported by `toetra.__all__`: `verify`, sessions,
findings, reports, statuses, counterexample replay, and the three public error
types.

Exit criteria:

- every public symbol has a stable reference entry;
- signatures, return values, lifecycle, status handling, artifact writing, and
  failure boundaries are documented from the implementation;
- examples import only from `toetra`;
- public reference pages do not expose private implementation modules as API.

### P25.2 — As-built architecture

Align architecture, compiler, IR, ModelBridge, backend, runtime, and status
pages with the implemented pipeline:

```text
source -> CST -> AST -> semantic validation -> IR1
       -> model-semantic lowering -> NNF -> IR2 + assumptions
       -> route qualification -> backend execution
       -> report -> provenance -> replay
```

Exit criteria:

- current pipeline stages and ownership match `src/toetra`;
- planned or removed artifacts are not presented as runtime types;
- the status matrix separates implemented V1 behavior from post-V1 direction;
- architecture pages link to the contracts governing each boundary.

### P25.3 — Extension guides

Create separate contributor paths for adding a model family, a framework
adapter, and a backend. Each path must identify the required schema, semantics,
capabilities, numeric policy, execution, reporting, replay, and test work.

Exit criteria:

- the three extension types are not conflated;
- each guide identifies registration points and private boundaries from the
  current source tree;
- each guide includes unit, contract, end-to-end, documentation, clean-install,
  and release expectations;
- no guide implies that an extension is public before the V1 extension rule is
  satisfied.

### P25.4 — Language reference consolidation

Organize the language documentation around three distinct questions: what
parses, what has accepted meaning, and what executes through the public V1
routes.

Exit criteria:

- syntax, semantic validity, and executable support are explicitly separated;
- regression and binary-classification observables use consistent terminology;
- supported and rejected examples agree with the grammar, semantic rules, and
  public V1 profile;
- post-V1 constructs are labelled as such and cannot be mistaken for support.

### P25.5 — Executable documentation

Make public snippets checkable and reuse canonical examples where practical.
Integrate drift detection into an existing durable documentation or CI gate.

Exit criteria:

- selected public Python and Toetra snippets are parsed or executed in tests;
- copied snippets have an identified canonical source;
- snippet failures report the owning page clearly;
- no temporary `p25-check` target is introduced.

### P25.6 — Consolidation and freeze

Review navigation, links, status labels, duplicated concepts, terminology, and
historical placement. Archive the completed P25 plan once the documentation is
frozen.

Exit criteria:

- `mkdocs build --strict` succeeds without broken navigation or links;
- no active page contradicts the public profile, public facade, accepted
  contracts, or as-built pipeline;
- completed planning material lives under `docs/history/roadmaps/`;
- all durable quality and release gates pass from a clean checkout.

## Patch delivery contract

Each P25 sub-step is delivered as an independently reviewable `.patch` against
the baseline produced by the preceding accepted step. Every delivery includes:

- the exact baseline and files changed;
- an application command using `git apply`;
- focused checks followed by the relevant durable gates;
- a reversal command using `git apply -R`;
- no unrelated source, version, or public-contract change.

P25 uses existing validation targets:

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

No permanent target named after P25 is added.
