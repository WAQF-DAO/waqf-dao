"""Deterministic on-chain notarization payload & ABI relayer for WaqfAuditRegistry.sol."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .merkle import from_hex, to_hex, verify_proof
from .privacy_shield import assert_zero_spill
from .psak412_snapshot import (
    DEFAULT_INSTITUTION_ANCHOR,
    PSAK412Snapshot,
    WaqfAssetLeaf,
    WaqfDistributionLeaf,
    WaqfPledgeLeaf,
    WaqfSroiClusterLeaf,
    canonical_json,
)

DEFAULT_L2_CHAIN_ID = 84532  # Base Sepolia L2 testnet default
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
AUDIT_REGISTRY_SIGNATURE = (
    "notarizeEpoch(string,bytes32,uint256,uint256,uint256,uint256,bytes32)"
)


def epoch_id_bytes32(epoch_code: str) -> str:
    """Derive deterministic bytes32 epochId from epoch_code."""
    if not epoch_code or not epoch_code.strip():
        raise ValueError("epoch_code must not be empty")
    assert_zero_spill(epoch_code)
    digest = hashlib.sha256(f"waqf:epoch:v1:{epoch_code.strip()}".encode("utf-8")).digest()
    return to_hex(digest)


def validate_evm_address(address: str) -> str:
    """Validate and normalize a 20-byte EVM address string."""
    if not isinstance(address, str) or not ADDRESS_RE.match(address):
        raise ValueError(f"Invalid EVM address: {address!r}")
    return address.lower()


def abi_encode_uint256(value: int) -> str:
    """Encode a non-negative integer as a 32-byte big-endian hex word (no 0x prefix)."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"uint256 requires non-negative int, got {value!r}")
    if value >= (1 << 256):
        raise ValueError(f"uint256 overflow: {value}")
    return f"{value:064x}"


def abi_encode_bytes32(hex_value: str) -> str:
    """Encode a 0x-prefixed 32-byte hex digest as 64 lowercase hex chars (no 0x prefix)."""
    return from_hex(hex_value).hex()


