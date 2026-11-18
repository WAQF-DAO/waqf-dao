#!/usr/bin/env bash
set -euo pipefail

export PATH="/root/.foundry/bin:/home/amalproduktif/.nvm/versions/node/v22.23.4/bin:/root/.local/bin:${PATH}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== [1/6] Smart Contracts (Foundry) ==="
(cd "${ROOT_DIR}/packages/contracts" && forge test -vv)

echo "=== [2/6] ERP Merkle Oracle Bridge ==="
(cd "${ROOT_DIR}/packages/oracle-bridge" && python3 -m unittest discover -s tests -v)

echo "=== [3/6] AI CIO Forensic & Compliance Sentinel ==="
(cd "${ROOT_DIR}/packages/ai-cio-sentinel" && python3 -m unittest discover -s tests -v)

echo "=== [4/6] Odoo 20.0 Addon Bytecode Check ==="
python3 -m compileall -q "${ROOT_DIR}/odoo-addons/waqf_dao_oracle"
echo "odoo-addons/waqf_dao_oracle compileall: PASS"

echo "=== [5/6] Web3 Explorer Typecheck, Merkle Parity & Vite Build ==="
(cd "${ROOT_DIR}/apps/explorer" && npm run typecheck && npm run test:merkle && npm run build)

echo "=== [6/6] Repository Hygiene & Zero-Spill Audit ==="
python3 "${ROOT_DIR}/scripts/audit_hygiene.py"
