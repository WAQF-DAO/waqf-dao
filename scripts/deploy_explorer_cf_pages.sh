#!/usr/bin/env bash
set -euo pipefail

export PATH="/root/.foundry/bin:/home/amalproduktif/.nvm/versions/node/v22.23.4/bin:/root/.local/bin:${PATH}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXPLORER_DIR="${ROOT_DIR}/apps/explorer"
PROJECT_NAME="${CF_PAGES_PROJECT:-waqf-dao-explorer}"
BRANCH_NAME="${CF_PAGES_BRANCH:-main}"
WRANGLER_PREFIX="/home/amalproduktif/amalproduktif.or.id"
STAGING_DIR="/home/amalproduktif/.cache/waqf-dao-pages-dist"
NODE_BIN_PATH="/home/amalproduktif/.nvm/versions/node/v22.23.4/bin:/usr/local/bin:/usr/bin:/bin"

cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

echo "=== [1/4] Typecheck, Merkle parity tests & Vite production build ==="
cd "${EXPLORER_DIR}"
npm run typecheck
npm run test:merkle
npm run build

echo "=== [2/4] Staging dist/ for amalproduktif Wrangler session ==="
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}"
cp -a "${EXPLORER_DIR}/dist/." "${STAGING_DIR}/"
chown -R amalproduktif:amalproduktif "${STAGING_DIR}"

echo "=== [3/4] Ensuring Cloudflare Pages project '${PROJECT_NAME}' exists ==="
cd "${WRANGLER_PREFIX}"
if ! sudo -u amalproduktif env -u CLOUDFLARE_API_TOKEN PATH="${NODE_BIN_PATH}" \
  npx wrangler pages project list 2>/dev/null | grep -qw "${PROJECT_NAME}"; then
  sudo -u amalproduktif env -u CLOUDFLARE_API_TOKEN PATH="${NODE_BIN_PATH}" \
    npx wrangler pages project create "${PROJECT_NAME}" --production-branch "${BRANCH_NAME}"
fi

echo "=== [4/4] Deploying '${PROJECT_NAME}' to Cloudflare Pages ==="
sudo -u amalproduktif env -u CLOUDFLARE_API_TOKEN PATH="${NODE_BIN_PATH}" \
  npx wrangler pages deploy "${STAGING_DIR}" \
  --project-name "${PROJECT_NAME}" \
  --branch "${BRANCH_NAME}" \
  --commit-dirty=true
