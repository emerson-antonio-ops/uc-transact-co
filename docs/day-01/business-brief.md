# TransactCo Business Brief

## Situation

TransactCo is a high-volume e-commerce company. Store operations and analytical
queries currently share the same Postgres database. The operational workload
creates and updates customers, products, orders, and payments. The analytical
workload scans and aggregates those records for reporting.

The two workloads compete for the same resources. Heavy analytical work can
affect store operations, while transactional traffic can make reporting slow or
unpredictable.

## The CFO's question

> How much revenue did we make yesterday, and why should I trust that number?

The request contains two different problems:

1. Calculate a number.
2. Establish the meaning and evidence that make the number trustworthy.

Day 1 focuses on the second problem before implementing a new analytical system.

## Known system boundary

- Postgres is the operational source.
- The relevant public tables are `customers`, `products`, `orders`, and
  `payments`.
- The initial investigation is read-only.
- The supplied analytical crossing lands operational data into DuckDB; Day 1
  investigates that boundary rather than extending it.
- Business meaning must survive that system crossing.

## Known stakeholders

| Stakeholder | Concern |
| --- | --- |
| CFO | A revenue number with defensible meaning |
| Store operations | Transactional reliability and responsiveness |
| Data team | Reproducible transformations and quality evidence |
| Engineering | Clear interfaces, permissions, and recovery paths |

## What is not decided for you

The following are intentionally open until evidence or an accountable owner
resolves them:

- Which business event recognizes revenue?
- Which payment and order statuses count?
- How should refunds affect the metric?
- Which timezone defines "yesterday"?
- How should late-arriving data change a previously published number?
- Who owns each semantic decision?

These are not trivia questions. They are examples of the boundary between
technical discovery and business authority.

## Day 1 mission

Understand the existing system, identify the evidence available, map its first
ontology, document confirmed rules and unresolved decisions, and propose the
questions that must be answered before building a trustworthy revenue model.
