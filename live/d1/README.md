# Day 1 — Interview the System Before You Build

Canonical live sequence · 19:00–22:00 · facilitator and participant edition

## The promise

By the end of the session, participants will not merely have watched an agent
query a database. They will have practiced a repeatable method for turning an
unclear brownfield request into:

- a bounded investigation contract;
- deliberately selected context;
- claims separated into facts, inferences, decisions, and questions;
- an evidence-aware ontology;
- an inspectable agent trajectory;
- a technical brief pending human review;
- a reusable `interview-the-system` skill.

These are six practiced capabilities, not six separate installable skills. The
closing reveal shows how prompt contracting, context selection, system
interviewing, ontology modeling, trajectory inspection, and technical briefing
compose into one reusable [`interview-the-system`](../../skills/interview-the-system/SKILL.md)
workflow.

The business question carried through the entire session is:

> How much revenue did TransactCo make yesterday, and why should the CFO trust
> that number?

## How to read this runbook

Every segment uses the same labels:

- **DECK** — show or explain the concept.
- **SAY** — a suggested transition or framing line.
- **DO** — facilitator action or exact command.
- **PASTE** — exact prompt for the agent.
- **FOLLOW ALONG** — participant action.
- **PROOF** — visible evidence required before moving on.
- **RECOVERY** — honest fallback if the live path fails.

The checkpoint files linked from each segment contain the same commands in a
smaller copy/paste surface.

## What is given, discovered, and unresolved

Keep these boundaries visible throughout the session.

| Category | What belongs here | Why |
| --- | --- | --- |
| Given | CFO question, four source tables, read-only authority, operational safety | Prevent irrelevant confusion |
| Discovered | Physical joins, cardinality, timestamps, status values, reconciliation signals | Make investigation real |
| Unresolved | Revenue recognition event, included statuses, refund policy, currency and timezone policy | Teach where business authority begins |

## Artifact workspace

All live agent writes go under this ignored directory:

```text
tmp/foundation-investigation/
├── manual/
│   ├── context-and-claims.md
│   ├── ontology-notes.md
│   ├── trace.jsonl
│   └── technical-brief.md
└── skill/
    ├── investigation.json
    ├── trace.jsonl
    └── technical-brief.md
```

Do not let the agent write anywhere else during this session.

## Three-hour run of show

| Time | Mode | Segment | Visible outcome |
| --- | --- | --- | --- |
| 19:00–19:15 | Deck → repository | [The business tension and inherited system](00-setup.md) | Healthy, inspectable brownfield |
| 19:15–19:30 | Agent demo | [Weak prompt](01-weak-prompt.md) | Unsupported assumptions become visible |
| 19:30–19:50 | Group → agent | [Investigation contract](02-investigation-contract.md) | Objective, authority, evidence, and stops confirmed |
| 19:50–20:15 | Repository → agent | [Deliberate context](03-context-inventory.md) | Context inventory and claim ledger |
| 20:15–20:25 | Break | Reset | Facilitator verifies the next commands |
| 20:25–20:45 | Postgres | [Physical answer](04-ontology.md) | Precise aggregates and visible assumptions |
| 20:45–21:00 | Ontology CLI | [Semantic answer](04-ontology.md) | `Revenue` is correctly blocked on owned decisions |
| 21:00–21:22 | Agent + trace | [Agentic investigation](05-agentic-investigation.md) | Tool, claim, evidence, rejection, and escalation trail |
| 21:22–21:38 | Agent + review | [Technical brief](06-technical-brief.md) | Durable draft with human gate |
| 21:38–21:55 | Skill reveal | [Automate the method](07-skill-reveal.md) | Validated evidence package from reusable skill |
| 21:55–22:00 | Reflection | [Close the loop](08-reflection.md) | Learning, decision, risk, and next action named |

The deck is braided into the demonstration. Do not give a one-hour lecture and
then open the repository.

## Participant preparation

Choose one participation mode before the session:

