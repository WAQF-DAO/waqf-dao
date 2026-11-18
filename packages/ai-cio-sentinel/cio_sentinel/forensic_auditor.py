"""Gate 2: 9-Point Biological, Engineering, Financial & Opportunity Cost Forensics."""

from __future__ import annotations

import math
from typing import Any

from .models import ForensicVerdict, RedFlag, TechnicalAgroParams, VerdictType, WaqfInvestmentProposal
from .shariah_gate import evaluate_shariah_gate

CWLS_RISK_FREE_YIELD_PCT = 6.0
NAUTERA_BENCHMARK_YIELD_PCT = 18.02

BIOFLOC_FCR_REALISTIC_MIN = 1.15
BIOFLOC_FCR_REALISTIC_MID = 1.20
BIOFLOC_FCR_REALISTIC_MAX = 1.30

FREEBOARD_M = 0.20
MAX_HARVEST_DENSITY_KG_M3 = 50.0
MAX_CAPEX_MARKUP_PCT = 25.0
MAX_COMMITTEE_RRR = 0.50

AQUACULTURE_SECTORS = frozenset(
    {
        "aquaculture",
        "tilapia",
        "nile_tilapia",
        "nila",
        "vannamei",
        "shrimp",
        "biofloc",
        "catfish",
        "lele",
        "patin",
        "fishery",
    }
)

IMPOSSIBILITY_CODES = frozenset(
    {
        "FORENSIC_FCR_IMPOSSIBLE",
        "FORENSIC_NET_EXCEEDS_GROSS",
    }
)


def compute_true_fcr(tech: TechnicalAgroParams) -> float:
    """Derive implied FCR from feed/harvest volumes when present, else claimed FCR."""
    if tech.claimed_feed_kg_per_cycle > 0.0 and tech.claimed_harvest_kg_per_cycle > 0.0:
        return tech.claimed_feed_kg_per_cycle / tech.claimed_harvest_kg_per_cycle
    return tech.claimed_fcr


def compute_circular_tank_volumes(
    diameter_m: float,
    height_m: float,
    tank_count: int,
    freeboard_m: float = FREEBOARD_M,
) -> tuple[float, float]:
    """Return ``(full_volume_m3, effective_water_volume_m3)`` for circular tanks."""
    if diameter_m <= 0.0 or height_m <= 0.0 or tank_count <= 0:
        return 0.0, 0.0
    radius_m = diameter_m / 2.0
    area_m2 = math.pi * (radius_m ** 2)
    full_vol = area_m2 * height_m * tank_count
    effective_height = max(0.0, height_m - freeboard_m)
    effective_vol = area_m2 * effective_height * tank_count
    return full_vol, effective_vol


def compute_risk_reward_ratio(capital_at_risk_pct: float, expected_net_cash_year1_pct: float) -> float:
    """Compute Risk-Reward Ratio = capital_at_risk_pct / max(expected_net_cash_year1_pct, 0.01)."""
    return capital_at_risk_pct / max(expected_net_cash_year1_pct, 0.01)


