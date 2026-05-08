# Academic Writing Mode

Use this reference when the user asks for any of the following:

- Thesis or dissertation outline
- Full thesis draft or chapter draft
- Abstract, introduction, related work, conclusion, or response-to-reviewers text
- Academic rewriting, polishing, or language normalization
- Figure or table captions, result narration, or literature review synthesis
- Authenticity revision for text the user describes as `降低AIGC`, `降检测`, `humanize`, or `改得更像人写`

This mode governs academic writing produced from the research workflow. It does not relax the evidence rules, stage gates, or completion discipline in the parent skill.

When reviewer comments, supervisor comments, automated paper review, or review scores are used, also read [review-and-claim-integrity.md](review-and-claim-integrity.md). A review score may guide triage, but the writing must still be governed by claim-evidence support, metrics, leakage audit status, and disclosed limitations.

## Mode Router

Treat external public writing skills as pattern sources, not as runtime dependencies.
Route academic-writing work through these four layers in order:

1. `base_style_router`
   - Use formal Chinese engineering thesis prose by default.
   - Absorb the role associated with `nsfc-humanization`: restrained academic tone, sentence tightening, and anti-slogan discipline.
2. `pattern_scanner`
   - Absorb the role associated with `humanizer`: find templated phrasing, repeated cadence, and empty transitions.
3. `natural_rewriter`
   - Absorb the role associated with `writing-humanize`: rewrite only flagged sentences or paragraphs, not the whole section by default.
4. `paper_guardrail`
   - Absorb the role associated with `typst-paper`: keep genre constraints, section purpose, evidence boundaries, and thesis conventions intact.

Derive and lock these explicit control fields before drafting or revising:

1. `writing_task_type`: `audit_only`, `targeted_rewrite`, `section_polish`, or `full_chapter_revision`
2. `section_type`: `abstract`, `introduction`, `related_work`, `methods`, `results`, `conclusion`, or `mixed`
3. `style_anchor_available`: whether real anchor material exists, such as past chapters, supervisor edits, accepted phrasing, or the user's own samples
4. `risk_tolerance`: `conservative`, `balanced`, or `aggressive`

Default routing rules:

1. If the user says `降低AIGC`, `降检测`, `humanize`, or `改得更像人写`, convert the task into authenticity revision instead of detector gaming.
2. For Chinese undergraduate theses and for `abstract`, `introduction`, `related_work`, or `conclusion`, use `base_style_router + pattern_scanner + natural_rewriter + paper_guardrail`.
3. For `methods`, `results`, figure narration, or table narration, prioritize `paper_guardrail`; allow `natural_rewriter` only on flagged high-risk sentences.
4. If `style_anchor_available` is false, keep the voice conservative and do not invent a personalized tone.
5. Default `risk_tolerance` to `balanced`, but force it to `conservative` for `methods` and `results`.

## Writing-Mode Intake

Before drafting, lock these items:

1. Document type: undergraduate thesis, master's thesis, journal paper, conference paper, report, or review.
2. Language and style target: Chinese academic prose, English scientific prose, or bilingual abstract.
3. Institution or venue constraints if known: chapter order, citation style, word count, abstract length, originality rules, AI-use disclosure rules.
4. Verified artifact set: opening report, task book, code, figures, tables, result files, literature notes, and any already accepted terminology.
5. Claim boundary: what is already verified, what is a reasonable engineering inference, and what remains unverified.
6. Review inputs if any: reviewer comments, score rubric, supervisor feedback, response requirements, and which comments are validity-critical versus style-preference.
7. Writing control fields: `writing_task_type`, `section_type`, `style_anchor_available`, and `risk_tolerance`.

If institution or venue constraints are unknown, default to a marked draft for a Chinese engineering undergraduate thesis in Markdown and say that formatting may need local adjustment later.

## Hard Constraints

