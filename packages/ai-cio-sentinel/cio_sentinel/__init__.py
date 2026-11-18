"""AI CIO Forensic & Compliance Sentinel for WAQF DAO."""

from .forensic_auditor import (
    CWLS_RISK_FREE_YIELD_PCT,
    NAUTERA_BENCHMARK_YIELD_PCT,
    audit_proposal,
    compute_circular_tank_volumes,
    compute_risk_reward_ratio,
    compute_true_fcr,
)
from .laya_triage_adapter import VALID_POOLS, triage_remark
from .models import (
    ContractWaterfallParams,
    ForensicVerdict,
    LandLegalParams,
    RedFlag,
    TechnicalAgroParams,
    TriageResult,
    WaqfInvestmentProposal,
)
from .shariah_gate import evaluate_shariah_gate

__all__ = [
    "CWLS_RISK_FREE_YIELD_PCT",
    "NAUTERA_BENCHMARK_YIELD_PCT",
    "VALID_POOLS",
    "ContractWaterfallParams",
    "ForensicVerdict",
    "LandLegalParams",
    "RedFlag",
    "TechnicalAgroParams",
    "TriageResult",
    "WaqfInvestmentProposal",
    "audit_proposal",
    "compute_circular_tank_volumes",
    "compute_risk_reward_ratio",
    "compute_true_fcr",
    "evaluate_shariah_gate",
    "triage_remark",
]