def abi_encode_dynamic_string_tail(value: str) -> list[str]:
    """Encode a dynamic UTF-8 string tail (length word + zero-right-padded 32-byte data words)."""
    raw = value.encode("utf-8")
    words = [abi_encode_uint256(len(raw))]
    if raw:
        padded_len = ((len(raw) + 31) // 32) * 32
        padded = raw.ljust(padded_len, b"\x00")
        for offset in range(0, padded_len, 32):
            words.append(padded[offset : offset + 32].hex())
    return words


def compute_function_selector(signature: str = AUDIT_REGISTRY_SIGNATURE) -> str:
    """Compute the 4-byte Keccak/SHA3 placeholder or explicit selector metadata.

    Note: Python stdlib hashlib does not expose Keccak-256 (only NIST SHA3-256),
    so we return ABI argument encoding cleanly and keep signature metadata explicit.
    """
    return signature


def build_notarization_payload(
    snapshot: PSAK412Snapshot,
    *,
    chain_id: int = DEFAULT_L2_CHAIN_ID,
    registry_address: str = ZERO_ADDRESS,
    salt: str | None = None,
) -> dict[str, Any]:
    """Build deterministic Merkle tree and ABI-ready WaqfAuditRegistry.sol notarization payload."""
    if chain_id <= 0:
        raise ValueError(f"chain_id must be positive, got {chain_id}")
    normalized_registry = validate_evm_address(registry_address)

    tree, leaf_entries = snapshot.build_merkle_tree(salt=salt)
    epoch_id = epoch_id_bytes32(snapshot.epoch_code)
    merkle_root = tree.root_hex
    nazhir_fee_bps = round(snapshot.nazhir_cash_fee_ratio * 10000)
    mauquf_alaih_bps = round(snapshot.mauquf_alaih_ratio * 10000)

    metadata_obj = {
        "schema": "waqf-dao.audit-registry.metadata.v1",
        "epoch_code": snapshot.epoch_code,
        "snapshot_date": snapshot.snapshot_date,
        "institution_name": snapshot.institution_name,
        "merkle_root": merkle_root,
        "leaf_count": tree.leaf_count,
        "nazhir_fee_bps": nazhir_fee_bps,
        "mauquf_alaih_bps": mauquf_alaih_bps,
        "sroi_ratio_bps": snapshot.sroi_ratio_bps,
        "pools": sorted(snapshot.pool_allocations_idr.keys()),
    }
    metadata_hash = to_hex(
        hashlib.sha256(canonical_json(metadata_obj).encode("utf-8")).digest()
    )

    abi_arguments = {
        "periodCode": snapshot.epoch_code,
        "merkleRoot": merkle_root,
        "totalAssetsIdr": int(snapshot.total_assets_idr),
        "tempWaqfLiabilitiesIdr": int(snapshot.temp_waqf_liabilities_idr),
        "netAssetsIdr": int(snapshot.net_assets_idr),
        "sroiRatioBps": int(snapshot.sroi_ratio_bps),
        "odooDbHash": metadata_hash,
    }

    # 7 head slots (7 * 32 = 224 bytes) -> dynamic string periodCode starts at byte offset 224
    encoded_words = [
        abi_encode_uint256(7 * 32),
        abi_encode_bytes32(merkle_root),
        abi_encode_uint256(int(snapshot.total_assets_idr)),
        abi_encode_uint256(int(snapshot.temp_waqf_liabilities_idr)),
        abi_encode_uint256(int(snapshot.net_assets_idr)),
        abi_encode_uint256(int(snapshot.sroi_ratio_bps)),
        abi_encode_bytes32(metadata_hash),
        *abi_encode_dynamic_string_tail(snapshot.epoch_code),
    ]

    cast_args = [
        snapshot.epoch_code,
        merkle_root,
        str(int(snapshot.total_assets_idr)),
        str(int(snapshot.temp_waqf_liabilities_idr)),
        str(int(snapshot.net_assets_idr)),
        str(int(snapshot.sroi_ratio_bps)),
        metadata_hash,
    ]

    return {
        "epoch_code": snapshot.epoch_code,
        "epoch_id": epoch_id,
        "chain_id": int(chain_id),
        "registry_address": normalized_registry,
        "contract_method": AUDIT_REGISTRY_SIGNATURE,
        "merkle_root": merkle_root,
        "leaf_count": tree.leaf_count,
        "total_assets_idr": int(snapshot.total_assets_idr),
        "temp_waqf_liabilities_idr": int(snapshot.temp_waqf_liabilities_idr),
        "net_assets_idr": int(snapshot.net_assets_idr),
        "reconciliation_diff_idr": int(snapshot.reconciliation_diff_idr),
        "nazhir_fee_bps": nazhir_fee_bps,
        "mauquf_alaih_bps": mauquf_alaih_bps,
        "sroi_ratio_bps": int(snapshot.sroi_ratio_bps),
        "metadata_hash": metadata_hash,
        "abi_arguments": abi_arguments,
        "abi_encoded_args_hex": "0x" + "".join(encoded_words),
        "cast_args": cast_args,
        "leaves": leaf_entries,
        "proofs": {str(entry["index"]): entry["proof"] for entry in leaf_entries},
    }


def build_genesis_snapshot() -> PSAK412Snapshot:
    """Construct the canonical Genesis Epoch 2026-11 PSAK 412 snapshot."""
    pool_allocations = {
        "WPUD": 450_000_000,
        "WPUM": 310_000_000,
        "WPAIR": 284_880_000,
        "WPPAL": 210_000_000,
        "WPMAS": 150_000_000,
    }

    pledges = (
        WaqfPledgeLeaf(
            aiw_number="AIW-YAPI-2026-0001",
            pledge_type="AIW",
            pool_code="WPUD",
            amount_idr=450_000_000,
            dated_at="2026-11-01",
            waqf_tenure="permanent",
            wakif_identifier="WAKIF-GENESIS-WPUD-001",
        ),
        WaqfPledgeLeaf(
            aiw_number="APAIW-YAPI-2026-0002",
            pledge_type="APAIW",
            pool_code="WPAIR",
            amount_idr=284_880_000,
            dated_at="2026-11-05",
            waqf_tenure="permanent",
            wakif_identifier="WAKIF-GENESIS-WPAIR-002",
        ),
        WaqfPledgeLeaf(
            aiw_number="APAIW-YAPI-2026-0003",
            pledge_type="APAIW",
            pool_code="WPUM",
            amount_idr=63_000_000,
            dated_at="2026-11-08",
            waqf_tenure="temporary",
            wakif_identifier="WAKIF-GENESIS-WPUM-003",
        ),
    )

    assets = (
        WaqfAssetLeaf(
            asset_code="ASSET-BPN-WPAIR-001",
            asset_class="CLEAN_WATER_INFRASTRUCTURE",
            certificate_ref="BPN-SHW-2026-0411",
            pool_code="WPAIR",
            book_value_idr=284_880_000,
        ),
        WaqfAssetLeaf(
            asset_code="ASSET-BPN-WPPAL-002",
            asset_class="PRODUCTIVE_AGRICULTURE_LAND",
            certificate_ref="BPN-SHW-2026-0412",
            pool_code="WPPAL",
            book_value_idr=210_000_000,
        ),
        WaqfAssetLeaf(
            asset_code="ASSET-PROD-WPMAS-003",
            asset_class="MOSQUE_EDUCATION_SOLAR_ASSET",
            certificate_ref="AIW-INV-2026-0413",
            pool_code="WPMAS",
            book_value_idr=150_000_000,
        ),
    )

    distributions = (
        WaqfDistributionLeaf(
            bast_number="BAST-2026-11-001",
            pool_code="WPAIR",
            mauquf_alaih_category="CLEAN_WATER_ACCESS",
            amount_idr=48_500_000,
            disbursed_at="2026-11-12",
            beneficiaries_count=1250,
        ),
        WaqfDistributionLeaf(
            bast_number="BAST-2026-11-002",
            pool_code="WPUM",
            mauquf_alaih_category="MICRO_ENTERPRISE_QARD_HASAN",
            amount_idr=35_000_000,
            disbursed_at="2026-11-15",
            beneficiaries_count=140,
        ),
    )

    sroi_clusters = (
        WaqfSroiClusterLeaf(
            cluster_code="SROI-CLEAN-WATER-01",
            cluster_name="Clean Water Waqf Infrastructure (4.11:1)",
            pool_code="WPAIR",
            beneficiaries_count=1250,
            sroi_ratio_bps=41100,
        ),
    )

    return PSAK412Snapshot(
        epoch_code="2026-11",
        snapshot_date="2026-11-18",
        institution_name=DEFAULT_INSTITUTION_ANCHOR,
        total_assets_idr=1_404_880_000,
        temp_waqf_liabilities_idr=63_000_000,
        net_assets_idr=1_341_880_000,
        reconciliation_diff_idr=0,
        nazhir_cash_fee_ratio=0.085,
        mauquf_alaih_ratio=0.825,
        sroi_ratio_bps=41100,
        pool_allocations_idr=pool_allocations,
        pledges=pledges,
        assets=assets,
        distributions=distributions,
        sroi_clusters=sroi_clusters,
    )


def generate_genesis_fixture_dict(
    *,
    chain_id: int = DEFAULT_L2_CHAIN_ID,
    registry_address: str = ZERO_ADDRESS,
) -> dict[str, Any]:
    """Generate the complete Genesis Epoch 2026-11 JSON fixture dictionary."""
    snapshot = build_genesis_snapshot()
    bundle = build_notarization_payload(
        snapshot,
        chain_id=chain_id,
        registry_address=registry_address,
        salt="waqf-dao-genesis-epoch-2026-11",
    )
    return {
        "schema": "waqf-dao.genesis-fixture.v1",
        "epoch_code": snapshot.epoch_code,
        "snapshot_date": snapshot.snapshot_date,
        "institution_name": snapshot.institution_name,
        "psak412_metrics": {
            "total_assets_idr": snapshot.total_assets_idr,
            "temp_waqf_liabilities_idr": snapshot.temp_waqf_liabilities_idr,
            "net_assets_idr": snapshot.net_assets_idr,
            "reconciliation_diff_idr": snapshot.reconciliation_diff_idr,
            "nazhir_cash_fee_ratio": snapshot.nazhir_cash_fee_ratio,
            "mauquf_alaih_ratio": snapshot.mauquf_alaih_ratio,
            "sroi_ratio_bps": snapshot.sroi_ratio_bps,
        },
        "genesis_pools": ["WPUD", "WPUM", "WPAIR", "WPPAL", "WPMAS"],
        "pool_allocations_idr": snapshot.pool_allocations_idr,
        "merkle_root": bundle["merkle_root"],
        "leaf_count": bundle["leaf_count"],
        "leaves": bundle["leaves"],
        "proofs": bundle["proofs"],
        "notarization_payload": {
            "epoch_id": bundle["epoch_id"],
            "chain_id": bundle["chain_id"],
            "registry_address": bundle["registry_address"],
            "contract_method": bundle["contract_method"],
            "metadata_hash": bundle["metadata_hash"],
            "abi_arguments": bundle["abi_arguments"],
            "abi_encoded_args_hex": bundle["abi_encoded_args_hex"],
            "cast_args": bundle["cast_args"],
        },
    }


def verify_fixture_dict(fixture: dict[str, Any]) -> tuple[bool, list[str]]:
    """Verify PSAK 412 invariants, Merkle root, and every leaf inclusion proof in a fixture."""
    errors: list[str] = []
    metrics = fixture.get("psak412_metrics", {})
    total_assets = metrics.get("total_assets_idr")
    temp_liab = metrics.get("temp_waqf_liabilities_idr")
    net_assets = metrics.get("net_assets_idr")
    diff = metrics.get("reconciliation_diff_idr")
    nazhir_ratio = metrics.get("nazhir_cash_fee_ratio")
    mauquf_ratio = metrics.get("mauquf_alaih_ratio")

    if total_assets != (temp_liab or 0) + (net_assets or 0):
        errors.append("PSAK 412 balance equation failed")
    if diff != 0:
        errors.append(f"reconciliation_diff_idr != 0 ({diff})")
    if nazhir_ratio is None or nazhir_ratio > 0.10:
        errors.append(f"nazhir_cash_fee_ratio exceeds 0.10 ({nazhir_ratio})")
    if mauquf_ratio is None or mauquf_ratio < 0.50:
        errors.append(f"mauquf_alaih_ratio below 0.50 ({mauquf_ratio})")

    leaves = fixture.get("leaves", [])
    merkle_root = fixture.get("merkle_root", "")
    if not leaves:
        errors.append("Fixture contains no leaves")
        return False, errors

    from .merkle import build_tree, leaf_hash_hex

    tree = build_tree([entry["canonical_json"] for entry in leaves])
    if tree.root_hex != merkle_root:
        errors.append(f"Merkle root mismatch: computed {tree.root_hex} != fixture {merkle_root}")

    for idx, entry in enumerate(leaves):
        expected_leaf_hex = leaf_hash_hex(entry["canonical_json"])
        if entry.get("leaf_hash") != expected_leaf_hex:
            errors.append(f"Leaf {idx} hash mismatch")
        proof = entry.get("proof")
        if proof is None:
            proof = fixture.get("proofs", {}).get(str(idx))
        if proof is None or not verify_proof(merkle_root, expected_leaf_hex, proof):
            errors.append(f"Leaf {idx} inclusion proof verification failed")

    return len(errors) == 0, errors


def write_genesis_fixture(output_path: Path) -> Path:
    """Write canonical Genesis Epoch 2026-11 fixture JSON to `output_path`."""
    fixture = generate_genesis_fixture_dict()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    return output_path
