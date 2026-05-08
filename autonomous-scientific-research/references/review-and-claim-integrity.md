# Review And Claim Integrity

Use this reference whenever a workflow includes automated review, LLM review, human reviewer comments, supervisor comments, paper-score rubrics, novelty scores, acceptance scores, or any other qualitative or numeric review signal.

## Core Rule

A review score is advisory. It is never the sole objective, acceptance test, keep-discard rule, or completion condition for a scientific workflow.

The governing objective is whether the scientific claims are valid under the locked protocol:

1. The claim is supported by verified artifacts or cited literature.
2. The user-defined primary metric and guardrail metrics pass under the locked evaluation protocol.
3. The leakage, overfitting, and protocol-drift audit is clean.
4. The result is reproducible enough for the stated deliverable.
5. The remaining limitations are disclosed rather than hidden.

If a review score conflicts with these checks, the checks win.

## Review Signal Triage

Classify each review comment before acting:

1. `validity-critical`: leakage, invalid split, wrong metric, missing baseline, unsupported claim, data or label error, false novelty, unreproducible result.
2. `method-critical`: weak experimental design, missing ablation, missing robustness check, unsuitable baseline, unjustified model choice.
3. `evidence-critical`: missing citation, claim not tied to result artifact, unsupported comparison, incomplete limitation.
4. `presentation-critical`: unclear figure, table, section organization, or result narration that blocks interpretation.
5. `style-preference`: wording, flow, tone, or reviewer taste that does not change claim validity.
6. `non-actionable`: vague praise or vague criticism without a testable required change.

Act in this order: validity-critical, method-critical, evidence-critical, presentation-critical, style-preference. Do not chase style-preference items while validity-critical items remain unresolved.

## Score Interpretation Rules

1. A high review score does not prove that the method works.
2. A low review score does not prove that the method is invalid.
3. Do not tune model family, hyperparameters, data pruning, paper claims, or wording only to raise a review score.
4. Do not use a review score to choose between candidate runs unless the compared runs already share the same locked data scope, split protocol, primary metric, guardrails, and leakage audit status.
5. If a review score improves while primary metric, guardrails, leakage audit, or claim support worsens, treat the branch as discard or exploratory.
6. If metrics improve but review comments expose leakage, overfitting, unsupported claims, or hidden protocol drift, invalidate or downgrade the branch until fixed.
7. If metrics and claim checks pass but the review score is weak, treat it as a communication, framing, baseline-context, or limitation-writing problem unless the comments identify a real technical defect.

## Claim Ledger

Maintain a claim ledger for Stage 3, Stage 4, and academic writing deliverables whenever results will be reported as scientific claims.

Use a compact table in the active stage report or paper audit ledger. Required fields:

`claim_id	claim_text	claim_type	evidence_artifact_or_citation	metric_or_check	protocol_scope	status	limitations	next_action`

Recommended `claim_type` values:

1. `literature fact`
2. `method design`
3. `implementation result`
4. `performance comparison`
5. `ablation finding`
6. `robustness finding`
7. `limitation`
8. `future work`

Recommended `status` values:

1. `supported`
2. `partially_supported`
3. `unsupported`
4. `pending_validation`
5. `superseded`
6. `invalidated`

No paper, thesis, report, or result summary may promote an `unsupported`, `pending_validation`, `superseded`, or `invalidated` claim as a completed contribution.

## Acceptance Gate

For target-driven Stage 3 or Stage 4 work, the acceptance gate must include all applicable items:

1. User-defined primary metric target.
2. Guardrail metrics.
3. Leakage and overfitting audit.
4. Baseline comparison under the same locked protocol.
5. Claim ledger status.
6. Reproducibility artifacts.
7. Unresolved limitations.
8. Reviewer comments triaged by severity.

The workflow is complete only when the acceptance gate passes or when a valid stop condition from `completion-discipline.md` applies.

## Cross-Review Discipline

If using automated reviewers or cross-model review:

1. Reviewer agents may critique artifacts, code, reports, figures, and claim ledgers, but they do not define the final objective.
2. Reviewer prompts must ask for evidence-grounded findings, not only a score.
3. A reviewer score must be accompanied by actionable findings or it is non-actionable.
4. A revision may be re-reviewed only after the report records what changed.
5. A reviewer must not approve unsupported claims just because the prose is fluent.
6. Keep reviewer outputs in the active log or audit ledger when they materially affected a decision.

## Completion Wording

When handing off, say which gates passed:

1. `Metric gate`: passed, failed, or not applicable.
2. `Guardrail gate`: passed, failed, or pending.
3. `Leakage/overfit audit`: clean, failed, or pending.
4. `Claim ledger`: all supported, partial, or has unresolved claims.
5. `Review comments`: critical resolved, noncritical pending, or not used.

Do not say "review score improved, therefore complete." Say what the score helped reveal, then tie completion to evidence, metrics, audits, and claims.