1. Never invent citations, result values, experimental settings, standards, equations, or completion status.
2. Never write a stronger claim than the verified evidence supports.
3. If a claim cannot be supported by the locked artifact set, either remove it, mark it as pending, or recast it as a limitation or future-work item.
4. Do not silently convert a planned capability into a completed capability.
5. Do not silently convert an idealized control input into an implemented actuator allocation layer if the evidence is only `delta + Mz`.
6. Do not use promotional, emotional, or advertising language.
7. Do not use absolute or overclaiming verbs such as `proved`, `fully solved`, `completely eliminated`, `perfectly matched`, `best`, `state-of-the-art`, `novel`, `first`, or `optimal` unless the evidence base explicitly justifies them.
8. In Chinese thesis writing, avoid `显著` unless statistical significance was actually tested. Prefer direct quantified language or restrained alternatives.
9. Avoid vague praise words without data, such as `很好`, `优秀`, `理想`, `先进`, `强大`, `鲁棒性很强`, or `效果显著`, unless the sentence immediately gives the supporting metric or comparison basis.
10. Avoid colloquial expressions, rhetorical questions, internet slang, and conversational fillers.
11. Use first person sparingly. Default to objective formulations such as `本文建立了...`, `针对...设计了...`, `仿真结果表明...`.
12. Separate four categories clearly in the text:
    - Verified literature fact
    - Verified project result
    - Reasonable engineering inference
    - Limitation or future work
13. Every substantive results paragraph must point to a figure, table, result file, or cited source.
14. Every figure and table must be introduced in the text before or when it appears, and the text must explain why it matters instead of only saying `如图所示`.
15. Related work must be organized by problem, method family, or validation setting. Do not write a long one-paper-one-sentence list without synthesis.
16. When polishing text, preserve the technical meaning, equations, symbols, and claim strength. Do not make the language smoother by making the claim stronger.
17. If the school or venue has an AI-use disclosure rule, keep the draft compatible with that rule and do not hide unsupported machine-generated content behind false certainty.
18. Do not promise lower detector scores, detector compatibility, or `undetectable` writing.
19. Do not add fake typos, fake anecdotes, fake reviewer concerns, invented local details, or artificial emotional tone as a "humanization" tactic.
20. Do not weaken technical precision for the sake of sounding natural.
21. Do not delete data boundaries, limitation statements, uncertainty, or qualifier words just to make the prose sound smoother.
22. If style matching is requested, prefer a real user writing sample over an unspecified request to sound "more human."
23. Safe Chinese de-templating is allowed only when it preserves evidence and technical meaning: restore explicit subjects when omission hurts clarity, reduce serial connectors such as `首先/其次/最后/综上所述`, cut template openers, adjust clause order, vary sentence length, and revise in paragraph-sized batches.
24. Do not inject filler particles or function words such as `的/了/到/过/会/有/能/把` merely to perturb detector outputs.
25. Do not use writer-side or process-side narration in the thesis body, especially in `methods`, `results`, figure analysis, or conclusion. High-risk examples include `为了回答……这一问题`, `需要特别说明`, `需要注意`, `换言之`, `与旧稿相比`, `这里可以看到`, and similar phrasing that explains the writing process instead of presenting research.
26. In thesis figure or table writing, put the analytical prose before the figure or table whenever possible: explain why the figure is needed, what experiment, metric, result file, or literature it is based on, and what aspect it is intended to show. Do not leave the main explanation to the caption alone.
27. After a targeted thesis revision pass, rebuild the exported artifact if one exists, such as `docx`, `pdf`, or a generated Markdown deliverable, and run a second-pass tone audit before handoff.
28. When the user asks to continue checking whether the manuscript still contains unsuitable language, default to a full-manuscript tone audit rather than editing isolated sentences only.
29. Never revise a paper, thesis, abstract, response letter, or figure narration solely to raise a review score. Revisions must preserve or improve claim validity.
30. Do not let a high review score justify unsupported novelty, inflated contribution wording, hidden leakage risk, or missing limitations.
31. If reviewer feedback conflicts with verified artifacts, metrics, or leakage audit findings, preserve the evidence boundary and explain the conflict rather than smoothing it away.

## Chinese Thesis Base Style

This is the default style layer for Chinese engineering theses.
It absorbs the useful part of `nsfc-humanization` without depending on it.

Core style rules:

1. Prefer explicit object-condition-result sentences over generic importance statements.
2. Prefer restrained written Chinese over policy slogans, promotional language, and broad historical framing.
3. Name the object, variable, dataset, scenario, or mechanism early.
4. Replace abstract praise with concrete findings, conditions, or limitations.
5. Keep sentence rhythm natural, but not casual.
6. When a long sentence contains multiple actions, split by function rather than by punctuation alone.

