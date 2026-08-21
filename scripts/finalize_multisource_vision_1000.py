#!/usr/bin/env python3
"""Finalize the diversified 1,000-paper full-text audit.

This stage reuses immutable parsed full-text records, deduplicates formal and
preprint versions by normalized title, DOI and PDF SHA-256, enforces the frozen
venue/year/source-type quotas, and writes the final traceable package.
"""
from __future__ import annotations

import argparse
import gzip
import json as stdjson
import pickle
from pathlib import Path

import build_multisource_vision_1000 as base

# ICML was added through the official PMLR supplement after the original
# metadata pass. It participates in exactly the same venue cap and quality gate.
base.VENUES["ICML"] = {
    "kind": "conference",
    "tier": "A",
    "search": "International Conference on Machine Learning",
    "patterns": ["international conference on machine learning", "icml"],
}

_original_dumps = base.json.dumps


def _json_default(obj):
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def _dumps(obj, *args, **kwargs):
    kwargs.setdefault("default", _json_default)
    return _original_dumps(obj, *args, **kwargs)


base.json.dumps = _dumps


def stronger_dedup(records):
    """Keep one record per normalized title, DOI and exact PDF bytes."""
    ordered = sorted(
        records,
        key=lambda r: (
            r["fulltext_score"],
            r["word_count"],
            r["work"].get("cited_by_count", 0),
            1 if r["work"].get("doi") else 0,
            1 if r["work"].get("authors") else 0,
        ),
        reverse=True,
    )
    seen_title, seen_doi, seen_sha = set(), set(), set()
    unique = []
    for r in ordered:
        title_key = base.norm_title(r["work"]["title"])
        doi_key = (r["work"].get("doi") or "").strip().lower()
        sha = r["pdf_sha256"]
        if title_key in seen_title or sha in seen_sha or (doi_key and doi_key in seen_doi):
            continue
        seen_title.add(title_key)
        seen_sha.add(sha)
        if doi_key:
            seen_doi.add(doi_key)
        # Make the dedup key independent of whether this copy arrived as a DOI
        # record or an official proceedings-page record.
        r["dedup_key"] = "title:" + title_key
        unique.append(r)
    return unique


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    records = []
    paths = sorted(Path(args.input_dir).rglob("*.pkl.gz"))
    if len(paths) < 15:
        raise SystemExit(f"Expected 15 parsed shards, found {len(paths)}")
    for p in paths:
        with gzip.open(p, "rb") as f:
            batch = pickle.load(f)
        records.extend(batch)
        print(p.name, len(batch), flush=True)

    unique = stronger_dedup(records)
    print("parsed records", len(records), "unique title/doi/sha", len(unique), flush=True)
    selected = base.balanced_select(unique, base.TARGET_N)
    base.write_outputs(selected, unique, Path(args.output))

    summary = stdjson.loads((Path(args.output) / "audit_summary.json").read_text(encoding="utf-8"))
    summary["input_parsed_shards"] = len(paths)
    summary["input_parsed_records"] = len(records)
    summary["eligible_unique_after_title_doi_sha_dedup"] = len(unique)
    summary["deduplication"] = "normalized title OR DOI OR exact PDF SHA-256"
    (Path(args.output) / "audit_summary.json").write_text(
        stdjson.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Rebuild integrity manifest because audit_summary was extended above.
    manifest = []
    for p in sorted(x for x in Path(args.output).rglob("*") if x.is_file() and x.name != "SHA256SUMS.txt"):
        manifest.append(f"{base.sha256_bytes(p.read_bytes())}  {p.relative_to(Path(args.output)).as_posix()}")
    (Path(args.output) / "SHA256SUMS.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(stdjson.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
