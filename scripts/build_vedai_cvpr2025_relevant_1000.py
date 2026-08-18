#!/usr/bin/env python3
"""Select and audit 1,000 VEDAI/BandLattice-relevant CVPR 2025 full papers.

All 2,800+ CVPR 2025 papers are parsed in full. A paper is counted only when
it has >=3,000 words, adequate section coverage, and extractable method,
experiment and quantitative-result evidence. Selection is based on full-text
relevance to nine evidence families behind the 18 VEDAI decision questions.
No copyrighted full paper text is copied into the output; only hashes,
metadata and short evidence excerpts are retained.
"""
from __future__ import annotations

import csv, hashlib, json, os, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import build_cvpr2025_fulltext_audit as base
import build_cvpr2025_fulltext_audit_v2 as v2

ROOT = Path(os.environ.get('CVPR_TEXT_ROOT','external/CVPR2025_TXT/papers'))
OUT = Path(os.environ.get('AUDIT_OUT','artifacts/vedai_cvpr2025_relevant_1000'))
TARGET = int(os.environ.get('TARGET_N','1000'))

FAMILIES = {
 'rgbt_multispectral_detection': (
   'rgb-t','rgbt','visible thermal','visible infrared','infrared visible','thermal object detection',
   'multispectral object detection','multispectral detection','cross-spectrum','cross-spectral',
   'hyperspectral object detection','spectral-spatial','spectral spatial','infrared small target',
 ),
 'hyperspectral_band_learning': (
   'hyperspectral','spectral band','band selection','band embedding','wavelength','spectral response',
   'multispectral band','channel sampling','channel embedding','arbitrary channel','variable channel',
 ),
 'missing_modality_variable_channels': (
   'missing modality','missing modalities','incomplete modality','partial modality','modality dropout',
   'arbitrary modality','available modalities','missing view','variable channel','channel dropout',
   'modality-agnostic','modality agnostic','modality missing','missing sensor',
 ),
 'sensor_failure_robustness': (
   'sensor failure','sensor corruption','modality corruption','adverse sensor','robust fusion','reliable fusion',
   'worst-case','worst case','certified robustness','failure mode','degraded modality','uncertainty-aware',
   'uncertainty aware','out-of-distribution','distribution shift','robust perception',
 ),
 'aerial_oriented_small_detection': (
   'oriented object detection','rotated object detection','oriented bounding box','rotated bounding box',
   'aerial object detection','remote sensing object detection','small object detection','tiny object detection',
   'uav object detection','drone object detection','dense object detection','aerial imagery',
 ),
 'fusion_alignment_registration': (
   'multimodal fusion','multi-modal fusion','cross-modal fusion','feature fusion','sensor fusion',
   'cross-modal alignment','cross modal alignment','image registration','misaligned modalities',
   'weakly aligned','spatial alignment','modality interaction','fusion network',
 ),
 'domain_shift_tta_generalization': (
   'domain adaptation','domain generalization','test-time adaptation','test time adaptation','source-free',
   'cross-domain','distribution shift','cross-dataset','sensor shift','domain shift','generalization',
 ),
 'evaluation_statistics_calibration': (
   'calibration','expected calibration error','confidence interval','bootstrap','cross-validation',
   'cross validation','statistical significance','selective prediction','risk-coverage','risk coverage',
   'uncertainty estimation','robust evaluation','worst subgroup','data leakage','spatial leakage',
 ),
 'efficient_deployment_selection': (
   'efficient','lightweight','real-time','real time','latency','flops','sensor selection','modality selection',
   'dynamic modality','conditional computation','mixture of experts','edge deployment','budgeted inference',
 ),
}

QUOTAS = {
 'rgbt_multispectral_detection': 75,
 'hyperspectral_band_learning': 70,
 'missing_modality_variable_channels': 85,
 'sensor_failure_robustness': 110,
 'aerial_oriented_small_detection': 190,
 'fusion_alignment_registration': 180,
 'domain_shift_tta_generalization': 105,
 'evaluation_statistics_calibration': 70,
 'efficient_deployment_selection': 115,
}
assert sum(QUOTAS.values()) == 1000