Good sentence tendencies:

1. State the target system or task early.
2. Make the condition visible.
3. Tie every claim to evidence, mechanism, or boundary.
4. End paragraphs on a result, implication, or limitation rather than on a slogan.

## Detector-Agnostic Authentic Revision

Use this mode because AI detectors are unreliable enough that they should not be treated as a stable optimization target, and public university guidance also warns about false positives and bias against non-native English writers.

Therefore:

1. Optimize for authorial authenticity, evidence alignment, and discipline-appropriate style instead of detector scores.
2. Use the user's real notes, outlines, past chapters, reviewer comments, terminology lists, and accepted phrasing as anchor material whenever possible.
3. If the user has no real anchor material, say that the output can only be a generic draft or revision rather than a reliable voice match.
4. Treat public writing skills only as pattern-harvest inputs for revision smells, not as authorities on what academic prose should claim.

## Unsafe Detector-Evasion Requests

When a user asks for detector evasion rather than authentic revision, refuse the unsafe tactic and redirect to evidence-led revision.

Unsafe requests include:

1. Mechanical filler-word injection such as `的/了/到/过/会/有/能/把` merely to perturb detector outputs.
2. Fake typos, punctuation noise, or formatting noise added to simulate human drafting.
3. Fake emotion, fake anecdote, fake lived experience, or invented local detail.
4. Promises or optimization commitments about lower detector scores, detector compatibility, or `undetectable` writing.
5. Whole-chapter laundering whose stated purpose is detector evasion rather than accurate revision.

## Source Skill Mapping

Map external skill influence like this:

1. `nsfc-humanization`
   - Responsible for formal Chinese academic tone, sentence tightening, and anti-slogan discipline.
   - Not responsible for section-by-section guardrails or detector strategy.
2. `humanizer`
   - Responsible for detecting template smells and repeated phrasing.
   - Not responsible for final wording by itself.
3. `writing-humanize`
   - Responsible for sentence-level and paragraph-level natural rewrites on flagged text.
   - Not responsible for adding facts, expanding evidence, or changing claim strength.
4. `typst-paper`
   - Responsible for paper genre guardrails, section norms, and academic structure awareness.
   - Not responsible for template-smell scanning.

Prohibited imports:

1. Do not import `undetectable` or detector-evasion strategies.
2. Do not import fake typo insertion, fake emotion, fake anecdote, or fake lived experience tactics.
3. Do not import rules that trade away technical precision for informality.
4. Do not import rules that remove limitation boundaries, uncertainty, or qualifiers in order to sound smoother.

## Template-Smell Scanner

Use this module before any substantial rewrite.
Scan for these high-risk patterns:

1. Broad-era framing with no immediate link to the actual object or scenario.
2. Empty importance claims such as `具有重要意义` without naming for whom and under what condition.
3. Overuse of `本文`, `因此`, `综上`, `进一步`, `需要指出的是`, `总体来看`, or similar transitions.
4. Paragraphs where most sentences share the same opening pattern or cadence.
5. Abstract noun stacks that hide the actor and action.
6. Method summaries that stack multiple steps without exposing data, variables, or decisions.
7. Contribution sentences that sound global while the evidence is local.
8. Conclusion sentences that close with vague value statements rather than verified findings or limitations.
9. Subjectless clauses where the actor disappears and the action reads like a floating requirement.
10. Transition chains such as `首先/其次/最后/综上所述` that duplicate structure the paragraph already shows.
11. Template openers that delay the real object, condition, dataset, or scenario.

Chinese-specific smells:

1. `随着...发展`
2. `在此背景下`
3. `具有重要理论意义和工程价值`
4. `为后续研究提供参考`
5. `构建完整闭环`
6. `进一步说明了...`
7. `由此可见`
8. `综上所述`
9. `为了回答……这一问题`
10. `需要特别说明`
11. `需要注意`
12. `换言之`
13. `与旧稿相比`
14. `可以看到` or `可以看出` when they act as empty transitions rather than evidence-led analysis

Output from this scanner should classify issues into:

1. template opener
2. empty transition
3. generic method summary
4. abstract evaluation
5. repeated cadence
6. evidence gap
7. author aside
8. revision trace
9. figure narration gap

## Public Pattern Harvest For De-Templating

