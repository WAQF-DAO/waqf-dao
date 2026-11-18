# -*- coding: utf-8 -*-
"""Odoo 20.0 model for WAQF DAO PSAK 412 Merkle notarization & UU PDP privacy shield."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import merkle_stdlib

SCHEMA_VERSION = "waqf-dao.psak412.leaf.v1"
DEFAULT_INSTITUTION_ANCHOR = "Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386)"
DEFAULT_ECOSYSTEM_ANCHORS = (
    "PT Produktif Indonesia Berdaya (PT PIB)",
    "Forum Wakaf Produktif (FWP)",
    "Asosiasi Nazhir Indonesia (ANI)",
)
DEFAULT_FRAMEWORK = "WAQF Framework (Wijhah - 'Azam - Qiyam - Fahs)"
AUDIT_REGISTRY_SIGNATURE = (
    "notarizeEpoch(string,bytes32,uint256,uint256,uint256,uint256,bytes32)"
)
TX_HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")
ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


class WaqfDaoNotarization(models.Model):
    """PSAK 412 ledger snapshot notarized via deterministic SHA-256 Merkle root on L2."""

    _name = "waqf.dao.notarization"
    _description = "WAQF DAO PSAK 412 Merkle Notarization"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "epoch_date desc, id desc"

    name = fields.Char(
        string="Notarization Reference",
        required=True,
        tracking=True,
        default="PSAK 412 Epoch Notarization",
    )
    epoch_code = fields.Char(
        string="Epoch Code",
        required=True,
        index=True,
        tracking=True,
        help="Accounting epoch identifier, e.g. 2026-11.",
    )
    epoch_date = fields.Date(
        string="Snapshot Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    institution_name = fields.Char(
        string="Nazhir Institution Anchor",
        required=True,
        default=DEFAULT_INSTITUTION_ANCHOR,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("bundled", "Merkle Bundled"),
            ("notarized", "On-Chain Notarized"),
            ("verified", "Verified"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )

    # PSAK 412 Statement of Financial Position & Activity Metrics (integer IDR)
    total_assets_idr = fields.Float(
        string="Total Assets (IDR)",
        digits=(18, 0),
        required=True,
        default=0.0,
        tracking=True,
    )
    temp_waqf_liabilities_idr = fields.Float(
        string="Temporary Waqf Liabilities (IDR)",
        digits=(18, 0),
        required=True,
        default=0.0,
        tracking=True,
    )
    net_assets_idr = fields.Float(
        string="Net Waqf Assets (IDR)",
        digits=(18, 0),
        required=True,
        default=0.0,
        tracking=True,
    )
    reconciliation_diff_idr = fields.Float(
        string="Reconciliation Diff (IDR)",
        digits=(18, 0),
        compute="_compute_reconciliation_diff",
        store=True,
    )
    nazhir_cash_fee_ratio = fields.Float(
        string="Nazhir Cash Fee Ratio",
        digits=(5, 4),
        required=True,
        default=0.085,
        help="UU 41/2004 statutory maximum is 0.1000 (10%).",
    )
    mauquf_alaih_ratio = fields.Float(
        string="Mauquf 'Alaih Allocation Ratio",
        digits=(5, 4),
        required=True,
        default=0.825,
        help="Minimum Shariah disbursement floor is 0.5000 (50%).",
    )
    sroi_ratio_bps = fields.Integer(
        string="SROI Ratio (bps)",
        required=True,
        default=41100,
        help="Social Return on Investment in basis points (41100 = 4.11x).",
    )

    # Genesis 5-Pool Breakdown (IDR)
    pool_wpud_idr = fields.Float(string="Pool WPUD (IDR)", digits=(18, 0), default=0.0)
    pool_wpum_idr = fields.Float(string="Pool WPUM (IDR)", digits=(18, 0), default=0.0)
    pool_wpair_idr = fields.Float(string="Pool WPAIR (IDR)", digits=(18, 0), default=0.0)
    pool_wppal_idr = fields.Float(string="Pool WPPAL (IDR)", digits=(18, 0), default=0.0)
    pool_wpmas_idr = fields.Float(string="Pool WPMAS (IDR)", digits=(18, 0), default=0.0)

    # Merkle & UU PDP Privacy Shield Outputs
    epoch_id_bytes32 = fields.Char(
        string="Epoch ID (bytes32)",
        size=66,
        readonly=True,
        copy=False,
    )
    merkle_root = fields.Char(
        string="Merkle Root",
        size=66,
        readonly=True,
        copy=False,
        tracking=True,
    )
    leaf_count = fields.Integer(
        string="Leaf Count",
        readonly=True,
        copy=False,
    )
    metadata_hash = fields.Char(
        string="Metadata Hash (bytes32)",
        size=66,
        readonly=True,
        copy=False,
    )
    leaf_manifest_json = fields.Text(
        string="Privacy-Shielded Leaf Manifest (JSON)",
        readonly=True,
        copy=False,
    )
    proof_bundle_json = fields.Text(
        string="Merkle Inclusion Proofs (JSON)",
        readonly=True,
        copy=False,
    )

    # Ethereum L2 Notarization Fields
    l2_chain_id = fields.Integer(
        string="L2 Chain ID",
        required=True,
        default=84532,
        help="Target EVM Layer-2 chain ID (e.g., 84532 Base Sepolia, 8453 Base Mainnet).",
    )
    registry_contract_address = fields.Char(
        string="WaqfAuditRegistry Address",
        size=42,
        default="0x0000000000000000000000000000000000000000",
    )
    l2_tx_hash = fields.Char(
        string="L2 Transaction Hash",
        size=66,
        copy=False,
        tracking=True,
    )
    notarized_at = fields.Datetime(
        string="Notarized At",
        readonly=True,
        copy=False,
    )
    abi_payload_json = fields.Text(
        string="WaqfAuditRegistry ABI Payload (JSON)",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        ("epoch_code_uniq", "unique(epoch_code)", "Epoch code must be unique per notarization."),
    ]

    @api.depends("total_assets_idr", "temp_waqf_liabilities_idr", "net_assets_idr")
    def _compute_reconciliation_diff(self) -> None:
        for rec in self:
            total_assets = round(rec.total_assets_idr or 0.0)
            liab_plus_net = round(rec.temp_waqf_liabilities_idr or 0.0) + round(rec.net_assets_idr or 0.0)
            rec.reconciliation_diff_idr = float(total_assets - liab_plus_net)

    @api.constrains(
        "epoch_code",
        "institution_name",
        "total_assets_idr",
        "temp_waqf_liabilities_idr",
        "net_assets_idr",
        "nazhir_cash_fee_ratio",
        "mauquf_alaih_ratio",
        "sroi_ratio_bps",
        "registry_contract_address",
    )
    def _check_psak412_and_zero_spill(self) -> None:
        for rec in self:
            try:
                merkle_stdlib.assert_zero_spill(rec.epoch_code or "")
                merkle_stdlib.assert_zero_spill(rec.institution_name or "")
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

            if rec.total_assets_idr < 0 or rec.temp_waqf_liabilities_idr < 0 or rec.net_assets_idr < 0:
                raise ValidationError(_("PSAK 412 asset and liability amounts must be non-negative."))

            total_assets = round(rec.total_assets_idr)
            expected_total = round(rec.temp_waqf_liabilities_idr) + round(rec.net_assets_idr)
            if total_assets != expected_total:
                raise ValidationError(
                    _(
                        "PSAK 412 balance mismatch: Total Assets (%(assets)s) must equal "
                        "Temporary Waqf Liabilities + Net Assets (%(expected)s)."
                    )
                    % {"assets": total_assets, "expected": expected_total}
                )

            if not (0.0 <= rec.nazhir_cash_fee_ratio <= 0.10):
                raise ValidationError(
                    _("UU 41/2004 violation: Nazhir cash fee ratio (%.4f) cannot exceed 0.1000.")
                    % rec.nazhir_cash_fee_ratio
                )

            if not (0.50 <= rec.mauquf_alaih_ratio <= 1.0):
                raise ValidationError(
                    _("Mauquf 'Alaih allocation ratio (%.4f) must be at least 0.5000.")
                    % rec.mauquf_alaih_ratio
                )

            if rec.sroi_ratio_bps < 0:
                raise ValidationError(_("SROI ratio (bps) must be non-negative."))

            if rec.registry_contract_address and not ADDRESS_RE.match(rec.registry_contract_address):
                raise ValidationError(_("Registry contract address must be a valid 20-byte 0x hex address."))

    def _resolved_pool_allocations(self) -> dict[str, int]:
        self.ensure_one()
        pools = {
            "WPUD": int(round(self.pool_wpud_idr or 0.0)),
            "WPUM": int(round(self.pool_wpum_idr or 0.0)),
            "WPAIR": int(round(self.pool_wpair_idr or 0.0)),
            "WPPAL": int(round(self.pool_wppal_idr or 0.0)),
            "WPMAS": int(round(self.pool_wpmas_idr or 0.0)),
        }
        if sum(pools.values()) == 0 and round(self.total_assets_idr) > 0:
            pools["WPUD"] = int(round(self.total_assets_idr))
        return pools

    def _collect_erp_canonical_leaves(self, salt: str | None = None) -> list[dict[str, Any]]:
        """Build privacy-shielded canonical PSAK 412 leaves from Odoo records & epoch summary."""
        self.ensure_one()
        total_assets = int(round(self.total_assets_idr))
        temp_liab = int(round(self.temp_waqf_liabilities_idr))
        net_assets = int(round(self.net_assets_idr))
        reconcile_diff = int(round(self.reconciliation_diff_idr))
        pool_allocs = self._resolved_pool_allocations()
        snapshot_date = self.epoch_date.isoformat() if self.epoch_date else ""

        leaves: list[dict[str, Any]] = []
        seq = 0

        pledge_total = 0
        dist_total = 0
        asset_total = 0
        child_leaves: list[dict[str, Any]] = []

        # Dynamically query waqf_core / l10n_id_waqf_psak112 models when present in env.
        if "waqf.pledge" in self.env:
            pledge_recs = self.env["waqf.pledge"].search([], order="id asc")
            for rec in pledge_recs:
                amount = int(round(getattr(rec, "amount", 0.0) or getattr(rec, "amount_idr", 0.0) or 0.0))
                if amount <= 0:
                    continue
                pledge_total += amount
                wakif_raw = str(
                    getattr(rec, "wakif_nik", "")
                    or getattr(rec, "partner_id", False) and rec.partner_id.vat
                    or getattr(rec, "partner_id", False) and rec.partner_id.id
                    or rec.id
                )
                child_leaves.append(
                    {
                        "schema": SCHEMA_VERSION,
                        "epoch": self.epoch_code,
                        "leaf_type": "waqf.pledge",
                        "aiw_number": str(getattr(rec, "aiw_number", "") or getattr(rec, "name", f"AIW-{rec.id}")),
                        "pledge_type": str(getattr(rec, "pledge_type", "AIW") or "AIW"),
                        "pool_code": str(getattr(rec, "pool_code", "WPUD") or "WPUD"),
                        "amount_idr": amount,
                        "dated_at": str(getattr(rec, "pledge_date", snapshot_date) or snapshot_date),
                        "waqf_tenure": str(getattr(rec, "waqf_tenure", "permanent") or "permanent"),
                        "wakif_commitment": merkle_stdlib.commit_wakif_identity(wakif_raw, salt=salt),
                    }
                )

        if "waqf.asset" in self.env:
            asset_recs = self.env["waqf.asset"].search([], order="id asc")
            for rec in asset_recs:
                book_val = int(round(getattr(rec, "book_value_idr", 0.0) or getattr(rec, "value", 0.0) or 0.0))
                asset_total += book_val
                child_leaves.append(
                    {
                        "schema": SCHEMA_VERSION,
                        "epoch": self.epoch_code,
                        "leaf_type": "waqf.asset",
                        "asset_code": str(getattr(rec, "code", "") or getattr(rec, "name", f"ASSET-{rec.id}")),
                        "asset_class": str(getattr(rec, "asset_type", "PRODUCTIVE_WAQF_ASSET") or "PRODUCTIVE_WAQF_ASSET"),
                        "certificate_ref": str(getattr(rec, "certificate_number", "") or f"BPN-{rec.id}"),
                        "pool_code": str(getattr(rec, "pool_code", "WPAIR") or "WPAIR"),
                        "book_value_idr": book_val,
                        "valuation_basis": "PSAK_412_FAIR_VALUE",
                    }
                )

        if "waqf.distribution" in self.env:
            dist_recs = self.env["waqf.distribution"].search([], order="id asc")
            for rec in dist_recs:
                amount = int(round(getattr(rec, "amount", 0.0) or getattr(rec, "amount_idr", 0.0) or 0.0))
                if amount <= 0:
                    continue
                dist_total += amount
                child_leaves.append(
                    {
                        "schema": SCHEMA_VERSION,
                        "epoch": self.epoch_code,
                        "leaf_type": "waqf.distribution",
                        "bast_number": str(getattr(rec, "bast_number", "") or getattr(rec, "name", f"BAST-{rec.id}")),
                        "pool_code": str(getattr(rec, "pool_code", "WPAIR") or "WPAIR"),
                        "mauquf_alaih_category": str(getattr(rec, "category", "MAUQUF_ALAIH") or "MAUQUF_ALAIH"),
                        "amount_idr": amount,
                        "disbursed_at": str(getattr(rec, "distribution_date", snapshot_date) or snapshot_date),
                        "beneficiaries_count": int(getattr(rec, "beneficiaries_count", 1) or 1),
                    }
                )

        summary_leaf = {
            "schema": SCHEMA_VERSION,
            "epoch": self.epoch_code,
            "leaf_type": "waqf.psak412_summary",
            "sequence": seq,
            "snapshot_date": snapshot_date,
            "institution_name": self.institution_name,
            "total_assets_idr": total_assets,
            "temp_waqf_liabilities_idr": temp_liab,
            "net_assets_idr": net_assets,
            "reconciliation_diff_idr": reconcile_diff,
            "nazhir_cash_fee_bps": round(self.nazhir_cash_fee_ratio * 10000),
            "mauquf_alaih_bps": round(self.mauquf_alaih_ratio * 10000),
            "sroi_ratio_bps": int(self.sroi_ratio_bps),
            "pool_allocations_idr": {k: int(v) for k, v in sorted(pool_allocs.items())},
            "components": {
                "statement_of_financial_position": {
                    "total_assets_idr": total_assets,
                    "temp_waqf_liabilities_idr": temp_liab,
                    "net_assets_idr": net_assets,
                    "reconciliation_diff_idr": reconcile_diff,
                },
                "statement_of_activity": {
                    "waqf_receipts_idr": pledge_total,
                    "mauquf_alaih_disbursement_idr": dist_total,
                    "nazhir_cash_fee_ratio_bps": round(self.nazhir_cash_fee_ratio * 10000),
                    "mauquf_alaih_ratio_bps": round(self.mauquf_alaih_ratio * 10000),
                },
                "statement_of_cash_flows": {
                    "operating_inflow_idr": pledge_total,
                    "productive_investing_idr": asset_total,
                    "distribution_outflow_idr": dist_total,
                    "closing_cash_idr": total_assets - asset_total,
                },
                "statement_of_managed_assets": {k: int(v) for k, v in sorted(pool_allocs.items())},
                "notes_and_sroi_disclosure": {
                    "sroi_ratio_bps": int(self.sroi_ratio_bps),
                    "shariah_standard": "AAOIFI SS-60 / PSAK 412 / UU 41-2004",
                    "framework": DEFAULT_FRAMEWORK,
                    "institutional_anchor": self.institution_name,
                    "ecosystem_anchors": list(DEFAULT_ECOSYSTEM_ANCHORS),
                },
            },
        }
        leaves.append(merkle_stdlib.scrub_payload(summary_leaf))

        for item in child_leaves:
            seq += 1
            item["sequence"] = seq
            leaves.append(merkle_stdlib.scrub_payload(item))

        return leaves

    def action_generate_merkle_bundle(self) -> dict[str, Any] | bool:
        """Compute deterministic Merkle root, proofs, and WaqfAuditRegistry ABI payload."""
        for rec in self:
            rec._check_psak412_and_zero_spill()
            if round(rec.reconciliation_diff_idr) != 0:
                raise UserError(_("Cannot generate Merkle bundle when reconciliation_diff_idr != 0."))

            pool_allocs = rec._resolved_pool_allocations()
            if sum(pool_allocs.values()) != round(rec.total_assets_idr):
                raise UserError(
                    _("Pool allocations sum (%s) must equal Total Assets (%s).")
                    % (sum(pool_allocs.values()), int(round(rec.total_assets_idr)))
                )

            salt = os.environ.get(merkle_stdlib.DEFAULT_SALT_ENV, "").strip() or None
            leaf_objs = rec._collect_erp_canonical_leaves(salt=salt)
            canonical_payloads = [merkle_stdlib.canonical_json(obj) for obj in leaf_objs]
            bundle = merkle_stdlib.build_merkle_bundle(canonical_payloads)

            manifest = [
                {
                    "index": idx,
                    "leaf_type": leaf_objs[idx]["leaf_type"],
                    "payload": leaf_objs[idx],
                    "canonical_json": canonical_payloads[idx],
                    "leaf_hash": bundle["leaves"][idx],
                    "proof": bundle["proofs"][idx],
                }
                for idx in range(len(leaf_objs))
            ]

            epoch_id = merkle_stdlib.to_hex(
                hashlib.sha256(f"waqf:epoch:v1:{rec.epoch_code.strip()}".encode("utf-8")).digest()
            )
            metadata_obj = {
                "schema": "waqf-dao.audit-registry.metadata.v1",
                "epoch_code": rec.epoch_code,
                "snapshot_date": rec.epoch_date.isoformat() if rec.epoch_date else "",
                "institution_name": rec.institution_name,
                "merkle_root": bundle["merkle_root"],
                "leaf_count": bundle["leaf_count"],
                "nazhir_fee_bps": round(rec.nazhir_cash_fee_ratio * 10000),
                "mauquf_alaih_bps": round(rec.mauquf_alaih_ratio * 10000),
                "sroi_ratio_bps": int(rec.sroi_ratio_bps),
                "pools": sorted(pool_allocs.keys()),
            }
            metadata_hash = merkle_stdlib.to_hex(
                hashlib.sha256(merkle_stdlib.canonical_json(metadata_obj).encode("utf-8")).digest()
            )

            abi_payload = {
                "chain_id": int(rec.l2_chain_id),
                "registry_address": (rec.registry_contract_address or "").lower(),
                "contract_method": AUDIT_REGISTRY_SIGNATURE,
                "epoch_id_reference": epoch_id,
                "leaf_count": int(bundle["leaf_count"]),
                "abi_arguments": {
                    "periodCode": rec.epoch_code,
                    "merkleRoot": bundle["merkle_root"],
                    "totalAssetsIdr": int(round(rec.total_assets_idr)),
                    "tempWaqfLiabilitiesIdr": int(round(rec.temp_waqf_liabilities_idr)),
                    "netAssetsIdr": int(round(rec.net_assets_idr)),
                    "sroiRatioBps": int(rec.sroi_ratio_bps),
                    "odooDbHash": metadata_hash,
                },
            }

            rec.write(
                {
                    "epoch_id_bytes32": epoch_id,
                    "merkle_root": bundle["merkle_root"],
                    "leaf_count": bundle["leaf_count"],
                    "metadata_hash": metadata_hash,
                    "leaf_manifest_json": json.dumps(manifest, indent=2),
                    "proof_bundle_json": json.dumps(
                        {str(i): bundle["proofs"][i] for i in range(bundle["leaf_count"])},
                        indent=2,
                    ),
                    "abi_payload_json": json.dumps(abi_payload, indent=2),
                    "state": "bundled",
                }
            )
        return True

    def action_mark_notarized(self) -> bool:
        for rec in self:
            if not rec.merkle_root:
                raise UserError(_("Generate the Merkle bundle before marking notarized."))
            if not rec.l2_tx_hash or not TX_HASH_RE.match(rec.l2_tx_hash.strip()):
                raise UserError(_("Provide a valid 0x-prefixed 32-byte L2 transaction hash."))
            rec.write(
                {
                    "l2_tx_hash": rec.l2_tx_hash.strip().lower(),
                    "notarized_at": fields.Datetime.now(),
                    "state": "notarized",
                }
            )
        return True

    def action_verify_bundle(self) -> bool:
        for rec in self:
            if not rec.merkle_root or not rec.leaf_manifest_json:
                raise UserError(_("No Merkle bundle to verify."))
            manifest = json.loads(rec.leaf_manifest_json)
            recomputed = merkle_stdlib.build_merkle_bundle(
                [entry["canonical_json"] for entry in manifest]
            )
            if recomputed["merkle_root"] != rec.merkle_root:
                raise UserError(
                    _("Merkle root verification failed: %s != %s")
                    % (recomputed["merkle_root"], rec.merkle_root)
                )
            for entry in manifest:
                if not merkle_stdlib.verify_proof(
                    rec.merkle_root, entry["leaf_hash"], entry["proof"]
                ):
                    raise UserError(_("Proof verification failed for leaf %s") % entry.get("index"))
            rec.write({"state": "verified"})
        return True

    def action_reset_draft(self) -> bool:
        self.write({"state": "draft"})
        return True

    @api.model
    def _cron_prepare_monthly_notarization(self) -> None:
        """Scheduled action preparing a monthly PSAK 412 Merkle notarization draft."""
        today = fields.Date.context_today(self)
        epoch_code = today.strftime("%Y-%m")
        existing = self.search([("epoch_code", "=", epoch_code)], limit=1)
        if existing:
            return
        self.create(
            {
                "name": f"PSAK 412 Epoch {epoch_code}",
                "epoch_code": epoch_code,
                "epoch_date": today,
                "total_assets_idr": 0.0,
                "temp_waqf_liabilities_idr": 0.0,
                "net_assets_idr": 0.0,
                "nazhir_cash_fee_ratio": 0.085,
                "mauquf_alaih_ratio": 0.825,
                "sroi_ratio_bps": 41100,
            }
        )