def _check_fcr_physics(tech: TechnicalAgroParams, true_fcr: float) -> list[RedFlag]:
    flags: list[RedFlag] = []
    sector_norm = tech.sector.strip().lower()
    if sector_norm not in AQUACULTURE_SECTORS:
        return flags

    if 0.0 < true_fcr < 1.0:
        required_feed_kg = (
            tech.claimed_harvest_kg_per_cycle * BIOFLOC_FCR_REALISTIC_MID
            if tech.claimed_harvest_kg_per_cycle > 0.0
            else 0.0
        )
        feed_deficit_kg = max(0.0, required_feed_kg - tech.claimed_feed_kg_per_cycle)
        flags.append(
            RedFlag(
                code="FORENSIC_FCR_IMPOSSIBLE",
                severity="CRITICAL",
                gate="BIOLOGICAL_PHYSICS",
                title="Biological Impossibility: Aquaculture FCR < 1.0",
                detail=(
                    f"Implied FCR is {true_fcr:.2f} (claimed {tech.claimed_fcr:.2f}), which violates "
                    "mass-conservation physics for aquaculture (realistic bioflok FCR "
                    f"{BIOFLOC_FCR_REALISTIC_MIN:.2f}-{BIOFLOC_FCR_REALISTIC_MAX:.2f}). "
                    f"Hidden unfunded feed deficit: {feed_deficit_kg:,.1f} kg/cycle."
                ),
                evidence={
                    "true_fcr": round(true_fcr, 4),
                    "claimed_fcr": tech.claimed_fcr,
                    "claimed_feed_kg_per_cycle": tech.claimed_feed_kg_per_cycle,
                    "claimed_harvest_kg_per_cycle": tech.claimed_harvest_kg_per_cycle,
                    "realistic_fcr_range": [BIOFLOC_FCR_REALISTIC_MIN, BIOFLOC_FCR_REALISTIC_MAX],
                    "required_feed_kg_at_1_20_fcr": round(required_feed_kg, 2),
                    "hidden_unfunded_feed_deficit_kg": round(feed_deficit_kg, 2),
                },
            )
        )
    elif 1.0 <= true_fcr < BIOFLOC_FCR_REALISTIC_MIN:
        flags.append(
            RedFlag(
                code="FORENSIC_FCR_BELOW_BENCHMARK",
                severity="HIGH",
                gate="BIOLOGICAL_PHYSICS",
                title="Optimistic FCR Below Industry Bioflok Floor",
                detail=(
                    f"Implied FCR {true_fcr:.2f} is below the {BIOFLOC_FCR_REALISTIC_MIN:.2f} "
                    "commercial bioflok benchmark."
                ),
                evidence={
                    "true_fcr": round(true_fcr, 4),
                    "realistic_min_fcr": BIOFLOC_FCR_REALISTIC_MIN,
                },
            )
        )

    if (
        tech.claimed_fcr > 0.0
        and tech.claimed_feed_kg_per_cycle > 0.0
        and tech.claimed_harvest_kg_per_cycle > 0.0
        and abs(tech.claimed_fcr - true_fcr) > 0.15
    ):
        flags.append(
            RedFlag(
                code="FORENSIC_FCR_CLAIM_MISMATCH",
                severity="HIGH",
                gate="BIOLOGICAL_PHYSICS",
                title="Claimed FCR Contradicts Feed/Harvest Mass Budget",
                detail=(
                    f"Proposal states FCR {tech.claimed_fcr:.2f}, but budgeted feed/harvest implies "
                    f"{true_fcr:.2f}."
                ),
                evidence={
                    "claimed_fcr": tech.claimed_fcr,
                    "implied_fcr": round(true_fcr, 4),
                },
            )
        )
    return flags


def _check_accounting_integrity(proposal: WaqfInvestmentProposal) -> list[RedFlag]:
    contract = proposal.contract_waterfall
    if contract.claimed_net_profit_idr > contract.claimed_gross_revenue_idr and (
        contract.claimed_net_profit_idr > 0.0 or contract.claimed_gross_revenue_idr > 0.0
    ):
        return [
            RedFlag(
                code="FORENSIC_NET_EXCEEDS_GROSS",
                severity="CRITICAL",
                gate="FINANCIAL_FORENSICS",
                title="Track Record Accounting Impossibility (Net Profit > Gross Revenue)",
                detail=(
                    f"Claimed net profit (IDR {contract.claimed_net_profit_idr:,.0f}) exceeds "
                    f"claimed gross revenue (IDR {contract.claimed_gross_revenue_idr:,.0f})."
                ),
                evidence={
                    "claimed_gross_revenue_idr": contract.claimed_gross_revenue_idr,
                    "claimed_net_profit_idr": contract.claimed_net_profit_idr,
                },
            )
        ]
    return []


