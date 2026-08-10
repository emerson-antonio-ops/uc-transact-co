# 00 - Setup (Checkpoint A: Environment)

Act 1 - Why this system matters (19:00-19:15)

## Question

The CFO asks: "How much revenue did we make yesterday, and why should I trust
that number?" Before answering anything, can we prove the system we inherited
is running and inspectable?

## Authority boundary

- Shell commands only; no agent yet.
- Read-only inspection. No schema changes, no data changes.
- Do not run `make inject`, `make reveal`, or `make score`.

## Run this

Before the session (once, with reliable network):

```bash
make bootstrap
```

Live, in front of the room:

```bash
make up
make doctor
make status
```

Then show the four tables exist and hold data, without interpreting
relationships yet:

```bash
make query-ro Q="select count(*) from raw.customers"
make query-ro Q="select count(*) from raw.products"
make query-ro Q="select count(*) from raw.orders"
make query-ro Q="select count(*) from raw.payments"
```

## Proof that counts

- `make doctor` reports a healthy environment.
- `make status` shows the clean baseline: ~5,000 customers, 400 products,
  ~64,000 orders, ~62,000 payments (order/payment counts are seed-relative).
- The room can restate the business problem and name the four entities.

## If it fails

Follow the recovery paths in `plan/semana.md` Appendix B6:
`make up && make doctor`, or for a disposable volume
`make reset && make doctor && make land`.
