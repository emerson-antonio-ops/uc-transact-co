# TransactCo — Agent Instructions

Brownfield commerce case for Semana Engenharia Agêntica. The numbers here must
earn trust: physical measurements are evidence, business meaning is owned by
humans. `Revenue` is formally **unresolved** (owner: Finance) — no agent may
choose a definition for it.

## Ground rules (all agents, all engines)

- Postgres access is read-only via `analytics_ro`; DuckDB `raw.*` mirrors
  `public.*`. Discover commands with `make help`.
- Approved context lives in `storage/specs/` — read-only; never overwrite it.
- Never touch `src/transactco/control`, the oracle, or injection/scoring
  surfaces (`make inject`, `make reveal`, `make score`).
- Any semantic decision — what counts as Revenue, which statuses, which
  timestamp — halts the work and escalates to the named owner.
- Verification is a gate you run (`make dbt-check`, `make test`), never a
  self-declaration.

## Agents

<!-- Entries below are written live at checkpoint live/d2/03-agent-pair.md,
     against the harness contract confirmed at checkpoint 02. -->
