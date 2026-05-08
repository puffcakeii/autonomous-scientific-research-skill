# Materials Science

## Literature Priority

Prioritize:

1. Seminal theory and characterization papers for the material class and property of interest.
2. High-impact journals and strong society journals in materials, chemistry, physics, and energy relevant to the topic.
3. Recent work from the last 5-10 years on synthesis-property-performance links, mechanism studies, and reproducible characterization.
4. Standards, test protocols, and benchmark measurement methods when claims depend on them.

## Intake Focus

Clarify:

1. Material system, composition range, processing route, and target property.
2. Available data: experiments, microscopy, spectroscopy, electrochemistry, simulations, or databases.
3. Whether the goal is mechanism understanding, performance optimization, prediction, screening, or process control.
4. Reproducibility constraints such as sample count, batch variation, and measurement uncertainty.

## Candidate Route Families

Typical Stage 1 routes:

1. Mechanism-first route:
   - Build around physical interpretation, phase behavior, transport, kinetics, or defect chemistry.
2. Characterization-fusion route:
   - Combine multiple characterization modalities to explain structure-property relations.
3. Data-driven property prediction route:
   - Use descriptors or learned representations to predict target properties.
4. Inverse design or screening route:
   - Search composition or process space for improved performance.
5. Multiscale simulation route:
   - Connect atomistic, mesoscale, and continuum evidence when experiments alone are insufficient.

## Refinement Heuristics

In Stage 2:

1. Prefer mechanisms that remain identifiable under the user's available measurements.
2. Check whether reported gains depend on narrow datasets, cherry-picked compositions, or inconsistent test protocols.
3. Separate intrinsic material behavior from electrode, device, fixture, or environmental artifacts.
4. If AI is used, preserve physically meaningful descriptors or constraints when possible.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Track sample provenance, preprocessing, normalization, and unit consistency.
2. Use proper train/validation splits across batches, compositions, or fabrication runs to avoid leakage.
3. Compare against accepted baselines such as simple descriptors, known empirical rules, or standard process recipes.
4. Validate with uncertainty, repeatability, and if possible out-of-distribution compositions or process conditions.
