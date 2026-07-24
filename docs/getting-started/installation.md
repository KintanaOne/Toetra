# Installation

FORML `1.0.0rc2` supports Python 3.11 and 3.12.

```bash
python -m pip install .
```

Development setup:

```bash
python -m pip install -r requirements-dev.txt
make ci
```

Validate the release candidate from a clean checkout:

```bash
make ci
make release-check
make review-bundle-check
```

The distribution gate builds reproducible artifacts, installs the wheel outside
the checkout, and executes both import and binary-classification public-API
probes.

```python
from forml import verify, VerificationSession, VerificationStatus
```

Normal user code imports from `forml`; `dsl` and `model` are internal/extension
surfaces.
