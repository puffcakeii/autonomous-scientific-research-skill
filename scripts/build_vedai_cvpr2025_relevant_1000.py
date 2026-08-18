#!/usr/bin/env python3
"""Fast, relevance-controlled full-text audit for the 18 VEDAI decisions.

The program parses every CVPR 2025 paper text, applies full-paper quality gates,
selects 1,000 papers by full-text evidence across nine decision families, and
retains only metadata, hashes and short evidence excerpts.
"""
from __future__ import annotations
import csv, hashlib, json, os, re, statistics
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT=Path(os.environ.get('CVPR_TEXT_ROOT','external/CVPR2025_TXT/papers'))
OUT=Path(os.environ.get('AUDIT_OUT','artifacts/vedai_cvpr2025_relevant_1000'))
TARGET=int(os.environ.get('TARGET_N','1000'))

FAMILIES={
'rgbt_multispectral_detection':['rgb-t','rgbt','visible thermal','visible infrared','infrared visible','thermal object detection','multispectral object detection','multispectral detection','cross spectral','hyperspectral object detection','spectral spatial','infrared small target','thermal detection'],
'hyperspectral_band_learning':['hyperspectral','spectral band','band selection','band embedding','wavelength','spectral response','multispectral band','channel sampling','channel embedding','arbitrary channel','variable channel','spectral remote sensing'],
'missing_modality_variable_channels':['missing modality','missing modalities','incomplete modality','partial modality','modality dropout','arbitrary modality','available modalities','missing view','variable channel','channel dropout','modality agnostic','missing sensor','partial observation'],
'sensor_failure_robustness':['sensor failure','sensor corruption','modality corruption','adverse sensor','robust fusion','reliable fusion','worst case','certified robustness','failure mode','degraded modality','uncertainty aware','out of distribution','distribution shift','robust perception','corruption robustness'],
'aerial_oriented_small_detection':['oriented object detection','rotated object detection','oriented bounding box','rotated bounding box','aerial object detection','remote sensing object detection','small object detection','tiny object detection','uav object detection','drone object detection','dense object detection','aerial imagery','small objects'],
'fusion_alignment_registration':['multimodal fusion','multi modal fusion','cross modal fusion','feature fusion','sensor fusion','cross modal alignment','image registration','misaligned modalities','weakly aligned','spatial alignment','modality interaction','fusion network','feature alignment'],
'domain_shift_tta_generalization':['domain adaptation','domain generalization','test time adaptation','source free','cross domain','distribution shift','cross dataset','sensor shift','domain shift','generalization','out of domain'],
'evaluation_statistics_calibration':['calibration','expected calibration error','confidence interval','bootstrap','cross validation','statistical significance','selective prediction','risk coverage','uncertainty estimation','robust evaluation','worst subgroup','data leakage','spatial leakage','evaluation protocol'],
'efficient_deployment_selection':['efficient','lightweight','real time','latency','flops','sensor selection','modality selection','dynamic modality','conditional computation','mixture of experts','edge deployment','budgeted inference','parameter efficient'],
}
QUOTAS={'rgbt_multispectral_detection':60,'hyperspectral_band_learning':55,'missing_modality_variable_channels':80,'sensor_failure_robustness':115,'aerial_oriented_small_detection':195,'fusion_alignment_registration':185,'domain_shift_tta_generalization':115,'evaluation_statistics_calibration':80,'efficient_deployment_selection':115}
assert sum(QUOTAS.values())==1000
QUESTIONS=[
('Q01_continue_or_stop','Should a four-band VEDAI BandLattice pilot continue or stop based on novelty scientific value and feasibility?'),
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
('Q18_better_direction','If BandLattice stops what higher-value RGB infrared problem can reuse VEDAI M3FD LLVIP or MMOT assets?')]
DATASETS=['VEDAI','DroneVehicle','LLVIP','M3FD','KAIST','FLIR','CVC-14','RGBT-Tiny','MMOT','MODA','HOD3K','DOTA','DIOR','FAIR1M','xView','VisDrone','MFNet','PST900','MUSES','nuScenes','Waymo','KITTI','COCO','ImageNet']
METRICS=['mAP','AP50','AP75','APs','APm','APl','IoU','F1','precision','recall','ECE','NLL','AUROC','AUPR','FLOPs','FPS','latency','HOTA','IDF1','AssA']
HEADINGS={'abstract':['abstract'],'introduction':['introduction'],'method':['method','methodology','approach','framework','architecture'],'experiments':['experiment','evaluation','implementation details'],'results':['results','performance','comparison'],'ablation':['ablation','component analysis','sensitivity analysis'],'limitations':['limitation','future work','failure cases'],'conclusion':['conclusion'],'references':['references','bibliography']}
METHOD_RE=re.compile(r'\b(method|approach|framework|architecture|model|module|network|we propose|our method)\b',re.I)
EXP_RE=re.compile(r'\b(experiment|experimental|evaluation|dataset|benchmark|implementation details)\b',re.I)
RESULT_RE=re.compile(r'\b(result|performance|outperform|improv(?:e|es|ed|ement)|mAP|AP50|AP75|accuracy|IoU|F1|AUROC)\b',re.I)
NUMBER_RESULT_RE=re.compile(r'(?:\b\d+(?:\.\d+)?\s*%|\b(?:mAP|AP50|AP75|accuracy|IoU|F1|AUROC)\b.{0,80}\d)',re.I)


