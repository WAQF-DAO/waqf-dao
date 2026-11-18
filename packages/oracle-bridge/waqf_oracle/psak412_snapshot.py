"""PSAK 412 (Accounting for Waqf) 5-component ledger snapshot validator & leaf builder.

Enforces statutory & Shariah accounting invariants:
- Balance identity: total_assets_idr == temp_waqf_liabilities_idr + net_assets_idr
- Zero reconciliation discrepancy: reconciliation_diff_idr == 0
- Law No. 41/2004 Nazhir fee cap: nazhir_cash_fee_ratio <= 0.10
- Minimum Mauquf 'Alaih distribution ratio: mauquf_alaih_ratio >= 0.50
- UU PDP privacy-shielded canonical UTF-8 JSON leaves sorted deterministically.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from .merkle import MerkleTree, build_tree, leaf_hash_hex
from .privacy_shield import assert_zero_spill, scrub_payload, shield_wakif_record

NAZHIR_CASH_FEE_MAX_RATIO = 0.10
MAUQUF_ALAIH_MIN_RATIO = 0.50
DEFAULT_INSTITUTION_ANCHOR = "Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386)"
DEFAULT_ECOSYSTEM_ANCHORS = (
    "PT Produktif Indonesia Berdaya (PT PIB)",
    "Forum Wakaf Produktif (FWP)",
    "Asosiasi Nazhir Indonesia (ANI)",
)
DEFAULT_FRAMEWORK = "WAQF Framework (Wijhah - 'Azam - Qiyam - Fahs)"
SCHEMA_VERSION = "waqf-dao.psak412.leaf.v1"


class PSAK412ValidationError(ValueError):
    """Raised when a PSAK 412 ledger snapshot violates statutory or accounting invariants."""


def canonical_json(data: dict[str, Any], *, raise_on_spill: bool = True) -> str:
    """Serialize a dict as deterministic canonical UTF-8 JSON."""
    scrubbed = scrub_payload(data, raise_on_spill=raise_on_spill)
    return json.dumps(scrubbed, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class WaqfPledgeLeaf:
    """Canonical leaf representing an AIW/APAIW waqf pledge certificate (`waqf.pledge`)."""

    aiw_number: str
    pledge_type: str  # e.g., "AIW" or "APAIW"
    pool_code: str
    amount_idr: int
    dated_at: str
    waqf_tenure: str = "permanent"  # "permanent" | "temporary"
    wakif_commitment: str = ""
    wakif_identifier: str = ""

    def to_canonical_dict(self, *, epoch_code: str, sequence: int, salt: str | None = None) -> dict[str, Any]:
        if self.amount_idr <= 0:
            raise PSAK412ValidationError(f"Pledge {self.aiw_number} amount_idr must be positive")
        if self.pledge_type not in {"AIW", "APAIW"}:
            raise PSAK412ValidationError(f"Unsupported pledge_type: {self.pledge_type}")
        if self.waqf_tenure not in {"permanent", "temporary"}:
            raise PSAK412ValidationError(f"Unsupported waqf_tenure: {self.waqf_tenure}")

        raw_record: dict[str, Any] = {
            "schema": SCHEMA_VERSION,
            "epoch": epoch_code,
            "leaf_type": "waqf.pledge",
            "sequence": sequence,
            "aiw_number": self.aiw_number,
            "pledge_type": self.pledge_type,
            "pool_code": self.pool_code,
            "amount_idr": int(self.amount_idr),
            "dated_at": self.dated_at,
            "waqf_tenure": self.waqf_tenure,
        }
        if self.wakif_commitment:
            raw_record["wakif_commitment"] = self.wakif_commitment
        elif self.wakif_identifier:
            raw_record["wakif_id"] = self.wakif_identifier
        else:
            raise PSAK412ValidationError(
                f"Pledge {self.aiw_number} requires wakif_commitment or wakif_identifier"
            )
        shielded = shield_wakif_record(raw_record, salt=salt, raise_on_spill=True)
        shielded.pop("wakif_id", None)
        return shielded


@dataclass(frozen=True)
class WaqfAssetLeaf:
    """Canonical leaf representing a BPN or productive waqf asset (`waqf.asset`)."""

    asset_code: str
    asset_class: str
    certificate_ref: str
    pool_code: str
    book_value_idr: int
    valuation_basis: str = "PSAK_412_FAIR_VALUE"

    def to_canonical_dict(self, *, epoch_code: str, sequence: int) -> dict[str, Any]:
        if self.book_value_idr < 0:
            raise PSAK412ValidationError(f"Asset {self.asset_code} book_value_idr cannot be negative")
        return scrub_payload(
            {
                "schema": SCHEMA_VERSION,
                "epoch": epoch_code,
                "leaf_type": "waqf.asset",
                "sequence": sequence,
                "asset_code": self.asset_code,
                "asset_class": self.asset_class,
                "certificate_ref": self.certificate_ref,
                "pool_code": self.pool_code,
                "book_value_idr": int(self.book_value_idr),
                "valuation_basis": self.valuation_basis,
            },
            raise_on_spill=True,
        )


@dataclass(frozen=True)
class WaqfDistributionLeaf:
    """Canonical leaf representing a BAST Mauquf 'Alaih disbursement (`waqf.distribution`)."""

    bast_number: str
    pool_code: str
    mauquf_alaih_category: str
    amount_idr: int
    disbursed_at: str
    beneficiaries_count: int = 1

    def to_canonical_dict(self, *, epoch_code: str, sequence: int) -> dict[str, Any]:
        if self.amount_idr <= 0:
            raise PSAK412ValidationError(f"Distribution {self.bast_number} amount_idr must be positive")
        if self.beneficiaries_count <= 0:
            raise PSAK412ValidationError(
                f"Distribution {self.bast_number} beneficiaries_count must be positive"
            )
        return scrub_payload(
            {
                "schema": SCHEMA_VERSION,
                "epoch": epoch_code,
                "leaf_type": "waqf.distribution",
                "sequence": sequence,
                "bast_number": self.bast_number,
                "pool_code": self.pool_code,
                "mauquf_alaih_category": self.mauquf_alaih_category,
                "amount_idr": int(self.amount_idr),
                "disbursed_at": self.disbursed_at,
                "beneficiaries_count": int(self.beneficiaries_count),
            },
            raise_on_spill=True,
        )


