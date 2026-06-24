#!/usr/bin/env bash
# Fetch the COLMAP golden dataset defined in tests/data/golden/colmap.yml
#
# Installs a sorted subset of images into tests/data/golden/images/ for
# acceptance tests. Images are downloaded from the network and are NOT committed
# to the repository.
#
# Usage (from repository root):
#   ./scripts/fetch_golden_colmap.sh
#   ./scripts/fetch_golden_colmap.sh --all     # all 128 images (slow)
#   ./scripts/fetch_golden_colmap.sh --count 30

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOLDEN_DIR="${REPO_ROOT}/tests/data/golden"
IMAGES_DIR="${GOLDEN_DIR}/images"
MANIFEST="${GOLDEN_DIR}/colmap.yml"

URL="https://github.com/colmap/colmap/releases/download/3.11.1/south-building.zip"
SUBSET_COUNT=20
USE_ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      USE_ALL=true
      shift
      ;;
    --count)
      SUBSET_COUNT="${2:?--count requires a number}"
      shift 2
      ;;
    -h | --help)
      echo "Usage: $0 [--all | --count N]"
      echo "Manifest: ${MANIFEST}"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "${MANIFEST}" ]]; then
  echo "Missing manifest: ${MANIFEST}" >&2
  exit 1
fi

command -v curl >/dev/null
command -v unzip >/dev/null

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "Manifest: ${MANIFEST}"
echo "Downloading COLMAP south-building dataset..."
curl -fsSL "${URL}" -o "${TMP_DIR}/south-building.zip"

echo "Extracting JPEG images..."
unzip -q "${TMP_DIR}/south-building.zip" "south-building/images/*.JPG" -d "${TMP_DIR}"

mkdir -p "${IMAGES_DIR}"
find "${IMAGES_DIR}" -mindepth 1 -delete

if [[ "${USE_ALL}" == true ]]; then
  echo "Installing all images into ${IMAGES_DIR}..."
  cp "${TMP_DIR}/south-building/images/"*.JPG "${IMAGES_DIR}/"
else
  echo "Installing ${SUBSET_COUNT} images (sorted) into ${IMAGES_DIR}..."
  find "${TMP_DIR}/south-building/images" -type f -name '*.JPG' | sort \
    | head -n "${SUBSET_COUNT}" \
    | while read -r src; do
      cp "${src}" "${IMAGES_DIR}/"
    done
fi

COUNT="$(find "${IMAGES_DIR}" -type f | wc -l | tr -d ' ')"
echo "Done. ${COUNT} images ready in ${IMAGES_DIR}."
echo "Next: pytest -m acceptance"
