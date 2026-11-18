"""Gate 1: Shariah, UU 41/2004, and PSAK 412 Constitutional Screening."""

from __future__ import annotations

from .models import RedFlag, WaqfInvestmentProposal

ALLOWED_PROTECTED_AKADS = frozenset(
    {
        "ijarah_qardh_hybrid",
        "cwls_sukuk",
        "back_to_back_po_murabahah",
    }
)

FORBIDDEN_UNPROTECTED_AKADS = frozenset(
    {
        "mudharabah",
        "musyarakah",
        "mudharabah_mutlaqah",
        "mudharabah_muqayyadah",
        "musyarakah_mutanaqisah",
    }
)

MIN_SINKING_FUND_PCT = 10.0
MAX_NAZHIR_TOTAL_PCT = 10.0
MIN_MAUQUF_ALAIH_PCT = 50.0
MIN_COMMERCIAL_LEASE_COLLATERAL_YEARS = 5.0


def evaluate_shariah_gate(proposal: WaqfInvestmentProposal) -> tuple[bool, list[RedFlag]]:
    """Screen a proposal against Hifzh al-Mal, UU 41/2004, and PSAK 412 guardrails.

    Returns:
        Tuple of ``(shariah_compliant, red_flags)``.
    """
    flags: list[RedFlag] = []
    contract = proposal.contract_waterfall
    land = proposal.land_legal

    akad_normalized = contract.akad_type.strip().lower().replace("-", "_").replace(" ", "_")

    # 1. Core waqf principal must not carry pure profit/loss equity impairment risk
    if akad_normalized in FORBIDDEN_UNPROTECTED_AKADS or akad_normalized not in ALLOWED_PROTECTED_AKADS:
        flags.append(
            RedFlag(
                code="SHARIAH_UNPROTECTED_AKAD",
                severity="CRITICAL",
                gate="SHARIAH_GOVERNANCE",
                title="Unprotected Akad on Core Waqf Principal (Hifzh al-Mal Violation)",
                detail=(
                    f"Akad '{contract.akad_type}' exposes core waqf principal to loss. "
                    f"Allowed principal-protected structures: {sorted(ALLOWED_PROTECTED_AKADS)}."
                ),
                evidence={
                    "akad_type": contract.akad_type,
                    "allowed_akads": sorted(ALLOWED_PROTECTED_AKADS),
                },
            )
        )

    if not contract.has_principal_guarantee:
        flags.append(
            RedFlag(
                code="SHARIAH_NO_PRINCIPAL_GUARANTEE",
                severity="CRITICAL",
                gate="SHARIAH_GOVERNANCE",
                title="Missing Principal Guarantee (Zero Principal Impairment Violated)",
                detail=(
                    "Core waqf mawquf bih must be backed by institutional principal guarantee, "
                    "collateralized qardh/ijarah, or sovereign sukuk backing."
                ),
                evidence={"has_principal_guarantee": contract.has_principal_guarantee},
            )
        )

    # 2. Sinking fund reserve floor (>= 10%)
    if contract.sinking_fund_pct < MIN_SINKING_FUND_PCT:
        flags.append(
            RedFlag(
                code="SHARIAH_INSUFFICIENT_SINKING_FUND",
                severity="CRITICAL",
                gate="SHARIAH_GOVERNANCE",
                title="Insufficient Sinking Fund Reserve (< 10.0%)",
                detail=(
                    f"Sinking fund allocation is {contract.sinking_fund_pct:.2f}%, "
                    f"below the mandatory {MIN_SINKING_FUND_PCT:.1f}% PSAK 412 capital preservation floor."
                ),
                evidence={
                    "sinking_fund_pct": contract.sinking_fund_pct,
                    "required_min_pct": MIN_SINKING_FUND_PCT,
                },
            )
        )

    # 3. UU 41/2004 Pasal 12 Nazhir fee ceiling (<= 10%)
    if contract.nazhir_total_pct > MAX_NAZHIR_TOTAL_PCT:
        flags.append(
            RedFlag(
                code="SHARIAH_NAZHIR_CAP_EXCEEDED",
                severity="CRITICAL",
                gate="SHARIAH_GOVERNANCE",
                title="Nazhir Fee Exceeds UU 41/2004 Statutory Ceiling (> 10.0%)",
                detail=(
                    f"Total Nazhir fee is {contract.nazhir_total_pct:.2f}%, violating the "
                    f"{MAX_NAZHIR_TOTAL_PCT:.1f}% cap under UU No. 41/2004 Pasal 12."
                ),
                evidence={
                    "nazhir_total_pct": contract.nazhir_total_pct,
                    "external_nazhir_fee_pct": contract.external_nazhir_fee_pct,
                    "statutory_max_pct": MAX_NAZHIR_TOTAL_PCT,
                },
            )
        )

    # 4. Double Nazhir stacking & Mauquf Alaih minimum share (< 50%)
    if contract.double_nazhir_stacking or (
        contract.external_nazhir_fee_pct > 0 and contract.nazhir_total_pct > MAX_NAZHIR_TOTAL_PCT
    ):
        flags.append(
            RedFlag(
                code="SHARIAH_DOUBLE_NAZHIR_STACKING",
                severity="HIGH",
                gate="SHARIAH_GOVERNANCE",
                title="Double Nazhir Fee Stacking Detected",
                detail=(
                    "Waterfall stacks an external Nazhir/intermediary fee on top of internal "
                    f"Nazhir management fees (external={contract.external_nazhir_fee_pct:.2f}%, "
                    f"total={contract.nazhir_total_pct:.2f}%)."
                ),
                evidence={
                    "double_nazhir_stacking": contract.double_nazhir_stacking,
                    "external_nazhir_fee_pct": contract.external_nazhir_fee_pct,
                    "nazhir_total_pct": contract.nazhir_total_pct,
                },
            )
        )

    if contract.mauquf_alaih_pct < MIN_MAUQUF_ALAIH_PCT:
        flags.append(
            RedFlag(
                code="SHARIAH_MAUQUF_ALAIH_BELOW_MIN",
                severity="HIGH",
                gate="SHARIAH_GOVERNANCE",
                title="Mauquf Alaih Beneficiary Share Below 50% Floor",
                detail=(
                    f"Beneficiary (mauquf alaih) allocation is {contract.mauquf_alaih_pct:.2f}%, "
                    f"below the {MIN_MAUQUF_ALAIH_PCT:.1f}% institutional threshold."
                ),
                evidence={
                    "mauquf_alaih_pct": contract.mauquf_alaih_pct,
                    "required_min_pct": MIN_MAUQUF_ALAIH_PCT,
                },
            )
        )

    # 5. Physical CAPEX construction on land missing AIW / BPN STW title
    has_aiw_and_stw = land.has_aiw_certificate and land.has_bpn_stw
    has_verified_lease_collateral = (
        land.offtaker_entity_verified
        and contract.has_principal_guarantee
        and land.tenure_years >= MIN_COMMERCIAL_LEASE_COLLATERAL_YEARS
    )
    deploys_permanent_capex = contract.upfront_capex_ratio_pct > 0.0

    if deploys_permanent_capex and (not has_aiw_and_stw or land.is_leasehold_or_state_land):
        if not has_verified_lease_collateral:
            flags.append(
                RedFlag(
                    code="SHARIAH_UNCERTIFIED_LAND_CAPEX",
                    severity="CRITICAL",
                    gate="SHARIAH_GOVERNANCE",
                    title="Permanent Physical CAPEX on Uncertified / Unsecured Land",
                    detail=(
                        "Deploying upfront physical CAPEX "
                        f"({contract.upfront_capex_ratio_pct:.1f}%) on land lacking AIW + BPN STW "
                        "title or verified multi-year commercial lease collateral creates "
                        "irreversible waqf principal impairment risk."
                    ),
                    evidence={
                        "has_aiw_certificate": land.has_aiw_certificate,
                        "has_bpn_stw": land.has_bpn_stw,
                        "is_leasehold_or_state_land": land.is_leasehold_or_state_land,
                        "tenure_years": land.tenure_years,
                        "offtaker_entity_verified": land.offtaker_entity_verified,
                        "upfront_capex_ratio_pct": contract.upfront_capex_ratio_pct,
                    },
                )
            )

    if not land.offtaker_entity_verified:
        flags.append(
            RedFlag(
                code="SHARIAH_UNVERIFIED_OFFTAKER",
                severity="HIGH",
                gate="SHARIAH_GOVERNANCE",
                title="Unverified Commercial Offtaker / Counterparty",
                detail=(
                    "Commercial offtaker entity has not passed institutional KYB/legal verification."
                ),
                evidence={"offtaker_entity_verified": land.offtaker_entity_verified},
            )
        )

    # 6. Capital Trap: Asset reverts to operator at end of term
    if contract.asset_reverts_to_operator_at_end:
        flags.append(
            RedFlag(
                code="SHARIAH_CAPITAL_TRAP_ASSET_REVERSION",
                severity="CRITICAL",
                gate="SHARIAH_GOVERNANCE",
                title="Capital Trap: Waqf-Funded Asset Reverts to Operator",
                detail=(
                    "Contract transfers residual asset ownership to the third-party operator at "
                    "term end, permanently extinguishing the waqf principal."
                ),
                evidence={"asset_reverts_to_operator_at_end": True},
            )
        )

    shariah_compliant = len(flags) == 0
    return shariah_compliant, flags
