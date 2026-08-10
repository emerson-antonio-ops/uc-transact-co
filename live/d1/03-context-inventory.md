# 03 - Context Inventory (Checkpoint C: Context inventory)

Act 3 - Why context matters (19:40-20:15)

## Question

The model knows what an order usually means. How does it learn what
TransactCo means by revenue - and how do we know which source taught it?

## Authority boundary

- The agent receives only the distributed context pack (business brief, data
  guide, operational DDL, read-only access instructions) - selected, in a
  deliberate order, not the whole repository.
- Read-only queries only.

## Run this

First inventory the sources with the room: for each one, why is it included,
what can it answer, what can it not answer. Then paste:

```text
You have been given, in order: the TransactCo business brief, the data guide,
the operational DDL at infra/postgres/init/01_schema.sql, and read-only
database access. Using only these sources, build an evidence ledger for the
revenue investigation. For each entry record: an ID, the statement, its status
(fact, inference, decision, or question), the exact source that supports it
(file path, schema object, or query), and the next action. Before using any
source, state which source you are opening and why. Do not use knowledge that
is not grounded in a listed source. If two sources disagree, record the
disagreement as a question instead of resolving it yourself.
```

## Proof that counts

- Every claim in the ledger points to a named source.
- The room can point to the context source that changed or supported at least
  one specific conclusion.
- Artifact produced: Context Inventory and Evidence Ledger.

## If it fails

Switch to the prepared context-inventory snapshot and review it live.

## Skill distilled

Fill
[`../../skills/d1/S2-context-selection.md`](../../skills/d1/S2-context-selection.md).
