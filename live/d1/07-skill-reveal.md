# 07 — Reveal `interview-the-system`

Time: 21:38–21:55 · Mode: manual method → reusable automation

## Question

We practiced the method manually. Can we make the next investigation start
with the same boundaries, evidence discipline, ontology, and human gate?

## Say

> We have practiced the method manually: grill, contract, context, physical
> evidence, ontology, trace, and human review. Now let’s encode the method.

Open [`../../skills/interview-the-system/SKILL.md`](../../skills/interview-the-system/SKILL.md)
and show the workflow headings.

Name the six capabilities the room has already practiced: prompt contracting,
context selection, system interviewing, ontology modeling, trajectory
inspection, and technical briefing. They now compose into one skill rather than
six disconnected prompt snippets.

## Paste — repository-readable form

```text
Read skills/interview-the-system/SKILL.md and apply it to this request:
“Investigate how TransactCo can answer how much Revenue it made yesterday and
why that answer should be trusted.”

Use the already approved Day 1 context and evidence, re-run only the read-only
checks needed for freshness, and write the complete evidence package under
tmp/foundation-investigation/skill/. Begin with the frontier grill and proposed
investigation contract. Wait for my confirmation before investigative tool use.
```

## Paste — installed-skill form

```text
$interview-the-system Investigate how TransactCo can answer how much Revenue it
made yesterday and why that answer should be trusted. Write the evidence
package under tmp/foundation-investigation/skill/.
```

Confirm the contract only after comparing it with the room’s decisions.

Expected package:

```text
tmp/foundation-investigation/skill/
├── investigation.json
├── technical-brief.md
└── trace.jsonl
```

The trace is optional. If present, it remains self-reported unless an
independent collector produced it.

## Validate

With a trace:

```bash
python3 skills/interview-the-system/scripts/validate_investigation.py \
  tmp/foundation-investigation/skill/investigation.json \
  tmp/foundation-investigation/skill/technical-brief.md \
  tmp/foundation-investigation/skill/trace.jsonl
```

Without a trace:

```bash
python3 skills/interview-the-system/scripts/validate_investigation.py \
  tmp/foundation-investigation/skill/investigation.json \
  tmp/foundation-investigation/skill/technical-brief.md
```

Inspect both manual and automated artifacts:

```bash
find tmp/foundation-investigation -maxdepth 2 -type f -print | sort
```

## Aha moment

> The skill is not a magical answer. It is the practiced method packaged with
> boundaries, artifacts, validation, and a human stop.

`CHECK_INVESTIGATION=PASS` proves structural completeness only. It does not
approve a Revenue definition or replace Finance.

## Proof that counts

- The skill begins with a frontier grill and waits for confirmation.
- The evidence package is structurally valid.
- Facts have evidence; questions and decisions have owners.
- `Revenue` remains unresolved until human semantic review.

Next: [`08-reflection.md`](08-reflection.md).