QUESTIONS = [
 ('Q01_continue_or_stop','Should a four-band VEDAI BandLattice pilot continue or stop based on novelty, value and feasibility?'),
 ('Q02_channel_semantics','Are R G B and infrared defensible as spectral band elements rather than independent modalities or sensors?'),
 ('Q03_threat_realism','What real deployment failures correspond to whole spectral band deletion or unavailable channels?'),
 ('Q04_deletion_budget','Should training and main evaluation include zero one two or three deleted bands and single-band states?'),
 ('Q05_only_15_subsets','Can exhaustive evaluation of fifteen subsets support a robustness paper or only an engineering ablation?'),
 ('Q06_novelty_gap','What novelty remains beyond channel embeddings arbitrary channels missing modalities mixture of experts and More-vs-Fewer ranking?'),
 ('Q07_strong_baselines','Which strong baselines are required for variable channels missing modalities multispectral and oriented detection?'),
 ('Q08_capacity_control','How should parameters FLOPs training compute initialization and augmentation be controlled?'),
 ('Q09_problem_threshold','How should a problem-space gate use mAP AP50 AP75 class AP worst-subset regret and uncertainty?'),
 ('Q10_success_threshold','What effect sizes and noninferiority margins are credible on a small object detection dataset?'),
 ('Q11_small_data_statistics','How should seeds folds scenes bootstrap clusters and confidence intervals be used for small correlated aerial data?'),
 ('Q12_fold_mapping','How should ten official folds be mapped to train validation test nested cross validation and leakage-safe evaluation?'),
 ('Q13_resolution','Is one resolution sufficient for a fatal pilot and when is a second resolution useful?'),
 ('Q14_second_dataset','Is a second dataset required and which public dataset supports multispectral oriented detection?'),
 ('Q15_journal_level','What evidence is required for a strong remote sensing or computer vision journal submission?'),
 ('Q16_veto_defects','What fatal defects can invalidate the threat model data protocol novelty or conclusions?'),
 ('Q17_minimum_pilot','What is the minimum decisive pilot with models folds seeds metrics compute cap and stop rules?'),
 ('Q18_better_direction','If BandLattice stops what higher-value RGB-infrared problem can reuse VEDAI M3FD LLVIP or MMOT assets?'),
]

PHRASE = {fam:[re.compile(r'(?<![a-z0-9])'+r'[\s_-]+'.join(re.escape(x) for x in re.split(r'[\s_-]+',p))+r'(?![a-z0-9])',re.I) for p in ps] for fam,ps in FAMILIES.items()}

def scores(rec):
    text = rec.title+'\n'+rec.abstract_excerpt+'\n'+' '.join(rec.research_problem+rec.method_claims+rec.experiment_protocol+rec.main_results+rec.ablation_evidence+rec.limitation_evidence)
    full = rec.source_path.read_text(encoding='utf-8',errors='ignore')[:70000]
    hay = text+'\n'+full
    out={}
    for fam, pats in PHRASE.items():
        title_hits=sum(len(p.findall(rec.title)) for p in pats)
        ev_hits=sum(len(p.findall(text)) for p in pats)
        full_hits=sum(len(p.findall(full)) for p in pats)
        out[fam]=12*title_hits+4*ev_hits+min(full_hits,20)
    return out

def quality(rec):
    return rec.word_count>=3000 and rec.section_coverage>=0.6 and rec.method_claims and rec.experiment_protocol and rec.main_results

def select(records):
    valid=[]
    for r in records:
        if not quality(r): continue
        r.family_scores=scores(r)
        r.selection_score=sum(min(v,30) for v in r.family_scores.values())+6*r.section_coverage+len(r.ablation_evidence)+.5*len(r.limitation_evidence)
        valid.append(r)
    selected=[]; used=set(); counts=Counter()
    # strict disjoint family quotas, then fill any shortfall by cross-family relevance.
    for fam, quota in QUOTAS.items():
        pool=sorted(valid,key=lambda r:(r.family_scores[fam],r.selection_score,r.word_count),reverse=True)
        for r in pool:
            if counts[fam]>=quota: break
            if r.paper_id in used or r.family_scores[fam]<=0: continue
            r.primary_family=fam; selected.append(r); used.add(r.paper_id); counts[fam]+=1
    if len(selected)<TARGET:
        for r in sorted(valid,key=lambda r:(r.selection_score,max(r.family_scores.values()),r.word_count),reverse=True):
            if r.paper_id in used or max(r.family_scores.values())<=0: continue
            fam=max(r.family_scores,key=r.family_scores.get)
            r.primary_family=fam; selected.append(r); used.add(r.paper_id); counts[fam]+=1
            if len(selected)>=TARGET: break
    if len(selected)<TARGET:
        raise RuntimeError(f'Only {len(selected)} relevant quality full texts; need {TARGET}')
    selected=selected[:TARGET]
    for i,r in enumerate(selected,1): r.selected_rank=i
    return valid,selected,counts