- **Hands-on:** each participant uses a fresh clone at the facilitator’s exact
  revision, Docker, `uv`, a terminal, and an agent with access to that clone.
- **Guided:** participants keep this runbook open, complete the follow-along
  tables, and inspect the facilitator’s evidence without running a local stack.

For hands-on participation, prepare before 19:00:

```bash
git clone https://github.com/luanmorenommaciel/uc-transact-co.git
cd uc-transact-co
git checkout <revision-provided-by-the-facilitator>
make bootstrap
```

Use `git checkout` here only in a fresh teaching clone. Participants with
existing work should preserve it and use a separate clone or worktree. During
the session, everyone uses the same revision and clean baseline; nobody runs
`make bootstrap`, `make reset`, or an injection command unless the facilitator
explicitly begins a separate exercise.

---

## Before participants join — facilitator preflight

Complete this while network access is reliable. `make bootstrap` rebuilds the
generated warehouse; do not run it over later participant work that must be
preserved.

```bash
cd /Users/luanmorenomaciel/GitHub/uc-transact-co
git status --short
git rev-parse --short HEAD
make bootstrap
make status
uv run transactco ontology validate
python3 /Users/luanmorenomaciel/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/interview-the-system
```

Expected gates:

- Git revision used for the session is recorded.
- The intended teaching worktree is clean.
- Postgres is healthy and seeded.
- DuckDB contains the four landed `raw.*` tables.
- Unit and delivery checks pass.
- Ontology prints `ONTOLOGY=VALID` while remaining `pending human review`.
- Skill prints `Skill is valid!`.

Create the artifact directories:

```bash
mkdir -p tmp/foundation-investigation/manual
mkdir -p tmp/foundation-investigation/skill
```

If these directories contain a previous rehearsal, move that rehearsal to a
clearly labeled archive before class. Do not silently mix prepared and live
artifacts.

Arrange four windows before 19:00:

1. Deck in presentation mode.
2. Editor open at this file.
3. Terminal at the repository root with a large font.
4. Agent session at the repository root.

Keep [`00-setup.md`](00-setup.md) open as the recovery card.

---

## 19:00–19:15 — Establish the business tension

### DECK

Use slides 1–3: Semana, the precise-but-wrong report, and the inherited system.

### SAY

> The CFO’s first question asks for SQL. The second asks for meaning, evidence,
> and safety. Tonight we will learn why those are different engineering
> problems.

Define only what participants need now:

- **Brownfield:** a system with history, implicit rules, and existing users.
- **Operational workload:** work that keeps the store running.
- **Analytical workload:** work that scans and explains the store.
- **Trustworthy metric:** a number with declared meaning, provenance, and proof.
- **Business time versus ingestion time:** when the event happened versus when
  its row arrived.

### DO

Open the repository root. Show `README.md`, `infra/`, `src/`, `tests/`, `live/`,
and `skills/` without explaining every file.

```bash
pwd
git rev-parse --short HEAD
make doctor
make status
```

### FOLLOW ALONG

Write down:

1. The business question.
2. The four visible source entities.
3. One reason an analytical query could harm an operational system.
4. One reason a numerically correct result could still be semantically wrong.

### PROOF

Do not continue until the room can say:

- Customers, Products, Orders, and Payments are present.
- The source is operational Postgres; the analytical copy is DuckDB.
- A row count proves availability, not business meaning.

Detailed card: [`00-setup.md`](00-setup.md).

---

## 19:15–19:30 — Experience the weak-prompt failure

### DECK

Use slide 4: a prompt is a contract for the next piece of work.

### SAY

> Let’s begin with the request most people would actually type. Do not judge the
> prose. Judge the work contract.

Run this demonstration with write tools disabled or deny any requested write.
The weak prompt must be pedagogically weak without making the environment
unsafe.

### PASTE

```text
Analyze this database and explain revenue.
```

### FOLLOW ALONG

While the response streams, record one example in each applicable row:

