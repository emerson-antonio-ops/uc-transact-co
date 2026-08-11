# Evidence package contract

The evidence package contains one machine-readable source of truth and one review surface.

## `investigation.json`

Required top-level fields:

```json
{
  "schema_version": "1.0",
  "status": "pending human review",
  "question": "Which records can support a defensible revenue metric?",
  "outcome": "Identify physical evidence and the business decisions still required.",
  "scope": {"in": ["local Postgres"], "out": ["production"]},
  "authority": {
    "read_only": true,
    "allowed_tools": ["psql read-only queries"],
    "prohibited_actions": ["writes", "schema changes"],
    "stop_conditions": ["sensitive data", "business definition required"]
  },
  "context_sources": [],
  "claims": [],
  "ontology": {"entities": [], "concepts": [], "events": [], "relationships": [], "rules": []},
  "open_questions": []
}
```

### Context source

Each source requires:

- `id`: stable local identifier;
- `kind`: `current`, `proposed`, `derived`, or `external`;
- `location`: reproducible source location;
- `purpose`: why it is in context;
- `freshness`: timestamp, version, commit, or explicit unknown value;
- `authority`: what the source is authoritative for.

### Claim

Each claim requires `id`, `statement`, `classification`, and `evidence_references`.

- `fact` requires at least one evidence reference.
- `inference` requires evidence inputs and visible reasoning.
- `decision` requires a named owner.
- `question` requires a named owner and next action.

Evidence references point to context-source IDs or other stable evidence IDs in the package.

### Ontology

Entities, concepts, events, and rules require a unique `name`. Relationships require `subject`, `predicate`, `object`, `status`, and `evidence_references`.

An `evidenced` relationship requires evidence. An `unresolved` relationship requires an owner and at least one question. Relationship endpoints must name a declared entity or concept.

### Open question

Each open question requires `question`, `owner`, and `next_action`. Use a role such as `Finance owner` when a person has not yet been identified; do not use `TBD` as ownership.

## `technical-brief.md`

The brief must contain these headings:

- `# Technical Brief`
- `## Status`
- `## Question and Outcome`
- `## Scope and Authority`
- `## Evidence Consulted`
- `## Findings`
- `## Ontology`
- `## Decisions and Open Questions`
- `## Risks and Stop Conditions`
- `## Human Review`

Status must remain `draft` or `pending human review` until a named reviewer accepts the business meaning.

## `trace.jsonl`

The optional trace contains one JSON object per line with:

- `timestamp` in ISO-8601 form;
- `timestamp_basis`, declaring that the ordering is approximate and reconstructed;
- `run_id`;
- `phase`;
- `action`;
- `target`;
- `outcome`;
- `evidence_references` as an array;
- `gate`;
- `telemetry`, exactly `self-declared`;
- `capture_mode`, exactly `retrospective_reconstruction`.

When supplied, the trace must contain at least one event. The validator checks
shape, provenance labels, and whether each evidence reference resolves to a
context-source or claim ID in `investigation.json`. A trace emitted by the
investigating agent is not independent proof that the actions occurred.
