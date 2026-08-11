# Day 2 — The Harness: Authority Before Construction

The question carried through the session is:

> The number waits for Finance. Meanwhile, build the pipeline — and tell me
> exactly what this agent can do on its own.

The audience should leave understanding that a capable model plus a clear goal
still needs written authority; that a harness is files in the repository, not
vibes; and that a visible refusal at a semantic boundary is a success state.

## The complete story

```mermaid
flowchart LR
    S0[00 Inheritance] --> S1[01 Unbounded]
    S1 --> S2[02 Contract]
    S2 --> S3[03 Agent pair]
    S3 --> S4[04 Sketch plans]
    S4 --> S5[05 Bounded build]
    S5 --> S6[06 Scaffold]
    S6 --> S7[07 Reflection]

    classDef setup fill:#E5E7EB,stroke:#4B5563,color:#111827
    classDef fail fill:#FEE2E2,stroke:#DC2626,color:#7F1D1D
    classDef authority fill:#DBEAFE,stroke:#2563EB,color:#172554
    classDef build fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef human fill:#FEF3C7,stroke:#D97706,color:#78350F
    class S0 setup
    class S1 fail
    class S2,S3 authority
    class S4,S5,S6 build
    class S7 human
```

## Sequence and deck switches

| Step | Session | Deck cue | Demo evidence | Durable result |
| ---: | --- | --- | --- | --- |
| [`00`](00-inheritance.md) | No agent, then an optional discarded warm-up | What survived the night | Three specs, healthy tables, empty shell parses; optionally the Day 1 skill reaching the same stop | Baseline only |
| [`01`](01-unbounded.md) | **NEW A** | Authority without rails | The overreaching plan, stopped | None — session discarded |
| [`02`](02-harness-contract.md) | **NEW B** | The agent proposes, a human confirms | Confirmed contract table | Contract in context |
| [`03`](03-agent-pair.md) | Continue B (human types) | Two roles, split on purpose | `AGENTS.md` diff | Agent pair in repo |
| [`04`](04-sketch-plans.md) | Continue B as architect | Plans before tasks | Two plans, revenue BLOCKED | `4-plan-transform.md` · `5-plan-serve.md` |
| [`05`](05-bounded-build.md) | **NEW C** — developer | One build passes, one refused | `dbt-check` PASS + refusal | `stg_orders.sql` |
| [`06`](06-scaffold.md) | **NEW D** — fresh | Practice becomes scaffold | Generated tree, empty stubs | Temporary scaffold |
| [`07`](07-reflection.md) | No agent | Turn two | Participant commitments | Team learning |

Switch in the same rhythm every time:

```text
DECK: explain why
  -> DEMO: perform one bounded action
  -> EVIDENCE: show only the named proof
  -> DECK: state what changed
  -> GATE: continue or keep the failure visible
```

## Output budgets

| Checkpoint | Visible agent response | Artifact budget |
| ---: | --- | --- |
| 00 bridge (optional) | One table, 6 rows, 150 words | None — read-only |
| 01 | The proposed plan only, 8 lines | None — never executed |
| 02 | One table, 10 rows | None — contract lives in context |
| 03 | None — the human types | Two entries in `AGENTS.md` |
| 04 | 120-word summary | Two plans, ≤10 items and 300 words each |
| 05 | One sentence per action | One staging model + sources file |
| 06 | 6 bullets, 150 words | Scaffold under `tmp/harness-scaffold/` |

## Artifact workspace

```text
storage/specs/
├── 1-context.md            # inherited from Day 1 — read-only tonight
├── 2-ontology.md           # inherited from Day 1 — read-only tonight
├── 3-technical-brief.md    # inherited from Day 1 — read-only tonight
├── 4-plan-transform.md     # written at checkpoint 04
└── 5-plan-serve.md         # written at checkpoint 04

dbt/models/staging/          # created at checkpoint 05 — must NOT exist before
tmp/harness-scaffold/        # created at checkpoint 06
```

`dbt/models/staging/` intentionally does not exist before the session; the
developer agent creates it live inside the contract's writable path.

## Shared boundaries

- Postgres access stays read-only (`analytics_ro`); DuckDB `raw.*` is the mirror.
- The three inherited specs are read-only tonight; no checkpoint may overwrite them.
- Gold revenue models cannot be built while `Revenue` is `unresolved` — the
  refusal at checkpoint 05 is the success state, never a failure to recover from.
- The optional Day 1 bridge at checkpoint 00 is read-only and its session is
  discarded; Session A must not inherit it.
- Session A demonstrates the overreach and is discarded.
- Session B carries contract → agent pair → plans, then stops.
- Session C is the developer: builds only inside `dbt/models/staging/`.
- Session D is fresh: the scaffold must work from artifacts, not chat memory.
- Instructor `_control`, injection, scoring, and reveal surfaces remain closed.
- Label any fallback artifact **prepared**.

## Completion gate

- [ ] The inheritance was verified live (specs, tables, empty shell).
- [ ] Optional: the Day 1 skill ran from files alone and stopped at `Revenue`.
- [ ] The unbounded overreach was visible and nothing was written.
- [ ] A human confirmed the harness contract, editing at least one row.
- [ ] The agent pair was typed by hand and exists in `AGENTS.md`.
- [ ] Two sketch plans exist with the revenue item visibly BLOCKED.
- [ ] `make dbt-check` passed on the staging model AND the refusal held.
- [ ] The scaffold regenerated the structure and its stubs were shown empty.
- [ ] The room filled the three commitment lines.

The planning source is [`../../plan/semana.md`](../../plan/semana.md); the deck
is [`../../presentation/d2.html`](../../presentation/d2.html). Day 1's runbook
([`../d1/`](../d1/)) remains the format precedent.
