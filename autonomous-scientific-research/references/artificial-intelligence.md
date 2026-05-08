# Artificial Intelligence

## Literature Priority

Prioritize:

1. Seminal papers that define the task family, benchmark, or architecture class.
2. Strong venues in machine learning, computer vision, NLP, multimodal learning, reinforcement learning, and trustworthy AI that match the task.
3. Recent work from the last 5-10 years on the state of the art, but anchor it against strong classic baselines instead of trend-chasing.
4. Official benchmark pages, model cards, and reference implementations when they materially affect reproducibility.

## Intake Focus

Clarify:

1. Task type: classification, regression, generation, control, retrieval, segmentation, reasoning, or multimodal fusion.
2. Data size, label quality, modality, privacy constraints, and compute budget.
3. Whether the goal is novelty, deployment performance, efficiency, interpretability, or robustness.
4. Whether the user needs a standalone AI method or an AI component embedded in another scientific domain.

## Candidate Route Families

Typical Stage 1 routes:

1. Strong baseline route:
   - simple, reproducible models with careful data curation and evaluation.
2. Architecture-focused route:
   - CNN, transformer, graph, sequence, or multimodal design based on the task structure.
3. Representation-learning route:
   - self-supervised, contrastive, transfer, or foundation-model adaptation.
4. Efficiency or deployment route:
   - distillation, pruning, quantization, low-rank adaptation, or compact architectures.
5. Hybrid route:
   - combine domain priors, symbolic rules, or physical models with learning.

## Refinement Heuristics

In Stage 2:

1. Compare against strong baselines before moving to complex architectures.
2. Check whether claimed improvements come from better data handling rather than real method gains.
3. Treat leakage, prompt contamination, benchmark overfitting, and distribution shift as first-order risks.
4. For scientific applications, let the application domain control the validation standard.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Fix data splits, seeds, metrics, and training protocols before tuning heavily.
2. Track ablations, error analysis, and compute cost.
3. Validate robustness, calibration, and out-of-distribution behavior when relevant.
4. If foundation models are used, state what is frozen, adapted, prompted, or fine-tuned and why.
