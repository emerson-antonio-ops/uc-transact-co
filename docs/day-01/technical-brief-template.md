# TransactCo Technical Brief

- Status: draft / reviewed / approved
- Authors:
- Review owner:
- Evidence window:

## 1. Business problem

What decision or outcome is required, and why does it matter?

## 2. Current system boundary

Describe the operational system, analytical pressure, interfaces, and authority
boundaries.

## 3. Data inventory

| Source/table | Purpose | Business time | Ingestion time | Evidence |
| --- | --- | --- | --- | --- |

## 4. Ontology v1

| Subject | Relationship | Object | Status | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |

## 5. Confirmed rules

| Rule | Scope | Evidence | Validation query/reference |
| --- | --- | --- | --- |

## 6. Facts, inferences, decisions, and questions

| ID | Statement | Status | Evidence | Owner | Next action |
| --- | --- | --- | --- | --- | --- |

## 7. Risks and constraints

- Operational safety:
- Data quality:
- Semantic ambiguity:
- Freshness:
- Privacy/security:
- Recovery:

## 8. Proposed analytical boundary

Describe what should cross from Postgres into DuckDB, in which direction, and
which meanings and constraints must survive.

## 9. Success measures

Define observable, falsifiable outcomes. Avoid "works correctly" without a
measurement or evidence source.

## 10. Non-goals

State what Day 1 is not authorizing or implementing.

## 11. ADR candidates

| Candidate | Decision required | Alternatives | Evidence | Missing owner/input |
| --- | --- | --- | --- | --- |

## 12. Open questions

| Question | Why it blocks or changes the design | Owner | Due/next step |
| --- | --- | --- | --- |

## 13. Evidence appendix

List repository paths, schema objects, safe query identifiers, and telemetry run
IDs. Do not paste credentials, personal data, or complete rows.

## Review gate

- [ ] Important claims are evidenced or explicitly uncertain.
- [ ] Business decisions have accountable owners.
- [ ] The proposed boundary is read-only and one-directional where required.
- [ ] The brief does not authorize later-day implementation.
- [ ] Human review is recorded.
