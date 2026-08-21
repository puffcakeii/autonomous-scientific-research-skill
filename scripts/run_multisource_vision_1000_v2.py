#!/usr/bin/env python3
"""Rate-limited multi-source metadata runner for the 1,000-paper audit."""
from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
from typing import Any

import requests

import build_multisource_vision_1000 as base

# Stable source IDs observed from OpenAlex plus search-based expansion for
# year-specific proceedings. These do not replace venue verification; every
# returned work is still classified and deduplicated from its metadata.
SEED_SOURCE_IDS = {
    "CVPR": ["S4363607701"],
    "ICCV": ["S4363607764"],
    "ECCV": ["S4306418318"],
    "NeurIPS": ["S4363606243"],
    "ICLR": ["S4306419637"],
    "AAAI": ["S4210191458"],
}


def robust_get_json(s: requests.Session, url: str, params: dict[str, Any], tries: int = 9) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            r = s.get(url, params=params, timeout=45)
            if r.status_code == 429:
                retry = r.headers.get("Retry-After")
                delay = float(retry) if retry and retry.isdigit() else min(60.0, 8.0 + attempt * 8.0)
                last = RuntimeError(f"HTTP 429; retry after {delay}s")
                time.sleep(delay)
                continue
            if r.status_code >= 500:
                last = RuntimeError(f"HTTP {r.status_code}")
                time.sleep(min(30.0, 3.0 + attempt * 4.0))
                continue
            r.raise_for_status()
            data = r.json()
            time.sleep(0.35)
            return data
        except Exception as exc:
            last = exc
            time.sleep(min(30.0, 2.0 + attempt * 3.0))
    raise RuntimeError(f"GET failed {url}: {last}")


def matching_source_ids(s: requests.Session, venue: str) -> list[str]:
    cfg = base.VENUES[venue]
    ids = list(SEED_SOURCE_IDS.get(venue, []))
    try:
        data = robust_get_json(s, f"{base.OPENALEX}/sources", {
            "search": cfg["search"], "per-page": 50, "mailto": "dax-literature-audit@example.com"
        })
    except Exception as exc:
        print("source-resolution-skip", venue, repr(exc), flush=True)
        return list(dict.fromkeys(ids))
    candidates = []
    for src in data.get("results") or []:
        name = base.norm_source(src.get("display_name") or "")
        score = 0.0
        for p in cfg["patterns"]:
            pn = base.norm_source(p)
            if name == pn:
                score += 25
            elif pn in name or name in pn:
                score += 10
        stype = str(src.get("type") or "").lower()
        if cfg["kind"] == "journal" and stype == "journal":
            score += 5
        if cfg["kind"] == "conference" and stype in {"conference", "repository"}:
            score += 3
        score += math.log1p(int(src.get("works_count") or 0)) / 20
        if score >= 7:
            sid = str(src.get("id") or "").rsplit("/", 1)[-1]
            if sid:
                candidates.append((score, sid, src.get("display_name"), src.get("works_count")))
    candidates.sort(reverse=True)
    # Journals are usually one stable source; conferences may have one source
    # per proceedings year, so retain several strong matches.
    limit = 2 if cfg["kind"] == "journal" else 8
    ids.extend(x[1] for x in candidates[:limit])
    ids = list(dict.fromkeys(ids))
    print("source", venue, ids, [(x[2], x[3]) for x in candidates[:limit]], flush=True)
    time.sleep(1.0)
    return ids


def query_candidates_v2():
    s = base.session()
    store: dict[str, base.Work] = {}
    select = "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location,best_oa_location,locations,ids,type,authorships"

    # Topic-first retrieval across all accepted venues.
    for family, query in base.QUERY_FAMILIES.items():
        cursor = "*"
        for _ in range(6):
            params = {
                "search": query,
                "filter": f"from_publication_date:{base.YEAR_MIN}-01-01,to_publication_date:{base.YEAR_MAX}-12-31,is_oa:true",
                "per-page": 200,
                "cursor": cursor,
                "select": select,
                "mailto": "dax-literature-audit@example.com",
            }
            data = robust_get_json(s, f"{base.OPENALEX}/works", params)
            for raw in data.get("results") or []:
                base.add_candidate(store, raw, {family})
            cursor = (data.get("meta") or {}).get("next_cursor")
            if not cursor:
                break
        print("family", family, "store", len(store), flush=True)

    # Venue-specific retrieval protects diversity and journal coverage.
    resolved: dict[str, list[str]] = {}
    for venue in base.VENUES:
        resolved[venue] = matching_source_ids(s, venue)

    for venue, ids in resolved.items():
        for sid in ids:
            for sort, pages in (("cited_by_count:desc", 3), ("publication_date:desc", 2)):
                cursor = "*"
                for _ in range(pages):
                    params = {
                        "filter": f"primary_location.source.id:{sid},from_publication_date:{base.YEAR_MIN}-01-01,to_publication_date:{base.YEAR_MAX}-12-31,is_oa:true",
                        "sort": sort,
                        "per-page": 200,
                        "cursor": cursor,
                        "select": select,
                        "mailto": "dax-literature-audit@example.com",
                    }
                    try:
                        data = robust_get_json(s, f"{base.OPENALEX}/works", params)
                    except Exception as exc:
                        print("works-source-skip", venue, sid, repr(exc), flush=True)
                        break
                    for raw in data.get("results") or []:
                        base.add_candidate(store, raw, {"venue_booster"}, forced_venue=venue)
                    cursor = (data.get("meta") or {}).get("next_cursor")
                    if not cursor:
                        break
        print("venue", venue, "store", len(store), flush=True)

    works = sorted(store.values(), key=lambda x: (-x.metadata_score, -x.cited_by_count, x.title.lower()))
    counts = Counter(w.venue for w in works)
    summary = {
        "candidate_count": len(works),
        "venue_counts": dict(sorted(counts.items())),
        "resolved_sources": resolved,
    }
    return works, summary


base.get_json = robust_get_json
base.query_candidates = query_candidates_v2

if __name__ == "__main__":
    raise SystemExit(base.main())
