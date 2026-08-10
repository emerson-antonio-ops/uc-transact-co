# 06 - Technical Brief (Checkpoint F: Technical brief)

Act 6 - Why documentation and reflection matter (21:35-22:00)

## Question

Everything we learned tonight lives in a chat session. What survives until
tomorrow?

## Authority boundary

- The agent writes the brief from the artifacts already produced, not from
  memory or new invention.
- The brief proposes; it does not approve. ADR candidates stay candidates.
- Human review closes the gate, not the agent.

## Run this

```text
Produce the TransactCo technical brief using the technical brief template.
Build it only from the artifacts of this session: Investigation Prompt v1,
the context inventory and evidence ledger, Ontology v1, and the investigation
trace. Every important claim must carry its evidence reference from the
ledger. Separate facts, inferences, decisions, and open questions - do not
upgrade an inference to a fact while summarizing. List ADR candidates with
the decision required, alternatives, evidence available, and the missing
owner or input; do not write them as approved decisions. Include the open
questions table with an owner for each question. Mark the brief status as
draft pending human review.
```

Then review it live as the human gate: pick two claims and trace each back to
its evidence; pick one open question and confirm it has an owner.

## Proof that counts

- The brief can be reviewed without replaying the chat.
- Facts, inferences, decisions, and questions are separated correctly.
- ADR candidates are proposals, not approved records.
- A human review is recorded and the gate outcome is explicit.
- Artifact produced: the d1 technical brief, status draft/reviewed.

## If it fails

Open the prepared draft brief and perform the same live human review on it.

## Skill distilled

Fill
[`../../skills/d1/S6-technical-brief.md`](../../skills/d1/S6-technical-brief.md),
then close the day with the reflection questions and the full skill set
review in [`../../skills/d1/README.md`](../../skills/d1/README.md).
