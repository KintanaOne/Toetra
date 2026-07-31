# Copyright and e-Soleau evidence

This procedure identifies the declared holder of Toetra's original copyright
and prepares dated evidence for the exact source state selected for public
exposure. It does not create copyright, transfer employee-created software
rights, register a trademark, or replace legal advice about disputed
ownership.

## Public ownership notice

The authoritative root notice is `COPYRIGHT.md`. It names
Tina RANDRIANARIJAONA-DUBIN as the declared copyright holder and licensor of
original Toetra source code and documentation for 2025–2026.

The claim excludes material listed in the root `THIRD_PARTY.md` file.
The project license grants noncommercial rights without transferring
copyright, while commercial rights require a separate written agreement.

## Build the exact deposit file

Use the complete canonical clone at the commit intended for public exposure:

```bash
git fetch --all --tags --prune
git status --short
git rev-parse --is-shallow-repository
git rev-parse HEAD
git rev-parse origin/main
make ci
make review-bundle
```

The status must be empty, the clone must not be shallow, and `HEAD` must equal
`origin/main`. Keep the resulting `dist/toetra_review_bundle.zip` unchanged.

The archive contains the source, documentation, licenses, ownership notice,
third-party notices, full commit identifier, and a deterministic manifest of
file sizes and SHA-256 digests. The manifest declares the copyright holder and
years but remains a project assertion; the INPI timestamp supplies independent
evidence of the deposited archive's existence and contents at the deposit
date.

## Deposit with INPI e-Soleau

In the INPI Soleau portal, use the civil identity of the declared holder and
select conservation of the file when retaining an INPI copy is desired. Upload
the exact review-bundle ZIP produced above, validate the deposit, and retain
privately:

- the unchanged ZIP;
- the full Git commit identifier;
- the ZIP SHA-256 printed by `make review-bundle`;
- the signed INPI receipt, deposit number, date, and confidential restitution
  code.

Do not commit the receipt, deposit number, restitution code, or a private INPI
account export. Record only that the deposit was completed and keep the
evidence outside the public repository.

An e-Soleau provides dated evidence; it does not grant intellectual-property
rights or certify that no employer, contributor, or other party has a competing
claim. A validated e-Soleau cannot be amended, so a materially changed source
state requires a new deposit if equivalent dated evidence is wanted.

Official guidance:

- [INPI — prepare an e-Soleau deposit](https://www.inpi.fr/realiser-demarches/propriete-intellectuelle/se-preparer-au-depot-dune-e-soleau)
- [INPI — copyright](https://www.inpi.fr/ressources/propriete-intellectuelle/droit-dauteur)
- [French Intellectual Property Code, Article L111-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000042814694)
- [French Intellectual Property Code, Article L113-9](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000039279818)
