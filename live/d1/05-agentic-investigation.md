# 05 — Agentic Investigation and Telemetry

Time: 21:00–21:22 · Slides 10–11 · Mode: deck → agent → trace

## Question

The final response cannot prove how the work was performed. Can we inspect the
trajectory from objective to evidence to human gate?

## Explain why

```text
objective -> context -> tool -> observation -> claim -> verification
          -> human decision -> durable artifact
```

Agentic Development is controlled tool-mediated work, not a longer chat.

## Authority boundary

- Read approved repository sources.
- Run approved read-only queries.
- Write only under `tmp/foundation-investigation/manual/`.
- Do not modify operational data, schema, source code, or infrastructure.
- Do not make business decisions.
- Escalate ambiguity to its named owner.

## Telemetry truth boundary

This trace is emitted by the investigating agent. It is **self-reported
telemetry**, useful for inspection but not independent proof. Say this aloud.

## Paste

```text
Continue the confirmed revenue investigation. Perform controlled, read-only
work and emit one JSON object per significant action to:
tmp/foundation-investigation/manual/trace.jsonl

Each event must contain: timestamp, run_id, actor, phase, action, target,
ontology_entity (nullable), evidence_references (array), outcome, and
duration_ms. Emit events for context loading, repository inspection, query
execution, claim proposal, verification, rejection, question escalation,
artifact update, gate evaluation, and completion.

Never record secrets, connection strings, personal data, complete rows, or
secret-bearing prompts. Include at least one assumption that is tested and
rejected, plus at least one question escalated to its human owner. Keep all
database actions read-only and all writes under
tmp/foundation-investigation/manual/.

At completion, summarize sources used, queries executed, claims verified,
claims rejected, questions escalated, and artifacts written. Clearly label the
trace as self-reported telemetry.
```

## Inspect

```bash
wc -l tmp/foundation-investigation/manual/trace.jsonl
sed -n '1,8p' tmp/foundation-investigation/manual/trace.jsonl
rg -n 'rejected|question|escalat|gate' tmp/foundation-investigation/manual/trace.jsonl
```

## Follow along

Locate one tool use, verified claim, rejected claim, escalated question, and
human gate.

## Proof that counts

- The trajectory connects actions to evidence.
- A rejected assumption remains visible.
- A missing business decision is escalated rather than invented.
- Nobody claims independent telemetry collection.

## Recovery

Inspect a rehearsed JSONL trace labeled **prepared**. A malformed live trace is
also useful evidence: keep the failure visible and explain the contract it
violated.

Next: [`06-technical-brief.md`](06-technical-brief.md).