def _check_capex_overpricing(tech: TechnicalAgroParams) -> tuple[float, list[RedFlag]]:
    if tech.benchmark_capex_per_unit_idr <= 0.0 or tech.capex_per_unit_idr <= 0.0:
        return 0.0, []
    markup_pct = (
        (tech.capex_per_unit_idr - tech.benchmark_capex_per_unit_idr)
        / tech.benchmark_capex_per_unit_idr
    ) * 100.0
    flags: list[RedFlag] = []
    if markup_pct > MAX_CAPEX_MARKUP_PCT:
        severity = "CRITICAL" if markup_pct >= 50.0 else "HIGH"
        flags.append(
            RedFlag(
                code="FORENSIC_CAPEX_OVERPRICING",
                severity=severity,
                gate="FINANCIAL_FORENSICS",
                title=f"CAPEX Overpricing / Mark-Up (+{markup_pct:.1f}% vs Benchmark)",
                detail=(
                    f"Unit CAPEX of IDR {tech.capex_per_unit_idr:,.0f} exceeds institutional "
                    f"benchmark IDR {tech.benchmark_capex_per_unit_idr:,.0f} by {markup_pct:.1f}% "
                    f"(ceiling +{MAX_CAPEX_MARKUP_PCT:.0f}%)."
                ),
                evidence={
                    "capex_per_unit_idr": tech.capex_per_unit_idr,
                    "benchmark_capex_per_unit_idr": tech.benchmark_capex_per_unit_idr,
                    "capex_markup_pct": round(markup_pct, 2),
                },
            )
        )
    return markup_pct, flags


def _check_agroclimate_thermal(tech: TechnicalAgroParams) -> list[RedFlag]:
    if tech.sector.strip().lower() not in AQUACULTURE_SECTORS or tech.has_thermal_control:
        return []
    is_cold_highland = tech.elevation_mdpl > 700.0 or tech.ambient_temp_c_min < 20.0
    if not is_cold_highland:
        return []

    if tech.claimed_cycles_per_year >= 4.0:
        return [
            RedFlag(
                code="FORENSIC_HIGHLAND_THERMAL_DEFICIT",
                severity="HIGH",
                gate="BIOLOGICAL_PHYSICS",
                title="Agroclimate & Thermal Physics Violation (Unheated Highland Cycles)",
                detail=(
                    f"Site at {tech.elevation_mdpl:.0f} mdpl (min {tech.ambient_temp_c_min:.1f}°C) "
                    f"claims {tech.claimed_cycles_per_year:.1f} cycles/year without thermal control; "
                    "realistic warm-water growth yields <= 2.5 - 3.0 cycles/year."
                ),
                evidence={
                    "elevation_mdpl": tech.elevation_mdpl,
                    "ambient_temp_c_min": tech.ambient_temp_c_min,
                    "claimed_cycles_per_year": tech.claimed_cycles_per_year,
                    "has_thermal_control": tech.has_thermal_control,
                    "realistic_max_cycles_per_year": "2.5 - 3.0",
                },
            )
        ]
    if tech.claimed_cycles_per_year > 3.0:
        return [
            RedFlag(
                code="FORENSIC_HIGHLAND_CYCLE_OPTIMISM",
                severity="MEDIUM",
                gate="BIOLOGICAL_PHYSICS",
                title="Optimistic Highland Cycle Assumption Without Heating",
                detail=(
                    f"Claiming {tech.claimed_cycles_per_year:.1f} cycles/year at "
                    f"{tech.elevation_mdpl:.0f} mdpl without thermal control exceeds 3.0 cycles."
                ),
                evidence={
                    "elevation_mdpl": tech.elevation_mdpl,
                    "ambient_temp_c_min": tech.ambient_temp_c_min,
                    "claimed_cycles_per_year": tech.claimed_cycles_per_year,
                },
            )
        ]
    return []


def _check_tank_overstocking(
    tech: TechnicalAgroParams,
    full_vol_m3: float,
    effective_vol_m3: float,
) -> list[RedFlag]:
    if effective_vol_m3 <= 0.0 or tech.claimed_harvest_kg_per_cycle <= 0.0:
        return []
    density_kg_m3 = tech.claimed_harvest_kg_per_cycle / effective_vol_m3
    if density_kg_m3 > MAX_HARVEST_DENSITY_KG_M3:
        severity = "CRITICAL" if density_kg_m3 >= 80.0 else "HIGH"
        return [
            RedFlag(
                code="FORENSIC_TANK_OVERSTOCKING",
                severity=severity,
                gate="BIOLOGICAL_PHYSICS",
                title="Extreme Circular Tank Harvest Biomass Overstocking",
                detail=(
                    f"Claimed harvest of {tech.claimed_harvest_kg_per_cycle:,.1f} kg across "
                    f"{effective_vol_m3:.2f} m³ effective water volume (0.2m freeboard) implies "
                    f"{density_kg_m3:.2f} kg/m³, exceeding the {MAX_HARVEST_DENSITY_KG_M3:.0f} kg/m³ limit."
                ),
                evidence={
                    "tank_count": tech.tank_count,
                    "tank_diameter_m": tech.tank_diameter_m,
                    "tank_height_m": tech.tank_height_m,
                    "full_water_volume_m3": round(full_vol_m3, 2),
                    "effective_water_volume_m3": round(effective_vol_m3, 2),
                    "harvest_biomass_density_kg_m3": round(density_kg_m3, 2),
                    "max_safe_density_kg_m3": MAX_HARVEST_DENSITY_KG_M3,
                },
            )
        ]
    return []


