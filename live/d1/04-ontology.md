# 04 — Postgres Versus Ontology

Time: 20:25–21:00 · Slides 8–9 · Mode: Postgres → ontology CLI → agent

## Question

Can the database return a precise result while the system still lacks a
defensible answer?

## Authority boundary

- Read-only Postgres queries.
- Physical evidence first; ontology is revealed second.
- No business policy may be invented.
- Candidate relationships remain inferred when constraints or authoritative
  declarations are absent.

## Part A — Ask Postgres

Paste into the agent:

```text
Using only the confirmed contract, approved physical context, and read-only
Postgres access, investigate yesterday’s candidate payment amount in UTC.
First inspect the available payment statuses. Then return the aggregate count
and sum by status for the previous completed UTC calendar day. Show the exact
query and evidence. Separate the physical result from every assumption needed
to call it Revenue. Do not inspect the ontology yet and do not choose a revenue
policy.
```

Terminal fallback:

```bash
make psql-ro
```

```sql
\pset pager off
\timing on
BEGIN TRANSACTION READ ONLY;

SELECT status, count(*) AS payment_rows, sum(amount) AS amount_sum
FROM public.payments
GROUP BY status
ORDER BY status;

WITH bounds AS (
  SELECT
    (date_trunc('day', now() AT TIME ZONE 'UTC') - interval '1 day')
      AT TIME ZONE 'UTC' AS start_utc,
    date_trunc('day', now() AT TIME ZONE 'UTC')
      AT TIME ZONE 'UTC' AS end_utc
)
SELECT
  p.status,
  count(*) AS payment_rows,
  sum(p.amount) AS amount_sum
FROM public.payments AS p
CROSS JOIN bounds AS b
WHERE p.paid_at >= b.start_utc
  AND p.paid_at < b.end_utc
GROUP BY p.status
ORDER BY p.status;

SELECT count(*) AS declared_foreign_keys
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
  AND contype = 'f';

COMMIT;
\q
```

Ask the room why none of these are yet authorized:

- captured amount equals Revenue;
- captured minus refunded equals Revenue;
- `paid_at` is the recognition timestamp;
- UTC is the Finance reporting timezone;
- a column join is a guaranteed business relationship.

## Part B — Ask the ontology

Explain the vocabulary:

- Entity — something with identity.
- Event — something that happened at a business time.
- Relationship — a typed connection.
- Rule — a declared constraint or invariant.
- Concept — shared business meaning.
- Provenance — evidence supporting an assertion.
- Owner — authority to decide unresolved meaning.

Run:

```bash
uv run transactco ontology validate
uv run transactco ontology list
uv run transactco ontology explain Revenue
uv run transactco ontology explain Revenue --json
```

Then paste:

```text
You may now inspect src/transactco/domain/transactco.ontology.json and the
output of `uv run transactco ontology explain Revenue --json`. Re-answer the
CFO’s question using both the physical query evidence and the ontology.
Separate: what the database proves, what the ontology currently declares,
which candidate inputs exist, which business decisions block a defensible
Revenue metric, and who owns those decisions. A controlled refusal is valid.
Do not invent a policy to make the answer complete.
```

## Aha moment

> Postgres gave us more data. Ontology gave us a safer answer.

`blocked_by_business_decisions` is the expected high-quality result. Finance
owns recognition, statuses, adjustments, currency, and timezone policy.

Ask the agent to preserve the observation:

```text
Write the ontology observations, evidence references, and owned unresolved
questions to tmp/foundation-investigation/manual/ontology-notes.md. Keep the
status pending human review.
```

## Proof that counts

- The physical aggregate is visible and reproducible.
- The assumptions needed to label it Revenue are explicit.
- Ontology entities and relationships have provenance and status.
- `Payment may_contribute_to Revenue` remains unresolved with a Finance owner.

Next: [`05-agentic-investigation.md`](05-agentic-investigation.md).