def norm(text): return re.sub(r'\s+',' ',text or '').strip()
def words(text): return re.findall(r"\b[\w'-]+\b",text)
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def title_from_path(path):
    s=re.sub(r'^\d+_','',path.parent.name).replace('_',' ')
    return norm(s)
def sentence_windows(text,terms,limit=5,width=650):
    low=text.lower(); hits=[]
    for t in terms:
        start=0
        while True:
            i=low.find(t.lower(),start)
            if i<0: break
            hits.append(i); start=i+len(t)
            if len(hits)>250: break
    out=[]
    for i in sorted(hits):
        if any(abs(i-j)<900 for j in [x[0] for x in out]): continue
        a=max(0,i-width//2); b=min(len(text),i+width//2)
        sn=norm(text[a:b])
        if len(sn)>120: out.append((i,sn))
        if len(out)>=limit: break
    return [s for _,s in out]
def find_urls(text):
    urls=re.findall(r'https?://[^\s<>\]\[)]+',text)
    return list(dict.fromkeys(u.rstrip('.,;') for u in urls if 'github.com' in u.lower()))[:10]
def parse(path):
    text=path.read_text(encoding='utf-8',errors='ignore').replace('\x00',' ')
    wc=len(words(text)); title=title_from_path(path); low=text.lower()
    flags={k:any(re.search(r'(?im)^\s*(?:\d+(?:\.\d+)*)?\s*'+re.escape(h)+r'\s*$',text) for h in hs) or any(h in low for h in hs) for k,hs in HEADINGS.items()}
    coverage=sum(flags.values())/len(flags)
    method=bool(METHOD_RE.search(text)); experiments=bool(EXP_RE.search(text)); results=bool(RESULT_RE.search(text) and NUMBER_RESULT_RE.search(text))
    fam={}
    for k,terms in FAMILIES.items():
        th=sum(low.count(t) for t in terms); title_hits=sum(title.lower().count(t) for t in terms)
        fam[k]=th+12*title_hits
    excerpts={k:sentence_windows(text,terms,3) for k,terms in FAMILIES.items() if fam[k]>0}
    general=sentence_windows(text,['we propose','our method','experiments','results','ablation','limitations','future work'],8)
    datasets=[d for d in DATASETS if re.search(r'(?<![A-Za-z0-9])'+re.escape(d)+r'(?![A-Za-z0-9])',text,re.I)]
    metrics=[m for m in METRICS if re.search(r'(?<![A-Za-z0-9])'+re.escape(m)+r'(?![A-Za-z0-9])',text,re.I)]
    return {'paper_id':path.parent.name.split('_',1)[0],'title':title,'path':str(path),'word_count':wc,'sha256':sha256(path),'flags':flags,'coverage':coverage,'method':method,'experiments':experiments,'results':results,'family_scores':fam,'excerpts':excerpts,'general_evidence':general,'datasets':datasets,'metrics':metrics,'code_urls':find_urls(text),'text_for_rank':text[:50000]}
def quality(r): return r['word_count']>=3000 and r['coverage']>=0.55 and r['method'] and r['experiments'] and r['results']
def select(records):
    valid=[]
    for r in records:
        if not quality(r): continue
        vals=r['family_scores']; r['selection_score']=sum(min(v,35) for v in vals.values())+8*r['coverage']+int(r['flags']['ablation'])+0.5*int(r['flags']['limitations'])
        valid.append(r)
    selected=[]; used=set(); counts=Counter()
    for fam,quota in QUOTAS.items():
        for r in sorted(valid,key=lambda x:(x['family_scores'][fam],x['selection_score'],x['word_count']),reverse=True):
            if counts[fam]>=quota: break
            if r['paper_id'] in used or r['family_scores'][fam]<=0: continue
            r['primary_family']=fam; selected.append(r); used.add(r['paper_id']); counts[fam]+=1
    if len(selected)<TARGET:
        for r in sorted(valid,key=lambda x:(x['selection_score'],max(x['family_scores'].values()),x['word_count']),reverse=True):
            if r['paper_id'] in used or max(r['family_scores'].values())<=0: continue
            fam=max(r['family_scores'],key=r['family_scores'].get); r['primary_family']=fam
            selected.append(r); used.add(r['paper_id']); counts[fam]+=1
            if len(selected)>=TARGET: break
    if len(selected)<TARGET: raise RuntimeError(f'Only {len(selected)} relevant quality papers; need {TARGET}')
    selected=selected[:TARGET]
    for i,r in enumerate(selected,1): r['rank']=i
    return valid,selected,counts

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths=sorted(ROOT.rglob('*.txt')); records=[]; failures=[]
    for i,p in enumerate(paths,1):
        try: records.append(parse(p))
        except Exception as e: failures.append({'path':str(p),'error':repr(e)})
        if i%400==0: print('parsed',i,'of',len(paths),flush=True)
    valid,selected,counts=select(records)
    rows=[]; notes={}
    for r in selected:
        row={'rank':r['rank'],'paper_id':r['paper_id'],'title':r['title'],'venue':'CVPR 2025','year':2025,'primary_family':r['primary_family'],'word_count':r['word_count'],'section_coverage':round(r['coverage'],4),'fulltext_sha256':r['sha256'],'datasets':' | '.join(r['datasets']),'metrics':' | '.join(r['metrics']),'code_urls':' | '.join(r['code_urls']),'source_path':r['path'],**{f'score_{k}':v for k,v in r['family_scores'].items()}}
        rows.append(row)
        notes[r['paper_id']]={'title':r['title'],'primary_family':r['primary_family'],'family_scores':r['family_scores'],'section_flags':r['flags'],'evidence_excerpts':r['excerpts'],'general_evidence':r['general_evidence'],'datasets':r['datasets'],'metrics':r['metrics']}
    with (OUT/'registry_1000.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (OUT/'structured_notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
    docs=[]
    for r in selected:
        n=notes[r['paper_id']]; ev=' '.join(s for arr in n['evidence_excerpts'].values() for s in arr)
        docs.append(r['title']+' '+ev+' '+' '.join(n['general_evidence'])+' '+r['text_for_rank'][:18000])
    vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),min_df=2,max_features=65000,sublinear_tf=True)
    X=vec.fit_transform(docs+[q for _,q in QUESTIONS]); sim=cosine_similarity(X[-18:],X[:-18])
    erows=[]; top={}
    for qi,(qid,q) in enumerate(QUESTIONS):
        items=[]
        for rank,idx in enumerate(np.argsort(-sim[qi])[:50],1):
            r=selected[int(idx)]; n=notes[r['paper_id']]
            ev=n['general_evidence'][:2]
            if n['evidence_excerpts'].get(r['primary_family']): ev=n['evidence_excerpts'][r['primary_family']][:2]+ev[:1]
            item={'question_id':qid,'question':q,'evidence_rank':rank,'similarity':round(float(sim[qi,idx]),6),'paper_rank':r['rank'],'paper_id':r['paper_id'],'title':r['title'],'primary_family':r['primary_family'],'evidence_excerpt':' || '.join(ev)}
            erows.append(item); items.append(item)
        top[qid]=items
    with (OUT/'question_evidence_matrix.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(erows[0])); w.writeheader(); w.writerows(erows)
    (OUT/'question_evidence_top50.json').write_text(json.dumps(top,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'source_fulltexts':len(paths),'parsed_fulltexts':len(records),'quality_eligible_fulltexts':len(valid),'selected_fulltexts':len(selected),'unique_paper_ids':len({r['paper_id'] for r in selected}),'unique_fulltext_sha256':len({r['sha256'] for r in selected}),'word_count_total':sum(r['word_count'] for r in selected),'word_count_min':min(r['word_count'] for r in selected),'word_count_median':statistics.median(r['word_count'] for r in selected),'family_quota_targets':QUOTAS,'family_selected_counts':dict(counts),'parse_failures':len(failures),'audit_scope':'All CVPR 2025 full papers were parsed; 1,000 were selected by full-text evidence for the 18 VEDAI/BandLattice decisions.','integrity_label':'Machine-assisted full-text structured audit; decision-critical collision papers receive a manual second pass.'}
    (OUT/'audit_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'parse_failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'README.md').write_text('# VEDAI/BandLattice relevance-controlled 1,000-paper audit\n\nEvery counted paper is a CVPR 2025 full paper that passed length, section, method, experiment and quantitative-result gates. Selection uses full-text evidence across nine decision families. No full copyrighted paper is redistributed. This is a machine-assisted full-text audit, not a claim of human sentence-by-sentence reading of all 1,000 papers.\n',encoding='utf-8')
    manifest=[]
    for p in sorted(x for x in OUT.rglob('*') if x.is_file() and x.name!='SHA256SUMS.txt'):
        manifest.append(f'{sha256(p)}  {p.relative_to(OUT).as_posix()}')
    (OUT/'SHA256SUMS.txt').write_text('\n'.join(manifest)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=='__main__': main()
