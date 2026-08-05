# Installation and availability

Toetra `1.0.0rc3` supports Python 3.11 and 3.12.

## Release-candidate availability

`1.0.0rc3` is an evaluation release candidate, not the stable `1.0.0` release.
It is not currently published on PyPI. The command `pip install toetra`
is not a documented installation path.

Install the candidate from a source checkout or extracted source archive. From
its repository root:

```bash
python -m pip install .
```

Confirm that the public package is importable:

```bash
python -c "from toetra import verify; print('Toetra import: OK')"
```

Normal user code imports only from `toetra`. The former top-level `dsl` and
`model` packages are not installed. Modules under `toetra._*` are private and
carry no compatibility guarantee.

## First run

From the same repository root:

```bash
python -m demo.quickstart.verify_model --demo
```

The quickstart trains a temporary scikit-learn `LinearRegression` model,
verifies two regression properties through `toetra.verify(...)`, and removes
its temporary files. It should finish with one `PROVED` result and one
`WITNESS`.

After installation, its standalone runner can also be copied outside the
checkout:

```bash
cp demo/quickstart/verify_model.py /tmp/toetra-quickstart.py
cd /tmp
python toetra-quickstart.py --demo
```

The release gate executes this outside-checkout form against a clean-installed
wheel without the source repository on the import path.

For trusted local model artifacts, the installed process interface can first
generate an executably validated starter specification and then run the same
workflow:

```bash
toetra init policy.toetra --model model.joblib --target score \
  --dataset reference.csv
toetra validate policy.toetra --model model.joblib --dataset reference.csv
toetra inspect policy.toetra --model model.joblib --dataset reference.csv
toetra verify policy.toetra --model model.joblib --dataset reference.csv \
  --format json --artifacts-dir artifacts/toetra
toetra replay artifacts/toetra/toetra-verification-report.json \
  --specification policy.toetra --model model.joblib --dataset reference.csv
```

`verify` returns `0` for positive conclusions, `1` for a formal failure, and `2`
for `UNKNOWN`. `replay` uses the same statuses for consistent, inconsistent, and
inconclusive concrete evidence. The JSON v6 and HTML verification files are each
committed atomically, and the verification manifest is written last.

## Development setup

Install the pinned development and documentation dependencies in editable mode:

```bash
python -m pip install -e ".[dev,docs]"
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

The four commands are separate quality, demonstration, distribution, and
review-bundle gates. After committing a clean candidate,
`make outside-in-check` repeats the documented first use and all four gates from
an exact fresh clone. See the
[repository contract](../contracts/repository-contract.md) for the frozen
package, test, demo, documentation, and automation boundaries.
