# ADR-0028 — Adopt a `src`-Based Single-Package Layout

> Status: Accepted
> Date: 2026-07-26
> Target: P24 — Repository final polish
> Scope: Python source layout, installable namespaces, internal package boundaries, and distribution validation

## Context

Toetra currently exposes one supported public facade, `toetra`, while its
implementation is installed through three top-level Python packages:
`toetra`, `dsl`, and `model`.

The documented contract already treats `dsl` and `model` as internal, but their
presence as top-level installed packages makes them look independently public.
The repository-root layout also lets Python import local source directories
when commands run from the checkout, which can hide packaging omissions that
only appear after installing a wheel or source distribution.

P24 is the last planned repository-layout change before the V1 documentation
and release-hardening phases. Deferring the package-layout decision would make
the same migration more expensive after additional models, frameworks,
backends, documentation, and downstream users exist.

## Decision

All installable Python code will live beneath one source root and one
installable top-level package:

```text
src/
└── toetra/
    ├── __init__.py
    ├── _compiler/
    │   ├── parser/
    │   ├── ast/
    │   ├── builder/
    │   ├── semantic/
    │   └── ir/
    ├── _language/
    ├── _models/
    ├── _backends/
    ├── _runtime/
    ├── _reporting/
    ├── _provenance/
    ├── _compatibility/
    └── examples/
```

The package mapping is responsibility-based:

| Current area | Canonical destination |
|---|---|
| parser, AST, builder, semantic analysis, IR | `toetra._compiler` |
| grammar and language vocabulary | `toetra._language` |
| model loading, detection, schema, encoders, and model semantics | `toetra._models` |
| backend contracts, registry, and implementations | `toetra._backends` |
| verification orchestration and replay | `toetra._runtime` |
| text, JSON, HTML, and records rendering | `toetra._reporting` |
| provenance construction and fingerprints | `toetra._provenance` |
| numeric and framework compatibility contracts | `toetra._compatibility` |

The migration will be direct. P24 will not preserve installed `dsl` or `model`
compatibility packages, aliases, or forwarding modules.

The supported public import surface remains the explicit facade exported by
`toetra.__all__`. The underscore-prefixed packages are implementation details;
their existence does not create a compatibility guarantee.

Development environments will install Toetra in editable mode:

```bash
python -m pip install -e ".[dev,docs]"
```

Release validation will continue to build wheel and source distributions,
install them in clean environments, and execute probes from outside the
repository checkout. The `src` layout complements those checks; it does not
replace them.

## Rationale

A single top-level installed namespace aligns the physical distribution with
the public contract. Responsibility-based internal packages also match the
documented architecture: language and parsing, AST, semantic
analysis, IR1, IR2, model bridge, backend, runtime, reporting, and provenance.

The `src` boundary reduces accidental imports from the checkout and makes
package discovery explicit. Performing the migration before V1 avoids carrying
known structural debt into later model and backend expansion.

## Consequences

- the wheel and source distribution will contain `toetra` as their only
  installable top-level package;
- every internal absolute import will move beneath `toetra`;
- setuptools, Pyright, tests, demos, release probes, package data, and review
  bundle paths must change in the same patch family;
- advanced users may inspect private modules, but only names re-exported by the
  public facade are stable;
- contributors must use an editable installation rather than relying on the
  repository root being importable;
- clean wheel and source-distribution tests remain mandatory.

## Alternatives considered

### Keep `toetra`, `dsl`, and `model` as top-level packages

Rejected because it preserves an ambiguous public surface and leaves the
checkout-import trap in place.

### Move everything beneath root-level `toetra/` without `src/`

Rejected for the long-term layout because it solves the namespace ambiguity but
not the isolation between repository files and the installed distribution.

### First move to `toetra._dsl` and `toetra._model`, then reorganize later

Rejected because it would require two large import migrations. P24 will move
directly to the responsibility-based final structure.

### Split internal subsystems into separately distributed packages

Rejected for V1. Toetra has one release lifecycle and one supported public API;
separate distributions would add coordination and compatibility overhead without
an established need.

## Acceptance criteria

P24 is complete only when:

```python
import importlib.util
import toetra

assert importlib.util.find_spec("toetra") is not None
assert importlib.util.find_spec("dsl") is None
assert importlib.util.find_spec("model") is None
```

and the release checks prove that wheel, source distribution, documentation,
demos, and review bundles use the canonical layout from clean environments.
