# Research Workflow

Read [stage3-experiment-loop.md](stage3-experiment-loop.md) before starting any confirmed Stage 3 campaign.
Read [review-and-claim-integrity.md](review-and-claim-integrity.md) before using reviewer comments, review scores, novelty scores, or score rubrics to make research or writing decisions.

## Stage 0: Problem Framing

Before searching or proposing methods:

1. Identify the research direction and the exact question to solve.
2. Identify the user's route-level requirements for the whole workflow and treat them as binding scope constraints, not as optional priorities.
3. Identify the user's data sources, data volume, labels, collection route, and data quality constraints.
4. Identify the application background, deployment environment, hardware or software constraints, and expected deliverables.
5. Identify the research goal: publishable novelty, engineering performance, interpretability, robustness, speed, cost, or a combination.
6. If the user already has baseline methods, mandatory papers, or preferred tools, treat them as required context.
7. If the user gives a review score, novelty score, target paper score, or reviewer rubric, record it as an advisory diagnostic and still define evidence-based acceptance gates.
8. If the route-level requirements are missing or unclear, stop and ask for them before proposing literature routes, plans, code, figures, charts, or diagrams.
9. If no real data source, real dataset, or clearly defined real data acquisition route exists, stop here. Do not produce candidate routes, best plans, implementation plans, figures, charts, diagrams, or other solution sketches.
10. You may inspect folder structure, file names, sample records, and obvious corruption non-destructively at this stage to understand feasibility. Do not start preprocessing, feature extraction, modeling, figure generation, or result reporting at Stage 0.
11. If the user explicitly asks for a safety copy of raw data, you may create that copy during Stage 0, but treat it as preservation only and not as permission to start implementation.

## Stage 1: Literature Review And Candidate Routes

Goal: build the problem map, then give 3-5 candidate routes.

Prerequisite: only proceed when Stage 0 captured binding route-level requirements and a real data source or real data acquisition route. If that prerequisite is not met, return only the missing-input notice.

Required actions:

1. Review seminal or classic papers that define the field, common assumptions, and standard baselines.
2. Review the last 5-10 years of recent progress, prioritizing top journals, top conferences, and highly credible primary sources.
3. Tie each paper back to the user's real problem rather than summarizing papers in isolation.
4. Extract the core problem formulation, data assumptions, main method, strengths, weaknesses, and fit to the user's constraints.
5. Produce 3-5 candidate routes, each with:
   - idea summary,
   - why it fits the user's setting,
   - likely data requirements,
   - expected strengths,
   - technical risks,
   - expected implementation difficulty,
   - estimated validation path,
   - likely reportable claims and the evidence needed to support them.
6. Stop in the chat and ask the user to confirm the route to pursue.
7. Do not create derived datasets, run batch preprocessing, train models, generate paper figures, or write result summaries during Stage 1.

Do not continue to Stage 2 until the user confirms a route in the chat.

## Stage 2: Best-Plan Refinement

Goal: turn the confirmed route into one detailed best plan.

Prerequisite: Stage 0 and Stage 1 must already satisfy the route-requirement gate and real-data gate.

Required actions:

1. Expand the literature review around the confirmed route and useful neighboring fields.
2. Check whether adjacent methods can fix known weaknesses in the confirmed route.
3. Revise the route if the expanded literature shows a better formulation.
4. Produce one best detailed plan with:
   - objective and hypothesis,
   - theoretical basis,
   - model or algorithm structure,
   - data pipeline,
   - preprocessing and feature choices,
   - training, optimization, or solution steps,
   - evaluation metrics,
   - baselines and ablations,
   - claim ledger structure and acceptance gates,
   - failure modes and mitigation,
   - expected outputs,
   - reproduction or validation path.
5. Clearly label any assumptions that still need confirmation.
6. Stop in the chat and ask the user to confirm before implementation.
7. Do not execute the planned pipeline, generate experimental results, or package a draft paper output during Stage 2.

## Stage 3: Implementation And Self-Check

Goal: run the method end to end and fix issues without fabricating progress.

