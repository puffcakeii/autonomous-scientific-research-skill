#!/usr/bin/env python3
"""Deterministic venue/ISSN metadata runner for the multi-source audit."""
from __future__ import annotations

import sys
import time
from collections import Counter
from typing import Any

import requests

import build_multisource_vision_1000 as base

CONFERENCE_SOURCES = {
    "CVPR": ["S4363607701"],
    "ICCV": ["S4363607764"],
    "ECCV": ["S4306418318"],
    "NeurIPS": ["S4363606243"],
    "ICLR": ["S4306419637"],
    "AAAI": ["S4210191458"],
}

JOURNAL_ISSNS = {
    "TPAMI": ["0162-8828"],
    "IJCV": ["0920-5691"],
    "TGRS": ["0196-2892"],
    "ISPRS JPRS": ["0924-2716"],
    "Pattern Recognition": ["0031-3203"],
    "Information Fusion": ["1566-2535"],
    "TIP": ["1057-7149"],
    "TMM": ["1520-9210"],
    "TCSVT": ["1051-8215"],
    "RSE": ["0034-4257"],
}


def get_json(s: requests.Session, url: str, params: dict[str, Any], tries: int = 8):
    last = None
    for attempt in range(tries):
        try:
            r = s.get(url, params=params, timeout=45)
            if r.status_code == 429:
                last = RuntimeError("HTTP 429")
                time.sleep(min(45, 6 + attempt * 6))
                continue
            if r.status_code >= 500:
                last = RuntimeError(f"HTTP {r.status_code}")
                time.sleep(min(25, 3 + attempt * 3))
                continue
            r.raise_for_status()
            time.sleep(0.25)
            return r.json()
        except Exception as exc:
            last = exc
            time.sleep(min(25, 2 + attempt * 3))
    raise RuntimeError(f"GET failed {url}: {last}")


def fetch_pages(s, store, *, venue, filter_expr, select, pages=5):
    for sort, n_pages in (("cited_by_count:desc", pages), ("publication_date:desc", 2)):
        cursor = "*"
        for _ in range(n_pages):
            params = {
                "filter": f"{filter_expr},from_publication_date:{base.YEAR_MIN}-01-01,to_publication_date:{base.YEAR_MAX}-12-31,is_oa:true",
                "sort": sort,
                "per-page": 200,
                "cursor": cursor,
                "select": select,
                "mailto": "dax-literature-audit@example.com",
            }
            try:
                data = get_json(s, f"{base.OPENALEX}/works", params)
            except Exception as exc:
                print("venue-query-skip", venue, filter_expr, repr(exc), flush=True)
                return
            for raw in data.get("results") or []:
                base.add_candidate(store, raw, {"venue_booster"}, forced_venue=venue)
            cursor = (data.get("meta") or {}).get("next_cursor")
            if not cursor:
                break


def query_candidates_v3():
    s = base.session()
    store = {}
    select = "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location,best_oa_location,locations,ids,type,authorships"

    for family, query in base.QUERY_FAMILIES.items():
        cursor = "*"
        for _ in range(5):
            params = {
                "search": query,
                "filter": f"from_publication_date:{base.YEAR_MIN}-01-01,to_publication_date:{base.YEAR_MAX}-12-31,is_oa:true",
                "per-page": 200,
                "cursor": cursor,
                "select": select,
                "mailto": "dax-literature-audit@example.com",
            }
            data = get_json(s, f"{base.OPENALEX}/works", params)
            for raw in data.get("results") or []:
                base.add_candidate(store, raw, {family})
            cursor = (data.get("meta") or {}).get("next_cursor")
            if not cursor:
                break
        print("family", family, "store", len(store), flush=True)

    for venue, sids in CONFERENCE_SOURCES.items():
        for sid in sids:
            fetch_pages(s, store, venue=venue, filter_expr=f"primary_location.source.id:{sid}", select=select, pages=5)
        print("conference", venue, "store", len(store), flush=True)

    for venue, issns in JOURNAL_ISSNS.items():
        for issn in issns:
            fetch_pages(s, store, venue=venue, filter_expr=f"primary_location.source.issn:{issn}", select=select, pages=5)
        print("journal", venue, "store", len(store), flush=True)

    works = sorted(store.values(), key=lambda x: (-x.metadata_score, -x.cited_by_count, x.title.lower()))
    counts = Counter(w.venue for w in works)
    return works, {
        "candidate_count": len(works),
        "venue_counts": dict(sorted(counts.items())),
        "conference_source_ids": CONFERENCE_SOURCES,
        "journal_issns": JOURNAL_ISSNS,
    }


base.get_json = get_json
base.query_candidates = query_candidates_v3

if __name__ == "__main__":
    raise SystemExit(base.main())
