# Live Session Guides

This folder is the executable teaching surface for Semana. Facilitator and
participants use the same files: every checkpoint states what we are trying to
learn, what the agent may do, what to run, what evidence to inspect, and what
must be true before continuing.

## Start here

- [`d1/README.md`](d1/README.md) — canonical three-hour Day 1 sequence
- [`d1/00-setup.md`](d1/00-setup.md) — preflight and environment gate
- [`d1/01-weak-prompt.md`](d1/01-weak-prompt.md) — experience the prompt failure
- [`d1/02-investigation-contract.md`](d1/02-investigation-contract.md) — bound the work
- [`d1/03-context-inventory.md`](d1/03-context-inventory.md) — select context and provenance
- [`d1/04-ontology.md`](d1/04-ontology.md) — Postgres versus ontology reveal
- [`d1/05-agentic-investigation.md`](d1/05-agentic-investigation.md) — controlled work and trace
- [`d1/06-technical-brief.md`](d1/06-technical-brief.md) — durable evidence package
- [`d1/07-skill-reveal.md`](d1/07-skill-reveal.md) — automate the practiced method
- [`d1/08-reflection.md`](d1/08-reflection.md) — close the learning loop

## The teaching loop

```text
DECK: create one question
  -> DEMO: test it against TransactCo
  -> EVIDENCE: inspect the result or visible failure
  -> DECK: name the canonical concept
  -> ARTIFACT: preserve what became true
  -> REFLECTION: state what remains unresolved
```

Use these transition lines consistently:

- Into the demo: **“We could debate this, but let’s test it.”**
- Back to the concept: **“Now let’s separate what looked impressive from what became provably true.”**
- Into the skill reveal: **“We have practiced the method manually. Now let’s encode the method.”**

## Non-negotiable safety boundary

- Day 1 investigation is read-only against Postgres and DuckDB.
- Agent writes are limited to `tmp/foundation-investigation/`.
- Do not run `make inject`, `make inject-quiet`, `make reveal`, `make score`,
  or inspect instructor-control implementation during Day 1.
- Do not place secrets, connection strings, personal data, or complete rows in
  prompts, traces, or documentation.
- Prepared fallback outputs must always be labeled **prepared**, never live.

The planning source is [`../plan/semana.md`](../plan/semana.md). The live Day 1
runbook is the operational source for what to do on screen.
