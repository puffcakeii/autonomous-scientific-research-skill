#!/usr/bin/env python3
"""Build a traceable 1,000-paper multi-source full-text vision audit.

The corpus is deliberately distributed across conferences, journals, years and
research themes. A work counts only if an open full text can be downloaded and
parsed, has sufficient length, and exposes method, experiment and quantitative
result evidence. Preprints and formal versions are deduplicated by DOI/title and
PDF SHA-256. The output stores metadata, hashes and short evidence excerpts,
not copyrighted full-paper text.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import dataclasses
import gzip
import hashlib
import json
import math
import os
import pickle
import random
import re
import shutil
import statistics
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

import fitz
import numpy as np
import requests

OPENALEX = "https://api.openalex.org"
YEAR_MIN = 2021
YEAR_MAX = 2026
TARGET_N = 1000
MIN_WORDS = 3000
MIN_PAGES = 5
MAX_PDF_MB = 60
RANDOM_SEED = 3407
USER_AGENT = "DaX-multisource-vision-audit/1.0 (academic literature audit)"

# No one venue may dominate. The final selection additionally enforces at
# least 12 venues, >=300 journal papers and >=500 conference papers.
VENUES: dict[str, dict[str, Any]] = {
    "CVPR": {"kind": "conference", "tier": "A", "search": "IEEE CVF Conference on Computer Vision and Pattern Recognition", "patterns": ["computer vision and pattern recognition", "cvpr"]},
    "ICCV": {"kind": "conference", "tier": "A", "search": "IEEE CVF International Conference on Computer Vision", "patterns": ["international conference on computer vision", "iccv"]},
    "ECCV": {"kind": "conference", "tier": "A", "search": "European Conference on Computer Vision", "patterns": ["european conference on computer vision", "computer vision eccv", "eccv"]},
    "NeurIPS": {"kind": "conference", "tier": "A", "search": "Advances in Neural Information Processing Systems", "patterns": ["neural information processing systems", "neurips", "nips"]},
    "ICLR": {"kind": "conference", "tier": "A", "search": "International Conference on Learning Representations", "patterns": ["international conference on learning representations", "iclr"]},
    "AAAI": {"kind": "conference", "tier": "A", "search": "AAAI Conference on Artificial Intelligence", "patterns": ["aaai conference on artificial intelligence", "proceedings of the aaai"]},
    "ACM MM": {"kind": "conference", "tier": "A", "search": "ACM International Conference on Multimedia", "patterns": ["acm international conference on multimedia", "acm multimedia"]},
    "WACV": {"kind": "conference", "tier": "B", "search": "Winter Conference on Applications of Computer Vision", "patterns": ["winter conference on applications of computer vision", "wacv"]},
    "TPAMI": {"kind": "journal", "tier": "A", "search": "IEEE Transactions on Pattern Analysis and Machine Intelligence", "patterns": ["transactions on pattern analysis and machine intelligence"]},
    "IJCV": {"kind": "journal", "tier": "A", "search": "International Journal of Computer Vision", "patterns": ["international journal of computer vision"]},
    "TGRS": {"kind": "journal", "tier": "A", "search": "IEEE Transactions on Geoscience and Remote Sensing", "patterns": ["transactions on geoscience and remote sensing"]},
    "ISPRS JPRS": {"kind": "journal", "tier": "A", "search": "ISPRS Journal of Photogrammetry and Remote Sensing", "patterns": ["isprs journal of photogrammetry and remote sensing"]},
    "Pattern Recognition": {"kind": "journal", "tier": "A", "search": "Pattern Recognition", "patterns": ["pattern recognition"]},
    "Information Fusion": {"kind": "journal", "tier": "A", "search": "Information Fusion", "patterns": ["information fusion"]},
    "TIP": {"kind": "journal", "tier": "A", "search": "IEEE Transactions on Image Processing", "patterns": ["transactions on image processing"]},
    "TMM": {"kind": "journal", "tier": "A", "search": "IEEE Transactions on Multimedia", "patterns": ["transactions on multimedia"]},
    "TCSVT": {"kind": "journal", "tier": "A", "search": "IEEE Transactions on Circuits and Systems for Video Technology", "patterns": ["transactions on circuits and systems for video technology"]},
    "RSE": {"kind": "journal", "tier": "A", "search": "Remote Sensing of Environment", "patterns": ["remote sensing of environment"]},
}

QUERY_FAMILIES: dict[str, str] = {
    "aerial_oriented_small": "aerial remote sensing oriented rotated small object detection",
    "domain_tta_sourcefree": "test time adaptation source free domain adaptation object detection",
    "domain_generalization": "domain generalization distribution shift object detection computer vision",
    "multimodal_spectral": "multimodal RGB thermal infrared multispectral hyperspectral detection",
    "robust_uncertainty": "robust uncertainty calibration out of distribution object detection",
    "open_vocab_foundation": "open vocabulary detection vision language foundation model remote sensing",
    "label_efficient": "semi supervised weakly supervised self supervised object detection",
    "efficient_deployment": "efficient lightweight real time object detection edge deployment",
    "tracking_video": "multi object tracking video perception detection",
    "segmentation": "remote sensing semantic instance segmentation foundation model",
    "generative_synthetic": "synthetic data diffusion generation object detection domain adaptation",
    "quality_alignment": "multimodal alignment registration image fusion detection",
}

THEMES: dict[str, tuple[str, ...]] = {
    "aerial_oriented_small": ("aerial", "remote sensing", "oriented object", "rotated object", "small object", "tiny object", "uav", "drone", "oriented bounding"),
    "domain_tta_sourcefree": ("test-time adaptation", "test time adaptation", "source-free", "source free", "domain adaptation", "domain generalization", "distribution shift"),
    "multimodal_spectral": ("multimodal", "multi-modal", "infrared", "thermal", "rgb-t", "rgbt", "multispectral", "hyperspectral", "spectral band", "sensor fusion"),
    "robust_uncertainty": ("uncertainty", "calibration", "out-of-distribution", "ood", "robustness", "worst-case", "reliability", "selective prediction"),
    "open_vocab_foundation": ("open-vocabulary", "open vocabulary", "vision-language", "vision language", "foundation model", "clip", "prompt", "large vision model"),
    "label_efficient": ("semi-supervised", "semi supervised", "weakly supervised", "few-shot", "few shot", "self-supervised", "self supervised", "pseudo-label"),
    "efficient_deployment": ("lightweight", "real-time", "real time", "latency", "flops", "edge device", "efficient", "pruning", "quantization"),
    "tracking_video": ("multi-object tracking", "multi object tracking", "tracking", "video object", "temporal association", "trajectory"),
    "segmentation": ("semantic segmentation", "instance segmentation", "panoptic", "segmentation", "salient object"),
    "generative_synthetic": ("synthetic data", "diffusion", "generative", "data generation", "simulation", "domain randomization"),
}

DIRECTION_QUERIES: dict[str, str] = {
    "source_free_oriented_tta": "source free test time adaptation oriented aerial small object detection reliability pseudo label angle",
    "reliable_calibrated_obb": "uncertainty calibration selective prediction oriented bounding box small object detection",
    "label_efficient_aerial_obb": "semi supervised weakly supervised aerial oriented object detection pseudo label",
    "open_vocab_aerial_detection": "open vocabulary vision language aerial remote sensing object detection",
    "efficient_edge_aerial_detection": "efficient lightweight edge real time aerial oriented object detection",
    "multimodal_spectral_detection": "multimodal infrared multispectral hyperspectral object detection missing modality",
}

SECTION_PATTERNS = {
    "abstract": (r"\babstract\b",),
    "introduction": (r"\bintroduction\b",),
    "related": (r"\brelated work\b", r"\bbackground\b"),
    "method": (r"\bmethod(?:ology)?\b", r"\bapproach\b", r"\bproposed method\b", r"\bframework\b"),
    "experiments": (r"\bexperiments?\b", r"\bexperimental results?\b", r"\bevaluation\b"),
    "ablation": (r"\bablation\b",),
    "limitations": (r"\blimitations?\b", r"\bdiscussion\b"),
    "conclusion": (r"\bconclusions?\b",),
    "references": (r"\breferences\b",),
}

DATASET_NAMES = (
    "COCO", "ImageNet", "LVIS", "Objects365", "OpenImages", "Cityscapes", "ADE20K",
    "BDD100K", "nuScenes", "Waymo", "KITTI", "Argoverse", "MOT17", "MOT20",
    "DOTA", "DIOR", "FAIR1M", "HRSC2016", "UCAS-AOD", "xView", "VisDrone",
    "KAIST", "LLVIP", "M3FD", "FLIR", "DroneVehicle", "VTUAV", "RGBT234",
    "LasHeR", "MFNet", "PST900", "LoveDA", "iSAID", "SpaceNet", "BigEarthNet",
    "SEN12MS", "SODA-A", "SODA-D", "AI-TOD", "TinyPerson", "CrowdHuman",
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9'\-]*\b")
URL_RE = re.compile(r"https?://[^\s\]\[)>(]+")
NUM_RE = re.compile(r"(?:\b\d+(?:\.\d+)?\s*%|\b\d+\.\d+\b)")
SPACE_RE = re.compile(r"\s+")


def norm_space(s: str) -> str:
    return SPACE_RE.sub(" ", (s or "").replace("\x00", " ")).strip()


def norm_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", norm_space(s).lower()).strip()


def norm_source(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", norm_space(s).lower()).strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reconstruct_abstract(inv: Any) -> str:
    if not isinstance(inv, dict):
        return ""
    pairs = []
    for token, positions in inv.items():
        for p in positions or []:
            pairs.append((int(p), token))
    pairs.sort()
    return " ".join(t for _, t in pairs)


def source_names(work: dict[str, Any]) -> list[str]:
    out = []
    for loc in [work.get("primary_location"), work.get("best_oa_location"), *(work.get("locations") or [])]:
        if not isinstance(loc, dict):
            continue
        src = loc.get("source") or {}
        name = src.get("display_name") if isinstance(src, dict) else None
        if name:
            out.append(norm_space(str(name)))
    return list(dict.fromkeys(out))


def classify_venue(work: dict[str, Any], forced: str | None = None) -> str | None:
    if forced in VENUES:
        return forced
    names = " | ".join(norm_source(x) for x in source_names(work))
    if not names:
        return None
    # Exact/specific matches first; Pattern Recognition must not consume generic text.
    order = ["TPAMI", "IJCV", "TGRS", "ISPRS JPRS", "Information Fusion", "TIP", "TMM", "TCSVT", "RSE", "Pattern Recognition", "CVPR", "ICCV", "ECCV", "NeurIPS", "ICLR", "AAAI", "ACM MM", "WACV"]
    for venue in order:
        for p in VENUES[venue]["patterns"]:
            pn = norm_source(p)
            if venue == "Pattern Recognition":
                if any(norm_source(x) == pn for x in source_names(work)):
                    return venue
            elif pn in names:
                return venue
    return None


def session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,application/pdf,*/*"})
    return s


def get_json(s: requests.Session, url: str, params: dict[str, Any], tries: int = 5) -> dict[str, Any]:
    last = None
    for attempt in range(tries):
        try:
            r = s.get(url, params=params, timeout=40)
            if r.status_code == 429:
                time.sleep(2 + attempt * 3)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed {url}: {last}")


def resolve_sources(s: requests.Session) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for venue, cfg in VENUES.items():
        data = get_json(s, f"{OPENALEX}/sources", {"search": cfg["search"], "per-page": 25, "mailto": "research@example.com"})
        best = None
        best_score = -1.0
        for src in data.get("results") or []:
            name = norm_source(src.get("display_name") or "")
            score = 0.0
            for p in cfg["patterns"]:
                pn = norm_source(p)
                if name == pn:
                    score += 20
                elif pn in name or name in pn:
                    score += 8
            stype = str(src.get("type") or "").lower()
            if cfg["kind"] == "journal" and stype == "journal":
                score += 3
            if cfg["kind"] == "conference" and stype in {"conference", "repository"}:
                score += 2
            score += math.log1p(int(src.get("works_count") or 0)) / 20
            if score > best_score:
                best, best_score = src, score
        if best and best_score >= 4:
            resolved[venue] = str(best["id"]).rsplit("/", 1)[-1]
        print("source", venue, resolved.get(venue), best.get("display_name") if best else None, round(best_score, 2), flush=True)
    return resolved


@dataclass
class Work:
    openalex_id: str
    title: str
    year: int
    doi: str
    venue: str
    kind: str
    tier: str
    cited_by_count: int
    authors: str
    abstract: str
    pdf_urls: list[str]
    landing_url: str
    query_families: set[str] = field(default_factory=set)
    metadata_score: float = 0.0


def candidate_pdf_urls(w: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for loc in [w.get("best_oa_location"), w.get("primary_location"), *(w.get("locations") or [])]:
        if not isinstance(loc, dict):
            continue
        for key in ("pdf_url", "landing_page_url"):
            u = loc.get(key)
            if not u:
                continue
            u = str(u).strip()
            if key == "landing_page_url" and not (u.lower().endswith(".pdf") or "openreview.net/pdf" in u or "arxiv.org/pdf" in u):
                continue
            urls.append(u)
    ids = w.get("ids") or {}
    arx = ids.get("arxiv") if isinstance(ids, dict) else None
    if arx:
        aid = str(arx).rsplit("/", 1)[-1]
        urls.append(f"https://arxiv.org/pdf/{aid}.pdf")
    # Prefer stable, openly downloadable hosts.
    preferred = ("openaccess.thecvf.com", "ecva.net", "proceedings.neurips.cc", "papers.nips.cc", "openreview.net", "proceedings.mlr.press", "arxiv.org", "ojs.aaai.org", "link.springer.com", "repository", "hal.science")
    urls = list(dict.fromkeys(urls))
    urls.sort(key=lambda u: (0 if any(h in u for h in preferred) else 1, len(u)))
    return urls[:8]


def metadata_relevance(title: str, abstract: str, families: set[str], cited: int, year: int, tier: str) -> float:
    hay = (title + " " + abstract).lower()
    terms = sum(min(hay.count(k), 4) for kws in THEMES.values() for k in kws)
    recency = max(0, year - 2020) * 0.15
    citation = math.log1p(max(0, cited))
    return 4.0 * len(families) + 1.2 * terms + citation + recency + (2.0 if tier == "A" else 0.0)


def authors_string(w: dict[str, Any]) -> str:
    names = []
    for a in w.get("authorships") or []:
        au = a.get("author") or {}
        n = au.get("display_name") if isinstance(au, dict) else None
        if n:
            names.append(norm_space(str(n)))
    return "; ".join(names[:30])


def add_candidate(store: dict[str, Work], raw: dict[str, Any], families: set[str], forced_venue: str | None = None) -> None:
    venue = classify_venue(raw, forced_venue)
    if not venue:
        return
    year = int(raw.get("publication_year") or 0)
    if not (YEAR_MIN <= year <= YEAR_MAX):
        return
    title = norm_space(raw.get("title") or "")
    if len(title) < 8:
        return
    urls = candidate_pdf_urls(raw)
    if not urls:
        return
    oid = str(raw.get("id") or "")
    if not oid:
        return
    doi = str(raw.get("doi") or "").lower().replace("https://doi.org/", "")
    landing = ""
    for loc in [raw.get("primary_location"), raw.get("best_oa_location")]:
        if isinstance(loc, dict) and loc.get("landing_page_url"):
            landing = str(loc["landing_page_url"])
            break
    cfg = VENUES[venue]
    obj = Work(
        openalex_id=oid,
        title=title,
        year=year,
        doi=doi,
        venue=venue,
        kind=cfg["kind"],
        tier=cfg["tier"],
        cited_by_count=int(raw.get("cited_by_count") or 0),
        authors=authors_string(raw),
        abstract=reconstruct_abstract(raw.get("abstract_inverted_index")),
        pdf_urls=urls,
        landing_url=landing,
        query_families=set(families),
    )
    obj.metadata_score = metadata_relevance(obj.title, obj.abstract, obj.query_families, obj.cited_by_count, obj.year, obj.tier)
    key = "doi:" + doi if doi else "title:" + norm_title(title)
    old = store.get(key)
    if old is None or obj.metadata_score > old.metadata_score:
        if old:
            obj.query_families.update(old.query_families)
        store[key] = obj
    else:
        old.query_families.update(families)
        old.pdf_urls = list(dict.fromkeys(old.pdf_urls + urls))[:8]
        old.metadata_score = metadata_relevance(old.title, old.abstract, old.query_families, old.cited_by_count, old.year, old.tier)


def query_candidates() -> tuple[list[Work], dict[str, Any]]:
    s = session()
    store: dict[str, Work] = {}
    select = "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location,best_oa_location,locations,ids,type,authorships"
    # Topic searches provide recall across locations and proceedings variants.
    for family, query in QUERY_FAMILIES.items():
        cursor = "*"
        for _ in range(8):
            params = {
                "search": query,
                "filter": f"from_publication_date:{YEAR_MIN}-01-01,to_publication_date:{YEAR_MAX}-12-31,is_oa:true",
                "per-page": 200,
                "cursor": cursor,
                "select": select,
                "mailto": "research@example.com",
            }
            data = get_json(s, f"{OPENALEX}/works", params)
            for raw in data.get("results") or []:
                add_candidate(store, raw, {family})
            cursor = (data.get("meta") or {}).get("next_cursor")
            if not cursor:
                break
        print("family", family, "store", len(store), flush=True)

    # Source-specific boosters protect venue and journal coverage.
    resolved = resolve_sources(s)
    for venue, sid in resolved.items():
        for sort, pages in (("cited_by_count:desc", 5), ("publication_date:desc", 3)):
            cursor = "*"
            for _ in range(pages):
                params = {
                    "filter": f"primary_location.source.id:{sid},from_publication_date:{YEAR_MIN}-01-01,to_publication_date:{YEAR_MAX}-12-31,is_oa:true",
                    "sort": sort,
                    "per-page": 200,
                    "cursor": cursor,
                    "select": select,
                    "mailto": "research@example.com",
                }
                data = get_json(s, f"{OPENALEX}/works", params)
                for raw in data.get("results") or []:
                    add_candidate(store, raw, {"venue_booster"}, forced_venue=venue)
                cursor = (data.get("meta") or {}).get("next_cursor")
                if not cursor:
                    break
        print("venue", venue, "store", len(store), flush=True)

    works = sorted(store.values(), key=lambda x: (-x.metadata_score, -x.cited_by_count, x.title.lower()))
    counts = Counter(w.venue for w in works)
    summary = {"candidate_count": len(works), "venue_counts": dict(sorted(counts.items())), "resolved_sources": resolved}
    return works, summary


def download_pdf(s: requests.Session, urls: list[str], out: Path) -> tuple[str, bytes] | None:
    for url in urls[:6]:
        try:
            with s.get(url, timeout=(15, 35), stream=True, allow_redirects=True) as r:
                if r.status_code != 200:
                    continue
                length = int(r.headers.get("content-length") or 0)
                if length > MAX_PDF_MB * 1024 * 1024:
                    continue
                chunks = []
                size = 0
                for chunk in r.iter_content(1024 * 256):
                    if not chunk:
                        continue
                    size += len(chunk)
                    if size > MAX_PDF_MB * 1024 * 1024:
                        chunks = []
                        break
                    chunks.append(chunk)
                if not chunks:
                    continue
                data = b"".join(chunks)
                if not data.startswith(b"%PDF"):
                    continue
                out.write_bytes(data)
                return r.url, data
        except Exception:
            continue
    return None


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str) -> dict[str, str]:
    low = text.lower()
    positions: list[tuple[int, str]] = []
    for name, pats in SECTION_PATTERNS.items():
        best = None
        for pat in pats:
            for m in re.finditer(pat, low, flags=re.I):
                ls = low.rfind("\n", 0, m.start()) + 1
                le = low.find("\n", m.start())
                if le < 0:
                    le = min(len(low), m.start() + 120)
                line = low[ls:le].strip()
                if len(line) <= 120:
                    best = m.start()
                    break
            if best is not None:
                break
        if best is not None:
            positions.append((best, name))
    positions.sort()
    sections: dict[str, str] = {}
    for i, (start, name) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        if name not in sections and end > start:
            sections[name] = text[start:end]
    return sections


def sentences(text: str) -> list[str]:
    compact = norm_space(text)
    return [s.strip() for s in SENTENCE_SPLIT.split(compact) if 45 <= len(s.strip()) <= 700]


def evidence(section: str, terms: Iterable[str], limit: int = 3, require_number: bool = False) -> list[str]:
    ranked = []
    for i, sent in enumerate(sentences(section)):
        low = sent.lower()
        score = sum(1.0 for t in terms if t in low)
        if require_number and NUM_RE.search(sent):
            score += 1.5
        if "we " in low or "our " in low:
            score += 0.25
        score -= i * 0.0002
        if score > 0:
            ranked.append((score, sent))
    ranked.sort(key=lambda x: (-x[0], len(x[1])))
    out, seen = [], set()
    for _, sent in ranked:
        key = re.sub(r"\W+", " ", sent.lower())[:180]
        if key not in seen:
            seen.add(key)
            out.append(sent)
        if len(out) >= limit:
            break
    return out


def theme_scores(title: str, text: str) -> dict[str, int]:
    hay = (title + "\n" + text[:80000]).lower()
    return {name: sum(min(hay.count(term), 20) for term in terms) for name, terms in THEMES.items()}


def extract_code_urls(text: str) -> list[str]:
    urls = []
    for u in URL_RE.findall(text):
        u = u.rstrip(".,;:")
        if any(h in u.lower() for h in ("github.com", "gitlab.com", "huggingface.co")):
            urls.append(u)
    return list(dict.fromkeys(urls))[:12]


def extract_datasets(text: str) -> list[str]:
    return [name for name in DATASET_NAMES if re.search(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])", text, re.I)]


def fulltext_score(work: Work, text: str, sections: dict[str, str], scores: dict[str, int], evidence_counts: dict[str, int]) -> float:
    direct = (
        2.2 * min(scores["aerial_oriented_small"], 20)
        + 2.2 * min(scores["domain_tta_sourcefree"], 20)
        + 1.8 * min(scores["multimodal_spectral"], 20)
        + 1.7 * min(scores["robust_uncertainty"], 20)
        + 1.5 * min(scores["open_vocab_foundation"], 20)
        + 1.3 * min(scores["label_efficient"], 20)
        + 1.0 * min(scores["efficient_deployment"], 20)
    )
    quality = 2.0 * len(sections) + 1.5 * sum(evidence_counts.values())
    return work.metadata_score + direct + quality


def process_work(work: Work, idx: int, root: Path) -> dict[str, Any] | None:
    s = session()
    pdf_path = root / f"{idx:06d}.pdf"
    got = download_pdf(s, work.pdf_urls, pdf_path)
    if not got:
        return None
    final_url, pdf_bytes = got
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        if page_count < MIN_PAGES:
            return None
        text = clean_text("\n".join(page.get_text("text") for page in doc))
    except Exception:
        return None
    words = WORD_RE.findall(text)
    if len(words) < MIN_WORDS:
        return None
    sections = split_sections(text)
    method_text = sections.get("method", "")
    exp_text = sections.get("experiments", "")
    intro_text = sections.get("introduction", sections.get("abstract", text[:12000]))
    conclusion_text = sections.get("conclusion", "")
    problem = evidence(intro_text, ("challenge", "problem", "however", "limitation", "difficult", "we address"), 3)
    methods = evidence(method_text, ("we propose", "our method", "framework", "architecture", "module", "loss", "objective"), 4)
    experiments = evidence(exp_text, ("dataset", "benchmark", "training", "implementation", "evaluation", "baseline"), 4)
    results = evidence(exp_text + "\n" + conclusion_text, ("outperform", "improve", "achieve", "result", "performance", "state-of-the-art"), 4, require_number=True)
    ablation = evidence(sections.get("ablation", exp_text), ("ablation", "component", "variant", "without", "effect"), 3, require_number=True)
    limitations = evidence(sections.get("limitations", conclusion_text), ("limitation", "future work", "fails", "cannot", "however"), 3)
    if not method_text or not exp_text or not methods or not experiments or not results:
        return None
    scores = theme_scores(work.title, text)
    # Require substantive relevance to at least one research family.
    if max(scores.values(), default=0) < 3:
        return None
    ev_counts = {"problem": len(problem), "method": len(methods), "experiment": len(experiments), "result": len(results), "ablation": len(ablation), "limitation": len(limitations)}
    key = "doi:" + work.doi if work.doi else "title:" + norm_title(work.title)
    rec = {
        "work": dataclasses.asdict(work),
        "dedup_key": key,
        "fulltext_url": final_url,
        "pdf_sha256": sha256_bytes(pdf_bytes),
        "page_count": page_count,
        "word_count": len(words),
        "section_names": sorted(sections),
        "section_coverage": sum(name in sections for name in ("abstract", "introduction", "method", "experiments", "conclusion")) / 5.0,
        "theme_scores": scores,
        "research_problem": problem,
        "method_claims": methods,
        "experiment_protocol": experiments,
        "main_results": results,
        "ablation_evidence": ablation,
        "limitation_evidence": limitations,
        "datasets": extract_datasets(text),
        "code_urls": extract_code_urls(text),
        "fulltext_score": 0.0,
    }
    rec["fulltext_score"] = round(fulltext_score(work, text, sections, scores, ev_counts), 6)
    return rec


def balanced_select(records: list[dict[str, Any]], target: int = TARGET_N) -> list[dict[str, Any]]:
    # Highest-quality duplicate survives.
    by_key: dict[str, dict[str, Any]] = {}
    by_sha: dict[str, dict[str, Any]] = {}
    for r in sorted(records, key=lambda x: (x["fulltext_score"], x["word_count"], x["work"]["cited_by_count"]), reverse=True):
        if r["dedup_key"] in by_key or r["pdf_sha256"] in by_sha:
            continue
        by_key[r["dedup_key"]] = r
        by_sha[r["pdf_sha256"]] = r
    eligible = list(by_key.values())
    eligible.sort(key=lambda x: (-x["fulltext_score"], -x["work"]["cited_by_count"], x["work"]["title"].lower()))
    if len(eligible) < target:
        raise RuntimeError(f"Only {len(eligible)} unique eligible full texts")

    by_venue: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in eligible:
        by_venue[r["work"]["venue"]].append(r)
    for rows in by_venue.values():
        rows.sort(key=lambda x: (-x["fulltext_score"], -x["work"]["cited_by_count"]))

    selected: list[dict[str, Any]] = []
    selected_sha: set[str] = set()
    venue_counts: Counter[str] = Counter()
    year_counts: Counter[int] = Counter()
    kind_counts: Counter[str] = Counter()
    MAX_PER_VENUE = 110
    MAX_PER_YEAR = 340

    def take(r: dict[str, Any]) -> bool:
        v = r["work"]["venue"]
        y = int(r["work"]["year"])
        if r["pdf_sha256"] in selected_sha or venue_counts[v] >= MAX_PER_VENUE or year_counts[y] >= MAX_PER_YEAR:
            return False
        selected.append(r)
        selected_sha.add(r["pdf_sha256"])
        venue_counts[v] += 1
        year_counts[y] += 1
        kind_counts[r["work"]["kind"]] += 1
        return True

    # Minimum venue representation: up to 55 from every venue with enough evidence.
    for venue in sorted(by_venue, key=lambda v: (-len(by_venue[v]), v)):
        quota = min(55, len(by_venue[venue]))
        for r in by_venue[venue]:
            if venue_counts[venue] >= quota:
                break
            take(r)

    # Protect at least 300 journal and 500 conference papers using round-robin.
    for desired_kind, minimum in (("journal", 300), ("conference", 500)):
        while kind_counts[desired_kind] < minimum and len(selected) < target:
            progressed = False
            for venue in sorted(v for v in by_venue if VENUES[v]["kind"] == desired_kind):
                for r in by_venue[venue]:
                    if take(r):
                        progressed = True
                        break
                if kind_counts[desired_kind] >= minimum or len(selected) >= target:
                    break
            if not progressed:
                break

    # Theme floors, overlapping by design.
    theme_min = {
        "aerial_oriented_small": 140,
        "domain_tta_sourcefree": 150,
        "multimodal_spectral": 110,
        "robust_uncertainty": 100,
        "open_vocab_foundation": 90,
        "label_efficient": 90,
        "efficient_deployment": 90,
    }
    for theme, minimum in theme_min.items():
        current = sum(r["theme_scores"].get(theme, 0) > 0 for r in selected)
        for r in eligible:
            if current >= minimum or len(selected) >= target:
                break
            if r["theme_scores"].get(theme, 0) > 0 and take(r):
                current += 1

    # Final score-ordered fill respecting source/year caps.
    for r in eligible:
        if len(selected) >= target:
            break
        take(r)
    if len(selected) < target:
        raise RuntimeError(f"Diversity caps permit only {len(selected)} papers")
    selected = selected[:target]
    for i, r in enumerate(selected, 1):
        r["selected_rank"] = i
    return selected


def short_join(values: list[str]) -> str:
    return " || ".join(norm_space(v)[:700] for v in values)


def direction_scores(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for direction, query in DIRECTION_QUERIES.items():
        terms = [t for t in re.split(r"\s+", query.lower()) if len(t) > 3]
        ranked = []
        for r in selected:
            hay = (r["work"]["title"] + " " + r["work"]["abstract"] + " " + short_join(r["method_claims"] + r["main_results"])).lower()
            score = sum(hay.count(t) for t in terms) + 0.05 * r["fulltext_score"]
            if score > 0:
                ranked.append((score, r))
        ranked.sort(key=lambda x: (-x[0], -x[1]["fulltext_score"]))
        rows.append({
            "direction": direction,
            "support_count": len(ranked),
            "direct_top30_count": sum(s >= 8 for s, _ in ranked[:30]),
            "top_papers": [r["work"]["title"] for _, r in ranked[:20]],
            "top_venues": dict(Counter(r["work"]["venue"] for _, r in ranked[:50])),
        })
    return rows


def write_outputs(selected: list[dict[str, Any]], eligible: list[dict[str, Any]], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fields = [
        "selected_rank", "title", "authors", "year", "venue", "source_kind", "venue_tier", "doi", "openalex_id",
        "landing_url", "fulltext_url", "pdf_sha256", "page_count", "word_count", "section_coverage", "cited_by_count",
        "query_families", "themes", "datasets", "code_urls", "research_problem", "method_claims", "experiment_protocol",
        "main_results", "ablation_evidence", "limitation_evidence", "fulltext_score",
    ]
    with (out / "registry_1000.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in selected:
            work = r["work"]
            w.writerow({
                "selected_rank": r["selected_rank"], "title": work["title"], "authors": work["authors"], "year": work["year"],
                "venue": work["venue"], "source_kind": work["kind"], "venue_tier": work["tier"], "doi": work["doi"],
                "openalex_id": work["openalex_id"], "landing_url": work["landing_url"], "fulltext_url": r["fulltext_url"],
                "pdf_sha256": r["pdf_sha256"], "page_count": r["page_count"], "word_count": r["word_count"],
                "section_coverage": r["section_coverage"], "cited_by_count": work["cited_by_count"],
                "query_families": ";".join(sorted(work["query_families"])),
                "themes": ";".join(k for k, v in r["theme_scores"].items() if v > 0), "datasets": ";".join(r["datasets"]),
                "code_urls": ";".join(r["code_urls"]), "research_problem": short_join(r["research_problem"]),
                "method_claims": short_join(r["method_claims"]), "experiment_protocol": short_join(r["experiment_protocol"]),
                "main_results": short_join(r["main_results"]), "ablation_evidence": short_join(r["ablation_evidence"]),
                "limitation_evidence": short_join(r["limitation_evidence"]), "fulltext_score": r["fulltext_score"],
            })
    with (out / "notes_1000.jsonl").open("w", encoding="utf-8") as f:
        for r in selected:
            compact = {k: v for k, v in r.items() if k not in {}}
            f.write(json.dumps(compact, ensure_ascii=False) + "\n")

    venue_counts = Counter(r["work"]["venue"] for r in selected)
    year_counts = Counter(int(r["work"]["year"]) for r in selected)
    kind_counts = Counter(r["work"]["kind"] for r in selected)
    theme_counts = {t: sum(r["theme_scores"].get(t, 0) > 0 for r in selected) for t in THEMES}
    distribution = []
    for venue in sorted(venue_counts):
        distribution.append({"venue": venue, "kind": VENUES[venue]["kind"], "count": venue_counts[venue], "share": venue_counts[venue] / len(selected)})
    with (out / "venue_distribution.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["venue", "kind", "count", "share"]); w.writeheader(); w.writerows(distribution)
    with (out / "year_distribution.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["year", "count", "share"]); w.writeheader()
        for year in sorted(year_counts):
            w.writerow({"year": year, "count": year_counts[year], "share": year_counts[year] / len(selected)})

    core = sorted(selected, key=lambda r: (-r["fulltext_score"], -r["work"]["cited_by_count"]))[:150]
    with (out / "core_150.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields2 = ["rank", "title", "year", "venue", "doi", "fulltext_url", "pdf_sha256", "fulltext_score", "themes", "method_evidence", "result_evidence"]
        w = csv.DictWriter(f, fieldnames=fields2); w.writeheader()
        for i, r in enumerate(core, 1):
            w.writerow({"rank": i, "title": r["work"]["title"], "year": r["work"]["year"], "venue": r["work"]["venue"],
                        "doi": r["work"]["doi"], "fulltext_url": r["fulltext_url"], "pdf_sha256": r["pdf_sha256"],
                        "fulltext_score": r["fulltext_score"], "themes": ";".join(k for k, v in r["theme_scores"].items() if v > 0),
                        "method_evidence": short_join(r["method_claims"]), "result_evidence": short_join(r["main_results"])})

    directions = direction_scores(selected)
    (out / "candidate_direction_matrix.json").write_text(json.dumps(directions, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "schema": "multisource_vision_fulltext_audit_v1",
        "selected_fulltexts": len(selected),
        "eligible_unique_fulltexts": len(eligible),
        "unique_pdf_sha256": len({r["pdf_sha256"] for r in selected}),
        "unique_doi_or_title": len({r["dedup_key"] for r in selected}),
        "year_range": [min(year_counts), max(year_counts)],
        "venue_count": len(venue_counts),
        "venue_counts": dict(sorted(venue_counts.items())),
        "kind_counts": dict(kind_counts),
        "year_counts": dict(sorted(year_counts.items())),
        "theme_counts": theme_counts,
        "max_single_venue_share": max(venue_counts.values()) / len(selected),
        "max_single_year_share": max(year_counts.values()) / len(selected),
        "word_count_total": sum(r["word_count"] for r in selected),
        "word_count_min": min(r["word_count"] for r in selected),
        "word_count_median": statistics.median(r["word_count"] for r in selected),
        "page_count_min": min(r["page_count"] for r in selected),
        "method_experiment_result_complete": sum(bool(r["method_claims"] and r["experiment_protocol"] and r["main_results"]) for r in selected),
        "integrity_label": "machine-assisted full-text review; core papers require human second-pass before final novelty claims",
    }
    (out / "audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    methodology = f"""# 多来源1000篇全文审计口径\n\n- 年份：{YEAR_MIN}–{YEAR_MAX}\n- 正式纳入：{len(selected)}篇独立全文\n- Venue：{len(venue_counts)}个；任何单一venue占比不超过{summary['max_single_venue_share']:.1%}\n- 来源结构：会议{kind_counts['conference']}篇，期刊{kind_counts['journal']}篇\n- 纳入条件：开放全文可下载、PDF不少于{MIN_PAGES}页、正文不少于{MIN_WORDS}词、方法/实验/定量结果证据均可定位\n- 去重：DOI或规范化标题去重，并以PDF SHA-256再次去重；预印本与正式版只计一次\n- 输出不附论文全文，仅保存元数据、全文URL、PDF哈希及短证据片段\n- 精读口径：逐篇机器辅助全文解析与结构化证据提取；不能冒充1000篇人工逐字阅读。最终创新判断需对核心150篇进行第二遍人工复核。\n"""
    (out / "METHODOLOGY.md").write_text(methodology, encoding="utf-8")

    # Hard integrity contract.
    assert len(selected) == 1000
    assert len(venue_counts) >= 12, venue_counts
    assert kind_counts["journal"] >= 300, kind_counts
    assert kind_counts["conference"] >= 500, kind_counts
    assert max(venue_counts.values()) <= 110, venue_counts
    assert max(year_counts.values()) <= 340, year_counts
    assert sum(c for y, c in year_counts.items() if y >= 2022) >= 700
    assert summary["unique_pdf_sha256"] == 1000
    assert summary["unique_doi_or_title"] == 1000
    assert summary["method_experiment_result_complete"] == 1000

    manifest = []
    for p in sorted(x for x in out.rglob("*") if x.is_file() and x.name != "SHA256SUMS.txt"):
        manifest.append(f"{sha256_bytes(p.read_bytes())}  {p.relative_to(out).as_posix()}")
    (out / "SHA256SUMS.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")


