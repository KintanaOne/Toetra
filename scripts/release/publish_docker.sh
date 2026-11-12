#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_REF:?IMAGE_REF is required}"
: "${GITHUB_SHA:?GITHUB_SHA is required}"

source_image="${1:?Source image is required}"
release_version="${RELEASE_VERSION:-}"

if [ -n "$release_version" ]; then
  if [[ ! "$release_version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "Expected a stable version such as 1.0.0." >&2
    exit 1
  fi

  actual_version="$(docker run --rm --pull=never "$source_image" --version)"
  if [ "$actual_version" != "toetra $release_version" ]; then
    echo "Requested version does not match the image: $actual_version" >&2
    exit 1
  fi
fi

tags=("edge" "sha-$GITHUB_SHA")
if [ -n "$release_version" ]; then
  tags+=("$release_version")
fi

for tag in "${tags[@]}"; do
  docker tag "$source_image" "$IMAGE_REF:$tag"
done

for tag in "${tags[@]}"; do
  docker push "$IMAGE_REF:$tag"
done