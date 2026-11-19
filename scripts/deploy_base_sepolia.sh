#!/usr/bin/env bash
set -euo pipefail

export PATH="/root/.foundry/bin:/home/amalproduktif/.nvm/versions/node/v22.23.4/bin:/root/.local/bin:${PATH}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACTS_DIR="${ROOT_DIR}/packages/contracts"
FIXTURE_PATH="${ROOT_DIR}/packages/oracle-bridge/fixtures/genesis_epoch_2026_11.json"
MANIFEST_PATH="${ROOT_DIR}/deployments/base-sepolia.json"

RPC_URL="${BASE_SEPOLIA_RPC_URL:-https://sepolia.base.org}"
KEYSTORE_PATH="${WAQF_KEYSTORE_PATH:-/root/.foundry/keystores/waqf-dao-sepolia}"
PASSWORD_FILE="${WAQF_PASSWORD_FILE:-/root/.waqf-dao-sepolia.pass}"
MIN_WEI="${MIN_DEPLOYER_WEI:-500000000000000}" # 0.0005 ETH minimum safety threshold
BLOCKSCOUT_API="${BLOCKSCOUT_VERIFIER_URL:-https://base-sepolia.blockscout.com/api}"

if [[ ! -f "${KEYSTORE_PATH}" || ! -f "${PASSWORD_FILE}" ]]; then
  echo "ERROR: Missing keystore (${KEYSTORE_PATH}) or password file (${PASSWORD_FILE})." >&2
  exit 1
fi

DEPLOYER_ADDR="$(cast wallet address --keystore "${KEYSTORE_PATH}" --password-file "${PASSWORD_FILE}")"
BALANCE_WEI="$(cast balance "${DEPLOYER_ADDR}" --rpc-url "${RPC_URL}")"
BALANCE_ETH="$(cast balance "${DEPLOYER_ADDR}" --rpc-url "${RPC_URL}" --ether)"

echo "Deployer Address : ${DEPLOYER_ADDR}"
echo "Base Sepolia Bal : ${BALANCE_ETH} ETH (${BALANCE_WEI} wei)"

if ! python3 -c "import sys; sys.exit(0 if int('${BALANCE_WEI}') >= int('${MIN_WEI}') else 1)"; then
  echo "ABORT: Insufficient Base Sepolia ETH on ${DEPLOYER_ADDR}." >&2
  echo "Dry-run gas estimate is ~0.00018 ETH; please fund at least 0.002 ETH (0.0005 ETH minimum) on Chain 84532 and re-run." >&2
  exit 2
fi

echo "=== [1/4] Broadcasting DeployGenesisPools.s.sol to Base Sepolia (84532) ==="
cd "${CONTRACTS_DIR}"
forge script script/DeployGenesisPools.s.sol \
  --rpc-url "${RPC_URL}" \
  --keystore "${KEYSTORE_PATH}" \
  --password-file "${PASSWORD_FILE}" \
  --sender "${DEPLOYER_ADDR}" \
  --broadcast

BROADCAST_JSON="${CONTRACTS_DIR}/broadcast/DeployGenesisPools.s.sol/84532/run-latest.json"
if [[ ! -f "${BROADCAST_JSON}" ]]; then
  echo "ERROR: Expected broadcast artifact not found at ${BROADCAST_JSON}" >&2
  exit 1
fi

AUDIT_REGISTRY="$(python3 -c '
import json, sys
data = json.load(open(sys.argv[1]))
for tx in data.get("transactions", []):
    if tx.get("transactionType") == "CREATE" and tx.get("contractName") == "WaqfAuditRegistry":
        print(tx["contractAddress"])
        sys.exit(0)
sys.exit(1)
' "${BROADCAST_JSON}")"

echo "Live WaqfAuditRegistry: ${AUDIT_REGISTRY}"

