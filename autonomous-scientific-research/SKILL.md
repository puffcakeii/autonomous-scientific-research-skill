---
name: autonomous-scientific-research
description: Literature-driven research planning, candidate-route comparison, best-plan refinement, budgeted experiment-loop execution, debugging, validation, claim-ledger auditing, and review-score sanity control for a user-specified scientific or engineering direction. Use when the user wants a research copilot for topic review, state-of-the-art survey, classic-paper review, recent-paper review from the last 5-10 years, candidate-method comparison, method refinement, experiment design, pipeline implementation, controlled Stage 3 experiment management, baseline locking, keep-discard tracking, literature-grounded debugging, reviewer-feedback triage, or simulation and engineering-software validation tied to real data sources, application background, and research goals, especially across materials science, control systems, signal processing, biomedical research, mechanical engineering, and artificial intelligence.
---

# Autonomous Scientific Research

Use this skill to execute a literature-grounded research workflow from topic intake to validated implementation.

## Mandatory Python Environment And Compute Device

When this skill runs Python code, use the configured GPU Python interpreter for the project.

Recommended configuration:

- Set `AUTONOMOUS_RESEARCH_PYTHON` to the absolute path of the intended GPU-enabled Python interpreter.
- Windows example: `$env:AUTONOMOUS_RESEARCH_PYTHON="C:\Users\<you>\.conda\envs\GPU\python.exe"`
- Linux/macOS example: `export AUTONOMOUS_RESEARCH_PYTHON="$HOME/miniconda3/envs/GPU/bin/python"`

Do not use another Python interpreter, Conda environment, virtualenv, system Python, Windows Store alias, or project-local environment for this skill's Python execution unless the user explicitly updates the configured interpreter.

If `AUTONOMOUS_RESEARCH_PYTHON` is unset and Python execution is required, stop and ask the user to configure it before running code.

For machine learning, deep learning, model training, inference, feature learning, representation learning, reinforcement learning, or other learning tasks, prefer CUDA GPU execution when it is useful and available in this environment. CPU execution is allowed when the task is small, CPU-only by design, more stable on CPU, or does not materially benefit from GPU acceleration. Do not switch to another environment to get CPU or GPU behavior. If a task truly requires CUDA and CUDA is unavailable in this environment, stop and report the environment blocker instead of changing environments.

Read [references/workflow.md](references/workflow.md) at the start of each new research goal.
Read [references/evidence-rules.md](references/evidence-rules.md) before collecting papers or making factual claims.
Read [references/completion-discipline.md](references/completion-discipline.md) before any stage where the user has an explicit target metric, end condition, or optimization goal.
Read [references/review-and-claim-integrity.md](references/review-and-claim-integrity.md) before using automated review, LLM review, human reviewer comments, supervisor comments, novelty scores, paper-score rubrics, or any review score as part of research or writing decisions.
Read [references/deliverable-templates.md](references/deliverable-templates.md) when drafting step outputs.
Read [references/academic-writing.md](references/academic-writing.md) when drafting or revising a thesis, dissertation, paper, chapter, abstract, literature review, figure caption, table caption, or any other academic prose deliverable.
Read [references/domain-selection.md](references/domain-selection.md) after intake to choose the right domain branch.
Read [references/stage3-experiment-loop.md](references/stage3-experiment-loop.md) before any confirmed Stage 3 execution campaign.
Read [references/experiment-registry.md](references/experiment-registry.md) before creating or updating the Stage 3 experiment registry.
If the project does not yet have a Stage 3 registry, initialize it with `scripts/init_stage3_registry.py`.

## Hard Constraints