Public writing-humanizer skills and prompt libraries repeatedly try to remove the same weak patterns.
Use them as revision-smell checks, not as bypass tactics.

Common revision smells:

1. Broad-era framing and empty importance claims at the start of a paragraph or sentence.
2. Promotional adjectives such as `revolutionary`, `game-changing`, `remarkable`, `先进`, `优秀`, or `效果很好` without immediate support.
3. Vague attribution such as `some studies show` or `已有研究表明` when the source should be named or the sentence should be cut.
4. Mechanical transition chains such as `first/second/finally` or `首先/其次/最后` when the paragraph order already carries the logic.
5. Repetitive sentence cadence or repeated sentence openings across a paragraph.
6. Abstract noun stacks that hide the actor and action.
7. Paragraphs that summarize in generalities without concrete variables, scenarios, datasets, figures, or limitation conditions.
8. Over-clean paragraphs with no sentence-length variation or local emphasis.
9. Subjectless clauses such as `应构建...` or `需完善...` when the actor should be named.
10. Template openers and serial connectors that can be cut because the surrounding structure already carries the logic.

## Safe Chinese De-Templating Heuristics

Use these heuristics only when they preserve evidence, terms, and claim boundaries:

1. Restore an explicit subject when omission makes the actor, object, or responsibility unclear.
2. Reduce serial connectors such as `首先`, `其次`, `最后`, and `综上所述` when paragraph order or section structure already provides the logic.
3. Cut template openers and begin closer to the object, condition, dataset, mechanism, or result.
4. Reorder front and back clause structure when the meaning is preserved and the revised sentence exposes condition-action-result more directly.
5. Mix shorter and longer sentences so the paragraph keeps an academic rhythm without becoming conversational.
6. Revise in paragraph-sized batches, then re-read each batch for local fluency before moving on.

## Natural Rewrite Pack

This module absorbs the useful part of `writing-humanize`.
Its job is targeted rewriting, not free paraphrase.

Rewrite rules:

1. Rewrite only flagged high-risk sentences or paragraphs unless `writing_task_type` is `full_chapter_revision`.
2. Preserve metrics, citations, terms, equations, symbol meaning, dataset names, and section purpose.
3. Prefer changing sentence order, subject placement, and clause packaging over changing claims.
4. Split long stacked sentences when they mix background, method, result, and value judgment.
5. Replace generic evaluative wording with concrete objects, conditions, or outcomes.
6. Keep the final tone academic rather than conversational.
7. Work through the draft in paragraph-sized batches unless a whole-chapter pass is explicitly required.

Allowed operations:

1. Split long sentences
2. Move conditions earlier
3. Replace abstract nouns with subjects and verbs
4. Collapse redundant transitions
5. Convert parallel stacks into stepwise statements
6. Tighten endings so the paragraph closes on a result or boundary
7. Restore explicit subjects where omission hides the actor or action
8. Reduce serial connectors when the structure is already visible
9. Cut template openers and start closer to the technical object or condition
10. Adjust clause order to foreground condition, action, or result
11. Vary sentence length while keeping the paragraph academic

Disallowed operations:

1. Adding facts, examples, anecdotes, or citations
2. Changing numerical meaning or comparison direction
3. Converting tentative claims into strong claims
4. Deleting qualifiers such as `可能`, `在当前设置下`, `主要`, or `尚未`
5. Mechanically injecting filler particles or function words to perturb detector outputs
6. Blanket one-pass laundering of all sections before a risk scan identifies the high-risk parts

## Thesis Manuscript Audit Loop

Use this loop for thesis chapter polishing, full-manuscript revision, or `docx/pdf` thesis cleanup:

1. Lock the control fields first: `writing_task_type`, `section_type`, `style_anchor_available`, and `risk_tolerance`.
2. Run a risk scan on the whole target scope before rewriting. The scan should cover at least:
   - template openers
   - author-aside phrasing
   - revision-trace phrasing
   - repeated `本文` paragraphs
   - figure narration gaps
   - overclaiming or unsupported evaluative wording