@dataclass(frozen=True)
class WaqfSroiClusterLeaf:
    """Canonical leaf representing an audited SROI impact cluster."""

    cluster_code: str
    cluster_name: str
    pool_code: str
    beneficiaries_count: int
    sroi_ratio_bps: int
    audit_methodology: str = DEFAULT_FRAMEWORK

    def to_canonical_dict(self, *, epoch_code: str, sequence: int) -> dict[str, Any]:
        if self.sroi_ratio_bps < 0:
            raise PSAK412ValidationError(f"Cluster {self.cluster_code} sroi_ratio_bps cannot be negative")
        if self.beneficiaries_count < 0:
            raise PSAK412ValidationError(
                f"Cluster {self.cluster_code} beneficiaries_count cannot be negative"
            )
        return scrub_payload(
            {
                "schema": SCHEMA_VERSION,
                "epoch": epoch_code,
                "leaf_type": "waqf.sroi_cluster",
                "sequence": sequence,
                "cluster_code": self.cluster_code,
                "cluster_name": self.cluster_name,
                "pool_code": self.pool_code,
                "beneficiaries_count": int(self.beneficiaries_count),
                "sroi_ratio_bps": int(self.sroi_ratio_bps),
                "audit_methodology": self.audit_methodology,
            },
            raise_on_spill=True,
        )