1. Treat the user's route-level requirements for the whole research workflow as binding scope constraints, not as soft preferences, optional priorities, or style hints.
2. This skill's workflow remains the governing process: user requirements must be enforced inside the stage order and confirmation gates, not used to bypass them.
3. If the user's route-level requirements are missing, incomplete, or ambiguous, stop and list what is missing before proposing methods, candidate routes, plans, code, experiments, figures, charts, or diagrams.
4. If no real data source, real dataset, or clearly defined real data acquisition route exists, stop after intake. Do not produce candidate routes, best plans, implementation plans, figures, charts, workflow diagrams, or other solution sketches.
5. Before the user confirms Stage 1 and Stage 2 in the chat, do not perform Stage 3 or Stage 4 work. In particular, do not run preprocessing, feature extraction, model training, validation, figure generation, report writing, or result packaging as if the route were accepted.
6. Before Stage 2 confirmation, limit work to non-destructive intake, data inventory, sample inspection, feasibility checks, and literature review. Do not create preservation copies, extra workspace folders, backups, or archive folders unless the user explicitly asks for them, and label any such copies as preparation rather than implementation.
7. If you prematurely implement, analyze, or generate results before the required confirmation gate, explicitly mark that branch as invalid exploratory work, do not present it as the requested deliverable, return to the last unmet confirmation gate, and wait for the user's decision.
8. For every stage after Stage 0, maintain a single current project file under the active report directory (`reports/` by default, or `方法文档/` under the Chinese layered layout) in addition to any active log directory. Do not let stage progress exist only in logs or code, and do not create backup or snapshot copies of the report unless the user explicitly asks for archival copies.
9. Every stage report and stage log must record an explicit chronological order for major steps, so the user can reconstruct what happened first, what changed later, and which outputs were regenerated. Avoid wall-clock timestamps unless the user explicitly requests them.
10. After Stage 2 is confirmed, if the user has set explicit target metrics for Stage 3 or Stage 4, do not pause the workflow just because the first implementation underperforms. Continue iterative debugging and correction until the target metrics are met, a hard blocker is verified, or the user explicitly pauses or redirects the work.
11. If the user explicitly permits pruning abnormal subjects, abnormal trials, or weakly informative subsets, you may remove them during Stage 3 only when the rule is stated in the report, the keep/drop decision is reproducible, and at least the user-required minimum sample scope is preserved.
12. During Stage 3, you may continue autonomously across multiple runs only while the campaign question, data scope, evaluation protocol, and editable surface remain fixed under the confirmed Stage 2 plan.
13. Before a Stage 3 experiment loop, lock the baseline, data version, label version, split protocol, primary metric, guardrail metrics, budget, editable surface, and keep-discard rule in the report or linked campaign note.
14. If labels, cohort scope, split protocol, validation protocol, or primary metrics change materially, start a new Stage 3 campaign and rerun the baseline instead of comparing against the previous loop as if nothing changed.
15. Every Stage 3 run must be recorded in the active Stage 3 experiment registry, with a keep, discard, blocked, or exploratory decision.
16. When the user explicitly asks to follow a reference repository's storage logic, mirror that layered layout instead of proliferating parallel folders. For research codebases in this workspace, prefer a root-level structure like `方法文档/`, `修复记录/`, `实验图表--结果/`, `results/`, `scripts/`, `src/`, plus domain-specific data folders such as `data_raw/`, `derived/`, `manifests/`, and `reference_inputs/` when needed.
17. Under that layered layout, human-readable stage reports belong in `方法文档/`; run logs, fix notes, and audit ledgers belong in `修复记录/`; publication-ready figures belong in `实验图表--结果/`; machine-readable tables and packaged deliverables belong in `results/`. Do not keep duplicate parallel roots such as both `reports/` and `方法文档/`, or both `figures/` and `实验图表--结果/`, unless the user explicitly requests compatibility copies.
18. When newer kept outputs supersede earlier exploratory iterations, consolidate the kept set and remove stale duplicate reports, logs, figures, and result tables after the retained outputs are stable and referenced. Do not retain old iteration clutter by default.
19. Before claiming any Stage 3 metric as valid, perform an explicit leakage and overfitting audit. At minimum check for label-informed sample pruning, test-set model or hyperparameter selection, test-subject transductive normalization or calibration, duplicated subject/session leakage, and train-test generalization gap.
20. Never use true evaluation labels to decide keep/drop, feature ranking, threshold selection, or cohort pruning inside the reported metric protocol. If such a rule is explored, mark it as exploratory and invalid for headline reporting.
21. Never tune model family, hyperparameters, calibration rules, or post-processing on the same held-out subjects later used for final reporting. Use nested selection, a separate validation split, or a lockbox cohort.
22. If a result depends on transductive subject-wise normalization, subject-wise percentile scaling, or test-time anchor calibration, label it clearly as transductive and do not present it as deployment-grade subject-independent generalization.
23. If a leakage or overfit audit invalidates a previously reported headline result, mark the old report and log as superseded, promote the audited result as the current reference, and keep the invalidated branch only as an explicitly labeled historical record if the user still wants it retained.
24. If the user explicitly authorizes subject pruning, trial pruning, or label-informed keep-drop screening, treat that branch as a disclosed `数据筛选/敏感性分析` or `data-selection sensitivity` branch. Record the rule, retained scope, affected sample counts, and reporting limits. Do not present it as an unbiased headline result unless the disclosure, protocol, and validation design support that claim.
25. Data selection never permits hidden sample removal, invented data, invented metrics, altered raw measurements, or false claims of unbiased population-level generalization. Unauthorized fabrication or undisclosed screening remains prohibited.
26. If the user defines Stage 4 as a fixed-data optimization phase, keep the official Stage 3 data version, cohort membership, keep-drop manifests, and label version locked, but do not require the model family to stay fixed unless the user says so.
27. Under that fixed-data Stage 4 mode, you may continue ablations, model replacement, calibration redesign, ensembling, threshold redesign, and robustness experiments inside the locked official Stage 3 dataset version in order to maximize the user's target metrics.
28. If the user sets an explicit Stage 4 metric goal such as `95%+`, treat Stage 4 as an optimization-plus-validation campaign on the locked official data version and continue iterating until the target is reached, a hard blocker is demonstrated, or the user redirects the work.
29. For any target-driven Stage 3 or Stage 4 campaign, maintain an explicit objective ledger in the active stage report with the end goal, acceptance test, current best audited result, remaining gap, tried branches, kept branch, discarded branches, allowed stop conditions, and next branch.
30. Do not treat a runnable baseline, one improved run, a report update, a figure, or a registry update as completion when the user's stated target metric or end condition remains unmet.
31. If the target remains unmet and at least one concrete next branch exists within the confirmed scope, continue iterating instead of ending with a generic progress summary.
32. A failed branch, flat branch, or disappointing metric is not a hard blocker by itself; record the result, keep or discard it explicitly, and pivot to the next justified branch.
33. Conclude a target-driven campaign only when the target is met and the required validation is complete, the user explicitly pauses or redirects, a mandatory confirmation gate is pending, a required external dependency is missing, or a hard blocker is proved with concrete evidence.
34. If a response must end while the target is still unmet, open that response by stating `Target not met` and then name the blocker, missing external input, or required user decision plainly.
35. When the deliverable is academic writing, bind every nontrivial claim to the verified artifact set or cited literature, and do not let fluent prose hide missing evidence.
36. When the deliverable is academic writing, do not promote planned, partial, or structural components to completed validated contributions.
37. When the deliverable is academic writing, avoid overclaiming novelty, superiority, significance, or completion status unless the evidence base explicitly supports it.
38. If the user asks to "lower AIGC," "humanize" text, or bypass AI detectors in an academic-writing task, do not optimize for detector evasion. Reframe the task as authentic revision grounded in evidence, disciplinary fit, and the user's real writing samples, and say so plainly.
39. Do not promise detector-score reductions or "undetectable" text, and do not fabricate typos, anecdotes, emotional reactions, or local details to simulate human authorship.
40. Do not import external community writing skills as direct truth or direct runtime dependencies; decompose them into routing roles, scan rules, rewrite rules, and academic guardrails inside this skill.
41. For `methods`, `results`, figure narration, and table narration, protect equations, metrics, figure references, data protocol, and limitation boundaries over stylistic smoothness.
42. For academic-writing revision, do not perform a whole-section rewrite until a risk scan identifies the high-risk paragraphs, unless the user explicitly requests a full-chapter rewrite.
43. If no real style anchor exists, default to restrained Chinese engineering thesis prose rather than inventing a personalized or conversational voice.
44. In Chinese academic authenticity revision, safe de-templating heuristics may include restoring explicit subjects where omission hurts clarity, reducing serial connectors such as `首先/其次/最后/综上所述`, cutting template openers, adjusting clause order, varying sentence length, and revising in paragraph-sized batches.
45. Keep unsafe detector-evasion requests separate from revision heuristics. Reject mechanical filler-word injection such as `的/了/到/过/会/有/能/把`, fake typos, fake emotion, fake anecdotes or lived experience, and promises of lower detector scores.
46. For thesis or manuscript polishing, do not let figure captions or table captions carry the main analytical burden. Put the purpose, evidence basis, and interpretation in the prose before the figure or table whenever the genre allows it.
47. For thesis or manuscript polishing, remove writer-side narration and revision-process traces such as `为了回答……这一问题`, `需要特别说明`, `需要注意`, `换言之`, `与旧稿相比`, or similar phrasing that sounds like the author is explaining how the paper was written.
48. For full-manuscript academic revision, after targeted edits regenerate the current deliverable artifact when one exists, then run a second-pass audit for banned phrase classes, repeated cadence, and repeated `本文` paragraphs before handoff.
49. When the academic deliverable is a thesis chapter, full thesis, or exported `docx/pdf`, record the audit keywords, scan outcome, and final artifact path in the current report or audit ledger instead of relying on memory.
50. Do not use a review score, novelty score, paper-score rubric, LLM reviewer grade, or supervisor-style rating as the sole objective or completion condition. Treat review signals as advisory diagnostics only.
51. For Stage 3, Stage 4, and academic writing deliverables, judge completion by claim validity, metric gates, guardrail metrics, leakage and overfitting audit status, reproducibility artifacts, and disclosed limitations before considering review scores.
52. If review score improvement conflicts with primary metrics, guardrails, leakage audits, or claim-evidence support, discard, downgrade, or mark the branch exploratory until the conflict is resolved.
53. Maintain a claim ledger for reportable scientific claims whenever results will be written into a thesis, paper, report, figure narration, or final result summary. Unsupported, pending, superseded, or invalidated claims must not be promoted as completed contributions.
54. When reviewer feedback is used, triage comments by severity: validity-critical, method-critical, evidence-critical, presentation-critical, style-preference, and non-actionable. Resolve validity, method, and evidence issues before optimizing tone or review score.