def cmd_metadata(args: argparse.Namespace) -> None:
    works, summary = query_candidates()
    Path(args.output).write_text(json.dumps([dataclasses.asdict(w) | {"query_families": sorted(w.query_families)} for w in works], ensure_ascii=False), encoding="utf-8")
    Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    if len(works) < 3500:
        raise SystemExit(f"Insufficient candidate pool: {len(works)}")


def cmd_shard(args: argparse.Namespace) -> None:
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    works = []
    for d in raw:
        d["query_families"] = set(d["query_families"])
        works.append(Work(**d))
    # Round-robin interleaving by venue before shard assignment protects diversity.
    by_v: dict[str, list[Work]] = defaultdict(list)
    for w in works:
        by_v[w.venue].append(w)
    interleaved: list[Work] = []
    maxlen = max(map(len, by_v.values()))
    for i in range(maxlen):
        for v in sorted(by_v):
            if i < len(by_v[v]):
                interleaved.append(by_v[v][i])
    works = [w for i, w in enumerate(interleaved) if i % args.shard_count == args.shard_id][: args.max_attempts]
    root = Path(tempfile.mkdtemp(prefix=f"multisource_{args.shard_id}_"))
    eligible = []
    try:
        with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(process_work, w, i, root): w for i, w in enumerate(works)}
            for n, fut in enumerate(cf.as_completed(futures), 1):
                try:
                    rec = fut.result()
                except Exception:
                    rec = None
                if rec:
                    eligible.append(rec)
                if len(eligible) >= args.target_per_shard:
                    for pending in futures:
                        pending.cancel()
                    break
                if n % 50 == 0:
                    print("shard", args.shard_id, "done", n, "eligible", len(eligible), flush=True)
        # Local dedup.
        unique = {}
        for r in sorted(eligible, key=lambda x: (x["fulltext_score"], x["word_count"]), reverse=True):
            unique.setdefault(r["pdf_sha256"], r)
        eligible = list(unique.values())
        with gzip.open(args.output, "wb", compresslevel=6) as f:
            pickle.dump(eligible, f, protocol=pickle.HIGHEST_PROTOCOL)
        print("shard", args.shard_id, "attempted", len(works), "eligible", len(eligible), flush=True)
        if len(eligible) < args.minimum_per_shard:
            raise SystemExit(f"Shard {args.shard_id} only produced {len(eligible)}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def cmd_merge(args: argparse.Namespace) -> None:
    allrec = []
    for p in sorted(Path(args.input_dir).rglob("shard_*.pkl.gz")):
        with gzip.open(p, "rb") as f:
            allrec.extend(pickle.load(f))
    print("merged records", len(allrec), flush=True)
    selected = balanced_select(allrec, TARGET_N)
    # Reconstruct eligible dedup list for reporting.
    unique = {}
    for r in sorted(allrec, key=lambda x: (x["fulltext_score"], x["word_count"]), reverse=True):
        if r["dedup_key"] not in unique and r["pdf_sha256"] not in {x["pdf_sha256"] for x in unique.values()}:
            unique[r["dedup_key"]] = r
    write_outputs(selected, list(unique.values()), Path(args.output))
    print((Path(args.output) / "audit_summary.json").read_text(encoding="utf-8"), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("metadata")
    p.add_argument("--output", default="candidates.json")
    p.add_argument("--summary", default="candidate_summary.json")
    p.set_defaults(func=cmd_metadata)
    p = sub.add_parser("shard")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--shard-id", type=int, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--max-attempts", type=int, default=650)
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--target-per-shard", type=int, default=145)
    p.add_argument("--minimum-per-shard", type=int, default=95)
    p.set_defaults(func=cmd_shard)
    p = sub.add_parser("merge")
    p.add_argument("--input-dir", required=True)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_merge)
    args = ap.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
