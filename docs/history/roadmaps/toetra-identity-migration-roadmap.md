# Canonical Toetra identity

> **Status:** Delivered in `1.0.0rc3` on 2026-07-26

After the regression and binary-classification semantics stabilized, the project
adopted Toetra as its single public identity before any stable release created a
legacy compatibility obligation.

## Public surface

The migration aligned:

- the Python distribution and sole public import namespace as `toetra`;
- the language name as Toetra Specification Language;
- the specification extension as `.toetra`;
- repository, documentation, examples, demos, and release metadata;
- persistent report, provenance, replay, compatibility, and artifact
  identifiers.

JSON reporting advanced to schema v6 so serialized identities and software
provenance fields could change explicitly. Historical schemas remained as
golden compatibility records rather than current outputs.

## Direct cutover

No compatibility package or dual file extension was introduced because no
project-controlled stable release had established the former development
identity as a public contract. Clean-install and repository checks reject
obsolete namespaces and extensions.

The cutover preserved the verification semantics and model routes accepted in
`1.0.0rc2`. The outcome became `1.0.0rc3`; the architectural decision is
recorded in
[ADR-0027](../../adr/ADR-0027-adopt-toetra-as-canonical-identity.md).
