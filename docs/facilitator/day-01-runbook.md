# Day 1 Facilitator Runbook

This runbook is operational evidence and recovery guidance. The canonical story,
slides, concepts, and timing live in [`plan/semana.md`](../../plan/semana.md).

## Validated baseline

Validated locally on 2026-08-10 from a newly recreated Docker volume:

```bash
make bootstrap
make status
```

Observed clean baseline with the default `.env.example` settings:

| Table | Rows |
| --- | ---: |
| `public.customers` | 5,000 |
| `public.products` | 400 |
| `public.orders` | approximately 64,000 |
| `public.payments` | approximately 62,000 |

The exact timestamps and final partial-day row counts are relative to seed time.
Do not promise identical order/payment counts or wall-clock timestamps on every
laptop.

## Pre-session checklist

- [ ] Docker is running.
- [ ] `uv` is installed.
- [ ] `make bootstrap` completed while network was reliable.
- [ ] The bootstrap output shows doctor readiness, passing unit contracts,
  seven passing delivery checks, and a passing dbt connection/parse.
- [ ] `make status` shows the expected clean row-count range and freshness.
- [ ] The reviewed baseline is committed, and the exact revision used for class
  is recorded.
- [ ] The Day 1 context pack opens locally.
- [ ] The presentation opens without missing fonts or assets.
- [ ] Weak-prompt and structured-prompt fallback outputs are available.
- [ ] Ontology v1 and technical-brief fallback artifacts are available.
- [ ] Telemetry collection has been implemented and rehearsed, or is described
  honestly as a manual contract demonstration.

`make bootstrap` intentionally replaces the generated `warehouse.duckdb` file
so the presentation starts with zero detector rows. Do not run it over a
participant's later-day work without first preserving that generated artifact.

## Safe Day 1 commands

```bash
make doctor
make status
make query-ro Q="select count(*) from raw.orders"
```

Use approved read-only SQL for live investigation. Do not run `make inject`,
`make reveal`, or `make score` during Day 1.

## Evidence already validated

- Fresh Docker-volume initialization applies the three Postgres init scripts.
- The baseline seeder completed and passed its clean-data assertions.
- `analytics_ro` could read the public path and was denied access to `_control`.
- `analytics_ro` was denied writes to `public.customers`.
- `make psql-ro` opened with the intended analytical role.
- `make query-ro` could read DuckDB and rejected a `CREATE TABLE` statement.
- DuckDB row counts matched Postgres for all four source tables.
- DuckDB contained no control/injected-incident tables.
- The all-defects scenario injected 14 incident records and landed successfully.
- Every named defect injector completed independently.
- The scorer returned 100% precision, recall, and F1 against a perfect validation
  fixture.
- Re-landing preserved existing `analytics.detections` rows.
- `dbt debug` connected to DuckDB and `dbt parse` validated the deliberately
  empty model shell.

## Truth boundary

The current seal protects the `analytics_ro` and DuckDB landing path. It does not
hide instructor truth from the owner of the local laptop or repository. Keep the
Day 1 agent on the approved context pack and operational investigation surfaces.
Before Day 4, choose whether a workflow seal is sufficient or move the oracle
and injection implementation into an instructor-controlled environment.

## Recovery paths

### Postgres is unavailable

```bash
make up
make doctor
```

If the volume is disposable and initialization is suspect:

```bash
make reset
make doctor
make land
```

`make reset` destroys the local teaching database volume. Never use it against a
non-disposable database.

### DuckDB landing is missing or stale

```bash
make land
make verify
```

### DuckDB extension is unavailable

Run `make setup` with network access. Keep a pre-warmed facilitator environment
and prepared evidence screenshots/output for the live session.

### The live agent run fails

- Keep the failure visible if it teaches a real boundary.
- Do not present a prepared output as if it were generated live.
- Switch to the prepared context inventory or ontology checkpoint.
- Continue the human review and skill distillation.

## Current gap

The repository contains a telemetry contract but no verified live telemetry
emitter or tracing adapter yet. This does not block the Postgres/DuckDB Day 1
investigation, but it blocks claiming that telemetry is being collected
automatically. Implement and rehearse that surface before putting it in the live
demo path.