Prerequisite: Stage 2 must have been confirmed in the chat, and the workflow must still be grounded in the real data source identified in Stage 0.

Required actions:

1. Define one Stage 3 campaign question at a time and lock the baseline, data scope, label version, split protocol, primary metric, guardrail metrics, budget, editable surface, and keep-discard rule before searching.
2. Initialize or update the active Stage 3 experiment registry before the first run of the campaign. Use `reports/stage3_experiment_registry.tsv` by default, or `方法文档/stage3_experiment_registry.tsv` when the project has adopted the Chinese layered layout.
3. Initialize or update the claim ledger for claims that may be reported from this campaign.
4. Run the baseline first under the locked protocol and record it explicitly as the comparison point for that campaign.
5. Implement the best plan in incremental, testable steps with one primary change axis per run unless the confirmed plan explicitly requires a coupled change.
6. Use the relevant theory and cited literature to explain design choices, debugging steps, and parameter changes.
7. After each major step, verify whether the step actually ran and produced the intended artifact.
8. Record every run as keep, discard, blocked, or exploratory and state why the decision was made.
9. If campaign-defining artifacts change materially, start a new campaign and rerun the baseline instead of mixing results into the previous loop.
10. Do not keep or discard a run solely because an automated reviewer or score rubric likes it. The decision must be grounded in the locked metric, guardrails, audit status, complexity, and claim support.
11. If errors or performance gaps appear, diagnose them from:
   - assumptions violated by the user's data,
   - implementation bugs,
   - metric misuse,
   - instability in optimization or simulation,
   - mismatch between literature conditions and the user's setting.
12. Debug by changing only what can be justified by the evidence or by explicit engineering reasoning.
13. Keep an implementation log of what changed, why it changed, what evidence supports the change, and whether the run was kept or discarded.
14. Do not claim completion until the pipeline runs end to end at the level the user requested, the current kept variant is clearly identified, the leakage/overfit audit is clean or explicitly bounded, and reportable claims are supported in the claim ledger.
15. If you discover that implementation began before the required Stage 1 or Stage 2 confirmation, stop, label the work as invalid exploratory output, and return to the missing confirmation gate instead of continuing forward.

## Stage 4: Fixed-Data Optimization, Validation, And Engineering Verification

Goal: on the locked official Stage 3 data version, further strengthen the best pipeline and then prove it is actually working against the stated goal.

Prerequisite: validation must still correspond to the real data source or real acquisition route established in Stage 0 unless the user explicitly updates that scope. By default, the official Stage 3 data version, keep-drop manifests, and label version remain fixed during Stage 4. The model does not have to remain fixed unless the user explicitly freezes it.

Required actions:

1. Keep the official Stage 3 data version fixed unless the user explicitly reopens the data scope.
2. Allow the model family, calibration rule, ensemble design, stage-threshold strategy, or other model-side components to change if the user wants Stage 4 to push the official metrics higher.
3. Choose optimization and validation methods that match the user's goal: stronger model search, ablation, robustness test, held-out evaluation, sensitivity study, or engineering simulation.
4. Record the exact Stage 4 setup: official data version, candidate models, split protocol, metrics, and outputs.
5. Compare all Stage 4 candidates against the locked official Stage 3 reference rather than silently mixing incomparable runs.
6. If the user has set an explicit target such as `95%+`, continue the Stage 4 loop on the fixed data version until the target is reached, a hard blocker is verified, or the user redirects the work.
7. Validate the best kept Stage 4 variant or a clearly labeled finalist set rather than silently promoting discarded or incomparable runs.
8. Compare observed results against the user's target and the literature baseline.
9. Run the final acceptance gate: primary metric, guardrail metrics, leakage/overfit audit, claim ledger, reproducibility artifacts, and critical reviewer comments if review was used.
10. If results are weak, loop back to Stage 2 or Stage 3 with a literature-grounded explanation.
11. Do not call the workflow complete until validation outputs exist, reportable claims are supported, and the gap to target is explained.