## Intake Gate

Before proposing methods, code, or experiments:

1. Extract the research direction, concrete problem, the user's route-level requirements for the whole workflow, target outputs, available data sources, application background, constraints, and success criteria.
2. If any of those inputs are missing and materially affect solution quality, say so and list the missing items before proceeding.
3. Treat the user's route-level requirements, real data, application scenario, and research objective as first-class constraints.
4. If there is no real data source, real dataset, or real data acquisition route, stop after intake and report the missing data requirement. Do not propose methods, routes, plans, code, experiments, figures, charts, or diagrams.
5. Match the response language to the user's language unless the user asks otherwise.

## Core Workflow

Follow the stage order in [references/workflow.md](references/workflow.md) and do not skip the confirmation gates.
Do not enter Stage 1 until the intake gate has captured both the user's route-level requirements and a real data source or real data acquisition route.

1. Stage 1: Review the relevant literature, especially seminal papers and high-quality papers from the last 5-10 years, then present 3-5 candidate research routes with tradeoffs and pause in the chat for user confirmation.
2. Stage 2: Expand the review around the confirmed route, including adjacent fields when useful, refine or correct the method, present one best detailed plan, and pause in the chat for user confirmation.
3. Stage 3: Implement the confirmed plan through controlled experiment campaigns: run a baseline first, search within a locked protocol, track keep-discard decisions, debug issues using theory and literature, maintain a claim ledger for reportable claims, and do not claim success until the full pipeline runs end to end and the stage acceptance target is satisfied or explicitly redefined by the user.
4. Stage 4: On the locked official Stage 3 data version, validate and further strengthen the finalist pipeline. Unless the user freezes the model, the model family may still change during Stage 4 while the official data version stays fixed. Use experiments, ablations, calibration, and robustness checks to push the official metrics toward the user's target, keep iterating while a justified next branch exists, and then validate the best kept Stage 4 variant through metric gates, guardrails, leakage/overfit audit, and claim-ledger checks.
5. Explicit confirmation means the user has replied in the chat to accept the route or best plan. Silence, implied intent, or prior implementation work does not satisfy the gate.

