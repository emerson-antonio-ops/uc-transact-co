# 00 — Environment and Business Tension

Time: 19:00–19:15 · Slides 1–3 · Mode: deck → repository

## Question

> How much revenue did TransactCo make yesterday, and why should the CFO trust
> that number?

Before answering, prove that the inherited system is healthy, inspectable, and
safe to investigate.

## Authority boundary

- Shell and repository inspection only; no agent investigation yet.
- Read-only inspection of the clean teaching environment.
- Do not run injection, reveal, scoring, reset, or source mutations.

## Facilitator preflight

Run before participants join:

```bash
cd /Users/luanmorenomaciel/GitHub/uc-transact-co
git status --short
git rev-parse --short HEAD
make bootstrap
make status
uv run transactco ontology validate
python3 /Users/luanmorenomaciel/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/interview-the-system
mkdir -p tmp/foundation-investigation/manual
mkdir -p tmp/foundation-investigation/skill
```

`make bootstrap` replaces the generated warehouse. Use it only for the clean
teaching baseline, never over work that must be preserved.

## Run live

```bash
pwd
git rev-parse --short HEAD
make doctor
make status
```

Show only the repository’s top-level structure and the four source entities.
Do not explain their full relationships yet.

## Say

> The first half of the CFO’s question asks for SQL. The second asks for
> semantics, evidence, system boundaries, and operational safety.

## Follow along

Record:

1. The four source entities.
2. The operational and analytical systems.
3. One reason a precise result could still be wrong.
4. One reason analytics could harm the operational store.

## Proof that counts

- `make doctor` reports the environment ready.
- `make status` shows Customers, Products, Orders, and Payments.
- Participants can explain that availability and row counts do not establish
  a Revenue definition.

## Recovery

```bash
make up
make doctor
```

For a disposable local teaching volume only, use the destructive recovery in
the [canonical runbook](README.md#recovery-matrix).

Next: [`01-weak-prompt.md`](01-weak-prompt.md).
