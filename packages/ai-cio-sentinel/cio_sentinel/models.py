"""Typed data models for the AI CIO Forensic & Shariah Screening Engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Mapping

Severity = Literal["CRITICAL", "HIGH", "MEDIUM"]
GateName = Literal[
    "SHARIAH_GOVERNANCE",
    "BIOLOGICAL_PHYSICS",
    "FINANCIAL_FORENSICS",
    "OPPORTUNITY_COST",
]
VerdictType = Literal["PASS", "CONDITIONAL_RESTRUCTURE", "REJECT_NO_GO"]
PoolCode = Literal["WPUD", "WPUM", "WPAIR", "WPPAL", "WPMAS"]


@dataclass(slots=True)
class LandLegalParams:
    """Land title, legal tenure, and commercial offtaker verification parameters."""

    has_aiw_certificate: bool
    has_bpn_stw: bool
    is_leasehold_or_state_land: bool
    tenure_years: float
    offtaker_entity_verified: bool

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> LandLegalParams:
        return cls(
            has_aiw_certificate=bool(data["has_aiw_certificate"]),
            has_bpn_stw=bool(data["has_bpn_stw"]),
            is_leasehold_or_state_land=bool(data["is_leasehold_or_state_land"]),
            tenure_years=float(data["tenure_years"]),
            offtaker_entity_verified=bool(data["offtaker_entity_verified"]),
        )


@dataclass(slots=True)
class TechnicalAgroParams:
    """Engineering, agroclimate, biological, and CAPEX benchmark parameters."""

    sector: str
    elevation_mdpl: float
    ambient_temp_c_min: float
    ambient_temp_c_max: float
    claimed_cycles_per_year: float
    claimed_fcr: float
    claimed_harvest_kg_per_cycle: float
    claimed_feed_kg_per_cycle: float
    tank_diameter_m: float
    tank_height_m: float
    tank_count: int
    has_thermal_control: bool
    capex_per_unit_idr: float
    benchmark_capex_per_unit_idr: float

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> TechnicalAgroParams:
        return cls(
            sector=str(data["sector"]),
            elevation_mdpl=float(data["elevation_mdpl"]),
            ambient_temp_c_min=float(data["ambient_temp_c_min"]),
            ambient_temp_c_max=float(data["ambient_temp_c_max"]),
            claimed_cycles_per_year=float(data["claimed_cycles_per_year"]),
            claimed_fcr=float(data["claimed_fcr"]),
            claimed_harvest_kg_per_cycle=float(data["claimed_harvest_kg_per_cycle"]),
            claimed_feed_kg_per_cycle=float(data["claimed_feed_kg_per_cycle"]),
            tank_diameter_m=float(data["tank_diameter_m"]),
            tank_height_m=float(data["tank_height_m"]),
            tank_count=int(data["tank_count"]),
            has_thermal_control=bool(data["has_thermal_control"]),
            capex_per_unit_idr=float(data["capex_per_unit_idr"]),
            benchmark_capex_per_unit_idr=float(data["benchmark_capex_per_unit_idr"]),
        )


@dataclass(slots=True)
class ContractWaterfallParams:
    """Shariah contract structure, PSAK 412 waterfall, and financial risk metrics."""

    akad_type: str
    has_principal_guarantee: bool
    sinking_fund_pct: float
    mauquf_alaih_pct: float
    nazhir_total_pct: float
    external_nazhir_fee_pct: float
    double_nazhir_stacking: bool
    asset_reverts_to_operator_at_end: bool
    upfront_capex_ratio_pct: float
    annual_cash_yield_pct: float
    annual_depreciation_pct: float
    capital_at_risk_pct: float
    expected_net_cash_year1_pct: float
    claimed_gross_revenue_idr: float
    claimed_net_profit_idr: float

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ContractWaterfallParams:
        return cls(
            akad_type=str(data["akad_type"]),
            has_principal_guarantee=bool(data["has_principal_guarantee"]),
            sinking_fund_pct=float(data["sinking_fund_pct"]),
            mauquf_alaih_pct=float(data["mauquf_alaih_pct"]),
            nazhir_total_pct=float(data["nazhir_total_pct"]),
            external_nazhir_fee_pct=float(data["external_nazhir_fee_pct"]),
            double_nazhir_stacking=bool(data["double_nazhir_stacking"]),
            asset_reverts_to_operator_at_end=bool(data["asset_reverts_to_operator_at_end"]),
            upfront_capex_ratio_pct=float(data["upfront_capex_ratio_pct"]),
            annual_cash_yield_pct=float(data["annual_cash_yield_pct"]),
            annual_depreciation_pct=float(data["annual_depreciation_pct"]),
            capital_at_risk_pct=float(data["capital_at_risk_pct"]),
            expected_net_cash_year1_pct=float(data["expected_net_cash_year1_pct"]),
            claimed_gross_revenue_idr=float(data["claimed_gross_revenue_idr"]),
            claimed_net_profit_idr=float(data["claimed_net_profit_idr"]),
        )


@dataclass(slots=True)
class WaqfInvestmentProposal:
    """Complete productive waqf investment proposal submitted for CIO forensic audit."""

    proposal_id: str
    title: str
    proposer: str
    location: str
    capital_requested_idr: float
    land_legal: LandLegalParams
    technical_agro: TechnicalAgroParams
    contract_waterfall: ContractWaterfallParams
    summary: str = ""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> WaqfInvestmentProposal:
        proposer_val = data.get("proposer", data.get("proposer_name", "Unknown Proposer"))
        return cls(
            proposal_id=str(data["proposal_id"]),
            title=str(data["title"]),
            proposer=str(proposer_val),
            location=str(data.get("location", "")),
            capital_requested_idr=float(data["capital_requested_idr"]),
            land_legal=LandLegalParams.from_dict(data["land_legal"]),
            technical_agro=TechnicalAgroParams.from_dict(data["technical_agro"]),
            contract_waterfall=ContractWaterfallParams.from_dict(data["contract_waterfall"]),
            summary=str(data.get("summary", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RedFlag:
    """Individual forensic or Shariah compliance violation detected during screening."""

    code: str
    severity: Severity
    gate: GateName
    title: str
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ForensicVerdict:
    """Combined 9-point CIO forensic due diligence and Shariah screening verdict."""

    proposal_id: str
    verdict: VerdictType
    risk_score_0_to_100: float
    shariah_compliant: bool
    risk_reward_ratio: float
    realistic_net_yield_pct: float
    true_fcr: float
    effective_water_volume_m3: float
    capex_markup_pct: float
    red_flags: list[RedFlag]
    benchmark_comparison: dict[str, Any]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "verdict": self.verdict,
            "risk_score_0_to_100": self.risk_score_0_to_100,
            "shariah_compliant": self.shariah_compliant,
            "risk_reward_ratio": self.risk_reward_ratio,
            "realistic_net_yield_pct": self.realistic_net_yield_pct,
            "true_fcr": self.true_fcr,
            "effective_water_volume_m3": self.effective_water_volume_m3,
            "capex_markup_pct": self.capex_markup_pct,
            "red_flags": [rf.to_dict() for rf in self.red_flags],
            "benchmark_comparison": self.benchmark_comparison,
            "recommendation": self.recommendation,
        }


@dataclass(slots=True)
class TriageResult:
    """Deterministic Laya System-1 compatible waqf pool classification result."""

    pool_code: PoolCode
    confidence: float
    abstain: bool
    needs_treasurer_review: bool
    zero_spill_violation: bool
    spill_reason: str | None = None
    matched_signals: list[str] = field(default_factory=list)
    pool_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
