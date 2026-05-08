# Biomedical Research

## Literature Priority

Prioritize:

1. Seminal biomedical and clinical papers that define the disease mechanism, signal modality, assay, or endpoint.
2. Strong biomedical engineering, medical imaging, bioinformatics, and clinical venues aligned with the user's task.
3. Recent work from the last 5-10 years on translational performance, cohort diversity, external validation, and clinically meaningful endpoints.
4. Reporting standards, clinical guidelines, and dataset documentation when they affect interpretation.

## Intake Focus

Clarify:

1. Data type: waveform, imaging, omics, pathology, tabular clinical data, or multimodal combinations.
2. Label source, annotation quality, patient or subject counts, class imbalance, and site effects.
3. Intended use: screening, diagnosis, prognosis, treatment support, biomarker discovery, or mechanism inference.
4. Ethical, privacy, and clinical-risk constraints.

## Candidate Route Families

Typical Stage 1 routes:

1. Biomarker or feature route:
   - interpretable statistical or mechanistic markers tied to biology.
2. Classical predictive modeling route:
   - structured modeling on curated features or tabular risk factors.
3. End-to-end representation route:
   - deep models on raw signals, images, or multimodal data.
4. Multimodal fusion route:
   - combine clinical, imaging, signal, or omics evidence.
5. Translational validation route:
   - design around external validation, subgroup analysis, and deployment realism from the start.

## Refinement Heuristics

In Stage 2:

1. Favor clinically meaningful endpoints over surrogate metrics when possible.
2. Check whether reported gains survive external validation, subgroup analysis, and site shift.
3. Distinguish prediction from causal or mechanistic claims.
4. Treat data leakage, patient overlap, and temporal leakage as critical failure modes.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Split data by patient, site, session, or time where appropriate.
2. Report calibration, sensitivity, specificity, AUROC, AUPRC, and subgroup behavior when relevant.
3. Keep preprocessing and cohort inclusion criteria explicit.
4. If the task may influence real decisions, state that the output is a research result unless the user explicitly seeks regulated clinical deployment guidance.
