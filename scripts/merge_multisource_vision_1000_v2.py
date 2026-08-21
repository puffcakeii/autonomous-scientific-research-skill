#!/usr/bin/env python3
"""Merge previously parsed full-text shards with deterministic JSON handling."""
from __future__ import annotations

import json as stdjson
import pathlib
import sys

import build_multisource_vision_1000 as base

_original_dumps = base.json.dumps


def _default(obj):
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _dumps(obj, *args, **kwargs):
    kwargs.setdefault("default", _default)
    return _original_dumps(obj, *args, **kwargs)


base.json.dumps = _dumps

if __name__ == "__main__":
    try:
        raise SystemExit(base.main())
    except BaseException:
        out = pathlib.Path("artifacts/multisource_vision_1000")
        summary = out / "audit_summary.json"
        if summary.exists():
            print("\n--- audit_summary_before_failure ---", file=sys.stderr)
            print(summary.read_text(encoding="utf-8"), file=sys.stderr)
        venue = out / "venue_distribution.csv"
        if venue.exists():
            print("\n--- venue_distribution_before_failure ---", file=sys.stderr)
            print(venue.read_text(encoding="utf-8"), file=sys.stderr)
        raise
