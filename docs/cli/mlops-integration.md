# MLOps integration

## Recommended gate sequence

A production pipeline should separate cheap structural checks from solver work:

```text
1. Retrieve immutable model and policy artifacts
2. Generate a starter policy with `init` when no reviewed policy exists yet
3. Validate at executable depth
4. Archive the resolved inspection JSON
5. Run formal verification
6. Archive JSON v6, HTML, and the run manifest
7. Gate explicitly on 0, 1, or 2
8. Replay archived witness/counterexample evidence when required
```


When bootstrapping a new policy, generate the declaration-bearing source once,
review it, and then version it with the pipeline configuration:

```bash
toetra init policy.toetra \
  --model artifacts/model.joblib \
  --target score \
  --dataset data/reference.csv
```

The generated smoke property is not an assurance gate. Replace it with the
intended formal properties before promoting the policy.

Example shell shape:

```bash
set -e

toetra validate policy.toetra \
  --model artifacts/model.joblib \
  --dataset data/reference.csv \
  --level executable \
  --format json \
  --output artifacts/toetra/validation.json

toetra inspect policy.toetra \
  --model artifacts/model.joblib \
  --dataset data/reference.csv \
  --format json \
  --output artifacts/toetra/inspection.json

set +e
toetra verify policy.toetra \
  --model artifacts/model.joblib \
  --dataset data/reference.csv \
  --format json \
  --output artifacts/toetra/verification.json \
  --artifacts-dir artifacts/toetra
status=$?
set -e

case "$status" in
  0) echo "Verification accepted" ;;
  1) echo "Property violation or missing witness"; exit 1 ;;
  2) echo "Verification inconclusive"; exit 2 ;;
  *) echo "Toetra process failure: $status"; exit "$status" ;;
esac

toetra replay artifacts/toetra/verification.json \
  --specification policy.toetra \
  --model artifacts/model.joblib \
  --dataset data/reference.csv \
  --format json \
  --output artifacts/toetra/replay.json
```

The example intentionally handles status `2` separately. A shell-wide
`set -e` around `verify` would erase the distinction between a formal failure,
an inconclusive result, and a process error. Replay has the same logical
`0`/`1`/`2` shape: consistent, inconsistent, or inconclusive.

## Reproducible CLI contract check

Before integrating a checkout or release candidate into an orchestrator, run
the same smoke scenario used by hosted CI:

```bash
make cli-smoke-check
```

The scenario runs outside the repository, compares CLI version metadata with
`pyproject.toml`, checks both supported entry points, and exercises the full
`init -> validate -> inspect -> verify -> replay` lifecycle. The release
installation gate invokes the same implementation against the built wheel.

## Container-job model

The first MLOps deployment target is a finite job, not a long-running service:

```text
orchestrator
→ start immutable Toetra image
→ mount or retrieve trusted artifacts
→ run validate / inspect / verify
→ publish atomic final artifacts
→ terminate with the documented process status
```

This maps naturally to Kubernetes Jobs, Argo steps, Kubeflow components,
Airflow tasks, GitHub Actions, GitLab CI, and Jenkins stages.

SIGTERM must trigger best-effort backend cancellation and status `143` when the
host allows cleanup. Consumers use complete atomic artifacts and the manifest,
not the mere existence of a partially populated directory, as completion
evidence.

## Artifact policy

Archive at least:

- the exact `.toetra` source;
- inspection JSON;
- verification JSON v6;
- HTML report for human review;
- run manifest;
- immutable model/dataset identifiers managed by the surrounding platform.

The report provenance fingerprints the content consumed by Toetra. The
surrounding platform remains responsible for access control, artifact retention,
signatures, trusted timestamps, and chain of custody.

## MLflow-style integration

An orchestrator may resolve a model URI through MLflow or another registry,
download the immutable local artifact, and then invoke Toetra with the local
path. The initial CLI does not fetch remote URIs itself.

```text
registry URI
→ orchestrator download and integrity policy
→ trusted local model artifact
→ toetra verify --model LOCAL_PATH
```

This separation keeps registry credentials and remote transport outside the
verification process while retaining Toetra content fingerprints in the
result.

## Security reminder

`.pkl` and `.joblib` deserialization may execute code. Pipelines must accept
such models only from a trusted, controlled source and should isolate execution
according to their threat model.