## Academic Writing Router

When the active deliverable is thesis writing, academic rewriting, language normalization, or authenticity revision, route the work through these four layers in order:

1. `base_style_router`: default to Chinese engineering thesis prose and absorb the formal, evidence-led style patterns associated with `nsfc-humanization`.
2. `pattern_scanner`: detect templated phrasing, repeated cadence, empty transitions, and broad unsupported framing using the role associated with `humanizer`.
3. `natural_rewriter`: revise only the flagged sentences or paragraphs using the role associated with `writing-humanize`; do not perform broad paraphrase unless the user explicitly asks for a full rewrite.
4. `paper_guardrail`: run section-specific academic checks using the role associated with `typst-paper`; this layer has veto power over stylistic smoothness.

For every academic-writing revision task, derive and lock these explicit control fields before drafting:

1. `writing_task_type`: `audit_only`, `targeted_rewrite`, `section_polish`, or `full_chapter_revision`.
2. `section_type`: `abstract`, `introduction`, `related_work`, `methods`, `results`, `conclusion`, or `mixed`.
3. `style_anchor_available`: whether real anchor material exists, such as past chapters, supervisor edits, accepted phrasing, or the user's own samples.
4. `risk_tolerance`: `conservative`, `balanced`, or `aggressive`.

Default routing rules:

