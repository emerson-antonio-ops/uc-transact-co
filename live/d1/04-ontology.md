# 04 - Ontology v1 (Checkpoint D: Ontology)

Act 4 - Why ontology matters (20:25-21:00)

## Question

When data crosses from Postgres to DuckDB, columns can survive while meaning
dies. What must remain true on both sides?

## Authority boundary

- Read-only queries only.
- The agent may propose relationships; it may not promote a candidate to a
  confirmed rule without evidence, and it may not invent business decisions.

## Run this

```text
Using the evidence ledger from the previous step and read-only database
access, model TransactCo Ontology v1. Derive candidate entities from the
schema and business brief. Derive candidate relationships from column names,
values, and observed data - the database has no foreign-key constraints, so
every relationship is a hypothesis until tested. For each edge (for example
Customer places Order, Order settled by Payment), run a read-only query that
tests cardinality or reconciliation, and attach the query as evidence. Output
a table with: subject, relationship, object, status (evidenced, inferred, or
open question), evidence, and owner. The edge "Payment may contribute to
Revenue" must remain conditional: record which business decisions would be
required to confirm it, and who should own each decision. Do not resolve
those decisions yourself.
```

## Proof that counts

- Every ontology edge is evidenced, explicitly inferred, or marked as an
  unresolved business decision with a named owner.
- At least one candidate relationship was tested against real data live.
- Artifact produced: TransactCo Ontology v1.

## If it fails

Switch to the ontology v1 backup and validate one edge manually with
`make query-ro`.

## Skill distilled

Fill
[`../../skills/d1/S4-ontology-modeling.md`](../../skills/d1/S4-ontology-modeling.md).