| Failure | Evidence from the response |
| --- | --- |
| Assumption presented as fact | |
| Important claim without a source | |
| Revenue semantics invented or ignored | |
| Authority boundary absent | |
| Stop condition absent | |

### SAY

> Fluency is not evidence. A confident answer can hide an undefined task.

### PROOF

The room identifies at least three concrete defects in the response. Keep the
output visible; it becomes comparison evidence.

Detailed card: [`01-weak-prompt.md`](01-weak-prompt.md).

---

## 19:30–19:50 — Construct the investigation contract

### DECK

Use slide 5: objective, context, authority, evidence, output, and stopping.

### SAY

> Before an agent interviews a system, we must agree on the question, the room
> it may enter, the evidence we will accept, and the moment it must call a
> human.

Ask the room the frontier questions:

1. What exact outcome does the CFO need?
2. Which systems and time window are in scope?
3. What may the agent inspect or write?
4. What evidence would support or falsify its claims?
5. Which decisions require a business owner?
6. What condition ends the investigation?

### PASTE

```text
Do not investigate yet. Draft an investigation contract for this question:
“How much revenue did TransactCo make yesterday, and why should the CFO trust
that number?”

The contract must contain: objective, expected outcome, in-scope systems and
time window, explicit exclusions, allowed tools, prohibited actions, evidence
required, output artifacts, and stop or escalation conditions. Use these
defaults unless the facilitator changes them:

- inspect only the approved repository paths and local teaching databases;
- run read-only queries only;
- write artifacts only under tmp/foundation-investigation/manual/;
- do not inspect _control, injection, scoring, or instructor-only surfaces;
- do not modify source code, schemas, operational data, or infrastructure;
- label material claims as fact, inference, decision, or question;
- stop when business meaning requires an accountable owner.

Return the proposed contract and wait for explicit confirmation before using
tools.
```

Review every clause aloud. Change it if the room finds a missing boundary, then
say:

```text
Contract confirmed. Do not widen it without asking.
```

### PROOF

The agent waits before tool use, the room can explain the failure prevented by
each clause, and the contract has a human confirmation.

Detailed card: [`02-investigation-contract.md`](02-investigation-contract.md).

---

## 19:50–20:15 — Select context and build the claim ledger

### DECK

Use slides 6–7: the prompt defines the work; context supplies the world.

### SAY

> More context is not automatically better context. Context engineering is the
> selection, ordering, provenance, and authority of evidence.

For this phase, approve only:

1. `README.md` — business tension and system boundary.
2. `infra/postgres/init/01_schema.sql` — physical Postgres structure.
3. `src/transactco/operational/seed.py` — generated baseline behavior.
4. `src/transactco/operational/postgres.py` — connection and source-table code.
5. Read-only Postgres queries — runtime evidence.

Do **not** approve `src/transactco/domain/` yet. The ontology reveal must come
after the room experiences the limitation of the physical answer.

### PASTE

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

### DO

Inspect the artifact rather than accepting the chat summary:

```bash
sed -n '1,260p' tmp/foundation-investigation/manual/context-and-claims.md
```

### FOLLOW ALONG

Choose one claim and answer:

- Which source supports it?
- Is that source authoritative for physical structure or business meaning?
- What would falsify the claim?

### PROOF

Every fact has a reproducible source. Revenue semantics remain open rather than
being inferred from table names.

Detailed card: [`03-context-inventory.md`](03-context-inventory.md).

---

## 20:15–20:25 — Break and reset

Keep Postgres running. During the break, verify:

```bash
make doctor
uv run transactco ontology validate
```

Open [`04-ontology.md`](04-ontology.md) and keep the physical-query fallback
ready. Do not run injection or reset commands.

---

## 20:25–20:45 — Ask Postgres for the physical answer

### DECK

Return with slide 8, but do not define ontology yet.

### SAY

> We have a precise question and grounded context. Now let’s ask the system that
> stores the transactions.

### PASTE

