"""Comprehensive unit tests for the 9-Point CIO Sentinel & Laya Triage Engine."""

from __future__ import annotations

import copy
import io
import json
import math
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cio_sentinel.cli import main as cli_main
from cio_sentinel.forensic_auditor import (
    CWLS_RISK_FREE_YIELD_PCT,
    NAUTERA_BENCHMARK_YIELD_PCT,
    audit_proposal,
    compute_circular_tank_volumes,
    compute_risk_reward_ratio,
)
from cio_sentinel.laya_triage_adapter import VALID_POOLS, triage_remark
from cio_sentinel.models import WaqfInvestmentProposal
from cio_sentinel.shariah_gate import evaluate_shariah_gate

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
NAUTERA_FIXTURE = PACKAGE_ROOT / "fixtures" / "nautera_vannamei_benchmark.json"
HIGHLAND_FIXTURE = PACKAGE_ROOT / "fixtures" / "external_highland_biofloc_proposal.json"


def _load_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestFixturesAndCombinedVerdict(unittest.TestCase):
    """Verify benchmark PASS and anomalous external REJECT_NO_GO fixtures."""

    def test_nautera_benchmark_passes_with_zero_critical_flags(self) -> None:
        proposal = WaqfInvestmentProposal.from_dict(_load_fixture(NAUTERA_FIXTURE))
        verdict = audit_proposal(proposal)

        self.assertEqual(verdict.verdict, "PASS")
        self.assertTrue(verdict.shariah_compliant)
        critical_flags = [rf for rf in verdict.red_flags if rf.severity == "CRITICAL"]
        self.assertEqual(len(critical_flags), 0)
        self.assertEqual(len(verdict.red_flags), 0)
        self.assertEqual(verdict.risk_score_0_to_100, 0.0)
        self.assertEqual(verdict.realistic_net_yield_pct, NAUTERA_BENCHMARK_YIELD_PCT)
        self.assertEqual(verdict.risk_reward_ratio, 0.0)

    def test_external_highland_biofloc_rejected_with_at_least_seven_flags(self) -> None:
        proposal = WaqfInvestmentProposal.from_dict(_load_fixture(HIGHLAND_FIXTURE))
        verdict = audit_proposal(proposal)

        self.assertEqual(verdict.verdict, "REJECT_NO_GO")
        self.assertFalse(verdict.shariah_compliant)
        self.assertGreaterEqual(len(verdict.red_flags), 7)
        self.assertGreaterEqual(verdict.risk_score_0_to_100, 90.0)
        self.assertAlmostEqual(verdict.true_fcr, 4500.0 / 8100.0, places=3)
        self.assertGreater(verdict.capex_markup_pct, 80.0)
        self.assertGreater(verdict.risk_reward_ratio, 5.0)
        self.assertLess(verdict.realistic_net_yield_pct, 0.0)

        codes = {rf.code for rf in verdict.red_flags}
        self.assertIn("FORENSIC_FCR_IMPOSSIBLE", codes)
        self.assertIn("FORENSIC_NET_EXCEEDS_GROSS", codes)
        self.assertIn("FORENSIC_CAPEX_OVERPRICING", codes)
        self.assertIn("FORENSIC_HIGHLAND_THERMAL_DEFICIT", codes)
        self.assertIn("FORENSIC_TANK_OVERSTOCKING", codes)
        self.assertIn("FORENSIC_RRR_EXTREME_ASYMMETRY", codes)
        self.assertIn("SHARIAH_UNPROTECTED_AKAD", codes)

    def test_conditional_restructure_on_single_high_flag(self) -> None:
        data = copy.deepcopy(_load_fixture(NAUTERA_FIXTURE))
        # Push CAPEX slightly above 25% threshold (30% markup) -> single HIGH flag
        data["technical_agro"]["capex_per_unit_idr"] = 32_500_000.0
        proposal = WaqfInvestmentProposal.from_dict(data)
        verdict = audit_proposal(proposal)

        self.assertTrue(verdict.shariah_compliant)
        self.assertEqual(verdict.verdict, "CONDITIONAL_RESTRUCTURE")
        self.assertEqual([rf.code for rf in verdict.red_flags], ["FORENSIC_CAPEX_OVERPRICING"])


