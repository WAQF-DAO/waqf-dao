"""Comprehensive unit test suite for WAQF DAO ERP Merkle Oracle Bridge."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from waqf_oracle.cli import main as cli_main
from waqf_oracle.merkle import (
    LEAF_DOMAIN,
    NODE_DOMAIN,
    build_tree,
    get_proof,
    leaf_hash,
    leaf_hash_hex,
    node_hash,
    to_hex,
    verify_proof,
)
from waqf_oracle.privacy_shield import (
    ZeroSpillViolationError,
    assert_zero_spill,
    commit_wakif_identity,
    redact_email,
    redact_nik,
    redact_phone,
    sanitize_zero_spill,
    scrub_payload,
    scrub_text,
    shield_wakif_record,
)
from waqf_oracle.psak412_snapshot import (
    PSAK412Snapshot,
    PSAK412ValidationError,
    WaqfAssetLeaf,
    WaqfDistributionLeaf,
    WaqfPledgeLeaf,
    WaqfSroiClusterLeaf,
    canonical_json,
)
from waqf_oracle.relayer import (
    build_genesis_snapshot,
    build_notarization_payload,
    verify_fixture_dict,
)


def _manual_leaf(payload: str) -> bytes:
    inner = hashlib.sha256(payload.encode("utf-8")).digest()
    return hashlib.sha256(LEAF_DOMAIN + inner).digest()


def _manual_node(a: bytes, b: bytes) -> bytes:
    left, right = (a, b) if a <= b else (b, a)
    return hashlib.sha256(NODE_DOMAIN + left + right).digest()


class TestMerkleSpecification(unittest.TestCase):
    """Exact bit-for-bit Merkle specification tests."""

    def test_01_single_leaf_tree(self) -> None:
        payload = '{"leaf":"single"}'
        tree = build_tree([payload])
        expected_leaf = _manual_leaf(payload)
        self.assertEqual(tree.root, expected_leaf)
        self.assertEqual(tree.root_hex, to_hex(expected_leaf))
        proof = tree.get_proof(0)
        self.assertEqual(proof, [])
        self.assertTrue(verify_proof(tree.root_hex, leaf_hash_hex(payload), proof))

    def test_02_two_leaf_tree_sorted_pair(self) -> None:
        p0, p1 = "alpha", "beta"
        l0, l1 = _manual_leaf(p0), _manual_leaf(p1)
        expected_root = _manual_node(l0, l1)
        tree = build_tree([p0, p1])
        self.assertEqual(tree.root, expected_root)
        self.assertEqual(get_proof(tree, 0), [to_hex(l1)])
        self.assertEqual(get_proof(tree, 1), [to_hex(l0)])
        self.assertTrue(verify_proof(tree.root_hex, to_hex(l0), tree.get_proof(0)))
        self.assertTrue(verify_proof(tree.root_hex, to_hex(l1), tree.get_proof(1)))

    def test_03_three_leaf_tree_odd_node_carried_unchanged(self) -> None:
        payloads = ["leaf-0", "leaf-1", "leaf-2"]
        l0, l1, l2 = (_manual_leaf(p) for p in payloads)
        h01 = _manual_node(l0, l1)
        expected_root = _manual_node(h01, l2)

        tree = build_tree(payloads)
        self.assertEqual(tree.root, expected_root)
        # Leaf 2 was unpaired at level 0 -> NO sibling emitted at level 0, only h01 at level 1.
        proof_2 = tree.get_proof(2)
        self.assertEqual(proof_2, [to_hex(h01)])
        self.assertEqual(tree.get_proof(0), [to_hex(l1), to_hex(l2)])
        self.assertEqual(tree.get_proof(1), [to_hex(l0), to_hex(l2)])
        for idx, p in enumerate(payloads):
            self.assertTrue(verify_proof(tree.root_hex, leaf_hash_hex(p), tree.get_proof(idx)))

    def test_04_four_leaf_balanced_tree(self) -> None:
        payloads = [f"item-{i}" for i in range(4)]
        leaves = [_manual_leaf(p) for p in payloads]
        h01 = _manual_node(leaves[0], leaves[1])
        h23 = _manual_node(leaves[2], leaves[3])
        expected_root = _manual_node(h01, h23)

        tree = build_tree(payloads)
        self.assertEqual(tree.root, expected_root)
        for idx, p in enumerate(payloads):
            proof = tree.get_proof(idx)
            self.assertEqual(len(proof), 2)
            self.assertTrue(verify_proof(tree.root_hex, leaf_hash_hex(p), proof))

    def test_05_five_leaf_tree_double_odd_promotion(self) -> None:
        payloads = [f"five-{i}" for i in range(5)]
        leaves = [_manual_leaf(p) for p in payloads]
        h01 = _manual_node(leaves[0], leaves[1])
        h23 = _manual_node(leaves[2], leaves[3])
        h0123 = _manual_node(h01, h23)
        expected_root = _manual_node(h0123, leaves[4])

        tree = build_tree(payloads)
        self.assertEqual(tree.root, expected_root)
        # Index 4 is carried unchanged across level 0 and level 1 -> proof has only 1 sibling (h0123).
        self.assertEqual(tree.get_proof(4), [to_hex(h0123)])
        for idx, p in enumerate(payloads):
            self.assertTrue(verify_proof(tree.root_hex, leaf_hash_hex(p), tree.get_proof(idx)))

    def test_06_seven_leaf_tree_all_proofs_valid(self) -> None:
        payloads = [f"seven-{i}" for i in range(7)]
        leaves = [_manual_leaf(p) for p in payloads]
        h01 = _manual_node(leaves[0], leaves[1])
        h23 = _manual_node(leaves[2], leaves[3])
        h45 = _manual_node(leaves[4], leaves[5])
        h0123 = _manual_node(h01, h23)
        h456 = _manual_node(h45, leaves[6])
        expected_root = _manual_node(h0123, h456)

        tree = build_tree(payloads)
        self.assertEqual(tree.root, expected_root)
        self.assertEqual(tree.get_proof(6), [to_hex(h45), to_hex(h0123)])
        for idx, p in enumerate(payloads):
            self.assertTrue(verify_proof(tree.root_hex, leaf_hash_hex(p), tree.get_proof(idx)))

    def test_07_tamper_rejection_and_empty_tree_error(self) -> None:
        with self.assertRaises(ValueError):
            build_tree([])

        payloads = ["a", "b", "c", "d", "e"]
        tree = build_tree(payloads)
        proof_0 = tree.get_proof(0)

        # Tampered leaf payload
        self.assertFalse(verify_proof(tree.root_hex, leaf_hash_hex("a-tampered"), proof_0))
        # Tampered root
        bad_root = "0x" + ("ff" * 32)
        self.assertFalse(verify_proof(bad_root, leaf_hash_hex("a"), proof_0))
        # Tampered sibling in proof
        tampered_proof = [proof_0[0], "0x" + ("00" * 32), *proof_0[2:]]
        self.assertFalse(verify_proof(tree.root_hex, leaf_hash_hex("a"), tampered_proof))
        # Malformed hex
        self.assertFalse(verify_proof(tree.root_hex, "0x1234", proof_0))
        # Wrong index proof for another leaf
        self.assertFalse(verify_proof(tree.root_hex, leaf_hash_hex("b"), proof_0))


class TestPSAK412Validation(unittest.TestCase):
    """PSAK 412 5-component ledger validation & canonical leaf generation tests."""

    def _base_kwargs(self) -> dict:
        return {
            "epoch_code": "2026-12",
            "snapshot_date": "2026-12-01",
            "total_assets_idr": 1_000_000_000,
            "temp_waqf_liabilities_idr": 100_000_000,
            "net_assets_idr": 900_000_000,
            "reconciliation_diff_idr": 0,
            "nazhir_cash_fee_ratio": 0.09,
            "mauquf_alaih_ratio": 0.80,
            "sroi_ratio_bps": 41100,
            "pool_allocations_idr": {
                "WPUD": 400_000_000,
                "WPUM": 200_000_000,
                "WPAIR": 200_000_000,
                "WPPAL": 100_000_000,
                "WPMAS": 100_000_000,
            },
        }

    def test_08_psak412_balance_mismatch_rejected(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["net_assets_idr"] = 899_999_999
        with self.assertRaises(PSAK412ValidationError):
            PSAK412Snapshot(**kwargs)

        kwargs_diff = self._base_kwargs()
        kwargs_diff["reconciliation_diff_idr"] = 1
        with self.assertRaises(PSAK412ValidationError):
            PSAK412Snapshot(**kwargs_diff)

    def test_09_nazhir_cap_and_mauquf_floor_rejected(self) -> None:
        kwargs_fee = self._base_kwargs()
        kwargs_fee["nazhir_cash_fee_ratio"] = 0.105
        with self.assertRaises(PSAK412ValidationError):
            PSAK412Snapshot(**kwargs_fee)

        kwargs_mauquf = self._base_kwargs()
        kwargs_mauquf["mauquf_alaih_ratio"] = 0.49
        with self.assertRaises(PSAK412ValidationError):
            PSAK412Snapshot(**kwargs_mauquf)

    def test_10_canonical_json_leaf_generation(self) -> None:
        kwargs = self._base_kwargs()
        kwargs["pledges"] = (
            WaqfPledgeLeaf(
                aiw_number="AIW-2026-01",
                pledge_type="AIW",
                pool_code="WPAIR",
                amount_idr=200_000_000,
                dated_at="2026-12-01",
                wakif_identifier="3273011205880003",
            ),
        )
        kwargs["assets"] = (
            WaqfAssetLeaf(
                asset_code="ASSET-01",
                asset_class="CLEAN_WATER",
                certificate_ref="BPN-001",
                pool_code="WPAIR",
                book_value_idr=200_000_000,
            ),
        )
        kwargs["distributions"] = (
            WaqfDistributionLeaf(
                bast_number="BAST-01",
                pool_code="WPAIR",
                mauquf_alaih_category="CLEAN_WATER",
                amount_idr=25_000_000,
                disbursed_at="2026-12-01",
                beneficiaries_count=500,
            ),
        )
        kwargs["sroi_clusters"] = (
            WaqfSroiClusterLeaf(
                cluster_code="SROI-CW-01",
                cluster_name="Clean Water 4.11:1",
                pool_code="WPAIR",
                beneficiaries_count=500,
                sroi_ratio_bps=41100,
            ),
        )
        snap = PSAK412Snapshot(**kwargs)
        tree, entries = snap.build_merkle_tree(salt="unit-test-salt")
        self.assertEqual(len(entries), 5)
        self.assertEqual(
            [e["leaf_type"] for e in entries],
            [
                "waqf.psak412_summary",
                "waqf.pledge",
                "waqf.asset",
                "waqf.distribution",
                "waqf.sroi_cluster",
            ],
        )
        # Ensure canonical JSON has no raw NIK and preserves deterministic key order.
        pledge_json = entries[1]["canonical_json"]
        self.assertNotIn("3273011205880003", pledge_json)
        self.assertIn("wakif_commitment", pledge_json)
        self.assertEqual(
            canonical_json({"b": 2, "a": 1}),
            '{"a":1,"b":2}',
        )
        for entry in entries:
            self.assertTrue(verify_proof(tree.root_hex, entry["leaf_hash"], entry["proof"]))


class TestPrivacyShieldAndZeroSpill(unittest.TestCase):
    """UU PDP PII scrubbing and Zero-Spill guardrail tests."""

    def test_11_nik_phone_email_scrubbing(self) -> None:
        sample = (
            "Wakif NIK 3273011205880003 and 3273-0112-0588-0004 "
            "telp +62 812-3456-7890 atau 081398765432, "
            "email wakif.amanah@example.org, nominal 1404880000 IDR"
        )
        cleaned = scrub_text(sample)
        self.assertNotIn("3273011205880003", cleaned)
        self.assertNotIn("3273-0112-0588-0004", cleaned)
        self.assertNotIn("812-3456-7890", cleaned)
        self.assertNotIn("081398765432", cleaned)
        self.assertNotIn("wakif.amanah@example.org", cleaned)
        self.assertIn("[REDACTED_NIK]", cleaned)
        self.assertIn("[REDACTED_PHONE]", cleaned)
        self.assertIn("[REDACTED_EMAIL]", cleaned)
        # Non-PII IDR balance figures must remain intact.
        self.assertIn("1404880000", cleaned)

        self.assertEqual(redact_nik("ID: 3201010101900001"), "ID: [REDACTED_NIK]")
        self.assertEqual(redact_phone("WA: +6281234567890"), "WA: [REDACTED_PHONE]")
        self.assertEqual(redact_email("Mail: test@waqf.id"), "Mail: [REDACTED_EMAIL]")

    def test_12_salted_wakif_commitment_and_shield_record(self) -> None:
        c1 = commit_wakif_identity("3273011205880003", salt="salt-a")
        c2 = commit_wakif_identity("3273011205880003", salt="salt-a")
        c3 = commit_wakif_identity("3273011205880003", salt="salt-b")
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)
        self.assertTrue(c1.startswith("0x") and len(c1) == 66)

        shielded = shield_wakif_record(
            {
                "wakif_name": "Hamba Allah",
                "wakif_nik": "3273011205880003",
                "wakif_phone": "+6281234567890",
                "wakif_email": "donor@example.com",
                "pool_code": "WPAIR",
                "note": "Contact 081299988877 or donor@example.com",
            },
            salt="salt-a",
        )
        self.assertEqual(shielded["wakif_commitment"], c1)
        self.assertNotIn("wakif_name", shielded)
        self.assertNotIn("wakif_nik", shielded)
        self.assertNotIn("wakif_phone", shielded)
        self.assertNotIn("wakif_email", shielded)
        self.assertNotIn("081299988877", shielded["note"])
        self.assertNotIn("donor@example.com", shielded["note"])

    def test_13_zero_spill_detection_and_sanitization(self) -> None:
        # Dynamically assembled forbidden strings to avoid self-matching audit_hygiene.py.
        term_a = "Indonesia" + " " + "Peduli"
        term_b = "Perkumpulan" + " " + "Indonesia" + " " + "Peduli"
        term_c = "CPI" + "PS"
        fake_ghp = "ghp_" + ("A1b2C3d4E5" * 3)

        for bad in (term_a, term_b, term_c, fake_ghp):
            with self.assertRaises(ZeroSpillViolationError):
                assert_zero_spill(f"text containing {bad}")
            sanitized = sanitize_zero_spill(f"prefix {bad} suffix")
            self.assertNotIn(bad, sanitized)

        payload_scrubbed = scrub_payload({"note": f"hello {term_c}"}, raise_on_spill=False)
        self.assertEqual(payload_scrubbed["note"], "hello [REDACTED_RESTRICTED_ENTITY]")


class TestGenesisFixtureAndRelayer(unittest.TestCase):
    """End-to-end Genesis Epoch 2026-11 fixture, relayer ABI, and CLI tests."""

    def test_14_genesis_fixture_roundtrip_and_abi_payload(self) -> None:
        fixture_path = PACKAGE_ROOT / "fixtures" / "genesis_epoch_2026_11.json"
        self.assertTrue(fixture_path.exists(), f"Missing fixture: {fixture_path}")
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

        ok, errors = verify_fixture_dict(fixture)
        self.assertTrue(ok, f"Fixture verification errors: {errors}")

        metrics = fixture["psak412_metrics"]
        self.assertEqual(metrics["total_assets_idr"], 1_404_880_000)
        self.assertEqual(metrics["temp_waqf_liabilities_idr"], 63_000_000)
        self.assertEqual(metrics["net_assets_idr"], 1_341_880_000)
        self.assertEqual(metrics["reconciliation_diff_idr"], 0)
        self.assertEqual(metrics["sroi_ratio_bps"], 41100)
        self.assertEqual(
            fixture["genesis_pools"],
            ["WPUD", "WPUM", "WPAIR", "WPPAL", "WPMAS"],
        )

        # Rebuild from snapshot and confirm bit-for-bit equality of Merkle root.
        snapshot = build_genesis_snapshot()
        bundle = build_notarization_payload(
            snapshot,
            salt="waqf-dao-genesis-epoch-2026-11",
        )
        self.assertEqual(bundle["merkle_root"], fixture["merkle_root"])
        self.assertEqual(
            bundle["contract_method"],
            "notarizeEpoch(string,bytes32,uint256,uint256,uint256,uint256,bytes32)",
        )
        # 7 head words + 1 string length word + 1 string data word ("2026-11") = 9 words.
        self.assertEqual(len(bundle["abi_encoded_args_hex"]), 2 + 9 * 64)
        self.assertEqual(len(bundle["cast_args"]), 7)
        self.assertEqual(bundle["cast_args"][0], "2026-11")

    def test_15_cli_verify_and_notarize_preview(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(cli_main(["verify-fixture"]), 0)
            self.assertEqual(cli_main(["notarize-preview"]), 0)

    def test_16_odoo_merkle_stdlib_matches_oracle_bit_for_bit(self) -> None:
        repo_root = PACKAGE_ROOT.parent.parent
        odoo_stdlib_path = repo_root / "odoo-addons" / "waqf_dao_oracle" / "models" / "merkle_stdlib.py"
        spec = importlib.util.spec_from_file_location("odoo_merkle_stdlib", odoo_stdlib_path)
        self.assertIsNotNone(spec)
        odoo_mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(odoo_mod)

        fixture_path = PACKAGE_ROOT / "fixtures" / "genesis_epoch_2026_11.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        payloads = [entry["canonical_json"] for entry in fixture["leaves"]]
        odoo_bundle = odoo_mod.build_merkle_bundle(payloads)

        self.assertEqual(odoo_bundle["merkle_root"], fixture["merkle_root"])
        self.assertEqual(odoo_bundle["leaf_count"], fixture["leaf_count"])
        for idx, entry in enumerate(fixture["leaves"]):
            self.assertEqual(odoo_bundle["leaves"][idx], entry["leaf_hash"])
            self.assertEqual(odoo_bundle["proofs"][idx], entry["proof"])
            self.assertTrue(
                odoo_mod.verify_proof(
                    odoo_bundle["merkle_root"],
                    odoo_bundle["leaves"][idx],
                    odoo_bundle["proofs"][idx],
                )
            )

        # Also check 1, 3, 5, 7 leaves parity and salted commitment parity.
        for n in (1, 3, 5, 7):
            items = [f"parity-{i}" for i in range(n)]
            py_tree = build_tree(items)
            odoo_tree = odoo_mod.build_merkle_bundle(items)
            self.assertEqual(odoo_tree["merkle_root"], py_tree.root_hex)
            self.assertEqual(odoo_tree["proofs"], py_tree.get_all_proofs())

        self.assertEqual(
            odoo_mod.commit_wakif_identity("3273011205880003", salt="sync-salt"),
            commit_wakif_identity("3273011205880003", salt="sync-salt"),
        )


if __name__ == "__main__":
    unittest.main()