```text
Using only the confirmed contract, approved physical context, and read-only
Postgres access, investigate yesterday’s candidate payment amount in UTC.
First inspect the available payment statuses. Then return the aggregate count
and sum by status for the previous completed UTC calendar day. Show the exact
query and evidence. Separate the physical result from every assumption needed
to call it Revenue. Do not inspect the ontology yet and do not choose a revenue
policy.
```

If the agent cannot execute SQL, use the terminal fallback:

```bash
make psql-ro
```

Then paste into `psql`:

```sql
\pset pager off
\timing on
BEGIN TRANSACTION READ ONLY;

SELECT status, count(*) AS payment_rows, sum(amount) AS amount_sum
FROM public.payments
GROUP BY status
ORDER BY status;

WITH bounds AS (
  SELECT
    (date_trunc('day', now() AT TIME ZONE 'UTC') - interval '1 day')
      AT TIME ZONE 'UTC' AS start_utc,
    date_trunc('day', now() AT TIME ZONE 'UTC')
      AT TIME ZONE 'UTC' AS end_utc
)
SELECT
  p.status,
  count(*) AS payment_rows,
  sum(p.amount) AS amount_sum
FROM public.payments AS p
CROSS JOIN bounds AS b
WHERE p.paid_at >= b.start_utc
  AND p.paid_at < b.end_utc
GROUP BY p.status
ORDER BY p.status;

SELECT count(*) AS declared_foreign_keys
FROM pg_constraint
WHERE connamespace = 'public'::regnamespace
  AND contype = 'f';

COMMIT;
\q
```

### FOLLOW ALONG

Do not calculate a final revenue metric. Instead, list the decisions hidden by
the aggregate:

- Which statuses count?
- Which event recognizes revenue?
- How are refunds, returns, discounts, fees, and taxes handled?
- Which timezone and currency policies apply?
- Does the absence of foreign keys change confidence in relationships?

### PROOF

Postgres returns precise values. The room can explain why precision does not
authorize the label `Revenue`.

---

## 20:45–21:00 — Query the ontology for meaning

### DECK

Use slides 8–9: ontology preserves meaning; entities, relationships, events,
rules, provenance, and owners.

### SAY

> The database can tell us what it stores. The ontology tells us what the
> organization has declared—and what it has not declared.

### DO

```bash
uv run transactco ontology validate
uv run transactco ontology list
uv run transactco ontology explain Revenue
```

Then show the machine-readable result:

```bash
uv run transactco ontology explain Revenue --json
```

### PASTE

```text
You may now inspect src/transactco/domain/transactco.ontology.json and the
output of `uv run transactco ontology explain Revenue --json`. Re-answer the
CFO’s question using both the physical query evidence and the ontology.
Separate: what the database proves, what the ontology currently declares,
which candidate inputs exist, which business decisions block a defensible
Revenue metric, and who owns those decisions. A controlled refusal is valid.
Do not invent a policy to make the answer complete.
```

### AHA MOMENT 1

Say this slowly:

> Postgres gave us more data. Ontology gave us a safer answer.

The expected result is `blocked_by_business_decisions`, owned by Finance. This
is not failure. It is higher-quality system behavior.

### DO

Ask the agent to write only the newly established ontology observations:

```text
Append the ontology observations, evidence references, and owned unresolved
questions to tmp/foundation-investigation/manual/ontology-notes.md. Keep the
status pending human review.
```

### PROOF

- Physical entities exist.
- Relationships without database constraints remain inferred unless tested.
- `Payment may_contribute_to Revenue` remains unresolved.
- Every unresolved meaning has an owner and exact question.

Detailed card: [`04-ontology.md`](04-ontology.md).

---

## 21:00–21:22 — Make the investigation inspectable

### DECK

Use slides 10–11: Agentic Development is controlled work; telemetry makes the
trajectory inspectable.

### SAY

> A chat gives us an answer. An agentic system performs bounded work through
> tools, observations, verification, and human gates. The final paragraph alone
> cannot prove that trajectory.

Draw the loop:

