# Ontology bridge

An ontology is the explicit bridge between physical records and business meaning. It prevents an agent from treating column names as definitions.

## Minimum model

- **Entity** — a thing with identity, such as Customer, Order, Product, or Payment.
- **Event** — something that happened at a time, such as OrderPlaced or PaymentCaptured.
- **Relationship** — a typed connection, such as Customer `places` Order.
- **Rule** — a constraint or invariant supported by evidence.
- **Concept** — shared business meaning, such as Revenue, ActiveCustomer, or FulfilledOrder.
- **Provenance** — where the assertion came from and how fresh it is.
- **Owner** — who can decide meaning when evidence cannot.

## Physical versus semantic query

A physical query can answer:

- Which tables and columns exist?
- How many payment rows have each status?
- What is the sum of `payments.amount` by day?
- Are keys complete and values internally consistent?

It cannot, by itself, answer:

- Which statuses count as realized revenue?
- Is revenue recognized at order, payment, settlement, or fulfillment time?
- Are refunds subtracted, and on which date?
- Which timezone and currency policy apply?

The ontology query should expose these missing decisions instead of returning a falsely precise number.

## Status discipline

- Use `evidenced` only when a cited source directly supports the assertion.
- Use `inferred` when evidence supports a reasoned interpretation but not a declared business contract.
- Use `unresolved` when the answer depends on a named owner or policy decision.

For an unresolved concept, include candidate inputs, its owner, the exact questions blocking it, and evidence showing why those questions matter.

## Live reveal pattern

1. Ask the agent to query the database for revenue. Let it discover tables, columns, statuses, and aggregates.
2. Ask what the number means. Separate the physical result from assumptions it introduced.
3. Query the ontology for `Revenue`.
4. Show that a high-quality answer may be a controlled refusal: candidate data exists, but business meaning is unresolved.
5. Ask the named owner to make the missing decisions, update the ontology, then rerun the query.

The aha moment is not that ontology produces more data. It produces a safer boundary between what the system stores and what the organization means.