echo "=== [2/4] Notarizing Genesis Epoch 2026-11 on-chain ==="
readarray -t CAST_ARGS < <(python3 -c '
import json, sys
fix = json.load(open(sys.argv[1]))
for arg in fix["notarization_payload"]["cast_args"]:
    print(arg)
' "${FIXTURE_PATH}")

NOTARIZE_TX_JSON="$(cast send "${AUDIT_REGISTRY}" \
  "notarizeEpoch(string,bytes32,uint256,uint256,uint256,uint256,bytes32)" \
  "${CAST_ARGS[@]}" \
  --rpc-url "${RPC_URL}" \
  --keystore "${KEYSTORE_PATH}" \
  --password-file "${PASSWORD_FILE}" \
  --json)"

NOTARIZE_TX_HASH="$(python3 -c 'import json, sys; print(json.loads(sys.stdin.read())["transactionHash"])' <<< "${NOTARIZE_TX_JSON}")"
echo "Epoch 2026-11 Notarized Tx: ${NOTARIZE_TX_HASH}"

echo "=== [3/4] Verifying epochCount & all 10 Merkle leaves against Base Sepolia ==="
EPOCH_COUNT="$(cast call "${AUDIT_REGISTRY}" "epochCount()(uint256)" --rpc-url "${RPC_URL}")"
echo "On-chain epochCount: ${EPOCH_COUNT}"

python3 - "${FIXTURE_PATH}" "${AUDIT_REGISTRY}" "${RPC_URL}" <<'PY'
import json, subprocess, sys

fixture = json.load(open(sys.argv[1]))
registry = sys.argv[2]
rpc_url = sys.argv[3]

for leaf in fixture["leaves"]:
    proof_arg = "[" + ",".join(leaf["proof"]) + "]"
    out = subprocess.check_output(
        [
            "cast", "call", registry,
            "verifyNotarizedLeaf(uint256,bytes32,bytes32[])(bool)",
            "0", leaf["leaf_hash"], proof_arg,
            "--rpc-url", rpc_url,
        ],
        text=True,
    ).strip()
    if out != "true":
        raise SystemExit(f"Leaf #{leaf['index']} verification failed: {out}")
print(f"Verified all {len(fixture['leaves'])} Genesis Epoch leaves on-chain: PASS")
PY

echo "=== [4/4] Updating manifest & running Blockscout source verification ==="
python3 - "${BROADCAST_JSON}" "${MANIFEST_PATH}" "${DEPLOYER_ADDR}" "${NOTARIZE_TX_HASH}" "${FIXTURE_PATH}" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

broadcast = json.loads(Path(sys.argv[1]).read_text())
manifest_path = Path(sys.argv[2])
deployer = sys.argv[3]
notarize_tx = sys.argv[4]
fixture_path = Path(sys.argv[5])

contracts = {}
for tx in broadcast.get("transactions", []):
    if tx.get("transactionType") == "CREATE" and tx.get("contractName"):
        contracts[tx["contractName"]] = {
            "address": tx["contractAddress"],
            "deployTxHash": tx.get("hash"),
        }

manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
manifest.update({
    "network": "Base Sepolia",
    "chainId": 84532,
    "rpcUrl": "https://sepolia.base.org",
    "blockscoutUrl": "https://base-sepolia.blockscout.com",
    "basescanUrl": "https://sepolia.basescan.org",
    "explorerUrl": manifest.get("explorerUrl", "https://waqf-dao-explorer.pages.dev"),
    "status": "deployed_and_notarized",
    "deployedAtUtc": datetime.now(timezone.utc).isoformat(),
    "deployerAddress": deployer,
    "contracts": contracts,
    "genesisEpoch": {
        "epochId": 0,
        "epochLabel": "2026-11",
        "merkleRoot": "0x8847ae1a98d62b44dbbfe44900cce0620b7e13914d9bd509d3d694f8fb3921cc",
        "leafCount": 10,
        "notarized": True,
        "txHash": notarize_tx,
    },
})
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

fixture = json.loads(fixture_path.read_text())
fixture["notarization_payload"]["registry_address"] = contracts["WaqfAuditRegistry"]["address"]
fixture_path.write_text(json.dumps(fixture, indent=2) + "\n")
PY

# Keyless source verification on Blockscout (best-effort per deployed contract)
python3 - "${MANIFEST_PATH}" "${BLOCKSCOUT_API}" <<'PY'
import json, subprocess, sys

manifest = json.load(open(sys.argv[1]))
verifier_url = sys.argv[2]
deployer = manifest["deployerAddress"]
contracts = manifest["contracts"]
reserve = contracts["LocalHalalReserveToken"]["address"]
sbt = contracts["WaqfIdentitySBT"]["address"]
oracle = contracts["ShariahOracle"]["address"]
splitter = contracts["PSAK412WaterfallSplitter"]["address"]
vault = contracts["WaqfPrincipalVault"]["address"]

specs = [
    ("LocalHalalReserveToken", "script/LocalHalalReserveToken.sol:LocalHalalReserveToken", ["address", "uint256"], [deployer, "1000000000000000"]),
    ("WaqfIdentitySBT", "src/identity/WaqfIdentitySBT.sol:WaqfIdentitySBT", ["address", "string", "string"], [deployer, "WAQF DAO Institutional Credential", "WAQFSBT"]),
    ("ShariahOracle", "src/oracle/ShariahOracle.sol:ShariahOracle", ["address", "address"], [deployer, deployer]),
    ("WaqfAuditRegistry", "src/oracle/WaqfAuditRegistry.sol:WaqfAuditRegistry", ["address", "address"], [deployer, deployer]),
    ("PSAK412WaterfallSplitter", "src/vaults/PSAK412WaterfallSplitter.sol:PSAK412WaterfallSplitter", ["address", "address", "address", "address", "uint16", "uint16", "uint16"], [deployer, reserve, deployer, deployer, "4000", "5050", "950"]),
    ("WaqfPrincipalVault", "src/vaults/WaqfPrincipalVault.sol:WaqfPrincipalVault", ["address", "address", "address", "address"], [deployer, reserve, oracle, splitter]),
    ("DigitalHisbahGovernor", "src/governance/DigitalHisbahGovernor.sol:DigitalHisbahGovernor", ["address", "address", "address", "address", "uint256", "uint256", "uint256"], [deployer, deployer, sbt, vault, "604800", "1000000000", "10"]),
]

for name, target, types, vals in specs:
    addr = contracts[name]["address"]
    sig = f"constructor({','.join(types)})"
    encoded = subprocess.check_output(["cast", "abi-encode", sig, *vals], text=True).strip()
    print(f"Verifying {name} ({addr}) on Blockscout...")
    res = subprocess.run(
        [
            "forge", "verify-contract", addr, target,
            "--chain-id", "84532",
            "--verifier", "blockscout",
            "--verifier-url", verifier_url,
            "--constructor-args", encoded,
        ],
        text=True,
    )
    if res.returncode != 0:
        print(f"WARNING: Blockscout verification exited {res.returncode} for {name} (non-fatal)")
PY

echo "Base Sepolia deployment & notarization COMPLETE."