def _check_yield_and_rrr(proposal: WaqfInvestmentProposal) -> tuple[float, float, list[RedFlag]]:
    contract = proposal.contract_waterfall
    realistic_net_yield_pct = contract.annual_cash_yield_pct - contract.annual_depreciation_pct
    rrr = compute_risk_reward_ratio(
        contract.capital_at_risk_pct,
        contract.expected_net_cash_year1_pct,
    )
    flags: list[RedFlag] = []

    if (
        not contract.has_principal_guarantee or contract.asset_reverts_to_operator_at_end
    ) and contract.annual_depreciation_pct > 0.0:
        if realistic_net_yield_pct <= 0.0:
            flags.append(
                RedFlag(
                    code="FORENSIC_CAPITAL_TRAP_NEGATIVE_YIELD",
                    severity="CRITICAL",
                    gate="FINANCIAL_FORENSICS",
                    title="Capital Trap: Negative Realistic Net Yield After Asset Depreciation",
                    detail=(
                        f"Headline cash yield ({contract.annual_cash_yield_pct:.2f}%) minus "
                        f"unhedged depreciation ({contract.annual_depreciation_pct:.2f}%) yields "
                        f"{realistic_net_yield_pct:.2f}% p.a., eroding waqf principal."
                    ),
                    evidence={
                        "annual_cash_yield_pct": contract.annual_cash_yield_pct,
                        "annual_depreciation_pct": contract.annual_depreciation_pct,
                        "realistic_net_yield_pct": round(realistic_net_yield_pct, 2),
                    },
                )
            )
        elif realistic_net_yield_pct < contract.annual_cash_yield_pct * 0.5:
            flags.append(
                RedFlag(
                    code="FORENSIC_DEPRECIATION_EROSION",
                    severity="HIGH",
                    gate="FINANCIAL_FORENSICS",
                    title="Severe Principal Depreciation Erosion (> 50% of Gross Yield)",
                    detail=(
                        f"Net yield drops from {contract.annual_cash_yield_pct:.2f}% to "
                        f"{realistic_net_yield_pct:.2f}% after accounting for depreciation."
                    ),
                    evidence={
                        "annual_cash_yield_pct": contract.annual_cash_yield_pct,
                        "annual_depreciation_pct": contract.annual_depreciation_pct,
                        "realistic_net_yield_pct": round(realistic_net_yield_pct, 2),
                    },
                )
            )

    if rrr >= 2.0:
        flags.append(
            RedFlag(
                code="FORENSIC_RRR_EXTREME_ASYMMETRY",
                severity="CRITICAL",
                gate="FINANCIAL_FORENSICS",
                title=f"Extreme Risk-Reward Asymmetry ({rrr:.2f} : 1 vs 0.50 : 1 Ceiling)",
                detail=(
                    f"Risking {contract.capital_at_risk_pct:.1f}% capital for "
                    f"{contract.expected_net_cash_year1_pct:.2f}% year-1 net cash produces "
                    f"RRR {rrr:.2f}:1, severely breaching the committee ceiling of {MAX_COMMITTEE_RRR:.2f}:1."
                ),
                evidence={
                    "capital_at_risk_pct": contract.capital_at_risk_pct,
                    "expected_net_cash_year1_pct": contract.expected_net_cash_year1_pct,
                    "risk_reward_ratio": round(rrr, 2),
                    "committee_max_rrr": MAX_COMMITTEE_RRR,
                },
            )
        )
    elif rrr > MAX_COMMITTEE_RRR:
        flags.append(
            RedFlag(
                code="FORENSIC_RRR_CEILING_EXCEEDED",
                severity="HIGH",
                gate="FINANCIAL_FORENSICS",
                title=f"Risk-Reward Ratio Exceeds Committee Ceiling ({rrr:.2f} : 1)",
                detail=(
                    f"RRR of {rrr:.2f}:1 breaches the institutional {MAX_COMMITTEE_RRR:.2f}:1 ceiling."
                ),
                evidence={
                    "risk_reward_ratio": round(rrr, 2),
                    "committee_max_rrr": MAX_COMMITTEE_RRR,
                },
            )
        )

    return realistic_net_yield_pct, rrr, flags


