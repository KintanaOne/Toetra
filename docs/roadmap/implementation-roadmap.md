# Implementation roadmap

> **Status:** Stable `1.0.0` sources prepared for publication
>
> **Scope:** stable V1 publication gates and evidence-led capability
> expansion

This roadmap starts from the product that exists today. Delivered work belongs
in the [project history](../history/roadmaps/index.md); current support is defined
by the [public V1 profile](../public-v1-profile.md), not by future plans.

## Current position

`1.0.0` is prepared for publication and installed from source while publication
remains pending. Its public executable profile includes:

- fitted single-output sklearn `LinearRegression`;
- direct fitted binary sklearn `LogisticRegression`;
- finite transformed numeric features and affine model encodings;
- homogeneous `forall` or `exists` point bindings;
- Z3 execution;
- text, JSON v6, HTML, Jupyter, records/DataFrame, provenance, and replay;
- equivalent `toetra` and `python -m toetra` command-line entry points;
- model-aware `init`, solver-free `validate` and `inspect`, formal `verify`, and
  delayed archived-evidence `replay`;
- stable process statuses, diagnostics, atomic outputs, manifests, execution
  overrides, and reproducible cross-platform smoke coverage;
- reproducible distributions, clean-install checks, outside-in rehearsal, and a
  reproducible review bundle.

The repository structure, public Python facade, documentation baseline, error
boundary, reporting contract, contribution surfaces, licensing, controlled
exposure procedure, and automation boundary are implemented foundations rather
than future roadmap items.

The [implementation status matrix](../architecture/status-matrix.md) separates
code present in the repository from built-in and publicly guaranteed routes.

## Immediate — validate the prepared stable sources

The source metadata and current contracts now describe stable V1. This does not
announce a GitHub Release, PyPI distribution, tag, or documentation deployment.
The remaining work is operational:

- expose the accepted commit and verify its public surfaces anonymously;
- after the preparation commit, rerun clean-checkout distribution and review
  gates and bind all resulting evidence to the same source state;
- exercise source, wheel, and source-distribution installation on the accepted
  Python and operating-system matrix;
- observe first-use, command-line, documentation, security, soundness, and MLOps
  integration feedback;
- correct blocking defects without widening the frozen V1 capability
  profile.

Publication remains a separate decision after gate acceptance. The historical
`1.0.0rc4` evaluation milestone is preserved in its
[release notes](../releases/1.0.0rc4.md).

## Next — publish the accepted `1.0.0` artifacts

Publication follows acceptance of the Python and process boundaries and all
remaining evidence. The release milestone includes:

- a final clean-checkout, metadata, provenance, and licensing audit;
- deterministic wheel, source distribution, and review bundle;
- wheel and source-distribution installation across the accepted compatibility
  matrix;
- demonstrations and documentation built against release artifacts;
- publication rehearsal, checksums, release notes, and rollback evidence;
- a separate, explicit publication action after acceptance.

This is a hardening milestone, not a late feature window. No calendar date
overrides a soundness, security, provenance, installation, or reproducibility
failure.

See the [prepared 1.0.0 release notes](../releases/1.0.0.md). No publication date
is set by this roadmap.

## Later — capability expansion

Post-V1 work will be selected from concrete user and integration evidence.
Candidate directions include:

- additional sklearn model families with auditable encoders;
- preprocessing-aware contracts and pipeline reconstruction;
- another framework adapter for an already-supported mathematical family;
- a second backend when it supplies a capability Z3 cannot;
- categorical, multi-output, or nonlinear reasoning;
- stronger property-based and Miova mutation campaigns;
- runtime monitoring and higher-level orchestration.

These are directions, not support promises. A model detector, schema
introspector, enum value, experimental encoder, or backend prototype does not
create a public route.

## How a capability becomes public

Model-family semantics, framework integration, and backend execution remain
separate extension responsibilities. A route becomes public only when all of
the following agree:

1. schema and observable semantics;
2. model-family lowering and formal encoding;
3. capability and numeric-compatibility policy;
4. backend translation and execution;
5. reporting, provenance, and replay;
6. unit, contract, end-to-end, clean-install, and release tests;
7. public-profile, reference, and release documentation.

Contributor entry points are documented in the
[extension architecture](../development/extensions.md), with dedicated guides
for a [model family](../development/adding-model-family.md),
[framework adapter](../development/adding-framework-adapter.md), and
[backend](../development/adding-backend.md).