1. If the user says `降AIGC`, `降检测`, `humanize`, or `改得更像人写`, reframe the request as authenticity revision rather than detector evasion.
2. For Chinese undergraduate theses and for `abstract`, `introduction`, `related_work`, or `conclusion`, use `base_style_router + pattern_scanner + natural_rewriter + paper_guardrail`.
3. For `methods`, `results`, figure narration, or table narration, prioritize `paper_guardrail`; allow `natural_rewriter` only on flagged high-risk sentences.
4. If `style_anchor_available` is false, keep the voice conservative and do not improvise a personalized tone.
5. Default `risk_tolerance` to `balanced`, but force it to `conservative` for `methods` and `results`.
6. Unless `writing_task_type` is `full_chapter_revision`, revise in paragraph-sized batches and re-check local fluency before moving to the next batch.

Default thesis-polish loop:

1. Scan the target chapter or manuscript first instead of rewriting immediately.
2. Classify findings into at least these buckets when applicable: `template opener`, `author aside`, `revision trace`, `figure narration gap`, `repeated cadence`, `repeated subject`, `overclaim`, and `evidence gap`.
3. Revise only the flagged paragraphs unless the user explicitly asks for a full-chapter rewrite.
4. If the manuscript has a generated artifact such as `docx`, `pdf`, or rendered Markdown preview source, rebuild it after the edits.
5. Re-scan the rebuilt artifact for banned phrase classes and repeated `本文` paragraphs before concluding that the polish pass is complete.

## Domain Routing

After the intake gate:

