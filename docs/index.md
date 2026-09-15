---
hide:
  - toc
---

<div class="toetra-hero" markdown>
  <div class="toetra-hero__brand"><img src="assets/brand/toetra-lockup-horizontal-reversed.png" alt="Toetra" /></div>
  <div class="toetra-hero__art" aria-hidden="true"><img src="assets/brand/toetra-symbol-color-1024.png" alt="" /></div>

  <span class="toetra-eyebrow">Evaluation release · 1.0.0rc4</span>

# State the behavior.<br /><span>Get the evidence.</span>

  Toetra is a declarative behavioral-specification and formal-verification
  framework for machine-learning models. Express a property over an explicit
  input domain, route it to Z3, and inspect the resulting evidence.

  [Start with Toetra](getting-started/overview.md){ .md-button .md-button--primary }
  [Explore on GitHub](https://github.com/KintanaOne/Toetra){ .md-button }
</div>

<div class="toetra-facts">
  <div><span>Language</span><strong><code>.toetra</code></strong></div>
  <div><span>Models</span><strong>Linear · binary logistic</strong></div>
  <div><span>Backend</span><strong>Z3</strong></div>
  <div><span>Evidence</span><strong>Report · provenance · replay</strong></div>
</div>

## From intent to inspectable evidence

Toetra gives data and ML practitioners a human-readable way to ask a precise
behavioral question without exposing solver formulas or framework internals.

<div class="toetra-card-grid" markdown>
  <div class="toetra-card" markdown>
### Declare the intent

  Write the expected behavior, its scope, and its input domain in the Toetra
  Specification Language.
  </div>

  <div class="toetra-card" markdown>
### Compile and route

  Toetra validates the specification, lowers its semantics, and selects a
  compatible verification route.
  </div>

  <div class="toetra-card" markdown>
### Inspect the result

  Read a proof, counterexample, witness, explicit no-witness outcome, or
  principled unknown—with provenance and concrete replay.
  </div>
</div>

!!! warning "Precise evaluation scope"

    `1.0.0rc4` is an evaluation release candidate, not the stable `1.0.0`
    release. It is installed from a source checkout or source archive and is not
    published on PyPI. The public V1 profile currently supports fitted
    single-output scikit-learn `LinearRegression` and direct fitted binary
    `LogisticRegression` models over finite transformed numeric features.

    [Read the authoritative V1 support profile](public-v1-profile.md)

## Run the self-contained verification

From the repository root with Python 3.11 or 3.12:

```bash
python -m pip install .
python -m demo.quickstart.verify_model --demo
toetra --help
```

The demo should produce one `PROVED` result and one `WITNESS`, then clean up
its temporary model and dataset.

<div class="toetra-path-grid" markdown>
  <div markdown>
  **New to Toetra**

  [Installation and availability](getting-started/installation.md)<br />
  [Your first Toetra properties](getting-started/first-property.md)
  </div>

  <div markdown>
  **Using the framework**

  [Public Python API](api-reference/index.md)<br />
  [CLI and automation](cli/overview.md)
  </div>

  <div markdown>
  **Understanding the system**

  [Architecture overview](architecture/overview.md)<br />
  [Language reference](language/overview.md)
  </div>

  <div markdown>
  **Checking the boundary**

  [Compatibility matrices](generated/numeric-compatibility-matrices.md)<br />
  [1.0.0rc4 release notes](releases/1.0.0rc4.md)
  </div>
</div>

## Verification pipeline

<div class="toetra-pipeline" aria-label="Toetra verification pipeline">
  <span>Specification</span>
  <i aria-hidden="true">→</i>
  <span>Semantic validation</span>
  <i aria-hidden="true">→</i>
  <span>IR and model lowering</span>
  <i aria-hidden="true">→</i>
  <span>Capability route</span>
  <i aria-hidden="true">→</i>
  <span>Z3</span>
  <i aria-hidden="true">→</i>
  <span>Evidence and replay</span>
</div>

The built-in routes reason over declared exact-real affine abstractions. Reports
preserve this trust boundary rather than claiming bit-exact framework execution.
