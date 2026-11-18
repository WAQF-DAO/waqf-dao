#!/usr/bin/env python3
"""Hygiene, secret-leak, and Zero-Spill guardrail scanner for WAQF DAO."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "out",
    "cache",
    "broadcast",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
}

TEXT_EXTENSIONS = {
    ".py",
    ".sol",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".json",
    ".md",
    ".rst",
    ".toml",
    ".yml",
    ".yaml",
    ".xml",
    ".csv",
    ".css",
    ".html",
    ".cff",
    ".sh",
    ".txt",
}

SECRET_PATTERNS = [
    ("GitHub OAuth token", re.compile(r"gho_" + r"[A-Za-z0-9]{20,}")),
    ("GitHub PAT", re.compile(r"ghp_" + r"[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained token", re.compile(r"github_pat_" + r"[A-Za-z0-9_]{20,}")),
    ("PEM Private Key", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?" + r"PRIVATE KEY")),
    ("OpenAI Key", re.compile(r"sk-proj-" + r"[A-Za-z0-9_-]{20,}")),
]

# Dynamic assembly prevents self-matching on this guardrail script itself.
FORBIDDEN_SPILL_PATTERNS = [
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
]


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname in {"Makefile", "LICENSE", ".env.example", ".gitignore"} or fpath.suffix.lower() in TEXT_EXTENSIONS:
                yield fpath


def main() -> int:
    violations: list[str] = []
    scanned = 0
    for fpath in iter_files(ROOT):
        rel = fpath.relative_to(ROOT)
        scanned += 1
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            violations.append(f"{rel}: failed to read ({exc})")
            continue

        for label, pattern in SECRET_PATTERNS:
            if pattern.search(content):
                violations.append(f"{rel}: detected {label}")

        for label, pattern in FORBIDDEN_SPILL_PATTERNS:
            if pattern.search(content):
                violations.append(f"{rel}: Zero-Spill violation ({label})")

    if violations:
        print(f"HYGIENE & ZERO-SPILL AUDIT: FAIL ({len(violations)} issues across {scanned} files)")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(f"HYGIENE & ZERO-SPILL AUDIT: PASS ({scanned} files scanned, 0 leaks, 0 spill violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
