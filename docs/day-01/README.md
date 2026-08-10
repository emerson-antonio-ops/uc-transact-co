# Day 1 - Prompt, Context, Ontology, and Evidence

Day 1 is a controlled investigation of an unfamiliar brownfield. The goal is not
to build transformation models or autonomous agents. The goal is to understand
TransactCo well enough to produce an evidence-backed technical brief.

## Learning outcome

By the end of the session, you should be able to:

- explain why a prompt is a work contract rather than a knowledge base;
- select context deliberately instead of dumping files;
- interview a system through documentation, schema, and read-only queries;
- model entities, relationships, rules, events, provenance, and owners;
- distinguish facts, inferences, decisions, and open questions;
- inspect the work trajectory through safe telemetry;
- produce a durable technical brief for human review.

## Context pack

Read these in order:

1. [`business-brief.md`](business-brief.md)
2. [`data-guide.md`](data-guide.md)
3. [`investigation-workbook.md`](investigation-workbook.md)
4. [`telemetry-contract.md`](telemetry-contract.md)
5. [`technical-brief-template.md`](technical-brief-template.md)
6. [`reflection.md`](reflection.md)

The repository contains material for the entire Semana. Day 1 intentionally uses
only this context pack, the operational schema, representative data, and approved
read-only commands. Incident injection, scoring, dbt models, the harness, and the
execution loop belong to later days.

## Working agreement

- Read before changing.
- Use read-only access during the investigation.
- Support important claims with a path, schema object, or query.
- Label inference as inference.
- Do not invent business decisions.
- Escalate questions that require an accountable owner.
- Never put credentials, personal data, or complete rows in telemetry or notes.

## Day 1 gate

Day 1 closes when the technical brief, ontology, evidence ledger, telemetry
summary, and open questions have been reviewed by a human.
