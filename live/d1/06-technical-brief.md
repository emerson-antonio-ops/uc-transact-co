# 06 — Technical Brief and Human Gate

Time: 21:22–21:38 · Slide 12 · Mode: agent → human review

## Question

What survives after the chat session closes?

## Authority boundary

- Use only artifacts and evidence created during the confirmed investigation.
- Do not introduce new claims while summarizing.
- ADRs remain candidates until an authorized human decides.
- Status remains `pending human review` while Revenue meaning is unresolved.

## Paste

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

## Inspect

```bash
sed -n '1,300p' tmp/foundation-investigation/manual/technical-brief.md
```

## Human review

1. Trace two facts to evidence.
2. Ask what would falsify one inference.
3. Verify the owner of one decision.
4. Verify the next action for one open question.
5. Confirm that structural review did not approve Revenue semantics.

## Proof that counts

- The brief can be reviewed without replaying chat history.
- Facts, inferences, decisions, and questions remain separate.
- Evidence references are reproducible.
- ADR candidates remain proposals.
- The human gate outcome is explicit.

Next: [`07-skill-reveal.md`](07-skill-reveal.md).
