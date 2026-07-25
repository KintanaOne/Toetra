# ADR-0027 — Adopt Toetra as the Canonical Product Identity

> Status: Accepted
> Date: 2026-07-24
> Target release: `1.0.0rc3`
> Scope: product identity, Python distribution, public namespace, specification language, persistent identifiers, repository and documentation

## Context

The project reached `1.0.0rc2` with a stable public verification route for
single-output affine regression and direct binary logistic classification.
Before the first general-availability release, the name `FORML` was found to
conflict with an existing Python distribution and can no longer serve as an
unambiguous public identity.

The existing name is present across multiple independent compatibility
surfaces:

- the product and documentation brand;
- the Python distribution and public import namespace;
- the repository and documentation URLs;
- the specification language name and `.forml` extension;
- grammar, fixture, example and demo filenames;
- JSON report schema identifiers and other persistent machine identifiers;
- release, review-bundle and generated-artifact names.

A partial rename would create two apparent products and make provenance,
installation and support contracts ambiguous. Because no project-controlled
stable `forml` distribution has been released, preserving a public compatibility
layer would introduce long-term debt without protecting an established user
base.

## Decision

The canonical public identity is **Toetra**.

The following names are normative:

| Surface | Canonical identity |
|---|---|
| Product and documentation brand | **Toetra** |
| Python distribution | `toetra` |
| Public Python namespace | `toetra` |
| Repository identity | `KintanaOne/Toetra` |
| Documentation site | the Toetra GitHub Pages site |
| Specification language | **Toetra Specification Language** |
| Specification extension | `.toetra` |
| Grammar filenames | `toetra_grammar.ebnf`, `toetra_grammar.lark` |
| Persistent project identifiers | `toetra.*` |
| Review bundle | `toetra_review_bundle.zip` |

The abbreviation `TSL` is not part of the public vocabulary. Documentation
must use the complete name **Toetra Specification Language** when a language
name is required, and simply “Toetra specification” where that is clearer.

The migration is a strict cutover:

- no public `forml` import alias is retained;
- no `.forml` compatibility extension is retained;
- no dual-brand documentation is maintained;
- no new release artifact may contain a mixed FORML/Toetra identity;
- historical references are limited to this ADR, migration notes and changelog
  entries where the former identity is necessary to explain the transition.

The current internal `dsl` and `model` package boundaries remain unchanged for
P23. They are internal implementation namespaces and moving them beneath
`toetra` would be an architectural refactor unrelated to the identity cutover.

The first release candidate under the new identity is `1.0.0rc3`. Renaming
persistent JSON schema identifiers is an incompatible machine-contract change,
so the report schema advances from v5 to v6 during P23 even when the report
shape remains otherwise equivalent.

## Migration invariants

Every P23 patch must preserve these invariants:

1. Verification semantics, backend conclusions and concrete replay behavior do
   not change as a consequence of the rename.
2. Existing regression and classification coverage remains green after each
   atomic patch.
3. A release artifact exposes exactly one canonical identity.
4. Public imports, file extensions, documentation examples and persistent
   identifiers change together with the tests that define their contracts.
5. Old identity detection becomes a release gate before `1.0.0rc3` is built.

## Migration order

The cutover proceeds in dependency order:

1. freeze the identity decision and migration inventory;
2. migrate the distribution and public Python facade;
3. migrate the specification extension, parser API names, grammars and samples;
4. migrate persistent machine identifiers and advance the report schema;
5. migrate documentation, demos, metadata and release engineering;
6. enable the old-identity gate, rename the remote repository and publish the
   candidate from the renamed repository.

A patch may temporarily leave the source tree in an intentionally transitional
state, but it must remain testable and the final release gates must reject any
unapproved former-identity occurrence.

## Rationale

A single identity minimizes user confusion, avoids PyPI ambiguity and keeps
installation, imports, files, reports and documentation aligned. Performing the
cutover before V1 GA is less costly and safer than carrying aliases throughout
the 1.x line.

Advancing the report schema version makes the changed identifier explicit to
machine consumers instead of presenting an incompatible identifier change as
an additive v5 update.

Keeping `dsl` and `model` in place limits P23 to an identity migration and avoids
mixing it with a package-layout redesign.

## Consequences

- `pip install toetra` and `from toetra import ...` become the only supported
  public Python entry points.
- `.toetra` becomes the only supported public specification extension.
- consumers of JSON reports must accept schema v6 and the `toetra.*` schema
  identifier.
- links and artifacts referring to the former repository name must be updated
  before publication.
- users of unpublished development snapshots may need to rename imports and
  specification files manually.
- the public behavior stabilized in `1.0.0rc2` remains the semantic baseline for
  `1.0.0rc3`.

## Alternatives considered

### Keep FORML as the product while changing only the PyPI name

Rejected because the distribution, import namespace and product would diverge,
making installation instructions and provenance needlessly confusing.

### Publish compatibility packages or import aliases

Rejected because there is no established project-controlled public package to
protect and the alias would reserve permanent maintenance work for no V1 user
benefit.

### Rename all internal packages beneath `toetra`

Deferred because this is an architectural package-layout change, not required
for a coherent public identity.

### Keep `.forml` as the language extension

Rejected because the file format would continue to advertise the superseded
identity and create ambiguity in tooling and documentation.

## Release gate

The final P23 release gate is:

```bash
make ci
make release-check
make review-bundle-check
git diff --check
```

It is followed by an explicit former-identity scan with only documented
historical exceptions allowed.
