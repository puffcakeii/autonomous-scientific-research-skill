#!/usr/bin/env python3
from __future__ import annotations

import re

import build_cvpr2025_fulltext_audit_v2 as audit


def safe_extract_datasets(text: str) -> list[str]:
    found: list[str] = []
    for name in audit.base.DATASET_PATTERNS:
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])", text, flags=re.I):
            found.append(name)
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9+\-]{2,20})\s+(?:dataset|benchmark)\b", text):
        token = m.group(1)
        if token.lower() not in audit.GENERIC_DATASET_TOKENS:
            found.append(token)
    return sorted(set(found), key=str.lower)[:30]


audit.base.extract_datasets = safe_extract_datasets

if __name__ == "__main__":
    raise SystemExit(audit.main())
