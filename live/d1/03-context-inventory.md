# 03 — Deliberate Context and Claim Ledger

Time: 19:50–20:15 · Slides 6–7 · Mode: repository → agent

## Question

The model knows what an order usually means. Which evidence teaches it what
TransactCo actually stores, and which source is authorized to define meaning?

## Explain why

The prompt defines the work. Context supplies the world. Context engineering is
selection, ordering, provenance, freshness, and authority—not dumping the whole
repository into the model.

## Approved context for this phase

| Order | Source | Can support | Cannot decide |
| ---: | --- | --- | --- |
| 1 | `README.md` | Business tension and published system boundary | Revenue policy |
| 2 | `infra/postgres/init/01_schema.sql` | Current physical schema | Business meaning of column names |
| 3 | `src/transactco/operational/seed.py` | Generated baseline behavior | Production policy |
| 4 | `src/transactco/operational/postgres.py` | Current source access implementation | Finance decisions |
| 5 | Read-only Postgres queries | Runtime physical evidence | Semantic authorization |

Do not approve `src/transactco/domain/` yet. It is revealed after the physical
query.

## Paste

```text
The investigation contract is confirmed. Before answering the CFO, build a
deliberate context inventory using only these approved sources, in this order:

1. README.md
2. infra/postgres/init/01_schema.sql
3. src/transactco/operational/seed.py
4. src/transactco/operational/postgres.py
5. approved read-only Postgres queries

Do not inspect src/transactco/domain/, _control, injection, scoring, or any
instructor-only surface yet.

For each context source record its location, purpose, kind (current, proposed,
derived, or external), freshness, authority, and what it cannot decide. Then
build a claim ledger. For every material statement record an ID, statement,
classification (fact, inference, decision, or question), evidence reference,
owner when required, and next action. Do not answer the revenue question yet.
Write the result to:
tmp/foundation-investigation/manual/context-and-claims.md
```

## Inspect

```bash
sed -n '1,260p' tmp/foundation-investigation/manual/context-and-claims.md
```

## Follow along

Pick one fact and one inference. For each, identify its source, authority,
freshness, and falsification test.

## Proof that counts

- Every fact points to reproducible evidence.
- Inferences remain labeled.
- Business decisions have owners.
- Revenue semantics remain unresolved.

Next: take the break, then open [`04-ontology.md`](04-ontology.md).
