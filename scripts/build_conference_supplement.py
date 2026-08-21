#!/usr/bin/env python3
"""Build vision-relevant full-text supplements from official conference sites."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import gzip
import hashlib
import json
import pickle
import re
import tempfile
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import build_multisource_vision_1000 as base

VISION_TERMS = (
    "image", "vision", "visual", "video", "object", "detection", "detector",
    "segmentation", "tracking", "track", "3d", "point cloud", "camera", "depth",
    "pose", "scene", "diffusion", "generative", "multimodal", "multi-modal",
    "domain", "adaptation", "generalization", "robust", "uncertainty", "calibration",
    "remote sensing", "aerial", "satellite", "foundation", "prompt", "contrastive",
    "self-supervised", "representation", "few-shot", "zero-shot", "open-vocabulary",
    "neural rendering", "nerf", "autonomous driving", "robot", "medical imaging",
    "compression", "efficient", "pruning", "quantization", "test-time", "source-free",
)


def title_score(title: str) -> int:
    low = title.lower()
    return sum(1 for t in VISION_TERMS if t in low)


def get(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=45)
    r.raise_for_status()
    return r.text


def pmlr_candidates(session: requests.Session) -> list[dict]:
    volumes = [(139, 2021), (162, 2022), (202, 2023), (235, 2024), (267, 2025)]
    out = []
    for volume, year in volumes:
        root = f"https://proceedings.mlr.press/v{volume}/"
        soup = BeautifulSoup(get(session, root), "html.parser")
        seen = set()
        for a in soup.find_all("a", href=True):
            href = urljoin(root, a["href"])
            text = " ".join(a.get_text(" ", strip=True).split())
            if not href.endswith(".html") or f"/v{volume}/" not in href:
                continue
            stem = Path(urlparse(href).path).stem
            if stem in {"index", ""} or href in seen or len(text) < 8:
                continue
            seen.add(href)
            if title_score(text) <= 0:
                continue
            pdf = f"https://proceedings.mlr.press/v{volume}/{stem}/{stem}.pdf"
            out.append({"title": text, "year": year, "venue": "ICML", "page_url": href, "pdf_url": pdf})
    out.sort(key=lambda x: (-title_score(x["title"]), -x["year"], x["title"].lower()))
    return out


def ecva_candidates(session: requests.Session) -> list[dict]:
    root = "https://www.ecva.net/papers.php"
    soup = BeautifulSoup(get(session, root), "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        href = urljoin(root, a["href"])
        if label != "pdf" or not href.lower().endswith(".pdf") or href in seen:
            continue
        if "2024" not in href and "eccv_2024" not in href.lower():
            continue
        seen.add(href)
        title = ""
        for tag_name in ("dt", "h3", "h4", "strong", "b"):
            prev = a.find_previous(tag_name)
            if prev:
                candidate = " ".join(prev.get_text(" ", strip=True).split())
                if 8 <= len(candidate) <= 400 and candidate.lower() not in {"pdf", "doi"}:
                    title = candidate
                    break
        if not title:
            # ECVA filenames preserve much of the title; final PDF full text is
            # still the evidence source even when this fallback is used.
            title = Path(urlparse(href).path).stem.replace("_", " ")
        out.append({"title": title, "year": 2024, "venue": "ECCV", "page_url": root, "pdf_url": href})
    out.sort(key=lambda x: (-title_score(x["title"]), x["title"].lower()))
    return out


def neurips_candidates(session: requests.Session) -> list[dict]:
    out, seen = [], set()
    for year in range(2021, 2026):
        root = f"https://proceedings.neurips.cc/paper_files/paper/{year}"
        soup = BeautifulSoup(get(session, root), "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(root, a["href"])
            title = " ".join(a.get_text(" ", strip=True).split())
            if "-Abstract-Conference.html" not in href or href in seen or len(title) < 8:
                continue
            seen.add(href)
            if title_score(title) <= 0:
                continue
            pdf = href.replace("-Abstract-Conference.html", "-Paper-Conference.pdf")
            out.append({"title": title, "year": year, "venue": "NeurIPS", "page_url": href, "pdf_url": pdf})
    out.sort(key=lambda x: (-title_score(x["title"]), -x["year"], x["title"].lower()))
    return out


def make_work(c: dict) -> base.Work:
    title = c["title"]
    venue = c["venue"]
    year = int(c["year"])
    oid = "official:" + hashlib.sha256((venue + "|" + str(year) + "|" + title).encode()).hexdigest()[:24]
    work = base.Work(
        openalex_id=oid,
        title=title,
        year=year,
        doi="",
        venue=venue,
        kind="conference",
        tier="A",
        cited_by_count=0,
        authors="",
        abstract="",
        pdf_urls=[c["pdf_url"]],
        landing_url=c["page_url"],
        query_families={"official_conference_supplement"},
    )
    work.metadata_score = base.metadata_relevance(title, "", work.query_families, 0, year, "A")
    return work


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--conference", choices=["ICML", "ECCV", "NeurIPS"], required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--target", type=int, default=150)
    ap.add_argument("--max-attempts", type=int, default=900)
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args()

    session = base.session()
    if args.conference == "ICML":
        candidates = pmlr_candidates(session)
    elif args.conference == "ECCV":
        candidates = ecva_candidates(session)
    else:
        candidates = neurips_candidates(session)
    print(args.conference, "official candidates", len(candidates), flush=True)
    candidates = candidates[: args.max_attempts]

    root = Path(tempfile.mkdtemp(prefix=f"{args.conference.lower()}_supplement_"))
    eligible = []
    try:
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(base.process_work, make_work(c), i, root): c for i, c in enumerate(candidates)}
            for n, fut in enumerate(cf.as_completed(futures), 1):
                try:
                    rec = fut.result()
                except Exception:
                    rec = None
                if rec:
                    eligible.append(rec)
                if len(eligible) >= args.target:
                    for pending in futures:
                        pending.cancel()
                    break
                if n % 50 == 0:
                    print(args.conference, "processed", n, "eligible", len(eligible), flush=True)
        unique = {}
        for rec in sorted(eligible, key=lambda r: (r["fulltext_score"], r["word_count"]), reverse=True):
            unique.setdefault(rec["pdf_sha256"], rec)
        eligible = list(unique.values())
        with gzip.open(args.output, "wb", compresslevel=6) as f:
            pickle.dump(eligible, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(args.conference, "eligible", len(eligible), flush=True)
        if len(eligible) < 110:
            raise SystemExit(f"{args.conference} produced only {len(eligible)} eligible full texts")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