3. Rewrite only the flagged paragraphs unless the user explicitly asks for a full rewrite.
4. Preserve equations, metrics, figure numbers, result values, protocol descriptions, and limitation boundaries.
5. Rebuild the manuscript artifact if the workflow uses a generated `docx`, `pdf`, or rendered output.
6. Re-scan the rebuilt artifact and do not conclude the pass until the high-risk phrase classes have been checked again.
7. Record the audit keywords, the scan result, and the final artifact path in the current report or audit ledger.

## Paper Guardrail

This module absorbs the useful part of `typst-paper`.
It protects section-specific academic behavior.

General guardrails:

1. Abstract, introduction, related work, methods, results, and conclusion must keep different rhetorical jobs.
2. Figure narration must identify object, metric, and interpretation.
3. Table narration must identify scope and comparison basis.
4. Conclusions must not exceed the verified evidence boundary.
5. Planned work must not be written as completed work.
6. Reviewer score improvement must not be treated as proof that a paper claim is valid.
7. Headline claims, abstract claims, contribution bullets, and conclusion claims must be traceable to the claim ledger or explicitly marked as literature-backed.

When section type is `methods`:

1. Protect equations, symbols, data protocol, and implementation logic.
2. Allow only local sentence cleanup unless the user explicitly asks for a larger rewrite.

When section type is `results`:

1. Protect numbers, metric names, dataset or scenario labels, comparison objects, and limitation boundaries.
2. Rewrite only interpretation language, not reported outcomes.

When section type is `abstract` or `conclusion`:

1. Remove over-generalized value claims.
2. Keep the boundary between what was built, what was verified, and what remains incomplete.

## Section-Level Writing Rules

### Abstract

Use a compact five-part structure:

1. Background and problem
2. Model and method
3. Validation setting
4. Key quantitative results
5. Main conclusion and limitation boundary if needed

Do not fill the abstract with literature review details.
Do not claim engineering deployment if the work is still simulation-only.

### Introduction

The introduction should usually do five jobs:

1. State the real engineering problem and why it matters
2. Explain the actual technical difficulty
3. Synthesize related work by route, not by chronology alone
4. Identify the gap the thesis actually addresses
5. State the thesis contributions and chapter arrangement

### Related Work Or Literature Review

Group the literature into 3-5 meaningful clusters.
For each cluster:

1. Summarize what the field already solved
2. State the remaining weakness
3. Explain how that weakness motivates the current thesis

### Methods

The methods section must define:

1. Assumptions and simplifications
2. Coordinate system and symbols
3. Model or algorithm structure
4. Data flow and training protocol
5. Parameters and their sources
6. Practical limitation of the current implementation boundary

Do not jump from formulas to conclusions without a sentence explaining the physical meaning.

### Results

The results section should be organized around research questions, not around screenshot order.
Each subsection should follow this order:

1. State the scenario
2. Point to the figure or table
3. State the quantitative outcome
4. Explain the mechanism
5. State the limitation if one exists

Additional thesis-result guardrails:

1. Do not open a results paragraph with writer-side framing such as `为了回答……这一问题`.
2. Do not describe the act of writing, revising, or comparing drafts inside the thesis body.
3. If a sentence only says `可以看出` or `由此可见`, make sure the specific figure, table, metric, or result file is explicitly named nearby.
4. If a figure analysis paragraph can stand without the figure number, it is probably too generic and should be tightened.

### Conclusion

The conclusion should not repeat the abstract verbatim.
It should contain:

1. What was built
2. What was verified
3. What the current evidence supports
4. What remains incomplete
5. What the next technical step is

## Output Contract

Unless the user explicitly requests another format, return academic-writing revision results in this order:

1. Risk scan
   - List the main issue types and the affected sentence or paragraph types.
2. Revised text
   - Provide only the revised portion requested by the user.
3. Retained evidence boundaries
   - State what was deliberately preserved, such as numbers, caveats, or section logic.
4. Unresolved issues
   - State any evidence gap, style-anchor gap, or section ambiguity that still remains.

For `audit_only`, omit the revised text and return the first, third, and fourth items only.

## Figure And Table Narration Rules

1. A figure caption must identify the scenario, variables, and comparison target.
2. A table caption must identify the metric family and scope.
3. In the正文, do not write only `如图 4-1 所示`. Before or when the figure appears, explain why the figure is presented, what result or evidence it is based on, and what aspect it is intended to reveal.
4. Do not let the caption replace the正文 analysis. Captions should identify the object; the analytical interpretation belongs in the prose.
5. Use one figure to support one primary claim where possible.
6. Keep the comparison axis consistent across grouped figures.
7. If a figure is only illustrative and not a headline result, do not let the main claim depend on it.
8. For thesis revision, prefer the sequence `purpose -> evidence basis -> 如图X所示 -> figure/table -> interpretation` whenever the layout allows it.

