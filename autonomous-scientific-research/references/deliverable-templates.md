# Deliverable Templates

Use these concise output skeletons and adapt them to the user's domain.

Global blocking rule:

1. If the user's route-level requirements are missing, or if no real data source, real dataset, or real data acquisition route exists, do not use the stage templates below.
2. In that blocked state, return only a missing-input notice that lists the missing route requirements or missing data-source items.
3. In that blocked state, do not generate candidate routes, plans, figures, charts, diagrams, or workflow sketches.

## Stage 1 Output

Include:

1. Problem framing tied to the user's research direction, data, background, and goal.
2. Short literature map:
   - classic papers,
   - recent high-level papers from the last 5-10 years,
   - what each cluster contributes.
3. Candidate routes table with 3-5 options.
4. Initial claim-risk notes: what each route would be able to claim only if later evidence supports it.
5. Recommendation summary and the exact route the user must confirm in the chat.

## Stage 2 Output

Include:

1. Confirmed route.
2. Expanded literature support from the target field and neighboring fields.
3. Best detailed plan:
   - theory,
   - pipeline,
   - data flow,
   - optimization or solution procedure,
   - metrics,
   - baselines,
   - ablations,
   - claim ledger and acceptance gates,
   - risks,
   - expected outputs.
4. Explicit assumptions and one clear confirmation question to answer in the chat.

## Stage 3 Output

Include:

1. Current campaign question and why this campaign exists.
2. Locked protocol for this campaign:
   - data scope or cohort,
   - label version,
   - split protocol,
   - primary metric,
   - guardrail metrics,
   - budget,
   - editable surface.
3. Baseline run and its metrics.
4. What was executed in this run.
5. What succeeded and what failed.
6. Evidence-backed diagnosis.
7. The exact modification made and the change axis it belongs to.
8. Claim-ledger update:
   - supported claims,
   - partially supported claims,
   - pending or invalidated claims,
   - evidence artifacts or citations.
9. Review-signal use, if any:
   - review comments triaged by severity,
   - why the score did or did not change the decision.
10. Registry summary:
   - kept runs,
   - discarded runs,
   - blocked or exploratory runs,
   - current best kept variant.
11. Current end-to-end status and next search axis.

## Stage 4 Output

Include:

1. Validation or simulation setup.
2. Tools and artifacts used.
3. The kept Stage 3 variant that entered validation.
4. Quantitative and qualitative results.
5. Comparison against goals and literature baselines.
6. Final acceptance gate:
   - metric gate,
   - guardrail gate,
   - leakage/overfit audit,
   - claim ledger,
   - critical reviewer comments if review was used.
7. Remaining gaps, limitations, and next iteration.
