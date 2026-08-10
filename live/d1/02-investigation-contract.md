# 02 - Investigation Contract (Checkpoint B: Prompt contrast)

Act 2 - Why prompts matter (19:15-19:40)

## Question

If a prompt is a contract for the next piece of work, what does the contract
for this investigation need to say?

## Authority boundary

- Read-only repository and database access.
- The agent must not modify the database or application code.
- The agent must stop and ask when a conclusion requires business authority.

## Run this

Build it with the audience clause by clause (objective, context, questions,
tools, authority, evidence, output, stopping), then paste:

```text
Investigate how TransactCo represents revenue. Use the approved repository
context and read-only database access. Identify the relevant entities,
relationships, business invariants, operational risks, and unresolved business
questions. Support every important claim with a repository path, schema object,
or query. Clearly label facts, inferences, decisions, and open questions. Do not
modify the database or application code. Stop and ask when a conclusion requires
business authority rather than technical evidence.
```

## Proof that counts

- The room can explain why each clause exists and predict the failure it
  prevents, by contrast with the weak-prompt run.
- Artifact produced: Investigation Prompt v1 (this file's prompt, plus any
  clause the room added live).

## If it fails

Use the saved structured-prompt output from the speaker notes for the
comparison, labeled as prepared.

## Skill distilled

Complete
[`../../skills/d1/S1-prompt-as-contract.md`](../../skills/d1/S1-prompt-as-contract.md)
using the weak-versus-structured contrast as evidence.
