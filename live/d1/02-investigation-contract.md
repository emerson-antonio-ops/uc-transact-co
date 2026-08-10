# 02 — Investigation Contract

Time: 19:30–19:50 · Slide 5 · Mode: group → agent

## Question

What must be agreed before an agent is allowed to interview an existing
system?

## Explain why

| Contract element | Failure it prevents |
| --- | --- |
| Objective and outcome | Impressive work that solves the wrong problem |
| Scope and exclusions | Silent expansion into unrelated or sensitive systems |
| Allowed tools | Tool use without authority |
| Prohibited actions | Accidental mutation or spoiler exposure |
| Required evidence | Unsupported claims presented as truth |
| Output artifacts | Knowledge trapped in chat history |
| Stop conditions | The agent inventing decisions it cannot own |

## Grill the frontier

Ask the room:

1. What exact outcome does the CFO need?
2. Which systems and time window are in scope?
3. What may the agent inspect or write?
4. What evidence would support or falsify a claim?
5. Which decisions need a business owner?
6. What ends or pauses the investigation?

## Paste

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

Review it with the room. Change missing or incorrect clauses. Then paste:

```text
Contract confirmed. Do not widen it without asking.
```

## Proof that counts

- No investigative tool was used before confirmation.
- The contract names objective, authority, evidence, output, and stops.
- Participants can name the failure prevented by each clause.

Next: [`03-context-inventory.md`](03-context-inventory.md).
