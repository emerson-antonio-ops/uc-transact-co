# TransactCo

> "The analytics are killing the store."

TransactCo is a high-volume e-commerce company. The storefront and the analytics
run on the same Postgres — `customers`, `products`, `orders`, `payments`. The two
workloads fight for the same resources: analytical scans stall order processing,
and transactional load makes the revenue report crawl. The CFO wants a dashboard
they can trust. Everyone knows that running it against the production database is
a time bomb.

The slowness is not the real problem. **The data lies in silence.** A renamed
column breaks a pipeline without raising an error. A duplicated payment inflates
revenue. An orphan order references a customer that does not exist. Nobody
notices — until the month-end close does not add up.

This repository is the system that already runs. It is the starting point, not
the finished product.

---

## What ships here, and what you build

| Ships in this repo | You build it live |
| --- | --- |
| Postgres with the schema applied at boot | The agents that read, move and transform |
| The correlated seeder | The dbt layers: `staging` → `intermediate` → `marts` |
| The 14-defect generator | The incident detector |
| The answer key isolated from the analytical path in `_control` | The loop that ties it together into one command |
| `make land` — the Postgres → DuckDB crossing | |

The base is deterministic and boring on purpose. Everything interesting is
what gets built on top of it.

---

## Quickstart

Requires Docker and [uv](https://docs.astral.sh/uv/). Nothing else.

```bash
make bootstrap # rebuild the clean Day 1 fixture and prove every base contract
make status    # row counts and freshness
```

Run `make setup` **before** class, not during it. It downloads the DuckDB
Postgres extension, and that is the one step that needs network.

`make help` lists everything.

---

## Architecture

One direction only. The whole warehouse is a single embedded file — no server,
no container. Close the laptop and the warehouse comes with you.

```
  POSTGRES · public.*                    _control.*
  customers · products                   the sealed answer key
  orders · payments                      never crosses  ✗
        │
        │  make land · ATTACH read-only
        ▼
  warehouse.duckdb  (one file)
  ├── raw.*            mirror of Postgres, drift included   ← ships ready
  ├── staging          cleaning                             ← you build
  ├── intermediate     business rules                       ← you build
  └── marts            fct_revenue_daily · dim_customers    ← you build
        │
        ▼
  "how much revenue yesterday, and was there an incident?"
```

`raw.*` is a faithful mirror. If a defect renamed a column upstream, the renamed
column lands here too — a landing step that quietly repaired the source would
hide the exact failure you are supposed to find.

### Documentation map

| Document | Audience | Purpose |
| --- | --- | --- |
| [`plan/semana.md`](plan/semana.md) | Facilitator | Canonical storytelling, curriculum, demo and validation plan |
| [`docs/day-01/`](docs/day-01/) | Participants | Day 1 concepts, data, worksheets and technical-brief artifacts |
| [`docs/facilitator/day-01-runbook.md`](docs/facilitator/day-01-runbook.md) | Facilitator | Commands, checkpoints, evidence and recovery paths |
| [`docs/semana-agentic-uc-transact-co-v2.pdf`](docs/semana-agentic-uc-transact-co-v2.pdf) | Internal team | Released Semana source document |

The root README spans the whole week and names later-day incident and scoring
surfaces. Do not load it into the Day 1 agent context. The participant entry
point for Day 1 is `docs/day-01/README.md`; the facilitator allowlist is defined
in `plan/semana.md`.

### The four tables

There are no foreign keys and no check constraints. That is deliberate. An
orphan payment cannot exist in a database that enforces referential integrity,
and a negative price cannot exist under a `CHECK` — a constrained schema would
make the whole case impossible. It is also what fast-growing transactional
systems actually look like after constraints get dropped "temporarily" for a
migration that shipped two years ago.

Every table carries two timestamps that mean different things: the business time
(`ordered_at`, `paid_at`) and `ingested_at`, when the row reached the database.
The gap between them is what makes late arrival and source staleness detectable.

The seam that holds the model together: **`payments.amount` should equal
`orders.total_amount`** for the same order. The seeded baseline honours it to the
cent.

---

## The 14 defects

Names only. What each one does is the answer key.

**Data quality** — `negative_price` · `missing_customer` · `invalid_quantity` ·
`duplicate_order` · `orphan_payment` · `malformed_data`

**Schema and behavior** — `schema_drift` · `late_arrival` · `volume_spike` ·
`recurring_incident` · `ambiguous_anomaly` · `destructive_fix` · `slow_source` ·
`multi_failure_cascade`

```bash
make inject                      # the default scenario, announced
make inject-quiet                # the same thing, in silence
make inject SCENARIO=deep        # six incidents
make inject SCENARIO=all         # all 14
make inject DEFECT=schema_drift  # one by name
make defects                     # list them
```

Injection is atomic. If anything fails, or if the answer key ends up pointing at
rows that no longer exist, the whole thing rolls back rather than shipping a
fixture that scores students wrong.

One of the 14 is not an incident at all. Finding out which one is the point.

---

## The detector contract

Your detector writes into `analytics.detections` in `warehouse.duckdb`. The table
is created empty by `make land` and is never overwritten by re-landing.

| column | meaning |
| --- | --- |
| `detection_id` | free-form, for your own grouping |
| `defect_type` | one of the 14 names |
| `target_table` | `customers` \| `products` \| `orders` \| `payments` |
| `row_key` | primary key of the offending row, as text (`NULL` if the defect has no rows) |
| `evidence` | free text, not scored — read out loud during review |
| `detected_at` | defaults to `now()` |

One row per offending row:

```sql
INSERT INTO analytics.detections (detection_id, defect_type, target_table, row_key, evidence)
SELECT 'orphans-01', 'orphan_payment', 'payments', CAST(p.payment_id AS VARCHAR),
       'order_id has no matching row in raw.orders'
FROM raw.payments p
LEFT JOIN raw.orders o USING (order_id)
WHERE o.order_id IS NULL;
```

Then:

```bash
make score
```

Scoring asks two questions separately, because they fail independently:

- **Did you find the right defect?** Incident-level precision and recall.
- **Did you find the right rows?** Row-level precision and recall.

A detector can name every incident correctly while pointing at the wrong rows,
and it can find exactly the right rows for an incident it has misnamed. Reporting
a defect that was never injected costs precision. So does flagging the one event
that looks like an incident and is not.

`make reveal` opens the answer key. Score first.

---

## The sealed oracle

The answer key lives in the `_control` schema and never crosses into DuckDB.
Postgres permissions enforce that boundary for the `analytics_ro` connection;
the landing script does not merely omit the schema by convention.

`make land` connects as `analytics_ro`, a role with `SELECT` on `public` and no
grant on `_control` at all. Every run attempts to read the answer key with that
role and prints the refusal:

```
sealed: permission denied for schema _control
```

This is a workflow and analytical-path seal, not an adversarial security boundary
against the owner of the laptop. A local administrator can inspect the injection
implementation, enter the container, or use instructor commands. Day 4 must give
the detector only the intended analytical context, or move instructor truth into
a separate controlled environment if a genuinely private holdout is required.

---

## Command reference

| command | what it does |
| --- | --- |
| `make setup` | `.env`, dependencies, DuckDB extension. Run before class. |
| `make bootstrap` | Rebuilds and proves the clean Day 1 fixture; removes the generated DuckDB file and later-day detections. |
| `make doctor` | Checks Postgres, schema, seal and extension. |
| `make test` | Runs the fast unit contract checks. |
| `make verify` | Verifies the clean baseline, Postgres/DuckDB parity and oracle isolation. |
| `make dbt-check` | Validates the empty dbt shell without creating student models. |
| `make up` / `make down` | Start / stop Postgres. |
| `make seed` | Load data and verify the baseline is clean. |
| `make land` | Postgres → DuckDB, and prove the seal. |
| `make inject` | Inject defects and seal the answer key. |
| `make inject-quiet` | The same, saying nothing about what landed. |
| `make score` | Score `analytics.detections` against the oracle. |
| `make reveal` | Open the answer key. |
| `make status` | Row counts and freshness. No spoilers. |
| `make reset` | Destroy the database and rebuild it clean. |
| `make psql` | Open `psql` in the container. |
| `make psql-ro` | Open Postgres as the Day 1 read-only role. |
| `make query Q="select 1"` | Run SQL against the warehouse. |
| `make query-ro Q="select 1"` | Run SQL against the warehouse in read-only mode. |

---

## Notes for running this

**Reproducibility.** The same `TRANSACTCO_SEED` reproduces the generation logic,
customer/catalog shape, and historical relationships for a given seed-time
anchor. The 90-day window is anchored to the moment you seed so freshness remains
meaningful. The partial current day is generated only up to that moment, so
laptops seeded at different times can have slightly different final row counts.
The answer key is written against each laptop's own rows.

**Size.** Roughly 64,000 orders over 90 days. Seeding takes about two seconds and
landing about one. Tune with `SEED_DAYS`, `SEED_ORDERS_PER_DAY`, `SEED_CUSTOMERS`
and `SEED_PRODUCTS` in `.env`.

**Starting over.** `make reset` destroys the volume, reapplies the schema at boot,
reseeds and deletes the warehouse file. Use it between rehearsals — injected
defects accumulate otherwise, and `make inject` refuses to inject the same defect
twice without `--force`.

**Credentials.** `.env.example` ships with local passwords in plain text. This is
a teaching fixture that runs on a laptop; nothing here is secret.

**dbt.** `dbt/` holds a project file and a DuckDB profile pointing at
`warehouse.duckdb`, and no models. The plumbing is here so nobody loses stage
time to a profile path; the transformations are the exercise. `make setup`
installs the adapter, and `make dbt-check` validates the empty shell.

---

## Troubleshooting

**`make land` fails on the extension.** DuckDB downloads the Postgres extension
on first use. Run `make setup` while you still have good network.

**Port 5432 already in use.** Set `POSTGRES_PORT` in `.env` to something else and
run `make up` again.

**Schema changes in `infra/postgres/init/` are not showing up.** Those scripts run
only when the data volume is created. `make reset` recreates it.

**`make seed` fails on a missing column.** A schema defect is still applied. Seeding
repairs that automatically; if it persists, `make reset`.