1. Use [references/domain-selection.md](references/domain-selection.md) to classify the task into one primary domain and, if needed, one secondary domain.
2. Load only the relevant domain reference files unless the problem is genuinely cross-domain.
3. For materials science, read [references/materials-science.md](references/materials-science.md).
4. For control or automation, read [references/control-systems.md](references/control-systems.md).
5. For signal processing or communications, read [references/signal-processing.md](references/signal-processing.md).
6. For biomedical or clinical-adjacent research, read [references/biomedical-research.md](references/biomedical-research.md).
7. For mechanical engineering and design/manufacturing tasks, read [references/mechanical-engineering.md](references/mechanical-engineering.md).
8. For artificial intelligence or machine learning research, read [references/artificial-intelligence.md](references/artificial-intelligence.md).
9. If multiple domains apply, state the primary domain, the supporting domain, and which validation standard dominates.
10. If the user asks for academic writing, keep the domain validation standard active inside the prose. For example, a control-systems thesis still needs control-oriented definitions, constraints, and validation language instead of generic essay language.

## Evidence And Integrity

1. Never invent papers, datasets, equations, experiments, parameters, results, or citations.
2. Separate verified facts, reasonable inferences, and unresolved assumptions.
3. If a claim, citation, or result cannot be verified, say so plainly.
4. Do not present a partial implementation, partial reproduction, or partial validation as complete.
5. Record approximations, substitutions, or guessed values explicitly.

## Software And Validation Handoff

1. Use domain-specific engineering software only when the user explicitly requests it or the workflow clearly requires software-specific artifacts or validation.
2. If validation needs MATLAB, Origin, or SOLIDWORKS, invoke the corresponding local skill and obey its planning and validation gates.
3. Treat tool warnings, failed exports, failed runs, or incomplete outputs as failed validation states.
4. This skill cannot override higher-priority system, developer, tool, or runtime permissions; treat it as the highest-priority research workflow only within those actual limits.

## Output Discipline

1. Keep citations attached to substantive factual claims.
2. For each stage, state the inputs, method, outputs, risks, and next decision.
3. Treat interaction as explicit confirmation in the chat, not as a UI-building task.
4. Keep the user in the loop at the mandatory confirmation points, then continue autonomously while the confirmed scope remains stable.
5. When blocked by missing route-level requirements or by the absence of a real data source, output only the missing-input notice and do not generate plans, figures, charts, diagrams, or workflow sketches.
6. During Stage 3 and Stage 4, update the single current stage report in the active report directory as the work progresses, not only at the end. The current label definition, preprocessing route, model variants, validation status, and known problems must remain visible there.
7. For Stage 3 and Stage 4, do not create timestamp-named subfolders, per-batch report snapshots, or backup report copies by default. Keep outputs under stable, human-readable names and update the current report in place. Create an archive or checkpoint folder only when the user explicitly requests it.
8. During Stage 3, keep the current campaign question, locked artifacts, baseline metrics, accepted variant, discarded ideas, and next search axis visible in the report and synchronized with the experiment registry.
9. If the project has adopted the Chinese layered layout by user request, interpret `reports/` in these rules as `方法文档/`, interpret `logs/` as `修复记录/`, and interpret `figures/` as `实验图表--结果/`. Do not create `方法文档/阶段快照/` or other timestamped snapshot folders unless the user explicitly requests archival snapshots.
10. During any target-driven Stage 3 or Stage 4 loop, each meaningful progress update must state the target, current best audited result, remaining gap, what was just tried, whether that branch is kept or discarded, and the next branch.
11. If the target is still unmet at handoff time, do not phrase the output as completed success; say `Target not met` and state exactly what is blocking further continuation.
12. For academic writing outputs, keep section purpose, claim-evidence mapping, and citation status visible while drafting, and keep unresolved placeholders explicitly marked instead of silently smoothing them away.
13. For academic-writing revision tasks, prefer claim-evidence auditing, de-templating, concision, paragraph restructuring, and style matching to real user samples over generic "humanizer" rewriting.
14. For academic-writing revision tasks, structure the output in this order unless the user explicitly requests a different format: risk scan, revised text, retained evidence boundaries, unresolved issues or needed anchor material.
15. For review-assisted research or writing outputs, report what the review signal changed and which gates actually passed: metric gate, guardrail gate, leakage/overfit audit, claim ledger, and critical reviewer comments.
