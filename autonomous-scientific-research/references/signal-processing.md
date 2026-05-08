# Signal Processing

## Literature Priority

Prioritize:

1. Foundational texts and seminal papers for the relevant transform, estimator, detector, or communication model.
2. Strong venues in signal processing, communications, radar, imaging, and inverse problems.
3. Recent work from the last 5-10 years on deep signal models, self-supervised methods, model-based deep unfolding, and task-specific benchmarks when relevant.
4. Dataset and benchmark papers when performance claims depend on public evaluation protocols.

## Intake Focus

Clarify:

1. Signal modality: audio, vibration, radar, EEG, ECG, RF, images, hyperspectral, or sensor streams.
2. Sampling rate, bandwidth, noise sources, channel effects, and artifact structure.
3. Whether the goal is denoising, detection, estimation, classification, reconstruction, or compression.
4. Latency, computational budget, and deployment constraints.

## Candidate Route Families

Typical Stage 1 routes:

1. Classical estimation route:
   - filtering, spectral analysis, matched filtering, adaptive estimation.
2. Model-based inverse route:
   - sparse recovery, Bayesian estimation, optimization-based reconstruction.
3. Feature-engineering route:
   - handcrafted time, frequency, and time-frequency features plus standard classifiers.
4. Deep signal route:
   - CNN, transformer, sequence model, or unfolding approach tied to the signal structure.
5. Hybrid route:
   - combine physical priors or DSP blocks with learned components.

## Refinement Heuristics

In Stage 2:

1. Preserve signal-generation assumptions where they are physically meaningful.
2. Compare learned pipelines against strong non-deep baselines, not only weak baselines.
3. Check leakage risks across subjects, sessions, devices, or channels.
4. If a model ignores phase, temporal alignment, or sampling assumptions, explain why that is acceptable.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Track preprocessing exactly: filtering, windowing, normalization, augmentation, and segmentation.
2. Validate on realistic noise, drift, and domain shift conditions.
3. Report metrics suited to the task: SNR, RMSE, AUROC, F1, BER, PSNR, SSIM, or task-specific measures.
4. For communications or radar tasks, include channel or scene assumptions in the validation setup.
