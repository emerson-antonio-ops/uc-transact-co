# 05 - Agentic Investigation (Checkpoint E: Agentic investigation)

Act 5 - Why Agentic Development and telemetry matter (21:00-21:35)

## Question

The final answer cannot prove how the work was done. Can we make the
investigation itself inspectable?

## Authority boundary

The minimum Foundation Investigation authority:

- read repository files from the approved context;
- run approved read-only queries;
- write the Foundation Investigation documentation artifacts;
- do not modify operational data;
- do not make business decisions;
- escalate ambiguity to the facilitator or named owner.

Honesty rule: until a live emitter is implemented and rehearsed, this is a
manual demonstration of the telemetry contract. Say so. Do not present it as
automated instrumentation.

## Run this

```text
Run the revenue investigation under the investigation contract, with this
addition: emit a JSONL telemetry event for every significant action, following
the investigation telemetry contract. Allowed event types: session_started,
phase_started, context_loaded, repository_inspected, query_executed,
claim_proposed, claim_verified, claim_rejected, question_opened,
artifact_updated, gate_evaluated, session_completed. Each event must carry:
timestamp, run_id, actor, phase, action, ontology_entity (nullable),
evidence_reference, outcome, duration_ms. Never record passwords, connection
strings, personal data, or complete database rows - use query identifiers,
aggregate counts, and file paths. When a claim fails verification, emit
claim_rejected and keep the rejection visible. When a conclusion requires
business authority, emit question_opened and escalate instead of deciding.
At the end, emit session_completed and print a summary: context sources used,
queries executed, claims verified and rejected, questions escalated, and
artifacts updated.
```

## Proof that counts

- The event stream shows tools, claims, evidence, and escalations.
- At least one rejected assumption is visible in the trace.
- At least one escalation to human authority is visible in the trace.
- The facilitator can reconstruct from the trace which sources and decisions
  produced the conclusions.
- Artifact produced: Foundation Investigation Trace.

## If it fails

Use the recorded JSONL trace, labeled as prepared, and walk the same
reconstruction exercise.

## Skill distilled

Fill
[`../../skills/d1/S3-system-interviewing.md`](../../skills/d1/S3-system-interviewing.md)
and
[`../../skills/d1/S5-trajectory-inspection.md`](../../skills/d1/S5-trajectory-inspection.md).
