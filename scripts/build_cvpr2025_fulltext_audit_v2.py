#!/usr/bin/env python3
"""Quality-controlled CVPR 2025 full-text audit.

This wrapper reuses the section/evidence parser from v1, fixes phrase matching,
filters malformed/short conversions, enforces topical coverage quotas, and
uses semantic clustering only after quality and relevance checks.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

import build_cvpr2025_fulltext_audit as base

base.OUT = Path(os.environ.get("AUDIT_OUT", "artifacts/cvpr1000_audit_v2"))
base.TARGET_N = int(os.environ.get("TARGET_N", "1000"))

# Quotas overlap; they are minimum coverage targets, not disjoint buckets.
THEME_QUOTAS = {
    "rgb_ir_multispectral": 45,
    "missing_degraded_modality": 12,
    "object_detection": 220,
    "small_aerial_remote": 70,
    "robustness_uncertainty_ood": 140,
    "multimodal_fusion_alignment": 180,
    "low_light_restoration_weather": 70,
    "tracking_video": 90,
    "segmentation": 90,
    "domain_generalization_adaptation": 50,
    "efficient_deployment": 100,
    "foundation_open_vocab_vlm": 100,
    "3d_robotics_autonomous": 100,
    "self_supervised_pretraining": 80,
    "synthetic_generation_world_models": 60,
    "medical_scientific_vision": 40,
}

GENERIC_DATASET_TOKENS = {
    "open", "training", "comprehensive", "enhanced", "each", "our", "new",
    "public", "large", "real", "synthetic", "benchmark", "evaluation", "test",
    "validation", "image", "video", "medical", "multimodal", "multi-modal",
}


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    # Treat spaces, underscores and hyphens as interchangeable separators while
    # preventing short tokens such as CT, SAM and AP from matching substrings.
    parts = [re.escape(p) for p in re.split(r"[\s_-]+", phrase.strip()) if p]
    body = r"[\s_-]+".join(parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.I)


THEME_REGEX = {
    theme: [(kw, phrase_pattern(kw)) for kw in keywords]
    for theme, keywords in base.THEMES.items()
}


def exact_theme_scores(title: str, text: str) -> dict[str, int]:
    hay = title + "\n" + text[:50000]
    scores: dict[str, int] = {}
    for theme, entries in THEME_REGEX.items():
        count = 0
        for _, pattern in entries:
            count += len(pattern.findall(hay))
        scores[theme] = count
    return scores


def clean_datasets(text: str) -> list[str]:
    values = base.extract_datasets(text)
    return [v for v in values if v.lower() not in GENERIC_DATASET_TOKENS]


base.theme_scores = exact_theme_scores
base.extract_datasets = clean_datasets


def quality_ok(r: base.PaperRecord) -> bool:
    return (
        r.word_count >= 3000
        and r.section_coverage >= 0.6
        and bool(r.method_claims)
        and bool(r.experiment_protocol)
        and bool(r.main_results)
    )


def direct_score(r: base.PaperRecord) -> float:
    s = r.theme_scores
    return (
        5.0 * min(s["rgb_ir_multispectral"], 10)
        + 5.0 * min(s["missing_degraded_modality"], 8)
        + 3.5 * min(s["object_detection"], 12)
        + 3.0 * min(s["small_aerial_remote"], 10)
        + 2.5 * min(s["robustness_uncertainty_ood"], 12)
        + 2.0 * min(s["multimodal_fusion_alignment"], 12)
        + 1.5 * min(s["domain_generalization_adaptation"], 8)
        + 1.2 * min(s["low_light_restoration_weather"], 8)
        + 1.0 * min(s["efficient_deployment"], 8)
    )


def evidence_score(r: base.PaperRecord) -> float:
    return (
        7.0 * r.section_coverage
        + 0.8 * len(r.research_problem)
        + 1.0 * len(r.method_claims)
        + 0.8 * len(r.experiment_protocol)
        + 1.0 * len(r.main_results)
        + 0.8 * len(r.ablation_evidence)
        + 0.5 * len(r.limitation_evidence)
        + 0.6 * min(len(r.datasets), 5)
        + 1.5 * min(len(r.code_urls), 2)
        + min(r.word_count / 7000.0, 1.5)
    )


def semantic_clusters(records: list[base.PaperRecord], n_clusters: int = 45) -> np.ndarray:
    docs = [
        r.title + " " + r.abstract_excerpt + " "
        + " ".join(r.research_problem + r.method_claims + r.main_results)
        for r in records
    ]
    tfidf = TfidfVectorizer(
        stop_words="english", max_features=40000, ngram_range=(1, 2),
        min_df=2, max_df=0.92, sublinear_tf=True,
    ).fit_transform(docs)
    n_components = min(160, tfidf.shape[0] - 1, tfidf.shape[1] - 1)
    reduced = TruncatedSVD(n_components=n_components, random_state=base.RANDOM_STATE).fit_transform(tfidf)
    reduced = normalize(reduced)
    labels = MiniBatchKMeans(
        n_clusters=n_clusters, random_state=base.RANDOM_STATE,
        n_init=20, batch_size=256, max_iter=300,
    ).fit_predict(reduced)
    return labels


def selection(records: list[base.PaperRecord]) -> list[base.PaperRecord]:
    valid = [r for r in records if quality_ok(r)]
    if len(valid) < base.TARGET_N:
        raise RuntimeError(f"Only {len(valid)} quality-controlled papers for target {base.TARGET_N}")

    labels = semantic_clusters(valid)
    for r, label in zip(valid, labels):
        r.cluster_id = int(label)
        r.selection_score = round(direct_score(r) + evidence_score(r), 4)

    selected: list[base.PaperRecord] = []
    selected_ids: set[str] = set()

    # Priority order protects direct collision coverage first.
    for theme, quota in THEME_QUOTAS.items():
        candidates = [r for r in valid if r.theme_scores[theme] > 0]
        candidates.sort(key=lambda r: (-r.selection_score, r.title.lower()))
        current = sum(theme in r.themes for r in selected)
        for r in candidates:
            if current >= quota:
                break
            if r.paper_id not in selected_ids:
                selected.append(r)
                selected_ids.add(r.paper_id)
                current += 1

    # Round-robin fill across semantic clusters to prevent one crowded topic
    # from dominating the final 1000-paper set.
    by_cluster: dict[int, list[base.PaperRecord]] = defaultdict(list)
    for r in valid:
        if r.paper_id not in selected_ids:
            by_cluster[r.cluster_id].append(r)
    for group in by_cluster.values():
        group.sort(key=lambda r: (-r.selection_score, r.title.lower()))

    cluster_order = sorted(by_cluster, key=lambda c: (-len(by_cluster[c]), c))
    cursor = {c: 0 for c in cluster_order}
    while len(selected) < base.TARGET_N:
        progressed = False
        for c in cluster_order:
            i = cursor[c]
            if i < len(by_cluster[c]):
                r = by_cluster[c][i]
                cursor[c] += 1
                if r.paper_id not in selected_ids:
                    selected.append(r)
                    selected_ids.add(r.paper_id)
                    progressed = True
                    if len(selected) >= base.TARGET_N:
                        break
        if not progressed:
            break

    if len(selected) < base.TARGET_N:
        for r in sorted(valid, key=lambda x: (-x.selection_score, x.title.lower())):
            if r.paper_id not in selected_ids:
                selected.append(r)
                selected_ids.add(r.paper_id)
            if len(selected) >= base.TARGET_N:
                break

    selected = selected[:base.TARGET_N]
    for rank, r in enumerate(selected, 1):
        r.selected_rank = rank
    return selected


def main() -> int:
    root = base.ROOT
    if not root.exists():
        print(f"ERROR: corpus root does not exist: {root}", file=sys.stderr)
        return 2
    paths = sorted(root.rglob("*.txt"))
    records: list[base.PaperRecord] = []
    failures = []
    for i, path in enumerate(paths, 1):
        try:
            records.append(base.build_record(path))
        except Exception as exc:
            failures.append({"path": str(path), "error": repr(exc)})
        if i % 250 == 0:
            print(f"parsed {i}/{len(paths)}")
    selected = selection(records)
    base.write_outputs(records, selected)

    # Add v2-specific quality/coverage audit.
    out = base.OUT
    audit = {
        "source_fulltexts": len(paths),
        "parsed_fulltexts": len(records),
        "quality_eligible_fulltexts": sum(quality_ok(r) for r in records),
        "selected_fulltexts": len(selected),
        "selection_word_count_min": min(r.word_count for r in selected),
        "selection_word_count_median": float(np.median([r.word_count for r in selected])),
        "theme_quota_targets": THEME_QUOTAS,
        "theme_quota_achieved": {
            t: sum(r.theme_scores[t] > 0 for r in selected) for t in THEME_QUOTAS
        },
        "cluster_counts": dict(sorted(Counter(r.cluster_id for r in selected).items())),
        "parse_failures": len(failures),
        "integrity_label": "machine-assisted full-text audit with manual second-pass required for core claims",
    }
    (out / "quality_control_summary.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "parse_failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