```text
objective -> context -> tool -> observation -> claim -> verification
          -> human decision -> durable artifact
```

Be explicit: the trace in this exercise is **self-reported telemetry emitted by
the investigating agent**. It demonstrates a contract and enables inspection;
it is not independent observation.

### PASTE

```text
Continue the confirmed revenue investigation. Perform controlled, read-only
work and emit one JSON object per significant action to:
tmp/foundation-investigation/manual/trace.jsonl

Each event must contain: timestamp, run_id, actor, phase, action, target,
ontology_entity (nullable), evidence_references (array), outcome, and
duration_ms. Emit events for context loading, repository inspection, query
execution, claim proposal, verification, rejection, question escalation,
artifact update, gate evaluation, and completion.

Never record secrets, connection strings, personal data, complete rows, or
secret-bearing prompts. Include at least one assumption that is tested and
rejected, plus at least one question escalated to its human owner. Keep all
database actions read-only and all writes under
tmp/foundation-investigation/manual/.

At completion, summarize sources used, queries executed, claims verified,
claims rejected, questions escalated, and artifacts written. Clearly label the
trace as self-reported telemetry.
```

### DO

Inspect the trajectory, not only the answer:

```bash
wc -l tmp/foundation-investigation/manual/trace.jsonl
sed -n '1,8p' tmp/foundation-investigation/manual/trace.jsonl
rg -n 'rejected|question|escalat|gate' tmp/foundation-investigation/manual/trace.jsonl
```

### FOLLOW ALONG

Find one example of each:

- tool or source used;
- claim verified;
- claim rejected;
- question escalated;
- human gate encountered.

### PROOF

The room can reconstruct why the answer stopped where it stopped. Do not claim
automatic telemetry collection or independent instrumentation.

Detailed card: [`05-agentic-investigation.md`](05-agentic-investigation.md).

---

## 21:22–21:38 — Turn evidence into a durable brief

### DECK

Use slide 12: evidence becomes valuable when it survives the session.

### SAY

> If the reasoning exists only in chat history, tomorrow’s implementation will
> rebuild context from memory and repeat today’s mistakes.

### PASTE

```text
Create tmp/foundation-investigation/manual/technical-brief.md using only the
confirmed contract, context inventory, claim ledger, physical query evidence,
ontology observations, and self-reported trace from this session. Do not add
new conclusions.

Use these exact headings:

# Technical Brief
## Status
## Question and Outcome
## Scope and Authority
## Evidence Consulted
## Findings
## Ontology
## Decisions and Open Questions
## Risks and Stop Conditions
## Human Review

Set Status to `pending human review`. Separate facts, inferences, decisions,
and questions. Keep ADRs as candidates rather than approved decisions. Give
every open question an owner and next action. End with a human-review checklist.
```

### DO

```bash
sed -n '1,300p' tmp/foundation-investigation/manual/technical-brief.md
```

Human gate:

1. Pick two facts and trace them to evidence.
2. Pick one inference and ask what would falsify it.
3. Pick one decision and verify its owner.
4. Pick one open question and verify its next action.
5. Leave the status pending if business meaning is not approved.

### PROOF

The brief can be reviewed without replaying the chat and does not turn
uncertainty into false certainty.

Detailed card: [`06-technical-brief.md`](06-technical-brief.md).

---

## 21:38–21:55 — Reveal the reusable skill

### SAY

> We have practiced the method manually: grill, contract, context, physical
> evidence, ontology, trace, and human review. Now let’s encode the method so the
> next investigation starts with these disciplines by default.

Open [`../../skills/interview-the-system/SKILL.md`](../../skills/interview-the-system/SKILL.md).
Show the workflow headings without reading the entire file.

### PASTE

Use this form in any agent that can read the repository:

```text
Read skills/interview-the-system/SKILL.md and apply it to this request:
“Investigate how TransactCo can answer how much Revenue it made yesterday and
why that answer should be trusted.”

Use the already approved Day 1 context and evidence, re-run only the read-only
checks needed for freshness, and write the complete evidence package under
tmp/foundation-investigation/skill/. Begin with the frontier grill and proposed
investigation contract. Wait for my confirmation before investigative tool use.
```

