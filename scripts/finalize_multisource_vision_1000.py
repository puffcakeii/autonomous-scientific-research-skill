#!/usr/bin/env python3
"""Finalize a diversified 1,000-paper full-text vision audit.

The final set is selected from immutable parsed full-text records by a binary
optimization problem. It enforces an exact 500/500 conference-journal split,
venue and year caps, recent-paper and topic floors, then enriches missing author
metadata from official proceedings pages without changing any PDF evidence.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import gzip
import json as stdjson
import math
import pickle
from collections import Counter
from pathlib import Path

import numpy as np
import requests
from bs4 import BeautifulSoup
from scipy.optimize import Bounds, LinearConstraint, milp

import build_multisource_vision_1000 as base

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

THEME_FLOORS = {
    "aerial_oriented_small": 140,
    "domain_tta_sourcefree": 150,
    "multimodal_spectral": 110,
    "robust_uncertainty": 100,
    "open_vocab_foundation": 90,
    "label_efficient": 90,
    "efficient_deployment": 90,
}


def stronger_dedup(records):
    """Keep one record per normalized title, DOI or exact PDF bytes."""
    ordered = sorted(
        records,
        key=lambda r: (
            r["fulltext_score"], r["word_count"],
            r["work"].get("cited_by_count", 0),
            bool(r["work"].get("doi")), bool(r["work"].get("authors")),
        ),
        reverse=True,
    )
    seen_title, seen_doi, seen_sha, unique = set(), set(), set(), []
    for r in ordered:
        title_key = base.norm_title(r["work"]["title"])
        doi_key = (r["work"].get("doi") or "").strip().lower()
        sha = r["pdf_sha256"]
        if title_key in seen_title or sha in seen_sha or (doi_key and doi_key in seen_doi):
            continue
        seen_title.add(title_key); seen_sha.add(sha)
        if doi_key:
            seen_doi.add(doi_key)
        r["dedup_key"] = "title:" + title_key
        unique.append(r)
    return unique


def optimized_select(records):
    """Maximize evidence quality subject to frozen diversity constraints."""
    n = len(records)
    quality = np.array([
        float(r["fulltext_score"])
        + 0.30 * math.log1p(int(r["work"].get("cited_by_count", 0)))
        + 0.02 * min(float(r["word_count"]) / 1000.0, 20.0)
        for r in records
    ])
    rows, lower, upper = [], [], []

    def add(mask, lo, hi):
        rows.append(np.asarray(mask, dtype=float)); lower.append(lo); upper.append(hi)

    add(np.ones(n), 1000, 1000)
    add([r["work"]["kind"] == "conference" for r in records], 500, 500)
    add([r["work"]["kind"] == "journal" for r in records], 500, 500)

    venue_available = Counter(r["work"]["venue"] for r in records)
    for venue, available in sorted(venue_available.items()):
        # Every substantial venue contributes at least 20 papers; tiny venues
        # remain optional and cannot distort the evidence base.
        lo = 20 if available >= 30 else 0
        add([r["work"]["venue"] == venue for r in records], lo, min(110, available))

    for year in range(2021, 2027):
        add([int(r["work"]["year"]) == year for r in records], 80, 300)
    add([int(r["work"]["year"]) >= 2022 for r in records], 700, np.inf)

    for theme, floor in THEME_FLOORS.items():
        add([r["theme_scores"].get(theme, 0) > 0 for r in records], floor, np.inf)

    constraints = LinearConstraint(np.vstack(rows), np.asarray(lower), np.asarray(upper))
    result = milp(
        -quality,
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=constraints,
        options={"time_limit": 180, "mip_rel_gap": 1e-7},
    )
    if not result.success:
        raise RuntimeError(f"Diversified selection failed: {result.message}")
    selected = [records[i] for i in np.flatnonzero(result.x > 0.5)]
    if len(selected) != 1000:
        raise RuntimeError(f"Optimizer returned {len(selected)} papers")
    selected.sort(key=lambda r: (-r["fulltext_score"], -r["work"].get("cited_by_count", 0), r["work"]["title"].lower()))
    for rank, r in enumerate(selected, 1):
        r["selected_rank"] = rank
    return selected


def _citation_authors(url: str) -> str:
    if not url or url.endswith("papers.php"):
        return ""
    try:
        s = requests.Session(); s.headers.update({"User-Agent": base.USER_AGENT})
        html = s.get(url, timeout=30).text
        soup = BeautifulSoup(html, "html.parser")
        values = [m.get("content", "").strip() for m in soup.select('meta[name="citation_author"]')]
        values = [v for v in values if v]
        return "; ".join(values)
    except Exception:
        return ""


def _ecva_author_map() -> dict[str, str]:
    mapping = {}
    try:
        s = requests.Session(); s.headers.update({"User-Agent": base.USER_AGENT})
        root = "https://www.ecva.net/papers.php"
        soup = BeautifulSoup(s.get(root, timeout=40).text, "html.parser")
        for a in soup.find_all("a", href=True):
            if a.get_text(" ", strip=True).lower() != "pdf":
                continue
            href = requests.compat.urljoin(root, a["href"])
            if "eccv_2024" not in href.lower():
                continue
            dd = a.find_parent("dd")
            authors = ""
            if dd:
                parts = []
                for child in dd.contents:
                    name = getattr(child, "name", None)
                    if name == "a":
                        break
                    if name == "br" and parts:
                        break
                    text = child.get_text(" ", strip=True) if hasattr(child, "get_text") else str(child).strip()
                    if text:
                        parts.append(text)
                authors = base.norm_space(" ".join(parts))
            if authors:
                mapping[href] = authors
    except Exception:
        pass
    return mapping


def enrich_authors(selected):
    ecva = _ecva_author_map()
    pending = []
    for r in selected:
        if r["work"].get("authors"):
            continue
        if r["work"]["venue"] == "ECCV":
            r["work"]["authors"] = ecva.get(r["fulltext_url"], "")
        if not r["work"].get("authors"):
            pending.append(r)
    with cf.ThreadPoolExecutor(max_workers=20) as ex:
        futures = {ex.submit(_citation_authors, r["work"].get("landing_url", "")): r for r in pending}
        for fut in cf.as_completed(futures):
            authors = fut.result()
            if authors:
                futures[fut]["work"]["authors"] = authors
    return {
        "selected_with_authors": sum(bool(r["work"].get("authors")) for r in selected),
        "selected_missing_authors": sum(not r["work"].get("authors") for r in selected),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    records, paths = [], sorted(Path(args.input_dir).rglob("*.pkl.gz"))
    if len(paths) < 15:
        raise SystemExit(f"Expected 15 parsed shards, found {len(paths)}")
    for p in paths:
        with gzip.open(p, "rb") as f:
            batch = pickle.load(f)
        records.extend(batch)
        print(p.name, len(batch), flush=True)

    unique = stronger_dedup(records)
    print("parsed records", len(records), "unique title/doi/sha", len(unique), flush=True)
    selected = optimized_select(unique)
    author_summary = enrich_authors(selected)
    out = Path(args.output)
    base.write_outputs(selected, unique, out)

    summary = stdjson.loads((out / "audit_summary.json").read_text(encoding="utf-8"))
    summary.update({
        "input_parsed_shards": len(paths),
        "input_parsed_records": len(records),
        "eligible_unique_after_title_doi_sha_dedup": len(unique),
        "deduplication": "normalized title OR DOI OR exact PDF SHA-256",
        "selection_method": "binary optimization with exact 500 conference / 500 journal split",
        "venue_minimum_for_substantial_sources": 20,
        "venue_maximum": 110,
        "year_minimum": 80,
        "year_maximum": 300,
        "theme_floor_constraints": THEME_FLOORS,
        **author_summary,
    })
    (out / "audit_summary.json").write_text(stdjson.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "AUTHOR_METADATA_NOTE.md").write_text(
        "# 作者元数据说明\n\n作者优先取自OpenAlex正式元数据；官方会议补充记录从PMLR、NeurIPS和ECVA页面的citation/作者字段补充。缺失作者不会影响PDF全文、哈希、方法、实验或结果证据，但在注册表中保持空值，不做猜测。\n",
        encoding="utf-8",
    )

    manifest = []
    for p in sorted(x for x in out.rglob("*") if x.is_file() and x.name != "SHA256SUMS.txt"):
        manifest.append(f"{base.sha256_bytes(p.read_bytes())}  {p.relative_to(out).as_posix()}")
    (out / "SHA256SUMS.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(stdjson.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
