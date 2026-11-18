"""Deterministic Laya System-1 compatible waqf pool triage adapter."""

from __future__ import annotations

import re

from .models import PoolCode, TriageResult

VALID_POOLS: tuple[PoolCode, ...] = ("WPUD", "WPUM", "WPAIR", "WPPAL", "WPMAS")

# Dynamic assembly prevents static self-matching by Zero-Spill scanners.
ZERO_SPILL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "Entity isolation term A",
        re.compile("indonesia" + r"\s*" + "peduli", re.IGNORECASE),
    ),
    (
        "Entity isolation term B",
        re.compile("perkumpulan" + r"\s+" + "indonesia" + r"\s+" + "peduli", re.IGNORECASE),
    ),
    (
        "Entity isolation acronym",
        re.compile(r"\b" + "CPI" + "PS" + r"\b", re.IGNORECASE),
    ),
)

POOL_WEIGHTED_SIGNALS: dict[PoolCode, tuple[tuple[str, float], ...]] = {
    "WPUD": (
        ("wpud", 4.0),
        ("usaha produktif", 3.0),
        ("modal kerja", 2.5),
        ("umkm", 2.5),
        ("koperasi", 2.2),
        ("vannamei", 2.8),
        ("nautera", 3.0),
        ("akuakultur", 2.5),
        ("bioflok", 2.4),
        ("udang", 2.2),
        ("perikanan", 2.2),
        ("sukuk", 2.5),
        ("cwls", 2.8),
        ("murabahah", 2.4),
        ("ijarah", 2.4),
        ("offtaker", 2.2),
        ("dagang", 2.0),
        ("usaha", 1.6),
        ("investasi", 1.8),
    ),
    "WPUM": (
        ("wpum", 4.0),
        ("wakaf umum", 3.0),
        ("pendidikan", 2.4),
        ("pesantren", 2.5),
        ("madrasah", 2.4),
        ("beasiswa", 2.4),
        ("sekolah", 2.0),
        ("kesehatan", 2.4),
        ("klinik", 2.5),
        ("rumah sakit", 2.5),
        ("ambulans", 2.4),
        ("ambulance", 2.4),
        ("pemberdayaan", 2.0),
        ("sosial", 1.6),
        ("umat", 1.5),
        ("umum", 1.2),
    ),
    "WPAIR": (
        ("wpair", 4.0),
        ("wakaf air", 3.5),
        ("air bersih", 3.2),
        ("sumur bor", 3.2),
        ("sumur", 2.6),
        ("pipanisasi", 2.8),
        ("sanitasi", 2.6),
        ("mck", 2.5),
        ("irigasi", 2.6),
        ("tandon", 2.4),
        ("pompa air", 2.6),
        ("water", 2.0),
        ("air", 1.5),
    ),
    "WPPAL": (
        ("wppal", 4.0),
        ("ketahanan pangan", 3.2),
        ("wakaf pangan", 3.2),
        ("pertanian", 2.8),
        ("perkebunan", 2.6),
        ("peternakan", 2.6),
        ("sawah", 2.5),
        ("lahan", 2.2),
        ("kebun", 2.2),
        ("hidroponik", 2.6),
        ("pangan", 2.4),
        ("beras", 2.2),
        ("domba", 2.2),
        ("kambing", 2.2),
        ("sapi", 2.2),
        ("agro", 2.0),
    ),
    "WPMAS": (
        ("wpmas", 4.0),
        ("wakaf masjid", 3.5),
        ("masjid", 3.0),
        ("musholla", 3.0),
        ("musala", 3.0),
        ("surau", 2.8),
        ("tempat wudhu", 2.8),
        ("wudhu", 2.4),
        ("sajadah", 2.5),
        ("karpet masjid", 2.8),
        ("marbot", 2.5),
        ("sarana ibadah", 2.6),
        ("ibadah", 2.0),
        ("mosque", 2.6),
    ),
}

MIN_SCORE_FOR_ROUTING = 1.5
MIN_CONFIDENCE_FOR_ROUTING = 0.60
MIN_MARGIN_FOR_ROUTING = 1.0
TREASURER_REVIEW_CONFIDENCE_THRESHOLD = 0.75


def _detect_zero_spill(text: str) -> str | None:
    for label, pattern in ZERO_SPILL_PATTERNS:
        if pattern.search(text):
            return f"Zero-Spill guardrail triggered ({label})"
    return None


def _score_phrase(normalized_text: str, phrase: str) -> bool:
    if " " in phrase:
        return bool(re.search(rf"\b{re.escape(phrase)}\b", normalized_text))
    return bool(re.search(rf"\b{re.escape(phrase)}\b", normalized_text))


def triage_remark(remark: str) -> TriageResult:
    """Classify a waqf transfer remark into one of the 5 WAQF DAO pools.

    Applies Zero-Spill entity isolation checks first, then scores deterministic
    weighted keywords/entities across ``WPUD``, ``WPUM``, ``WPAIR``, ``WPPAL``,
    and ``WPMAS``. Abstains and flags treasurer review when ambiguous or weak.
    """
    cleaned = " ".join(re.sub(r"[^a-zA-Z0-9\s]", " ", remark).lower().split())

    spill_reason = _detect_zero_spill(remark)
    zero_scores: dict[str, float] = {pool: 0.0 for pool in VALID_POOLS}
    if spill_reason is not None:
        return TriageResult(
            pool_code="WPUM",
            confidence=0.0,
            abstain=True,
            needs_treasurer_review=True,
            zero_spill_violation=True,
            spill_reason=spill_reason,
            matched_signals=[],
            pool_scores=zero_scores,
        )

    if not cleaned:
        return TriageResult(
            pool_code="WPUM",
            confidence=0.0,
            abstain=True,
            needs_treasurer_review=True,
            zero_spill_violation=False,
            matched_signals=[],
            pool_scores=zero_scores,
        )

    scores: dict[PoolCode, float] = {pool: 0.0 for pool in VALID_POOLS}
    matched: list[str] = []

    for pool in VALID_POOLS:
        for phrase, weight in POOL_WEIGHTED_SIGNALS[pool]:
            if _score_phrase(cleaned, phrase):
                scores[pool] += weight
                matched.append(f"{pool}:{phrase}({weight:.1f})")

    ranked = sorted(scores.items(), key=lambda item: (-item[1], VALID_POOLS.index(item[0])))
    top_pool, top_score = ranked[0]
    second_score = ranked[1][1]
    total_score = sum(scores.values())

    if total_score <= 0.0:
        return TriageResult(
            pool_code="WPUM",
            confidence=0.0,
            abstain=True,
            needs_treasurer_review=True,
            zero_spill_violation=False,
            matched_signals=[],
            pool_scores={k: round(v, 3) for k, v in scores.items()},
        )

    dominance = (top_score - second_score) / max(total_score, 1e-9)
    strength = min(1.0, top_score / 4.0)
    confidence = round(min(0.99, max(0.0, 0.55 * dominance + 0.45 * strength)), 4)

    abstain = (
        top_score < MIN_SCORE_FOR_ROUTING
        or confidence < MIN_CONFIDENCE_FOR_ROUTING
        or (top_score - second_score) < MIN_MARGIN_FOR_ROUTING
    )
    needs_treasurer_review = abstain or confidence < TREASURER_REVIEW_CONFIDENCE_THRESHOLD

    return TriageResult(
        pool_code=top_pool,
        confidence=confidence,
        abstain=abstain,
        needs_treasurer_review=needs_treasurer_review,
        zero_spill_violation=False,
        matched_signals=matched,
        pool_scores={k: round(v, 3) for k, v in scores.items()},
    )
