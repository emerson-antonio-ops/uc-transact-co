# Day 1 Telemetry Contract

Telemetry makes the investigation trajectory inspectable. It should help answer
what the agent inspected, which tools it used, what it claimed, how claims were
verified, where it became uncertain, and which artifacts changed.

Telemetry does not make an answer correct by itself. It provides evidence about
the process that produced the answer.

## Minimum event types

```text
session_started
phase_started
context_loaded
repository_inspected
query_executed
claim_proposed
claim_verified
claim_rejected
question_opened
artifact_updated
gate_evaluated
session_completed
```

## Minimum event fields

| Field | Purpose |
| --- | --- |
| `timestamp` | When the event occurred |
| `run_id` | Which investigation run produced it |
| `actor` | Human or agent responsible for the action |
| `phase` | Current Day 1 phase |
| `action` | Event type |
| `ontology_entity` | Optional business entity affected |
| `evidence_reference` | Path, schema object, or safe query identifier |
| `outcome` | Success, failure, rejection, escalation, or open |
| `duration_ms` | Optional elapsed time |

## JSONL example

```json
{"timestamp":"2026-08-10T22:05:00Z","run_id":"day01-demo","actor":"agent","phase":"context","action":"context_loaded","ontology_entity":null,"evidence_reference":"docs/day-01/business-brief.md","outcome":"success","duration_ms":18}
```

## Safety rules

Never record:

- passwords or secret-bearing connection strings;
- `.env` contents;
- personal customer data;
- complete database rows;
- private instructor material;
- full prompts containing secrets;
- the later-day oracle or incident details.

Prefer query identifiers, aggregate counts, hashes, and file paths over raw data.

## End-of-session summary

Report:

- time to first verified claim;
- context sources used;
- read-only queries executed;
- verified and rejected claims;
- open questions and escalations;
- artifacts updated;
- gate outcome.

## Implementation status

This file defines the Day 1 contract. A live emitter or tracing adapter must be
implemented and rehearsed separately before the facilitator promises live
telemetry collection. Manual event capture can demonstrate the schema, but must
not be presented as automated instrumentation.
