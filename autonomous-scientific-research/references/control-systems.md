# Control Systems

## Literature Priority

Prioritize:

1. Foundational control theory for stability, robustness, observability, controllability, and optimization.
2. Core venues such as Automatica, IEEE Transactions, IFAC publications, and strong domain-specific control venues.
3. Recent work from the last 5-10 years on learning-enhanced control, data-driven control, safe control, and real-time deployment if relevant.
4. Plant-specific literature for the user's system class: aerospace, robotics, power systems, process control, vehicles, or biomedical control.

## Intake Focus

Clarify:

1. Plant dynamics, operating regime, disturbances, constraints, and measurable states.
2. Whether the goal is regulation, tracking, estimation, fault tolerance, or optimal operation.
3. Solver, sampling time, actuator/sensor limits, and real-time constraints.
4. Whether validation must be analytical, simulated, hardware-in-the-loop, or experimental.

## Candidate Route Families

Typical Stage 1 routes:

1. Classical route:
   - PID, lead-lag, loop shaping, gain scheduling.
2. Model-based modern route:
   - state feedback, observers, LQR/LQG, MPC.
3. Robust route:
   - H-infinity, mu-synthesis, disturbance observers, sliding mode.
4. Adaptive or nonlinear route:
   - adaptive control, backstepping, feedback linearization, Lyapunov-based design.
5. Learning-augmented route:
   - model learning, policy refinement, safe RL only when the validation path is credible.

## Refinement Heuristics

In Stage 2:

1. Prefer the simplest controller that can satisfy the user's constraints and proof burden.
2. Separate plant-model uncertainty from controller-structure weakness.
3. Require explicit stability or feasibility arguments for any advanced method.
4. If learning is introduced, define safety envelopes, fallback logic, and comparison against strong model-based baselines.

## Implementation And Validation

During Stage 3 and Stage 4:

1. Keep units, sign conventions, and state definitions explicit.
2. Do not accept algebraic-loop, update, or simulation warnings as complete.
3. Validate nominal performance, robustness to parameter variation, disturbance rejection, and constraint handling.
4. If the task uses engineering software, follow the software-specific skill and keep the final model readable.
