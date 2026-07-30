# Contributing to Toetra

Thank you for helping evaluate Toetra. The project is currently at
`1.0.0rc3`: a deliberately narrow release candidate whose public behavior is
frozen while the repository is exposed and observed.

## Before opening a pull request

- Use the issue forms for reproducible defects, documentation problems, or
  post-V1 proposals.
- Do not open a public issue for a suspected vulnerability. Follow
  [SECURITY.md](SECURITY.md).
- Discuss substantial semantic, architectural, or public-contract changes
  before implementing them.
- Keep new capabilities outside P27. The CLI belongs to P28 and the stable
  release cut belongs to P29.

## Development setup

Use Python 3.11 or 3.12 from a clean checkout:

```bash
python -m pip install -e ".[dev,docs]"
make ci
```

On a Windows host where Smart App Control blocks Ruff's native executable, use
`make ci-local` locally and keep hosted CI authoritative for lint.

## Change expectations

- Keep the public nine-name Python facade and JSON v6 contract unchanged unless
  an accepted later project explicitly changes them.
- Put behavior changes behind focused unit, integration, or end-to-end tests.
- Update user documentation in the same change as user-visible behavior.
- Preserve deterministic wheel, sdist, demo, and review-bundle evidence.
- Never commit secrets, private datasets, local paths, serialized models, build
  output, or patch files.

When the change affects packaging, public examples, documentation contracts, or
release evidence, also run:

```bash
make release-check
make demo-check
make review-bundle-check
```

## Pull requests

Keep each pull request focused and explain its contract impact. Complete the
pull-request checklist, wait for all required CI jobs, and address review
comments before merge.

Contributions accepted into this repository are provided under the project's
[Apache-2.0 license](LICENSE).