def short(s,n=520):
    s=re.sub(r'\s+',' ',s or '').strip(); return s[:n]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted(ROOT.rglob('*.txt')); records=[]; failures=[]
    for i,p in enumerate(paths,1):
        try: records.append(base.build_record(p))
        except Exception as e: failures.append({'path':str(p),'error':repr(e)})
        if i%250==0: print('parsed',i,'/',len(paths))
    valid, selected, family_counts=select(records)
    rows=[]; notes={}
    for r in selected:
        row={
          'rank':r.selected_rank,'paper_id':r.paper_id,'title':r.title,'venue':'CVPR 2025','year':2025,
          'primary_family':r.primary_family,'word_count':r.word_count,'section_coverage':round(r.section_coverage,4),
          'fulltext_sha256':r.sha256,'datasets':' | '.join(r.datasets),'metrics':' | '.join(r.metrics),
          'code_urls':' | '.join(r.code_urls),'source_path':str(r.source_path),
          **{f'score_{k}':v for k,v in r.family_scores.items()},
        }
        rows.append(row)
        notes[r.paper_id]={
          'title':r.title,'primary_family':r.primary_family,'family_scores':r.family_scores,
          'research_problem':[short(x) for x in r.research_problem],
          'method_claims':[short(x) for x in r.method_claims],
          'experiment_protocol':[short(x) for x in r.experiment_protocol],
          'main_results':[short(x) for x in r.main_results],
          'ablation_evidence':[short(x) for x in r.ablation_evidence],
          'limitation_evidence':[short(x) for x in r.limitation_evidence],
        }
    with (OUT/'registry_1000.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (OUT/'structured_notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
    # Rank the 1,000 full-text evidence summaries for each of the 18 attached questions.
    docs=[]
    for r in selected:
        n=notes[r.paper_id]
        docs.append(r.title+' '+' '.join(n['research_problem']+n['method_claims']+n['experiment_protocol']+n['main_results']+n['ablation_evidence']+n['limitation_evidence']))
    vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),min_df=2,max_features=70000,sublinear_tf=True)
    X=vec.fit_transform(docs+[q for _,q in QUESTIONS]); sims=cosine_similarity(X[-len(QUESTIONS):],X[:-len(QUESTIONS)])
    erows=[]; top={}
    for qi,(qid,q) in enumerate(QUESTIONS):
        order=np.argsort(-sims[qi])[:50]; qlist=[]
        for rank,idx in enumerate(order,1):
            r=selected[int(idx)]; n=notes[r.paper_id]
            evidence=(n['method_claims']+n['experiment_protocol']+n['main_results']+n['ablation_evidence']+n['limitation_evidence'])
            item={'question_id':qid,'question':q,'evidence_rank':rank,'similarity':round(float(sims[qi,idx]),6),'paper_rank':r.selected_rank,'paper_id':r.paper_id,'title':r.title,'primary_family':r.primary_family,'evidence_excerpt':' || '.join(evidence[:3])}
            erows.append(item); qlist.append(item)
        top[qid]=qlist
    with (OUT/'question_evidence_matrix.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(erows[0])); w.writeheader(); w.writerows(erows)
    (OUT/'question_evidence_top50.json').write_text(json.dumps(top,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={
      'source_fulltexts':len(paths),'parsed_fulltexts':len(records),'quality_eligible_fulltexts':len(valid),
      'selected_fulltexts':len(selected),'unique_paper_ids':len({r.paper_id for r in selected}),
      'unique_fulltext_sha256':len({r.sha256 for r in selected}),'word_count_total':sum(r.word_count for r in selected),
      'word_count_min':min(r.word_count for r in selected),'word_count_median':statistics.median(r.word_count for r in selected),
      'family_quota_targets':QUOTAS,'family_selected_counts':dict(family_counts),'parse_failures':len(failures),
      'audit_scope':'CVPR 2025 full papers selected by full-text relevance to the 18 VEDAI/BandLattice decision questions',
      'integrity_label':'machine-assisted full-text structured audit; decision-critical papers require manual second pass',
    }
    (OUT/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'parse_failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),encoding='utf-8')
    readme=f'''# VEDAI/BandLattice 1000-paper relevance-controlled audit\n\n- Source: all parsed CVPR 2025 full papers ({len(paths)} files).\n- Counted papers: 1,000.\n- Each counted paper passed full-text length, section, method, experiment and quantitative-result gates.\n- Selection was performed on full-text evidence across nine decision families, not title-only search.\n- The output excludes full copyrighted paper text; it stores registry, hashes and short structured evidence.\n- This is a machine-assisted full-text audit, not a claim of human sentence-by-sentence close reading of all papers.\n'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    # integrity manifest
    manifest=[]
    for p in sorted(x for x in OUT.rglob('*') if x.is_file() and x.name!='SHA256SUMS.txt'):
        manifest.append(f'{sha(p)}  {p.relative_to(OUT).as_posix()}')
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__': main()
