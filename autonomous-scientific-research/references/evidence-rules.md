# Evidence Rules

## Source Priority

Use this order unless the user explicitly asks otherwise:

1. Peer-reviewed journal papers and conference papers from respected venues in the target field.
2. Seminal papers and authoritative review papers that define the field.
3. Official documentation, standards, or benchmark leaderboards when they materially affect implementation.
4. Preprints only when they are necessary, clearly labeled, and not treated as equal to peer-reviewed evidence.

## Literature Coverage

For each new research goal:

1. Cover both classic foundations and the last 5-10 years of progress.
2. Use the shorter end of the window for very fast-moving fields and the longer end for more stable fields.
3. Prefer direct paper pages, publisher pages, DOI pages, conference proceedings, or official project pages.
4. If the user supplies seed papers, treat them as mandatory inputs and then expand outward.

## Claim Discipline

1. Cite the papers or sources behind substantive method claims, benchmark claims, or historical claims.
2. Distinguish clearly between:
   - source-backed fact,
   - model inference from the sources,
   - open uncertainty.
3. Do not cite papers you did not actually inspect.
4. Do not pad the bibliography with irrelevant papers.
5. If a citation is incomplete, state what is missing instead of guessing.
6. If a result will become a paper, thesis, report, figure narration, table narration, or final claim, track it in the claim ledger described in [review-and-claim-integrity.md](review-and-claim-integrity.md).
7. Do not let review scores, reviewer praise, or novelty ratings substitute for source-backed evidence or verified artifacts.

## Paper Selection Heuristics

Prefer papers that are:

1. Methodologically central to the user's problem.
2. Published in strong venues or by credible groups.
3. Reproducible enough to support implementation.
4. Close to the user's data type, scale, and application constraints.
5. Strong baselines or strong competitors for the user's intended route.

## Implementation Integrity

1. Do not fabricate dataset properties, parameter settings, simulation conditions, or reported results.
2. Do not present a design as literature-backed when the literature only loosely suggests it.
3. If an implementation detail is absent from the papers, mark the detail as an engineering choice or a proposed hypothesis.
4. If verification is not possible, say the result is unverified.
5. Do not infer, invent, or assume a real data source, real dataset, or real data acquisition route in order to unblock candidate routes or plans.
