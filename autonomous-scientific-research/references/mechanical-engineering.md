# Mechanical Engineering

## Literature Priority

Prioritize:

1. Foundational mechanics, materials, heat transfer, fluid, manufacturing, or design literature relevant to the subsystem.
2. Strong mechanical, manufacturing, robotics, and tribology venues tied to the task.
3. Recent work from the last 5-10 years on digital twins, data-driven modeling, additive manufacturing, optimization, and advanced sensing when relevant.
4. Standards, design codes, and validated simulation practice when claims depend on safety or compliance.

## Intake Focus

Clarify:

1. The component, mechanism, or system boundary.
2. Loading conditions, duty cycle, operating environment, and failure modes.
3. Available data: CAD, test data, sensor logs, simulation outputs, manufacturing parameters.
4. Whether the goal is performance improvement, fault diagnosis, design optimization, life prediction, or control integration.

## Candidate Route Families

Typical Stage 1 routes:

1. First-principles route:
   - analytical or reduced-order modeling from mechanics and thermofluids.
2. High-fidelity simulation route:
   - FEA, CFD, multibody dynamics, or coupled simulation.
3. Experimental characterization route:
   - test rigs, modal analysis, fatigue testing, wear testing, or process experiments.
4. Design optimization route:
   - parameter optimization, topology optimization, surrogate-assisted design.
5. Data-enhanced route:
   - combine simulation, sensors, and learning models for prediction or digital twins.

## Refinement Heuristics

In Stage 2:

1. Match model fidelity to the user's available geometry, material data, and computation budget.
2. Check whether literature results depend on unrealistically clean boundary conditions.
3. Separate geometric, material, and operational uncertainties.
4. If learning models are used, preserve physical feasibility and manufacturability constraints.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Keep geometry version, material parameters, mesh assumptions, and boundary conditions explicit.
2. Compare simplified models against higher-fidelity or experimental baselines when possible.
3. Validate sensitivity to tolerances, loads, and environmental variation.
4. If CAD or engineering simulation software is used, save validation artifacts and note what was directly simulated versus inferred.