If the skill is installed in the agent environment, the short invocation is:

```text
$interview-the-system Investigate how TransactCo can answer how much Revenue it
made yesterday and why that answer should be trusted. Write the evidence
package under tmp/foundation-investigation/skill/.
```

Confirm the contract when it matches the room’s decisions. Let the skill
produce:

- `investigation.json`;
- `technical-brief.md`;
- `trace.jsonl` when emitted.

### DO

Validate the result:

```bash
python3 skills/interview-the-system/scripts/validate_investigation.py \
  tmp/foundation-investigation/skill/investigation.json \
  tmp/foundation-investigation/skill/technical-brief.md \
  tmp/foundation-investigation/skill/trace.jsonl
```

If no trace was emitted, omit the final path.

Then show the package:

```bash
find tmp/foundation-investigation -maxdepth 2 -type f -print | sort
```

### AHA MOMENT 2

> The skill is not a magical answer. It is the method we just practiced,
> packaged with boundaries, artifacts, validation, and a human stop.

The validator finishing with `CHECK_INVESTIGATION=PASS` proves structural
completeness. It does not approve the Revenue definition; semantic review still
belongs to the named human owner.

Detailed card: [`07-skill-reveal.md`](07-skill-reveal.md).

---

## 21:55–22:00 — Reflect and close

Do not ask for vague impressions. Point to the artifacts and ask:

1. **What did we learn?**
2. **Why does it matter?**
3. **What decision follows?**
4. **What breaks downstream if that decision is wrong?**
5. **What remains manual and who owns it?**

Expected synthesis:

- A prompt establishes a work contract; it does not supply the world.
- Context is selected evidence with provenance and authority.
- Postgres answers physical questions; ontology governs declared meaning.
- Agentic Development is bounded tool use plus observation, verification, and
  human gates.
- Self-reported telemetry improves inspectability but is not independent proof.
- The reusable skill automates the method, not the business decision.

Close with:

> Today we learned to interview the system before changing it. Next, we use
> that grounded understanding to construct controlled analytical work.

Detailed card: [`08-reflection.md`](08-reflection.md).

---

## Recovery matrix

| Failure | Keep visible | Recovery |
| --- | --- | --- |
| Postgres unavailable | Connection failure | `make up && make doctor` |
| Local teaching volume is disposable and corrupt | Failed initialization | `make reset && make doctor && make land` — destructive to the local teaching volume |
| DuckDB missing or stale | Missing landing evidence | `make land && make verify` |
| Agent cannot run SQL | Tool limitation | Use `make psql-ro` and the supplied read-only SQL |
| Weak or structured agent run stalls | Real failure | Use prepared output, labeled **prepared** |
| Ontology CLI fails | Error output | Open the JSON and inspect `Revenue` manually; do not invent meaning |
| Trace is malformed | Validation or parsing failure | Keep it visible and inspect the contract manually |
| Skill run exceeds time | Incomplete live package | Show the grill and human stop live, then validate a rehearsed package labeled **prepared** |

Never repair a live failure by widening authority, revealing instructor truth,
or pretending a prepared artifact was generated in the room.

## Final completion gate

Day 1 closes only when participants can point to evidence for all of these:

- [ ] The environment was healthy and inspected read-only.
- [ ] The weak prompt’s failures were named.
- [ ] A human confirmed the investigation contract.
- [ ] Context sources were selected and bounded.
- [ ] Facts, inferences, decisions, and questions were separated.
- [ ] Postgres returned a physical result without silently defining Revenue.
- [ ] Ontology exposed the missing business decisions and owner.
- [ ] The agent trajectory showed evidence, rejection, and escalation.
- [ ] The technical brief remained pending human review.
- [ ] The reusable skill produced a structurally valid evidence package.
- [ ] The room stated what remains manual.