def _check_opportunity_cost(
    proposal: WaqfInvestmentProposal,
    realistic_net_yield_pct: float,
    rrr: float,
) -> tuple[dict[str, Any], list[RedFlag]]:
    contract = proposal.contract_waterfall
    sector_norm = proposal.technical_agro.sector.strip().lower()
    flags: list[RedFlag] = []

    if realistic_net_yield_pct < CWLS_RISK_FREE_YIELD_PCT:
        flags.append(
            RedFlag(
                code="OPPORTUNITY_BELOW_CWLS_RISK_FREE",
                severity="HIGH",
                gate="OPPORTUNITY_COST",
                title="Realistic Net Yield Below Sovereign CWLS Risk-Free Floor (6.0%)",
                detail=(
                    f"Realistic net yield ({realistic_net_yield_pct:.2f}% p.a.) underperforms "
                    f"sovereign CWLS / Sukuk ({CWLS_RISK_FREE_YIELD_PCT:.2f}% p.a. risk-free)."
                ),
                evidence={
                    "realistic_net_yield_pct": round(realistic_net_yield_pct, 2),
                    "cwls_risk_free_yield_pct": CWLS_RISK_FREE_YIELD_PCT,
                },
            )
        )

    if sector_norm in AQUACULTURE_SECTORS and realistic_net_yield_pct < NAUTERA_BENCHMARK_YIELD_PCT:
        if not contract.has_principal_guarantee or realistic_net_yield_pct < (
            NAUTERA_BENCHMARK_YIELD_PCT - 2.0
        ):
            severity = "HIGH" if not contract.has_principal_guarantee else "MEDIUM"
            flags.append(
                RedFlag(
                    code="OPPORTUNITY_BELOW_INTERNAL_BENCHMARK",
                    severity=severity,
                    gate="OPPORTUNITY_COST",
                    title="Inferior to Internal Aquaculture Benchmark (Nautera 18.02% Protected)",
                    detail=(
                        f"Proposal yields {realistic_net_yield_pct:.2f}% p.a. (principal_guarantee="
                        f"{contract.has_principal_guarantee}) vs internal Nautera benchmark "
                        f"at {NAUTERA_BENCHMARK_YIELD_PCT:.2f}% p.a. with 100% principal protection."
                    ),
                    evidence={
                        "realistic_net_yield_pct": round(realistic_net_yield_pct, 2),
                        "nautera_benchmark_yield_pct": NAUTERA_BENCHMARK_YIELD_PCT,
                        "has_principal_guarantee": contract.has_principal_guarantee,
                    },
                )
            )

    comparison = {
        "cwls_risk_free_yield_pct": CWLS_RISK_FREE_YIELD_PCT,
        "internal_nautera_yield_pct": NAUTERA_BENCHMARK_YIELD_PCT,
        "proposal_claimed_yield_pct": round(contract.annual_cash_yield_pct, 2),
        "proposal_realistic_net_yield_pct": round(realistic_net_yield_pct, 2),
        "spread_vs_cwls_pct": round(realistic_net_yield_pct - CWLS_RISK_FREE_YIELD_PCT, 2),
        "spread_vs_nautera_pct": round(realistic_net_yield_pct - NAUTERA_BENCHMARK_YIELD_PCT, 2),
        "capital_at_risk_pct": round(contract.capital_at_risk_pct, 2),
        "risk_reward_ratio": round(rrr, 2),
        "committee_max_rrr": MAX_COMMITTEE_RRR,
    }
    return comparison, flags


