# Stage 3 Experiment Registry

Use a tab-separated registry file in the active report directory:

- default layout: `reports/stage3_experiment_registry.tsv`
- Chinese layered layout: `方法文档/stage3_experiment_registry.tsv`

Create it at the start of the first confirmed Stage 3 campaign. Do not create both locations unless the user explicitly asks for compatibility copies.

The registry is not a replacement for the report or the claim ledger. It is the machine-readable run ledger that keeps the keep-discard history explicit.

Use [review-and-claim-integrity.md](review-and-claim-integrity.md) when any run is influenced by automated review, human reviewer comments, novelty scores, or paper-score rubrics. The registry may reference those review signals, but review scores do not replace metrics, guardrails, leakage checks, or claim support.

## Required Columns

Use this header:

`run_order	campaign	run_id	parent_run_id	role	change_axis	change_summary	scope_version	status	decision	primary_metric	primary_value	guardrail_summary	artifacts	report_ref	notes`

## Column Meanings

1. `run_order`: simple chronological order for the run record, such as `1`, `2`, `3`, or `001`, `002`, `003`.
2. `campaign`: stable name for the current Stage 3 campaign.
3. `run_id`: unique run identifier.
4. `parent_run_id`: baseline or prior run this run extends; use `root` for the baseline.
5. `role`: `baseline` or `candidate`.
6. `change_axis`: the main axis touched in this run, such as labels, preprocessing, feature set, model, regularization, pruning, or validation.
7. `change_summary`: one-sentence description of what changed.
8. `scope_version`: concise fingerprint of the locked scope, such as `cohort-v2|label-fi_wave_hybrid|loso-v1|metric-qwk`.
9. `status`: execution state such as `completed`, `failed`, `invalid`, or `timed_out`.
10. `decision`: `keep`, `discard`, `blocked`, or `exploratory`.
11. `primary_metric`: primary metric name for the campaign.
12. `primary_value`: primary metric value for this run.
13. `guardrail_summary`: short summary of important guardrails such as calibration, monotonicity, subgroup behavior, leakage checks, or critical claim-ledger checks affected by the run.
14. `artifacts`: key output files for the run.
15. `report_ref`: report or log section that explains the run in human-readable form.
16. `notes`: free-text justification, failure reason, next action, or review-signal triage if a reviewer score or comment affected the run.

## Usage Rules

1. Add one row per run, including failed or invalid runs.
2. Record the baseline as the first row of each campaign.
3. Do not overwrite discarded or blocked runs just because a later run improved.
4. If the campaign-defining scope changes, start a new campaign name or a new `scope_version`.
5. Keep the registry append-only unless the previous entry is factually wrong.
6. Use the report to explain the reasoning and the registry to preserve the exact decision trail.
7. Do not record a run as `keep` solely because a review score improved.
8. If a run changes any reportable claim, update the claim ledger in the active report or paper audit ledger and reference that update from `report_ref` or `notes`.

## Suggested Conventions

Use simple values that survive repeated edits:

1. campaign names like `label-refinement-waveform` or `loso-model-search`,
2. run ids like `wave-0001`, `wave-0002`,
3. artifact lists separated by `;`,
4. report references as relative paths with section names when useful.