## Paragraph Recipe

For most engineering thesis paragraphs, use this order:

1. Topic sentence: what this paragraph is about
2. Evidence sentence: figure, table, equation, or citation
3. Interpretation sentence: why that evidence matters
4. Boundary sentence: condition, caveat, or transition

## Prompt Library

Use or adapt these prompt patterns when revising academic prose.
They are designed for authentic revision, not detector evasion.

### 1. Voice Calibration Prompt

Analyze the user's writing samples and extract:

1. preferred sentence length
2. typical transition habits
3. degree of directness
4. hedging style
5. preferred subject choices
6. tolerance for first-person usage

Then revise the target text to match that profile while preserving all technical content, citations, numbers, equations, and limitations.
Report the inferred style profile before rewriting.

### 2. Claim-Evidence Audit Prompt

Read the draft paragraph by paragraph.
For each substantive claim, label it as:

1. source-backed
2. project-verified
3. engineering inference
4. unsupported

Do not rewrite first.
Return a compact audit table, then propose only the revisions needed to align claims with evidence.

### 3. De-Templating Prompt

Identify sentences that sound formulaic because they rely on:

1. empty lead-ins
2. vague attribution
3. inflated significance claims
4. repeated cadence
5. abstract noun stacks
6. redundant transitions

Rewrite only those sentences.
Keep the surrounding structure, terminology, figures, and citation mapping intact.
After rewriting, list which pattern each changed sentence fixed.

### 4. Concision Prompt

Revise the text for concision.
Delete redundancy, collapse weak multi-word phrases into precise words, reduce unnecessary `to be` constructions, and remove introductory filler.
Do not shorten by deleting methods, caveats, or quantitative detail.

### 5. Register-Control Prompt

Rewrite the text for the target genre:

1. journal abstract
2. thesis introduction
3. methods section
4. results section
5. discussion
6. reviewer response

Keep the section-specific tone.
Do not make a methods section conversational.
Do not make a reviewer response defensive or theatrical.

### 6. Meaning-Preservation Prompt

Rewrite for fluency while preserving:

1. claims
2. scope
3. caveats
4. causality
5. statistical meaning
6. temporal order
7. terminology
8. citation anchors

Flag any sentence where a fluent rewrite would risk changing the technical meaning.

### 7. Chinese Academic Revision Prompt

请按“真实性修订”而不是“降检测”的原则处理下面这段中文学术文本：

1. 删除空泛套话和自明连接词；
2. 把抽象评价改成具体对象、变量、条件或结果；
3. 保留术语、数据、限定词和证据关系；
4. 让句式更自然，但不要口语化、营销化、网文化；
5. 不添加不存在的经历、情绪、案例或引文；
6. 如果某个判断缺证据，直接标出来，不要替我圆过去。

输出顺序：

1. 问题句清单；
2. 修订后的正文；
3. 仍缺证据的地方。

### 8. Reviewer Response Prompt

Rewrite the response letter to sound precise, respectful, and accountable.
Cut generic gratitude, avoid defensive repetition, and tie every reply to a concrete manuscript change, experiment, citation, or rationale.
If the response lacks a real manuscript action, flag it instead of decorating it.

### 9. Chinese Thesis De-Templating Prompt

Input requirements:

1. target section
2. original text
3. must-keep terms
4. citations or figure references if any

Must preserve:

1. all numbers and metrics
2. all citations and figure references
3. claim boundary

Do not modify:

1. equations
2. dataset names
3. comparison direction

Output order:

1. high-risk template patterns
2. revised text
3. retained boundaries

Applicable sections:

1. abstract
2. introduction
3. research goals
4. technical route
5. conclusion

### 10. Section-Safe Natural Rewrite Prompt

Input requirements:

1. target section
2. original paragraph
3. protected technical items

Must preserve:

1. metrics
2. terminology
3. equations or symbols
4. cited evidence

Do not modify:

1. result values
2. data protocol
3. figure or table meaning

