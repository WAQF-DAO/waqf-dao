"""UU PDP (Law No. 27/2022) Privacy Shield & Zero-Spill sanitization engine.

Provides:
- Salted SHA-256 commitments for wakif (donor) identities without storing raw PII.
- Redaction of Indonesian 16-digit NIKs, phone numbers, and email addresses.
- Zero-Spill enforcement using dynamically assembled patterns to guarantee
  zero cross-entity leakage and zero secret token exposure.
"""

from __future__ import annotations

import hashlib
import os
import re
from typing import Any

DEFAULT_SALT_ENV = "WAQF_ORACLE_PDP_SALT"
PUBLIC_FALLBACK_SALT = "waqf-dao-uupdp-public-domain-v1"

NIK_PATTERN = re.compile(
    r"(?<![0-9a-fA-FxX])\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}(?![0-9a-fA-F])"
)
PHONE_PATTERN = re.compile(
    r"(?<![0-9a-fA-FxX])"
    r"(?:"
    r"(?:\+?62|0)[\s.-]?8[1-9][0-9][\s.-]?\d{3,4}[\s.-]?\d{3,5}"
    r"|"
    r"(?:\+?62[\s.-]?|\(?0)(?:2[1-9]|[3-9]\d)\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
    r")"
    r"(?!\d)"
)
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Dynamically assembled patterns prevent self-matching by scripts/audit_hygiene.py.
FORBIDDEN_SPILL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
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

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("GitHub OAuth token", re.compile(r"gho_" + r"[A-Za-z0-9]{20,}")),
    ("GitHub PAT", re.compile(r"ghp_" + r"[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained token", re.compile(r"github_pat_" + r"[A-Za-z0-9_]{20,}")),
    ("PEM Private Key", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?" + r"PRIVATE KEY")),
    ("OpenAI Key", re.compile(r"sk-proj-" + r"[A-Za-z0-9_-]{20,}")),
)

RAW_PII_KEYS: frozenset[str] = frozenset(
    {
        "wakif_name",
        "wakif_nik",
        "wakif_phone",
        "wakif_email",
        "wakif_address",
        "nik",
        "phone",
        "mobile",
        "email",
        "address",
        "donor_name",
        "donor_nik",
        "donor_phone",
        "donor_email",
    }
)


class ZeroSpillViolationError(ValueError):
    """Raised when restricted entity identifiers or secret tokens are detected."""


def resolve_pdp_salt(salt: str | None = None) -> str:
    """Resolve the UU PDP commitment salt from argument, environment, or public domain tag."""
    if salt is not None:
        cleaned = salt.strip()
        if not cleaned:
            raise ValueError("PDP commitment salt must not be empty")
        return cleaned
    env_salt = os.environ.get(DEFAULT_SALT_ENV, "").strip()
    return env_salt if env_salt else PUBLIC_FALLBACK_SALT


def commit_wakif_identity(identifier: str, salt: str | None = None) -> str:
    """Compute a salted SHA-256 commitment (0x-prefixed 64-char hex) for wakif identity."""
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("Wakif identifier must be a non-empty string")
    assert_zero_spill(identifier)
    resolved_salt = resolve_pdp_salt(salt)
    normalized = " ".join(identifier.strip().lower().split())
    payload = f"waqf:uupdp:v1:{resolved_salt}:{normalized}".encode("utf-8")
    return "0x" + hashlib.sha256(payload).hexdigest()


def redact_nik(text: str) -> str:
    """Replace 16-digit Indonesian NIK sequences with [REDACTED_NIK]."""
    return NIK_PATTERN.sub("[REDACTED_NIK]", text)


def redact_phone(text: str) -> str:
    """Replace Indonesian mobile/landline phone numbers with [REDACTED_PHONE]."""
    return PHONE_PATTERN.sub("[REDACTED_PHONE]", text)


def redact_email(text: str) -> str:
    """Replace email addresses with [REDACTED_EMAIL]."""
    return EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)


def assert_zero_spill(text: str) -> None:
    """Raise ZeroSpillViolationError if text contains restricted entity terms or secret tokens."""
    for label, pattern in FORBIDDEN_SPILL_PATTERNS:
        if pattern.search(text):
            raise ZeroSpillViolationError(f"Zero-Spill violation detected: {label}")
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise ZeroSpillViolationError(f"Secret pattern detected: {label}")


def sanitize_zero_spill(text: str) -> str:
    """Replace restricted entity terms and secret patterns with redaction placeholders."""
    cleaned = text
    for _, pattern in FORBIDDEN_SPILL_PATTERNS:
        cleaned = pattern.sub("[REDACTED_RESTRICTED_ENTITY]", cleaned)
    for _, pattern in SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED_SECRET]", cleaned)
    return cleaned


def scrub_text(text: str, *, raise_on_spill: bool = True) -> str:
    """Scrub PII (NIK, phone, email) and enforce or sanitize Zero-Spill rules."""
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    if raise_on_spill:
        assert_zero_spill(text)
    else:
        text = sanitize_zero_spill(text)
    cleaned = redact_nik(text)
    cleaned = redact_phone(cleaned)
    cleaned = redact_email(cleaned)
    return cleaned


def scrub_payload(data: Any, *, raise_on_spill: bool = True) -> Any:
    """Recursively scrub strings and strip raw PII keys from nested JSON-like data."""
    if isinstance(data, str):
        return scrub_text(data, raise_on_spill=raise_on_spill)
    if isinstance(data, dict):
        sanitized: dict[str, Any] = {}
        for key, value in data.items():
            key_str = str(key)
            if raise_on_spill:
                assert_zero_spill(key_str)
            if key_str.lower() in RAW_PII_KEYS:
                continue
            sanitized[key_str] = scrub_payload(value, raise_on_spill=raise_on_spill)
        return sanitized
    if isinstance(data, list):
        return [scrub_payload(item, raise_on_spill=raise_on_spill) for item in data]
    if isinstance(data, tuple):
        return [scrub_payload(item, raise_on_spill=raise_on_spill) for item in data]
    return data


def shield_wakif_record(
    record: dict[str, Any],
    *,
    salt: str | None = None,
    raise_on_spill: bool = True,
) -> dict[str, Any]:
    """Convert raw wakif record into a UU PDP privacy-shielded record with salted commitment."""
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    existing_commitment = record.get("wakif_commitment")
    if isinstance(existing_commitment, str) and existing_commitment.startswith("0x") and len(existing_commitment) == 66:
        commitment = existing_commitment.lower()
    else:
        raw_id = (
            record.get("wakif_nik")
            or record.get("nik")
            or record.get("wakif_email")
            or record.get("email")
            or record.get("wakif_id")
            or record.get("wakif_name")
            or record.get("donor_name")
        )
        if not raw_id:
            raise ValueError("Cannot derive wakif_commitment without identifier or existing commitment")
        commitment = commit_wakif_identity(str(raw_id), salt=salt)

    shielded = scrub_payload(record, raise_on_spill=raise_on_spill)
    shielded["wakif_commitment"] = commitment
    return shielded
