#!/usr/bin/env python3
"""Build a traceable 1000-paper full-text audit from the CVPR 2025 text mirror.

The script reads every converted full paper, performs section-aware evidence
extraction, clusters the corpus for coverage, selects exactly 1000 papers, and
writes a registry, compact evidence chunks, copied full texts, checksums and
summary reports. It deliberately labels the output as machine-assisted
full-text audit rather than human close reading.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(os.environ.get("CVPR_TEXT_ROOT", "external/CVPR2025_TXT/papers"))
OUT = Path(os.environ.get("AUDIT_OUT", "artifacts/cvpr1000_audit"))
TARGET_N = int(os.environ.get("TARGET_N", "1000"))
RANDOM_STATE = 3407

THEMES: dict[str, tuple[str, ...]] = {
    "rgb_ir_multispectral": (
        "thermal", "infrared", "rgb-t", "rgbt", "multispectral", "hyperspectral",
        "spectral band", "cross-spectrum", "cross-spectral", "visible infrared",
    ),
    "multimodal_fusion_alignment": (
        "multimodal", "multi-modal", "cross-modal", "fusion", "alignment",
        "modality", "sensor fusion", "feature fusion",
    ),
    "missing_degraded_modality": (
        "missing modality", "incomplete modality", "modality dropout", "sensor failure",
        "missing view", "corrupted modality", "degraded modality", "partial modality",
    ),
    "object_detection": (
        "object detection", "detector", "bounding box", "instance detection",
        "oriented object", "rotated object", "open-vocabulary detection",
    ),
    "small_aerial_remote": (
        "small object", "tiny object", "aerial", "remote sensing", "satellite",
        "drone", "uav", "oriented bounding", "dense object",
    ),
    "tracking_video": (
        "tracking", "multi-object tracking", "single object tracking", "video object",
        "temporal association", "trajectory",
    ),
    "segmentation": (
        "segmentation", "semantic segmentation", "instance segmentation", "panoptic",
        "salient object", "camouflaged object",
    ),
    "robustness_uncertainty_ood": (
        "robust", "robustness", "uncertainty", "out-of-distribution", "ood",
        "adversarial", "certified", "calibration", "reliability", "worst-case",
    ),
    "domain_generalization_adaptation": (
        "domain adaptation", "domain generalization", "test-time adaptation",
        "source-free", "cross-domain", "distribution shift",
    ),
    "foundation_open_vocab_vlm": (
        "foundation model", "vision-language", "vision language", "open-vocabulary",
        "large vision", "clip", "prompt", "segment anything", "sam",
    ),
    "self_supervised_pretraining": (
        "self-supervised", "self supervised", "pretraining", "pre-training",
        "masked image", "contrastive learning", "representation learning",
    ),
    "low_light_restoration_weather": (
        "low-light", "low light", "nighttime", "night-time", "dehazing", "deraining",
        "fog", "adverse weather", "image restoration", "enhancement",
    ),
    "efficient_deployment": (
        "efficient", "lightweight", "real-time", "real time", "edge device",
        "quantization", "pruning", "latency", "flops", "mobile",
    ),
    "synthetic_generation_world_models": (
        "synthetic data", "data generation", "diffusion", "world model", "simulation",
        "generative", "image-to-image", "image to image",
    ),
    "3d_robotics_autonomous": (
        "3d detection", "lidar", "autonomous driving", "robot", "embodied",
        "point cloud", "occupancy", "bev", "pose estimation",
    ),
    "medical_scientific_vision": (
        "medical image", "pathology", "ct", "mri", "ultrasound", "microscopy",
        "scientific imaging",
    ),
}

DATASET_PATTERNS = (
    "COCO", "ImageNet", "LVIS", "Objects365", "OpenImages", "Cityscapes", "ADE20K",
    "BDD100K", "nuScenes", "Waymo", "KITTI", "Argoverse", "MOT17", "MOT20",
    "LaSOT", "TrackingNet", "GOT-10k", "DOTA", "DIOR", "xView", "VisDrone",
    "KAIST", "LLVIP", "M3FD", "FLIR", "DroneVehicle", "VTUAV", "RGBT234",
    "LasHeR", "MFNet", "PST900", "NYUDv2", "SUN RGB-D", "SemanticKITTI",
    "LoveDA", "iSAID", "SpaceNet", "BigEarthNet", "SEN12MS", "Hyperion",
    "ACDC", "Dark Zurich", "NightOwls", "ExDark", "LOL", "SICE",
)

METRIC_PATTERNS = (
    "mAP", "AP50", "AP75", "AP", "IoU", "mIoU", "F1", "accuracy", "AUC",
    "HOTA", "MOTA", "IDF1", "RMSE", "MAE", "PSNR", "SSIM", "FPS", "latency",
)

SECTION_HEADINGS = {
    "abstract": (r"\babstract\b",),
    "introduction": (r"\b1\.?\s+introduction\b", r"\bintroduction\b"),
    "related_work": (r"\brelated work\b", r"\bbackground\b"),
    "method": (r"\bmethod(?:ology)?\b", r"\bapproach\b", r"\bproposed method\b"),
    "experiments": (r"\bexperiments?\b", r"\bexperimental results?\b", r"\bevaluation\b"),
    "limitations": (r"\blimitations?\b", r"\bdiscussion\b"),
    "conclusion": (r"\bconclusions?\b",),
    "references": (r"\breferences\b",),
}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
SPACE = re.compile(r"\s+")
URL_RE = re.compile(r"https?://[^\s\]\[)>(]+")
NUMBER_RESULT_RE = re.compile(r"(?:\b\d+(?:\.\d+)?\s*%|\b\d+\.\d+\b)")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalized_title_from_path(path: Path) -> str:
    folder = path.parent.name
    folder = re.sub(r"^\d+_", "", folder)
    return folder.replace("_", " ").strip()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sentences(text: str, max_len: int = 600) -> list[str]:
    compact = SPACE.sub(" ", text).strip()
    out: list[str] = []
    for s in SENTENCE_SPLIT.split(compact):
        s = s.strip(" \n\t•-")
        if 35 <= len(s) <= max_len:
            out.append(s)
    return out


def find_section_positions(text: str) -> list[tuple[int, str]]:
    lower = text.lower()
    positions: list[tuple[int, str]] = []
    for name, pats in SECTION_HEADINGS.items():
        best = None
        for pat in pats:
            for m in re.finditer(pat, lower, flags=re.I):
                pos = m.start()
                line_start = lower.rfind("\n", 0, pos) + 1
                line_end = lower.find("\n", pos)
                if line_end == -1:
                    line_end = min(len(lower), pos + 120)
                line = lower[line_start:line_end].strip()
                if len(line) <= 100:
                    best = pos
                    break
            if best is not None:
                break
        if best is not None:
            positions.append((best, name))
    # Keep the first plausible occurrence per section and sort.
    positions = sorted(set(positions))
    return positions


def split_sections(text: str) -> dict[str, str]:
    pos = find_section_positions(text)
    if not pos:
        return {"full": text}
    sections: dict[str, str] = {}
    for i, (start, name) in enumerate(pos):
        end = pos[i + 1][0] if i + 1 < len(pos) else len(text)
        if name not in sections and end > start:
            sections[name] = text[start:end].strip()
    if pos[0][0] > 0:
        sections["front_matter"] = text[:pos[0][0]].strip()
    return sections


def pick_evidence(section_text: str, keywords: Sequence[str], limit: int = 3,
                  require_number: bool = False) -> list[str]:
    scored: list[tuple[float, str]] = []
    for idx, sent in enumerate(sentences(section_text)):
        low = sent.lower()
        score = sum(1.0 for kw in keywords if kw in low)
        if require_number and NUMBER_RESULT_RE.search(sent):
            score += 1.5
        if "we " in low or "our " in low:
            score += 0.2
        score -= idx * 0.0005
        if score > 0:
            scored.append((score, sent))
    scored.sort(key=lambda x: (-x[0], len(x[1])))
    result: list[str] = []
    seen = set()
    for _, sent in scored:
        key = re.sub(r"\W+", " ", sent.lower())[:160]
        if key not in seen:
            seen.add(key)
            result.append(sent)
        if len(result) >= limit:
            break
    return result


def theme_scores(title: str, text: str) -> dict[str, int]:
    hay = (title + "\n" + text[:30000]).lower()
    return {name: sum(hay.count(kw) for kw in kws) for name, kws in THEMES.items()}


def extract_datasets(text: str) -> list[str]:
    found = []
    for name in DATASET_PATTERNS:
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])", text, flags=re.I):
            found.append(name)
    # Add likely dataset names around the word dataset, conservatively.
    for m in re.finditer(r"\b([A-Z][A-Za-z0-9+\-]{2,20})\s+(?:dataset|benchmark)\b", text):
        token = m.group(1)
        if token.lower() not in {"the", "our", "this", "new", "large", "public"}:
            found.append(token)
    return sorted(set(found), key=str.lower)[:30]


def extract_metrics(text: str) -> list[str]:
    return [m for m in METRIC_PATTERNS if re.search(rf"\b{re.escape(m)}\b", text, flags=re.I)]


def extract_urls(text: str) -> list[str]:
    urls = []
    for u in URL_RE.findall(text):
        u = u.rstrip(".,;")
        if any(x in u.lower() for x in ("github.com", "gitlab.com", "huggingface.co", "project")):
            urls.append(u)
    return sorted(set(urls))[:12]


def compact_section(sections: dict[str, str], names: Sequence[str], max_chars: int = 14000) -> str:
    parts = [sections.get(n, "") for n in names if sections.get(n)]
    return "\n".join(parts)[:max_chars]


@dataclass
class PaperRecord:
    paper_id: str
    title: str
    year: int
    venue: str
    source_path: str
    fulltext_sha256: str
    word_count: int
    char_count: int
    section_names: list[str]
    section_coverage: float
    themes: list[str]
    theme_scores: dict[str, int]
    datasets: list[str]
    metrics: list[str]
    code_urls: list[str]
    research_problem: list[str]
    method_claims: list[str]
    contribution_claims: list[str]
    experiment_protocol: list[str]
    main_results: list[str]
    ablation_evidence: list[str]
    limitation_evidence: list[str]
    implementation_evidence: list[str]
    abstract_excerpt: str
    cluster_id: int = -1
    selection_score: float = 0.0
    selected_rank: int = -1


def build_record(path: Path) -> PaperRecord:
    raw = path.read_bytes()
    text = clean_text(raw.decode("utf-8", errors="replace"))
    title = normalized_title_from_path(path)
    sections = split_sections(text)
    abstract = sections.get("abstract") or sections.get("front_matter", "")
    intro = compact_section(sections, ("abstract", "introduction", "front_matter"), 16000)
    method = compact_section(sections, ("method", "introduction"), 18000)
    exp = compact_section(sections, ("experiments", "conclusion", "limitations"), 22000)
    all_for_evidence = text[:120000]
    ts = theme_scores(title, all_for_evidence)
    active = sorted([k for k, v in ts.items() if v > 0], key=lambda k: (-ts[k], k))
    present = set(sections)
    expected = {"abstract", "introduction", "method", "experiments", "conclusion"}
    coverage = len(present & expected) / len(expected)
    pid = path.parent.name.split("_", 1)[0]
    return PaperRecord(
        paper_id=f"cvpr2025_{pid}",
        title=title,
        year=2025,
        venue="CVPR",
        source_path=str(path),
        fulltext_sha256=sha256_bytes(raw),
        word_count=len(text.split()),
        char_count=len(text),
        section_names=sorted(sections),
        section_coverage=round(coverage, 3),
        themes=active,
        theme_scores=ts,
        datasets=extract_datasets(all_for_evidence),
        metrics=extract_metrics(all_for_evidence),
        code_urls=extract_urls(all_for_evidence),
        research_problem=pick_evidence(intro, (
            "challenge", "problem", "limitation", "fails", "difficult", "bottleneck", "gap",
        ), 3),
        method_claims=pick_evidence(abstract + "\n" + method, (
            "we propose", "we present", "we introduce", "we develop", "our method", "framework",
        ), 4),
        contribution_claims=pick_evidence(intro, (
            "contribution", "we make", "our contributions", "first", "novel",
        ), 4),
        experiment_protocol=pick_evidence(exp, (
            "dataset", "benchmark", "training", "evaluation", "implementation", "split",
        ), 4),
        main_results=pick_evidence(exp, (
            "outperform", "achieve", "improve", "state-of-the-art", "superior", "gain",
        ), 4, require_number=True),
        ablation_evidence=pick_evidence(exp, (
            "ablation", "component", "variant", "w/o", "without", "effect of",
        ), 4),
        limitation_evidence=pick_evidence(compact_section(sections, ("limitations", "conclusion", "experiments"), 14000), (
            "limitation", "future work", "fails", "failure", "however", "remaining", "restricted",
        ), 3),
        implementation_evidence=pick_evidence(exp, (
            "implementation", "gpu", "epoch", "batch size", "learning rate", "optimizer", "flops", "fps",
        ), 4),
        abstract_excerpt=SPACE.sub(" ", abstract)[:1800],
    )


def selection(records: list[PaperRecord]) -> list[PaperRecord]:
    docs = []
    for r in records:
        evidence = " ".join(r.research_problem + r.method_claims + r.main_results)
        docs.append(r.title + " " + r.abstract_excerpt + " " + evidence)
    vectorizer = TfidfVectorizer(
        stop_words="english", max_features=30000, ngram_range=(1, 2), min_df=2,
        sublinear_tf=True, norm="l2",
    )
    X = vectorizer.fit_transform(docs)
    n_clusters = min(50, max(20, len(records) // 45))
    model = MiniBatchKMeans(
        n_clusters=n_clusters, random_state=RANDOM_STATE, batch_size=512,
        n_init=10, max_iter=150,
    )
    labels = model.fit_predict(X)
    dist = model.transform(X)

    # Score balances direct relevance, section completeness, evidence density,
    # code/data reproducibility, and centrality within each thematic cluster.
    for i, r in enumerate(records):
        r.cluster_id = int(labels[i])
        relevance = sum(min(v, 8) for v in r.theme_scores.values())
        direct = (
            4 * r.theme_scores["rgb_ir_multispectral"]
            + 3 * r.theme_scores["multimodal_fusion_alignment"]
            + 3 * r.theme_scores["missing_degraded_modality"]
            + 2 * r.theme_scores["object_detection"]
            + 2 * r.theme_scores["small_aerial_remote"]
            + 2 * r.theme_scores["robustness_uncertainty_ood"]
            + r.theme_scores["domain_generalization_adaptation"]
        )
        evidence_density = (
            len(r.method_claims) + len(r.main_results) + len(r.ablation_evidence)
            + len(r.experiment_protocol) + len(r.limitation_evidence)
        )
        centrality = 1.0 / (1.0 + float(dist[i, labels[i]]))
        reproducibility = min(len(r.datasets), 4) + min(len(r.code_urls), 2) * 2
        r.selection_score = round(
            1.5 * direct + 0.35 * relevance + 6 * r.section_coverage
            + 0.8 * evidence_density + 0.8 * reproducibility + 4 * centrality,
            4,
        )

    by_cluster: dict[int, list[PaperRecord]] = defaultdict(list)
    for r in records:
        by_cluster[r.cluster_id].append(r)
    for vals in by_cluster.values():
        vals.sort(key=lambda r: (-r.selection_score, r.title.lower()))

    selected: list[PaperRecord] = []
    selected_ids = set()
    # First guarantee broad cluster coverage.
    base_quota = TARGET_N // n_clusters
    remainder = TARGET_N % n_clusters
    cluster_order = sorted(by_cluster, key=lambda c: (-len(by_cluster[c]), c))
    for j, cid in enumerate(cluster_order):
        quota = base_quota + (1 if j < remainder else 0)
        for r in by_cluster[cid][:quota]:
            selected.append(r)
            selected_ids.add(r.paper_id)

    # Fill any shortage by global relevance.
    if len(selected) < TARGET_N:
        for r in sorted(records, key=lambda r: (-r.selection_score, r.title.lower())):
            if r.paper_id not in selected_ids:
                selected.append(r)
                selected_ids.add(r.paper_id)
            if len(selected) >= TARGET_N:
                break
    # Trim only if a tiny quota imbalance occurred.
    selected = sorted(selected, key=lambda r: (-r.selection_score, r.cluster_id, r.title.lower()))[:TARGET_N]
    for rank, r in enumerate(selected, 1):
        r.selected_rank = rank
    return selected


def write_outputs(records: list[PaperRecord], selected: list[PaperRecord]) -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "fulltext").mkdir(parents=True)
    (OUT / "evidence_chunks").mkdir(parents=True)

    selected_by_id = {r.paper_id: r for r in selected}
    fields = [
        "selected_rank", "paper_id", "title", "year", "venue", "word_count",
        "section_coverage", "cluster_id", "selection_score", "themes", "datasets",
        "metrics", "code_urls", "source_path", "fulltext_sha256",
    ]
    with (OUT / "registry.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in sorted(selected, key=lambda x: x.selected_rank):
            d = asdict(r)
            for k in ("themes", "datasets", "metrics", "code_urls"):
                d[k] = " | ".join(d[k])
            w.writerow({k: d[k] for k in fields})

    with (OUT / "paper_evidence.jsonl").open("w", encoding="utf-8") as f:
        for r in sorted(selected, key=lambda x: x.selected_rank):
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    # Split compact evidence into manageable chunks for downstream manual review.
    ordered = sorted(selected, key=lambda x: x.selected_rank)
    for start in range(0, len(ordered), 40):
        chunk = ordered[start:start + 40]
        with (OUT / "evidence_chunks" / f"chunk_{start // 40 + 1:02d}.jsonl").open("w", encoding="utf-8") as f:
            for r in chunk:
                f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    checksum_lines = []
    for r in ordered:
        src = Path(r.source_path)
        dst = OUT / "fulltext" / f"{r.paper_id}.txt"
        shutil.copy2(src, dst)
        checksum_lines.append(f"{r.fulltext_sha256}  fulltext/{dst.name}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    # Theme and cluster counts.
    theme_counts = Counter()
    dataset_counts = Counter()
    cluster_counts = Counter()
    for r in selected:
        theme_counts.update(r.themes)
        dataset_counts.update(r.datasets)
        cluster_counts[r.cluster_id] += 1

    summary = {
        "corpus_total_fulltexts": len(records),
        "selected_fulltexts": len(selected),
        "target": TARGET_N,
        "venue": "CVPR",
        "year": 2025,
        "machine_assisted_fulltext_audit": True,
        "human_close_reading_claimed": False,
        "word_count_total": sum(r.word_count for r in selected),
        "word_count_median": statistics.median(r.word_count for r in selected),
        "word_count_min": min(r.word_count for r in selected),
        "word_count_max": max(r.word_count for r in selected),
        "mean_section_coverage": round(statistics.mean(r.section_coverage for r in selected), 4),
        "papers_with_method_evidence": sum(bool(r.method_claims) for r in selected),
        "papers_with_result_evidence": sum(bool(r.main_results) for r in selected),
        "papers_with_ablation_evidence": sum(bool(r.ablation_evidence) for r in selected),
        "papers_with_limitations_evidence": sum(bool(r.limitation_evidence) for r in selected),
        "papers_with_code_urls": sum(bool(r.code_urls) for r in selected),
        "theme_counts": dict(theme_counts.most_common()),
        "top_datasets": dict(dataset_counts.most_common(50)),
        "cluster_counts": dict(sorted(cluster_counts.items())),
    }
    (OUT / "audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    direct = [
        r for r in selected
        if r.theme_scores["rgb_ir_multispectral"] > 0
        or r.theme_scores["missing_degraded_modality"] > 0
        or (
            r.theme_scores["multimodal_fusion_alignment"] > 1
            and r.theme_scores["object_detection"] > 0
        )
        or (
            r.theme_scores["small_aerial_remote"] > 0
            and r.theme_scores["object_detection"] > 0
        )
        or (
            r.theme_scores["robustness_uncertainty_ood"] > 0
            and r.theme_scores["object_detection"] > 0
        )
    ]
    direct.sort(key=lambda r: (-r.selection_score, r.title.lower()))
    with (OUT / "direct_conflict_subset.jsonl").open("w", encoding="utf-8") as f:
        for r in direct:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    report = [
        "# CVPR 2025 1000-paper full-text audit",
        "",
        f"- Source corpus full texts found: **{len(records)}**",
        f"- Selected and copied full texts: **{len(selected)}**",
        f"- Total selected word count: **{summary['word_count_total']:,}**",
        f"- Median words per paper: **{summary['word_count_median']:,}**",
        f"- Mean canonical-section coverage: **{summary['mean_section_coverage']:.3f}**",
        f"- Direct conflict subset size: **{len(direct)}**",
        "",
        "## Integrity statement",
        "",
        "Every selected item is a complete CVPR 2025 paper converted from PDF to text. ",
        "The pipeline reads the full text, records SHA-256, parses major sections, and ",
        "extracts evidence for problem, method, experiments, results, ablations, ",
        "implementation, limitations, datasets and code. This is a machine-assisted ",
        "full-text audit. It is not represented as 1000 papers of human line-by-line ",
        "close reading. Core papers must still receive manual second-pass verification.",
        "",
        "## Theme counts",
        "",
    ]
    for k, v in theme_counts.most_common():
        report.append(f"- {k}: {v}")
    report += ["", "## Top datasets", ""]
    for k, v in dataset_counts.most_common(30):
        report.append(f"- {k}: {v}")
    (OUT / "FULLTEXT_AUDIT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> int:
    if not ROOT.exists():
        print(f"ERROR: corpus root does not exist: {ROOT}", file=sys.stderr)
        return 2
    paths = sorted(ROOT.rglob("*.txt"))
    if len(paths) < TARGET_N:
        print(f"ERROR: only {len(paths)} full texts found, need {TARGET_N}", file=sys.stderr)
        return 3
    records: list[PaperRecord] = []
    failures = []
    for i, path in enumerate(paths, 1):
        try:
            records.append(build_record(path))
        except Exception as exc:
            failures.append({"path": str(path), "error": repr(exc)})
        if i % 250 == 0:
            print(f"parsed {i}/{len(paths)}")
    selected = selection(records)
    if len(selected) != TARGET_N:
        raise RuntimeError(f"selected {len(selected)} not {TARGET_N}")
    write_outputs(records, selected)
    (OUT / "parse_failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "source_texts": len(paths), "parsed": len(records), "failures": len(failures),
        "selected": len(selected), "output": str(OUT),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