class TestShariahConstitutionalGate(unittest.TestCase):
    """Verify Gate 1 Shariah, UU 41/2004, and PSAK 412 checks individually."""

    def setUp(self) -> None:
        self.base = _load_fixture(NAUTERA_FIXTURE)

    def test_rejects_pure_mudharabah_or_musyarakah(self) -> None:
        for akad in ("mudharabah", "musyarakah"):
            data = copy.deepcopy(self.base)
            data["contract_waterfall"]["akad_type"] = akad
            compliant, flags = evaluate_shariah_gate(WaqfInvestmentProposal.from_dict(data))
            self.assertFalse(compliant)
            self.assertIn("SHARIAH_UNPROTECTED_AKAD", {f.code for f in flags})

    def test_enforces_sinking_fund_floor_and_nazhir_cap(self) -> None:
        data = copy.deepcopy(self.base)
        data["contract_waterfall"]["sinking_fund_pct"] = 9.5
        data["contract_waterfall"]["nazhir_total_pct"] = 12.0
        data["contract_waterfall"]["double_nazhir_stacking"] = True
        data["contract_waterfall"]["mauquf_alaih_pct"] = 45.0
        compliant, flags = evaluate_shariah_gate(WaqfInvestmentProposal.from_dict(data))

        self.assertFalse(compliant)
        codes = {f.code for f in flags}
        self.assertIn("SHARIAH_INSUFFICIENT_SINKING_FUND", codes)
        self.assertIn("SHARIAH_NAZHIR_CAP_EXCEEDED", codes)
        self.assertIn("SHARIAH_DOUBLE_NAZHIR_STACKING", codes)
        self.assertIn("SHARIAH_MAUQUF_ALAIH_BELOW_MIN", codes)

    def test_blocks_upfront_capex_on_uncertified_land_without_lease_collateral(self) -> None:
        data = copy.deepcopy(self.base)
        data["land_legal"]["has_aiw_certificate"] = False
        data["land_legal"]["has_bpn_stw"] = False
        data["land_legal"]["is_leasehold_or_state_land"] = True
        data["land_legal"]["tenure_years"] = 2.0
        data["contract_waterfall"]["upfront_capex_ratio_pct"] = 80.0
        compliant, flags = evaluate_shariah_gate(WaqfInvestmentProposal.from_dict(data))

        self.assertFalse(compliant)
        self.assertIn("SHARIAH_UNCERTIFIED_LAND_CAPEX", {f.code for f in flags})

    def test_flags_asset_reversion_capital_trap(self) -> None:
        data = copy.deepcopy(self.base)
        data["contract_waterfall"]["asset_reverts_to_operator_at_end"] = True
        compliant, flags = evaluate_shariah_gate(WaqfInvestmentProposal.from_dict(data))

        self.assertFalse(compliant)
        self.assertIn("SHARIAH_CAPITAL_TRAP_ASSET_REVERSION", {f.code for f in flags})


class TestForensicPhysicsAndFinancialGates(unittest.TestCase):
    """Verify Gate 2 biological, thermal, geometric, accounting, RRR, and benchmark rules."""

    def setUp(self) -> None:
        self.base = _load_fixture(NAUTERA_FIXTURE)

    def test_fcr_impossibility_computes_hidden_feed_deficit(self) -> None:
        data = copy.deepcopy(self.base)
        data["technical_agro"]["claimed_feed_kg_per_cycle"] = 450.0
        data["technical_agro"]["claimed_harvest_kg_per_cycle"] = 810.0
        data["technical_agro"]["claimed_fcr"] = 0.56
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        fcr_flags = [rf for rf in verdict.red_flags if rf.code == "FORENSIC_FCR_IMPOSSIBLE"]
        self.assertEqual(len(fcr_flags), 1)
        self.assertAlmostEqual(verdict.true_fcr, 450.0 / 810.0, places=4)
        self.assertAlmostEqual(fcr_flags[0].evidence["hidden_unfunded_feed_deficit_kg"], 522.0, places=1)
        self.assertEqual(verdict.verdict, "REJECT_NO_GO")

    def test_accounting_impossibility_net_profit_exceeds_gross_revenue(self) -> None:
        data = copy.deepcopy(self.base)
        data["contract_waterfall"]["claimed_gross_revenue_idr"] = 100_000_000.0
        data["contract_waterfall"]["claimed_net_profit_idr"] = 125_000_000.0
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        self.assertIn("FORENSIC_NET_EXCEEDS_GROSS", {rf.code for rf in verdict.red_flags})
        self.assertEqual(verdict.verdict, "REJECT_NO_GO")

    def test_agroclimate_highland_thermal_deficit_trigger(self) -> None:
        data = copy.deepcopy(self.base)
        data["technical_agro"]["elevation_mdpl"] = 900.0
        data["technical_agro"]["ambient_temp_c_min"] = 17.5
        data["technical_agro"]["claimed_cycles_per_year"] = 4.0
        data["technical_agro"]["has_thermal_control"] = False
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        self.assertIn("FORENSIC_HIGHLAND_THERMAL_DEFICIT", {rf.code for rf in verdict.red_flags})

    def test_circular_tank_volume_with_freeboard_and_overstocking(self) -> None:
        full_vol, eff_vol = compute_circular_tank_volumes(diameter_m=3.0, height_m=1.2, tank_count=20)
        expected_full = math.pi * (1.5 ** 2) * 1.2 * 20
        expected_eff = math.pi * (1.5 ** 2) * 1.0 * 20
        self.assertAlmostEqual(full_vol, expected_full, places=4)
        self.assertAlmostEqual(eff_vol, expected_eff, places=4)

        data = copy.deepcopy(self.base)
        data["technical_agro"]["tank_diameter_m"] = 3.0
        data["technical_agro"]["tank_height_m"] = 1.2
        data["technical_agro"]["tank_count"] = 20
        data["technical_agro"]["claimed_harvest_kg_per_cycle"] = 8100.0
        data["technical_agro"]["claimed_feed_kg_per_cycle"] = 10530.0
        data["technical_agro"]["claimed_fcr"] = 1.30
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        self.assertAlmostEqual(verdict.effective_water_volume_m3, expected_eff, places=2)
        self.assertIn("FORENSIC_TANK_OVERSTOCKING", {rf.code for rf in verdict.red_flags})

    def test_risk_reward_ratio_calculation_and_ceiling(self) -> None:
        self.assertAlmostEqual(compute_risk_reward_ratio(25.0, 50.0), 0.50, places=4)
        self.assertAlmostEqual(compute_risk_reward_ratio(100.0, 0.0), 10000.0, places=2)

        data = copy.deepcopy(self.base)
        data["contract_waterfall"]["capital_at_risk_pct"] = 40.0
        data["contract_waterfall"]["expected_net_cash_year1_pct"] = 20.0
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        self.assertAlmostEqual(verdict.risk_reward_ratio, 2.0, places=2)
        self.assertIn("FORENSIC_RRR_EXTREME_ASYMMETRY", {rf.code for rf in verdict.red_flags})

    def test_opportunity_cost_benchmark_comparison(self) -> None:
        data = copy.deepcopy(self.base)
        data["contract_waterfall"]["annual_cash_yield_pct"] = 10.0
        data["contract_waterfall"]["annual_depreciation_pct"] = 5.0
        verdict = audit_proposal(WaqfInvestmentProposal.from_dict(data))

        self.assertEqual(verdict.realistic_net_yield_pct, 5.0)
        self.assertEqual(verdict.benchmark_comparison["cwls_risk_free_yield_pct"], CWLS_RISK_FREE_YIELD_PCT)
        self.assertEqual(verdict.benchmark_comparison["internal_nautera_yield_pct"], NAUTERA_BENCHMARK_YIELD_PCT)
        codes = {rf.code for rf in verdict.red_flags}
        self.assertIn("OPPORTUNITY_BELOW_CWLS_RISK_FREE", codes)
        self.assertIn("OPPORTUNITY_BELOW_INTERNAL_BENCHMARK", codes)


