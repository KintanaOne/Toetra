# ADR-0031 — Adopt noncommercial and separate commercial licensing

- **Status:** Accepted
- **Date:** 2026-07-31

## Context

Apache-2.0 permits commercial use, redistribution, hosted services, and
commercial derivatives without a separate agreement. That does not preserve
the intended launch boundary for Toetra: the source should be publicly
reviewable and usable for noncommercial purposes without granting third parties
the right to launch a competing commercial service before OntoLogIA.

The repository has not yet completed its controlled public exposure. The
licensing decision must therefore be corrected before the accepted public
commit is selected.

## Decision

Toetra source code and original documentation are offered under the
PolyForm Noncommercial License 1.0.0, identified by SPDX as
`PolyForm-Noncommercial-1.0.0`.

Use outside the purposes permitted by that license requires a separate written
commercial agreement with the Toetra licensor. The public repository does not
itself grant the right to use Toetra for a commercial hosted-service,
managed-service, or SaaS offering.

The repository describes this route in `COMMERCIAL_LICENSE.md` but does not
publish generic commercial terms. A commercial license exists only when a
separate written agreement is executed.

This license is source-available and noncommercial, not open source under the
Open Source Definition. Public documentation must use those terms accurately.

Third-party material keeps its own license. In particular, the Cleveland
dataset remains under CC BY 4.0 and is not relicensed by PolyForm.

Until an explicit contributor agreement is available and accepted, outside
code or documentation contributions are not merged. Public issues, reviews,
reproductions, and proposals remain welcome.

## Consequences

- README, package metadata, distribution artifacts, public-surface checks, and
  review bundles must agree on `PolyForm-Noncommercial-1.0.0`.
- GitHub may report the license as `NOASSERTION` or leave its detected license
  empty; the authoritative proof is the exact public `LICENSE` file and package
  metadata.
- Copies previously distributed under Apache-2.0, if any, keep the rights
  already granted for those copies. This decision governs distributions made
  from this commit onward.
- Before adopting this ADR, the repository owner confirms authority to
  relicense all Toetra-originated material in the accepted commit.

## Supersedes

This ADR supersedes only the Apache-2.0 licensing decision in ADR-0022. The
frozen V1 functionality, compatibility, and release gates remain unchanged.