@dataclass(frozen=True)
class PSAK412Components:
    """Five-component PSAK 412 financial reporting structure."""

    statement_of_financial_position: dict[str, int]
    statement_of_activity: dict[str, Any]
    statement_of_cash_flows: dict[str, int]
    statement_of_managed_assets: dict[str, int]
    notes_and_sroi_disclosure: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PSAK412Snapshot:
    """Validated PSAK 412 epoch snapshot generating deterministic Merkle leaves."""

    epoch_code: str
    snapshot_date: str
    total_assets_idr: int
    temp_waqf_liabilities_idr: int
    net_assets_idr: int
    reconciliation_diff_idr: int
    nazhir_cash_fee_ratio: float
    mauquf_alaih_ratio: float
    sroi_ratio_bps: int
    pool_allocations_idr: dict[str, int]
    institution_name: str = DEFAULT_INSTITUTION_ANCHOR
    pledges: tuple[WaqfPledgeLeaf, ...] = field(default_factory=tuple)
    assets: tuple[WaqfAssetLeaf, ...] = field(default_factory=tuple)
    distributions: tuple[WaqfDistributionLeaf, ...] = field(default_factory=tuple)
    sroi_clusters: tuple[WaqfSroiClusterLeaf, ...] = field(default_factory=tuple)
    components: PSAK412Components | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Enforce all PSAK 412 accounting, UU 41/2004, and Zero-Spill invariants."""
        if not self.epoch_code or not self.epoch_code.strip():
            raise PSAK412ValidationError("epoch_code must not be empty")
        if not self.snapshot_date or not self.snapshot_date.strip():
            raise PSAK412ValidationError("snapshot_date must not be empty")
        assert_zero_spill(self.epoch_code)
        assert_zero_spill(self.institution_name)

        if self.total_assets_idr < 0:
            raise PSAK412ValidationError("total_assets_idr must be non-negative")
        if self.temp_waqf_liabilities_idr < 0:
            raise PSAK412ValidationError("temp_waqf_liabilities_idr must be non-negative")
        if self.net_assets_idr < 0:
            raise PSAK412ValidationError("net_assets_idr must be non-negative")

        expected_total = self.temp_waqf_liabilities_idr + self.net_assets_idr
        if self.total_assets_idr != expected_total:
            raise PSAK412ValidationError(
                f"PSAK 412 balance mismatch: total_assets_idr ({self.total_assets_idr}) != "
                f"temp_waqf_liabilities_idr + net_assets_idr ({expected_total})"
            )

        if self.reconciliation_diff_idr != 0:
            raise PSAK412ValidationError(
                f"PSAK 412 reconciliation error: reconciliation_diff_idr must be 0, "
                f"got {self.reconciliation_diff_idr}"
            )

        if not (0.0 <= self.nazhir_cash_fee_ratio <= NAZHIR_CASH_FEE_MAX_RATIO):
            raise PSAK412ValidationError(
                f"UU 41/2004 violation: nazhir_cash_fee_ratio ({self.nazhir_cash_fee_ratio:.4f}) "
                f"exceeds maximum cap {NAZHIR_CASH_FEE_MAX_RATIO:.2f}"
            )

        if not (MAUQUF_ALAIH_MIN_RATIO <= self.mauquf_alaih_ratio <= 1.0):
            raise PSAK412ValidationError(
                f"Mauquf 'Alaih allocation violation: mauquf_alaih_ratio "
                f"({self.mauquf_alaih_ratio:.4f}) is below minimum {MAUQUF_ALAIH_MIN_RATIO:.2f}"
            )

        if self.sroi_ratio_bps < 0:
            raise PSAK412ValidationError("sroi_ratio_bps must be non-negative")

        if not self.pool_allocations_idr:
            raise PSAK412ValidationError("pool_allocations_idr must contain at least one pool")
        for pool_code, amount in self.pool_allocations_idr.items():
            assert_zero_spill(pool_code)
            if amount < 0:
                raise PSAK412ValidationError(f"Pool {pool_code} allocation cannot be negative")
        pool_sum = sum(self.pool_allocations_idr.values())
        if pool_sum != self.total_assets_idr:
            raise PSAK412ValidationError(
                f"Pool allocations sum ({pool_sum}) must equal total_assets_idr ({self.total_assets_idr})"
            )

        if self.components is not None:
            fp = self.components.statement_of_financial_position
            if fp.get("total_assets_idr") != self.total_assets_idr:
                raise PSAK412ValidationError("Component 1 total_assets_idr mismatch")
            if fp.get("temp_waqf_liabilities_idr") != self.temp_waqf_liabilities_idr:
                raise PSAK412ValidationError("Component 1 temp_waqf_liabilities_idr mismatch")
            if fp.get("net_assets_idr") != self.net_assets_idr:
                raise PSAK412ValidationError("Component 1 net_assets_idr mismatch")
            if fp.get("reconciliation_diff_idr", 0) != 0:
                raise PSAK412ValidationError("Component 1 reconciliation_diff_idr must be 0")
            if sum(self.components.statement_of_managed_assets.values()) != self.total_assets_idr:
                raise PSAK412ValidationError(
                    "Component 4 statement_of_managed_assets sum must equal total_assets_idr"
                )

    def resolved_components(self) -> PSAK412Components:
        """Return explicit 5-component structure or derive deterministic defaults."""
        if self.components is not None:
            return self.components
        total_distributed = sum(item.amount_idr for item in self.distributions)
        total_pledged = sum(item.amount_idr for item in self.pledges)
        return PSAK412Components(
            statement_of_financial_position={
                "total_assets_idr": int(self.total_assets_idr),
                "temp_waqf_liabilities_idr": int(self.temp_waqf_liabilities_idr),
                "net_assets_idr": int(self.net_assets_idr),
                "reconciliation_diff_idr": int(self.reconciliation_diff_idr),
            },
            statement_of_activity={
                "waqf_receipts_idr": int(total_pledged),
                "mauquf_alaih_disbursement_idr": int(total_distributed),
                "nazhir_cash_fee_ratio_bps": round(self.nazhir_cash_fee_ratio * 10000),
                "mauquf_alaih_ratio_bps": round(self.mauquf_alaih_ratio * 10000),
            },
            statement_of_cash_flows={
                "operating_inflow_idr": int(total_pledged),
                "productive_investing_idr": int(sum(a.book_value_idr for a in self.assets)),
                "distribution_outflow_idr": int(total_distributed),
                "closing_cash_idr": int(self.total_assets_idr - sum(a.book_value_idr for a in self.assets)),
            },
            statement_of_managed_assets={k: int(v) for k, v in sorted(self.pool_allocations_idr.items())},
            notes_and_sroi_disclosure={
                "sroi_ratio_bps": int(self.sroi_ratio_bps),
                "shariah_standard": "AAOIFI SS-60 / PSAK 412 / UU 41-2004",
                "framework": DEFAULT_FRAMEWORK,
                "institutional_anchor": self.institution_name,
                "ecosystem_anchors": list(DEFAULT_ECOSYSTEM_ANCHORS),
            },
        )

    def build_summary_leaf(self, sequence: int = 0) -> dict[str, Any]:
        """Build the canonical PSAK 412 5-component summary leaf."""
        comp = self.resolved_components()
        return scrub_payload(
            {
                "schema": SCHEMA_VERSION,
                "epoch": self.epoch_code,
                "leaf_type": "waqf.psak412_summary",
                "sequence": sequence,
                "snapshot_date": self.snapshot_date,
                "institution_name": self.institution_name,
                "total_assets_idr": int(self.total_assets_idr),
                "temp_waqf_liabilities_idr": int(self.temp_waqf_liabilities_idr),
                "net_assets_idr": int(self.net_assets_idr),
                "reconciliation_diff_idr": int(self.reconciliation_diff_idr),
                "nazhir_cash_fee_bps": round(self.nazhir_cash_fee_ratio * 10000),
                "mauquf_alaih_bps": round(self.mauquf_alaih_ratio * 10000),
                "sroi_ratio_bps": int(self.sroi_ratio_bps),
                "pool_allocations_idr": {k: int(v) for k, v in sorted(self.pool_allocations_idr.items())},
                "components": comp.to_dict(),
            },
            raise_on_spill=True,
        )

    def build_canonical_leaves(self, *, salt: str | None = None) -> list[dict[str, Any]]:
        """Build ordered canonical leaf entries with payload JSON and leaf_hash."""
        raw_dicts: list[dict[str, Any]] = []
        seq = 0
        raw_dicts.append(self.build_summary_leaf(sequence=seq))
        seq += 1

        for pledge in self.pledges:
            raw_dicts.append(pledge.to_canonical_dict(epoch_code=self.epoch_code, sequence=seq, salt=salt))
            seq += 1
        for asset in self.assets:
            raw_dicts.append(asset.to_canonical_dict(epoch_code=self.epoch_code, sequence=seq))
            seq += 1
        for dist in self.distributions:
            raw_dicts.append(dist.to_canonical_dict(epoch_code=self.epoch_code, sequence=seq))
            seq += 1
        for cluster in self.sroi_clusters:
            raw_dicts.append(cluster.to_canonical_dict(epoch_code=self.epoch_code, sequence=seq))
            seq += 1

        entries: list[dict[str, Any]] = []
        for idx, leaf_obj in enumerate(raw_dicts):
            payload_str = canonical_json(leaf_obj, raise_on_spill=True)
            entries.append(
                {
                    "index": idx,
                    "leaf_type": leaf_obj["leaf_type"],
                    "payload": leaf_obj,
                    "canonical_json": payload_str,
                    "leaf_hash": leaf_hash_hex(payload_str),
                }
            )
        return entries

    def build_merkle_tree(self, *, salt: str | None = None) -> tuple[MerkleTree, list[dict[str, Any]]]:
        """Build the MerkleTree and attach per-leaf inclusion proofs."""
        entries = self.build_canonical_leaves(salt=salt)
        tree = build_tree([entry["canonical_json"] for entry in entries])
        for entry in entries:
            entry["proof"] = tree.get_proof(entry["index"])
        return tree, entries
