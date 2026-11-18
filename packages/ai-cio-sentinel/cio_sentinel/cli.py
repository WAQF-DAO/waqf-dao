"""CLI entrypoint for AI CIO Forensic & Compliance Sentinel."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .forensic_auditor import audit_proposal
from .laya_triage_adapter import triage_remark
from .models import ForensicVerdict, TriageResult, WaqfInvestmentProposal


def format_verdict_markdown(proposal: WaqfInvestmentProposal, verdict: ForensicVerdict) -> str:
    """Render a ForensicVerdict into an institutional IC Markdown audit report."""
    lines = [
        f"# CIO Forensic & Shariah Audit Report: {proposal.title}",
        "",
        f"- **Proposal ID**: `{verdict.proposal_id}`",
        f"- **Proposer**: {proposal.proposer}",
        f"- **Location**: {proposal.location or 'N/A'}",
        f"- **Capital Requested**: IDR {proposal.capital_requested_idr:,.0f}",
        f"- **Verdict**: **{verdict.verdict}**",
        f"- **Risk Score (0-100)**: {verdict.risk_score_0_to_100:.2f}",
        f"- **Shariah & PSAK 412 Compliant**: `{verdict.shariah_compliant}`",
        "",
        "## Core Forensic Metrics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Risk-Reward Ratio (RRR) | {verdict.risk_reward_ratio:.2f} : 1 (max 0.50 : 1) |",
        f"| Realistic Net Yield | {verdict.realistic_net_yield_pct:.2f}% p.a. |",
        f"| True Implied FCR | {verdict.true_fcr:.4f} |",
        f"| Effective Water Volume (0.2m freeboard) | {verdict.effective_water_volume_m3:.2f} m³ |",
        f"| CAPEX Mark-Up vs Benchmark | {verdict.capex_markup_pct:+.2f}% |",
        "",
        "## Opportunity Cost Benchmark Comparison",
        "",
        "| Benchmark | Yield (% p.a.) | Spread |",
        "| --- | --- | --- |",
        (
            f"| Sovereign CWLS / Sukuk (Risk-Free) | "
            f"{verdict.benchmark_comparison['cwls_risk_free_yield_pct']:.2f}% | "
            f"{verdict.benchmark_comparison['spread_vs_cwls_pct']:+.2f}% |"
        ),
        (
            f"| Internal Aquaculture Benchmark (Nautera) | "
            f"{verdict.benchmark_comparison['internal_nautera_yield_pct']:.2f}% | "
            f"{verdict.benchmark_comparison['spread_vs_nautera_pct']:+.2f}% |"
        ),
        "",
        f"## Red Flags ({len(verdict.red_flags)})",
        "",
    ]

    if not verdict.red_flags:
        lines.append("- None detected.")
    else:
        for idx, rf in enumerate(verdict.red_flags, start=1):
            lines.append(
                f"{idx}. **[{rf.severity}] [{rf.gate}] `{rf.code}` — {rf.title}**\n"
                f"   {rf.detail}"
            )

    lines.extend(["", "## Recommendation", "", verdict.recommendation, ""])
    return "\n".join(lines)


def format_triage_markdown(remark: str, result: TriageResult) -> str:
    """Render a TriageResult into Markdown."""
    lines = [
        "# Laya Pool Triage Result",
        "",
        f"- **Remark**: `{remark}`",
        f"- **Pool Code**: `{result.pool_code}`",
        f"- **Confidence**: {result.confidence:.4f}",
        f"- **Abstain**: `{result.abstain}`",
        f"- **Needs Treasurer Review**: `{result.needs_treasurer_review}`",
        f"- **Zero-Spill Violation**: `{result.zero_spill_violation}`",
    ]
    if result.spill_reason:
        lines.append(f"- **Spill Reason**: {result.spill_reason}")
    if result.matched_signals:
        lines.append(f"- **Matched Signals**: {', '.join(result.matched_signals)}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cio-sentinel",
        description="WAQF DAO AI CIO Forensic Due Diligence, Shariah Gate & Laya Triage CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_cmd = subparsers.add_parser("audit", help="Run 9-point forensic & Shariah audit on JSON proposal")
    audit_cmd.add_argument("proposal_path", type=Path, help="Path to proposal JSON file")
    audit_cmd.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format (default: markdown)",
    )

    triage_cmd = subparsers.add_parser("triage", help="Classify transfer remark into WAQF DAO pool")
    triage_cmd.add_argument("remark", type=str, help="Transfer remark string to classify")
    triage_cmd.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit":
        payload = json.loads(args.proposal_path.read_text(encoding="utf-8"))
        proposal = WaqfInvestmentProposal.from_dict(payload)
        verdict = audit_proposal(proposal)
        if args.format == "json":
            print(json.dumps(verdict.to_dict(), indent=2))
        else:
            print(format_verdict_markdown(proposal, verdict))
        return 0

    if args.command == "triage":
        result = triage_remark(args.remark)
        if args.format == "markdown":
            print(format_triage_markdown(args.remark, result))
        else:
            print(json.dumps(result.to_dict(), indent=2))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