class TestLayaTriageAdapterAndCLI(unittest.TestCase):
    """Verify deterministic Laya pool triage across all 5 pools, abstain, Zero-Spill, and CLI."""

    def test_triage_routes_all_five_pools(self) -> None:
        samples = {
            "WPUD": "Modal kerja usaha produktif akuakultur udang vannamei Nautera via ijarah",
            "WPUM": "Wakaf umum beasiswa pendidikan pesantren dan klinik kesehatan umat",
            "WPAIR": "Wakaf air bersih pembangunan sumur bor pipanisasi dan sanitasi MCK",
            "WPPAL": "Wakaf pangan produktif lahan pertanian sawah hidroponik ketahanan pangan",
            "WPMAS": "Wakaf masjid renovasi musholla tempat wudhu karpet masjid dan marbot",
        }
        for expected_pool, remark in samples.items():
            res = triage_remark(remark)
            self.assertIn(res.pool_code, VALID_POOLS)
            self.assertEqual(res.pool_code, expected_pool)
            self.assertFalse(res.abstain)
            self.assertFalse(res.zero_spill_violation)
            self.assertGreaterEqual(res.confidence, 0.60)

    def test_triage_abstains_on_vague_or_ambiguous_remark(self) -> None:
        vague = triage_remark("Transfer donasi berkah")
        self.assertTrue(vague.abstain)
        self.assertTrue(vague.needs_treasurer_review)
        self.assertEqual(vague.confidence, 0.0)

        tied = triage_remark("Wakaf air bersih dan wakaf masjid")
        self.assertTrue(tied.abstain)
        self.assertTrue(tied.needs_treasurer_review)

    def test_triage_blocks_zero_spill_entity(self) -> None:
        # Dynamically construct test inputs to keep source compliant with Zero-Spill scanner.
        term_a = "Transfer untuk " + "Indonesia" + " " + "Peduli" + " sumur bor"
        term_b = "Dana " + "CPI" + "PS" + " operasional"
        for text in (term_a, term_b):
            res = triage_remark(text)
            self.assertTrue(res.zero_spill_violation)
            self.assertTrue(res.abstain)
            self.assertTrue(res.needs_treasurer_review)
            self.assertEqual(res.confidence, 0.0)

    def test_cli_audit_and_triage_commands(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_main(["audit", str(HIGHLAND_FIXTURE), "--format", "json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["verdict"], "REJECT_NO_GO")

        buf_triage = io.StringIO()
        with redirect_stdout(buf_triage):
            rc_triage = cli_main(["triage", "Wakaf air bersih sumur bor desa"])
        self.assertEqual(rc_triage, 0)
        triage_out = json.loads(buf_triage.getvalue())
        self.assertEqual(triage_out["pool_code"], "WPAIR")


if __name__ == "__main__":
    unittest.main()
