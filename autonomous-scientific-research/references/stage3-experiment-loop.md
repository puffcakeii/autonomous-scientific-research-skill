# Stage 3 Experiment Loop

## Purpose

Use Stage 3 as a controlled autonomous experiment loop after the user has confirmed Stage 2.

This loop borrows the useful parts of small-scale autoresearch systems:

1. baseline first,
2. locked protocol,
3. bounded editable surface,
4. one main change axis per run,
5. keep-discard decisions after every run,
6. continuous iteration while the campaign stays within the confirmed scope.

Do not borrow the parts that would weaken scientific integrity:

1. do not skip literature or confirmation gates,
2. do not optimize a single score blindly, including review scores, novelty scores, paper-score rubrics, or LLM reviewer grades,
3. do not treat incomparable runs as evidence of progress,
4. do not let autonomous iteration rewrite the research question without user confirmation.

## Campaign Preconditions

Before the first run of a Stage 3 campaign, define:

1. one campaign question,
2. one baseline variant,
3. one locked data or cohort scope,
4. one locked label version,
5. one locked split protocol,
6. one primary metric and the guardrail metrics,
7. one editable surface,
8. one budget,
9. one keep-discard rule,
10. one registry file,
11. one claim ledger location for reportable claims.

The campaign note may live in the canonical Stage 3 report or in a dedicated campaign note linked from it.

## Lock The Protocol

Record the following before searching:

1. dataset or cohort version,
2. label definition version,
3. split protocol,
4. feature or preprocessing contract,
5. model family if it is fixed,
6. primary metric,
7. guardrail metrics,
8. wall-clock, epoch, or trial budget,
9. files or modules that may be edited,
10. files or modules that are locked,
11. review signals, if any, and how they may be used without overriding metrics, guardrails, or claim validity.

If labels, cohort membership, split protocol, or the primary metric change materially, start a new campaign and rerun the baseline.

## Baseline First

The first comparable run of a campaign must be the baseline.

Use the baseline to:

1. establish the true starting point,
2. confirm the pipeline still runs,
3. provide the reference for later keep-discard decisions,
4. detect whether a later change only looks better because the protocol drifted.

Never compare a candidate run against a stale baseline from an earlier campaign.

## Editable Surface

Keep the editable surface narrow.

Examples:

1. allow changes only in feature extraction and model configuration,
2. lock labels and data splits while testing model variants,
3. lock the model and only change label construction during a label-refinement campaign,
4. lock evaluation scripts unless Stage 2 explicitly approved evaluation redesign.

Narrow edit scopes make autonomous iteration more stable and make attribution of gains more believable.

## Loop Cycle

For each run:

1. choose the smallest evidence-backed next change,
2. state the hypothesis before running,
3. execute the run,
4. record commands, scripts, or artifacts,
5. record metrics and failure states,
6. update or check affected claim-ledger rows,
7. decide keep, discard, blocked, or exploratory,
8. update the report and registry,
9. choose the next search axis.

Default to one main change axis per run. Couple multiple axes only when the method is inherently joint or the smaller isolated run would be misleading.

## Keep-Discard Rules

Use these defaults unless the user specified a stricter rule:

1. Keep a run when it improves the primary metric under the locked protocol and does not violate guardrails.
2. Discard a run when it fails to improve meaningfully, breaks the locked protocol, or creates unjustified complexity.
3. Mark a run blocked when the run crashed, timed out, produced invalid artifacts, or triggered an unresolved warning that invalidates comparison.
4. Mark a run exploratory when it happened outside the confirmed scope or before the required gate.
5. Treat tiny gains with large complexity, fragility, or interpretability cost as discard or provisional keep, not automatic progress.
6. Never keep a run solely because a reviewer score improved.
7. Discard or mark exploratory any run whose review score improved while leakage risk, guardrail metrics, claim support, or protocol comparability worsened.
8. Treat reviewer comments as diagnostic input: validity-critical, method-critical, and evidence-critical comments can block keep decisions; style-preference comments cannot override clean metrics and supported claims by themselves.

## Search Heuristics

Prefer these search orders:

1. fix data correctness, label correctness, and leakage risks before model complexity,
2. exhaust simple and theory-backed changes before larger architecture jumps,
3. compare against strong classical baselines instead of only weak deep baselines,
4. use failure analysis to pick the next axis rather than random variation,
5. use claim-ledger gaps to choose missing ablations, robustness checks, or citation work,
6. stop widening the search when the campaign question has been answered or when the protocol no longer fits the current hypothesis.

For biomedical and signal-processing work, keep patient, subject, session, and device leakage checks inside the loop rather than only in the final validation.

## When To Reconfirm With The User

Pause and ask again when:

1. the campaign would change the confirmed research question,
2. the data scope or cohort membership would change beyond an already approved rule,
3. the primary success metric would change,
4. the interpretation of success would change,
5. the confirmed Stage 2 plan is invalidated by new evidence.

Do not ask again after every run when the campaign remains inside the locked protocol.

## Registry Discipline

Use [experiment-registry.md](experiment-registry.md) to keep the campaign machine-readable.

The report tells the story. The registry preserves exact run-level decisions.