Output order:

1. protected items
2. revised paragraph
3. residual risk

Applicable sections:

1. methods
2. results
3. figure explanation
4. table explanation

### 11. High-Risk Paragraph Audit Prompt

Input requirements:

1. full section text
2. section type

Must preserve:

1. paragraph order
2. current evidence mapping

Do not modify:

1. the text itself in the first pass

Output order:

1. paragraph risk ranking
2. issue labels
3. rewrite priority recommendation

Applicable sections:

1. all sections, especially long introductions and conclusions

### 12. Voice And Guardrail Combo Prompt

Input requirements:

1. user writing samples if available
2. target section
3. protected evidence items

Must preserve:

1. evidence boundary
2. section function
3. all quantitative statements

Do not modify:

1. unsupported claims into stronger claims
2. limitations into achievements

Output order:

1. inferred voice profile
2. revised text
3. guardrail check
4. unresolved anchor gaps

For review-assisted revisions, also return:

1. critical comments resolved
2. comments deferred and why
3. claims changed, narrowed, or removed
4. any score or rating treated as advisory only

Applicable sections:

1. abstract
2. introduction
3. conclusion
4. response to reviewers

## Final Self-Check Before Handing Off Draft Text

1. Can every quantitative statement be traced to a file, figure, table, or cited paper?
2. Did any sentence overstate the evidence?
3. Did any planned feature get written as if it were completed?
4. Are limitations written explicitly where needed?
5. Are all figures and tables called out and interpreted in the text?
6. Is the related work synthesized rather than listed mechanically?
7. Is the language formal, concise, and free of colloquial phrasing?
8. Would the user be able to mark which parts are already verified and which parts still need confirmation?
9. Did the rewrite change only what was intended by `writing_task_type`?
10. Did `methods` and `results` stay within `conservative` risk tolerance unless the user explicitly overrode it?
11. If review comments or scores were used, were validity, method, and evidence comments resolved before style-preference items?
12. Are any high-score but unsupported claims still present in the abstract, contribution list, conclusion, figure narration, or response letter?

## Source Notes

Treat the following as inspiration layers, not equal-evidence sources:

- Hard-rule layer:
  - Purdue OWL APA stylistics basics and avoiding bias
  - Purdue OWL plagiarism best practices
  - Elsevier Researcher Academy writing guidance
  - University thesis-writing guidance on formal, precise, and normative academic language
  - University guidance that AI detectors are unreliable and may produce false positives
- Soft-structure layer:
  - GitHub and skill communities that organize academic writing as role + task + constraints + refinement loops
  - Public writing-humanizer skill libraries, used only as pattern-harvest inputs for de-templating

Representative links:

- Vanderbilt University, "Guidance on AI Detection and Why We're Disabling Turnitin's AI Detector"
  - https://www.vanderbilt.edu/brightspace/2023/08/16/guidance-on-ai-detection-and-why-were-disabling-turnitins-ai-detector/
- Stanford HAI, "AI-Detectors Biased Against Non-Native English Writers"
  - https://hai.stanford.edu/news/ai-detectors-biased-against-non-native-english-writers
- Purdue OWL, "Revising and Editing"
  - https://owl.purdue.edu/owl/graduate_writing/introduction_to_writing/revising_and_editing.html
- Purdue OWL, "Style"
  - https://owl.purdue.edu/owl/graduate_writing/graduate_writing_topics/graduate_writing_style_new.html
- Purdue OWL, "Active and Passive Voice"
  - https://owl.purdue.edu/owl/general_writing/academic_writing/active_and_passive_voice/index.html
- Public community examples reviewed for pattern harvest only:
  - https://gist.github.com/ehc-io/c023793416e1fac75e539ba7b943d80e
  - https://skillsplayground.com/skills/shipshitdev-library-humanizer/
  - https://skillsplayground.com/skills/charlesjones-dev-claude-code-plugins-dev-writing-humanize/
  - https://skillsplayground.com/skills/huangwb8-chineseresearchlatex-nsfc-humanization/
  - https://skillsplayground.com/skills/bahayonghang-academic-writing-skills-typst-paper/

Use the hard-rule layer to decide what academic text may or may not claim.
Use the soft-structure layer only to improve workflow, prompting structure, and section decomposition.
