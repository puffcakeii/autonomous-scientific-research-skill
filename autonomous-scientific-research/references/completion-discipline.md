# Completion Discipline

Use this reference whenever the user gives a target metric, explicit finish line, or asks for optimization, debugging, continued iteration, or Stage 3 or Stage 4 work to keep going.

If the target includes a review score, novelty score, paper-score rubric, LLM reviewer grade, or supervisor-style rating, read [review-and-claim-integrity.md](review-and-claim-integrity.md). Treat the score as advisory; it cannot replace claim validity, metric gates, guardrails, leakage audit, or reproducibility.

## Objective Ledger

Before substantial target-driven work, record these items in the active stage report:

- End goal
- Acceptance test
- Current best audited result
- Remaining gap
- Hard constraints
- Allowed freedoms
- Claim ledger status
- Leakage and overfitting audit status
- Review-comment triage status if review was used
- Tried branches
- Current kept branch
- Allowed stop conditions
- Next branch

## Non-Completion States

Treat these states as in progress, not done:

1. A baseline runs but the target is not met.
2. The pipeline is end to end but the target metric is still below requirement.
3. A report, figure, or table was generated but the research question is still unresolved.
4. A promising improvement exists but required leakage, robustness, or validation checks are incomplete.
5. A review score improved but validity-critical, method-critical, or evidence-critical review comments remain unresolved.
6. A claim planned for the paper, thesis, report, or final summary is still unsupported, pending validation, superseded, or invalidated.

## Required Iteration Behavior

1. When one branch fails, record why and pivot to the next justified branch.
2. When the result is flat, inspect the dominant failure mode and choose the next search axis deliberately instead of ending.
3. Keep or discard each branch explicitly in the report.
4. If you can name a concrete next step inside the confirmed scope, the campaign is still live.

## Valid Stop Conditions

1. The acceptance test is met and required validation is complete.
2. The user explicitly pauses, redirects, or narrows scope.
3. A mandatory confirmation gate requires the user's reply.
4. A required external dependency is missing and cannot be safely replaced.
5. A hard blocker is proved with concrete evidence.

The acceptance test is not met by review score alone. It must include the relevant metric gate, guardrail gate, leakage/overfit audit, claim-ledger status, and reproducibility artifacts.

## Hard Blocker Standard

1. The blocker is reproducible and specific.
2. The suspected cause was tested rather than guessed.
3. At least two materially different next branches were tried, or the remaining path clearly requires new external input, permissions, or a scope change.
4. The stage report states what was tried and why continuation is blocked.

## Required Handoff Wording

If the target remains unmet at the end of a message, open with `Target not met` and state the blocker, missing input, or required user decision before anything else. If only the review score improved, say so explicitly and name the unresolved metric, audit, claim, or validation gate.
