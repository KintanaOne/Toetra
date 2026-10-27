# PyPI publication

Publication remains pending. Adding this workflow does not publish Toetra or
change its license. The workflow is deliberately manual, uses Trusted Publishing
(OIDC), and never receives a permanent PyPI token.

## One-time configuration

On PyPI, register the GitHub publisher using these exact values:

| Field | Value |
|---|---|
| Project | `toetra` |
| Owner | `KintanaOne` |
| Repository | `Toetra` |
| Workflow filename | `publish-pypi.yml` |
| Environment | `pypi` |

In GitHub **Settings → Environments**, create `pypi`, restrict deployment to
`main`, and configure a required reviewer when available and desired. Allow the
maintainer to approve their own deployment if they are the only reviewer.
Ensure the repository action allowlist includes the pinned
`pypa/gh-action-pypi-publish` action as well as the GitHub actions already used.
No `PYPI_TOKEN` secret is required.

## Publish a version

1. Commit and push the reviewed preparation to `main`, including the workflow
   and the updated checks. The workflow must exist on the default branch.
2. Open **Actions → Publish Toetra to PyPI → Run workflow**.
3. Select `main` and enter the exact version from `pyproject.toml`, initially
   `1.0.0`. Clicking **Run workflow** authorizes a real upload after validation.
4. The workflow calls the existing CI for this exact commit: both Python quality
   jobs, the single reproducible build, demos, bundle, and all eight installation
   combinations. A failed or skipped validation prevents publication.
5. Approve the `pypi` environment deployment if an approval is configured.
6. The upload job downloads the archives from the same workflow run. It checks
   their SHA-256 hashes, exact names, metadata, source version, and requested
   stable version. Only the two archives are copied to `publish-dist/`; the
   checksum file is retained separately and is not uploaded as a Python package.
7. The pinned PyPA action uploads those exact bytes to PyPI using OIDC and
   generates attestations. Nothing is rebuilt in the upload job.

Only a manual run from `KintanaOne/Toetra` on `main` can publish. Pushes and pull
requests keep running validation without publication rights. Concurrent
publication runs are serialized and are never cancelled during an upload.

## Verify and recover

After a successful upload, check the PyPI project/version and install
`toetra==1.0.0` in a new environment outside the checkout. Run `toetra --version`
and the standalone quickstart. Then update the current documentation and its
status checks together to reflect the actual published state. Historical RC
notes remain unchanged. This workflow does not create a Git tag or GitHub Release.

The action fails on an existing file rather than silently skipping it. PyPI
does not allow overwriting published files. If an upload is interrupted, inspect
which files reached PyPI before attempting recovery; do not replace archives
under the same filenames. Publish a new version or perform a reviewed upload of
only the missing original archive, as appropriate. For a defective release,
consider yanking it and shipping a corrected version.

References: [Trusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
and [new projects](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
