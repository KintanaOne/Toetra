# Installation

FORML `1.0.0rc1` supports Python 3.11 and 3.12.

## Install the project

From a source checkout:

```bash
python -m pip install .
```

## Development environment

```bash
python -m pip install -r requirements-dev.txt
make ci
```

`make ci` is non-mutating: it checks lint, formatting, typing, generated
compatibility matrices, the public documentation contract, tests, notebooks, and
MkDocs without rewriting the checkout.

## Release validation

```bash
make release-check
make review-bundle-check
```

The first command builds reproducible wheel and source distributions and installs
the wheel in a clean virtual environment outside the repository. The second
builds the review bundle twice and compares the resulting bytes.

## Import check

```python
from forml import verify, VerificationSession, VerificationStatus
```

Normal user code should import from `forml`. The `dsl` and `model` packages expose
internal and extension contracts and are not the primary compatibility surface.
