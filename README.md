# Autonomous Scientific Research Skill

A Codex skill for literature-grounded scientific and engineering research workflows.

This skill is designed for staged research execution:

- Stage 0: problem framing and real-data gate
- Stage 1: literature review and candidate research routes
- Stage 2: best-plan refinement and user confirmation
- Stage 3: controlled implementation and experiment loops
- Stage 4: fixed-data optimization, validation, and engineering verification

It emphasizes evidence discipline, baseline locking, experiment registries, claim ledgers, leakage and overfitting audits, and review-score sanity checks.

## Install

Copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\autonomous-scientific-research "$env:USERPROFILE\.codex\skills\autonomous-scientific-research"
```

Then restart Codex.

## Python Configuration

For research code execution, configure the GPU Python interpreter expected by the skill:

```powershell
$env:AUTONOMOUS_RESEARCH_PYTHON="C:\Users\<you>\.conda\envs\GPU\python.exe"
```

Persist that environment variable using your normal shell or OS configuration if needed.

## Contents

- `autonomous-scientific-research/SKILL.md`: main skill instructions and hard constraints
- `autonomous-scientific-research/references/`: detailed workflow, evidence, domain, writing, and review-integrity rules
- `autonomous-scientific-research/scripts/init_stage3_registry.py`: helper for Stage 3 experiment registries
- `autonomous-scientific-research/agents/openai.yaml`: UI metadata

## Notes

- Review scores are advisory only. Completion depends on metric gates, guardrails, leakage/overfit audits, claim support, and reproducibility.
- The skill requires a real data source or clear data acquisition route before proposing research routes.
- No license file is included yet. Add a license before inviting reuse or contributions.
