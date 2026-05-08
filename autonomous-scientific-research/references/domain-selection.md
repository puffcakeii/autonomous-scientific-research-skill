# Domain Selection

## Purpose

Select the minimum domain context needed for the user's research goal.

## Classification Rule

After intake, classify the request by:

1. The scientific object being studied.
2. The dominant method family.
3. The dominant evaluation environment.
4. The main deliverable: theory, algorithm, experiment, device, simulation, or translation to practice.

Pick one primary domain from the list below. Add one secondary domain only if it materially changes the literature search, implementation path, or validation design.

## Domain Mapping

Use these cues:

1. Materials science:
   - materials discovery, synthesis, microstructure, characterization, electrochemistry, catalysis, polymers, semiconductors, batteries, corrosion, surface engineering.
2. Control systems:
   - plant modeling, observers, estimators, state feedback, MPC, PID, adaptive control, robust control, trajectory tracking, stability proof, hardware-in-the-loop.
3. Signal processing:
   - denoising, spectral analysis, filtering, detection, estimation, communications, radar, array processing, inverse problems, time-frequency analysis.
4. Biomedical research:
   - biomedical signals, medical imaging, diagnostics, prognosis, intervention support, patient cohorts, assays, clinical endpoints, translational validation.
5. Mechanical engineering:
   - structures, mechanisms, kinematics, dynamics, tribology, thermal-fluid coupling, manufacturing, topology optimization, fatigue, digital twins.
6. Artificial intelligence:
   - representation learning, deep learning, multimodal learning, generative models, reinforcement learning, foundation models, benchmarking, alignment.

## Cross-Domain Rule

Use two domains when the user's problem combines:

1. AI plus a scientific or engineering field.
2. Signal processing plus biomedical data.
3. Control plus mechanical systems.
4. Materials plus AI-guided discovery.
5. Any case where the data modality and validation regime come from different fields.

In cross-domain cases:

1. Let the application field define the data and validation standard.
2. Let the method field define the candidate algorithm families.
3. Say explicitly which field governs the final success criteria.
