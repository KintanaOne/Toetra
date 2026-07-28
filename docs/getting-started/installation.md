# Installation

Toetra `1.0.0rc3` supports Python 3.11 and 3.12.

```bash
python -m pip install .
```

Development setup:

```bash
python -m pip install -r requirements-dev.txt
make ci
```

If Windows Smart App Control blocks Ruff's unsigned native executable, use the
non-Ruff local gate and rely on hosted CI for the authoritative lint result:

```bash
make ci-local
```

Validate the release candidate from a clean checkout:

```bash
make ci
make demo-check
make release-check
make review-bundle-check
```

The distribution gate builds reproducible artifacts, installs the wheel outside
the checkout, and executes both import and binary-classification public-API
probes.

```python
from toetra import verify, VerificationSession, VerificationStatus
```

Normal user code imports only from `toetra`. The former top-level `dsl` and
`model` packages are not installed. Modules under `toetra._*` are private and
carry no compatibility guarantee.

See the [repository contract](../contracts/repository-contract.md) for the
frozen package, test, demo, documentation, and automation boundaries. Release
validation deliberately keeps `ci`, demonstrations, distribution, and
review-bundle reproducibility as explicit gates.