def _determine_verdict(
    shariah_compliant: bool,
    red_flags: list[RedFlag],
) -> tuple[VerdictType, float, str]:
    critical_count = sum(1 for f in red_flags if f.severity == "CRITICAL")
    high_count = sum(1 for f in red_flags if f.severity == "HIGH")
    medium_count = sum(1 for f in red_flags if f.severity == "MEDIUM")

    risk_score = min(100.0, critical_count * 25.0 + high_count * 12.0 + medium_count * 5.0)
    has_impossibility = any(f.code in IMPOSSIBILITY_CODES for f in red_flags)

    if has_impossibility or critical_count >= 2 or risk_score >= 50.0:
        verdict: VerdictType = "REJECT_NO_GO"
        recommendation = (
            "REJECT / NO-GO: Proposal exhibits severe biological/accounting anomalies, "
            "asymmetric principal risk, or constitutional Shariah/PSAK 412 breaches. "
            "Redirect capital to Sovereign CWLS (6.0%) or Nautera Benchmark (18.02% protected)."
        )
    elif not shariah_compliant or critical_count == 1 or high_count >= 1:
        verdict = "CONDITIONAL_RESTRUCTURE"
        recommendation = (
            "CONDITIONAL RESTRUCTURE: Remediate flagged Shariah governance, collateral, "
            "CAPEX pricing, or RRR ceiling violations before IC approval."
        )
    else:
        verdict = "PASS"
        recommendation = (
            "PASS: Proposal satisfies Hifzh al-Mal Shariah constitutional screening, "
            "biological/engineering physics, RRR ceiling (<= 0.50:1), and yield benchmarks."
        )

    return verdict, risk_score, recommendation


def audit_proposal(proposal: WaqfInvestmentProposal) -> ForensicVerdict:
    """Run the full 9-point CIO Forensic & Shariah Screening Engine on a proposal."""
    shariah_compliant, shariah_flags = evaluate_shariah_gate(proposal)
    tech = proposal.technical_agro

    # Point 1: FCR physics
    true_fcr = compute_true_fcr(tech)
    fcr_flags = _check_fcr_physics(tech, true_fcr)

    # Point 2: Accounting integrity
    accounting_flags = _check_accounting_integrity(proposal)

    # Point 3: CAPEX mark-up
    capex_markup_pct, capex_flags = _check_capex_overpricing(tech)

    # Point 4: Agroclimate & thermal physics
    thermal_flags = _check_agroclimate_thermal(tech)

    # Point 5: Circular tank volume & overstocking
    full_vol_m3, effective_vol_m3 = compute_circular_tank_volumes(
        tech.tank_diameter_m,
        tech.tank_height_m,
        tech.tank_count,
    )
    overstock_flags = _check_tank_overstocking(tech, full_vol_m3, effective_vol_m3)

    # Points 6 & 7: True Net Yield & RRR Gate
    realistic_net_yield_pct, rrr, yield_rrr_flags = _check_yield_and_rrr(proposal)

    # Point 8: Opportunity Cost Benchmark
    benchmark_comparison, opportunity_flags = _check_opportunity_cost(
        proposal,
        realistic_net_yield_pct,
        rrr,
    )

    all_flags = [
        *shariah_flags,
        *fcr_flags,
        *accounting_flags,
        *capex_flags,
        *thermal_flags,
        *overstock_flags,
        *yield_rrr_flags,
        *opportunity_flags,
    ]

    # Point 9: Combined Verdict Engine
    verdict, risk_score, recommendation = _determine_verdict(shariah_compliant, all_flags)

    return ForensicVerdict(
        proposal_id=proposal.proposal_id,
        verdict=verdict,
        risk_score_0_to_100=round(risk_score, 2),
        shariah_compliant=shariah_compliant,
        risk_reward_ratio=round(rrr, 2),
        realistic_net_yield_pct=round(realistic_net_yield_pct, 2),
        true_fcr=round(true_fcr, 4),
        effective_water_volume_m3=round(effective_vol_m3, 2),
        capex_markup_pct=round(capex_markup_pct, 2),
        red_flags=all_flags,
        benchmark_comparison=benchmark_comparison,
        recommendation=recommendation,
    )
