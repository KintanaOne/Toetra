# Documentation and user experience

> **Status:** Delivered in late July 2026 for the `1.0.0rc3` evaluation
> candidate

With the implementation and repository structure stable, the documentation was
rebuilt around the product that actually existed rather than planned
capabilities.

## Documentation baseline

The public reference established clear authorities for:

- the nine-symbol Python facade and `verify(...)` workflow;
- the as-built compiler, model bridge, runtime, and reporting pipeline;
- language syntax, semantics, and executable support levels;
- regression and direct binary-classification routes;
- model-family, framework-adapter, and backend extension responsibilities;
- current limitations and release-candidate availability.

Canonical snippets became executable and CI-checked so the README, onboarding,
examples, and reference pages could not silently diverge.

## Error and reporting experience

Syntax, construction, semantic, artifact, model, compatibility, routing, and
backend failures were normalized at the public boundary while preserving their
owning stage and chained private cause. Stable diagnostic codes, remediation
hints, and source context made failures actionable without collapsing them into
logical conclusions.

Terminal text, HTML/Jupyter, records/DataFrame, and JSON v6 were aligned around
one conclusion, execution context, numeric trust boundary, evidence,
provenance, and diagnostic contract.

## First use and public evaluation

The quickstart became copyable outside the repository and executable against a
clean-installed wheel. Public notebooks were checked both from the repository
root and their own directories. The README and documentation landing page now
state that `1.0.0rc3` is source-installed, not published on PyPI, and not the
stable release.

Repository audit, contribution and security surfaces, outside-in rehearsal,
controlled exposure, reproducible artifacts, provenance, copyright, and
noncommercial licensing completed the preparation for public evaluation.
