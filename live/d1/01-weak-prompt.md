# 01 — Weak Prompt

Time: 19:15–19:30 · Slide 4 · Mode: deck → agent

## Question

What happens when we give the agent the request most people would actually
type?

## Authority boundary

- Run with write tools disabled, or deny every write request.
- Minimal context is intentional.
- The prompt is weak; the environment must remain safe.

## Paste exactly

```text
Analyze this database and explain revenue.
```

Do not rescue the agent while it answers.

## Follow along

Capture evidence from the response:

| Failure | Evidence from the response |
| --- | --- |
| Assumption presented as fact | |
| Important claim without a source | |
| Revenue semantics invented or ignored | |
| Authority boundary absent | |
| Stop condition absent | |

## Say

> Fluency is not evidence. A confident answer can hide an undefined task.

## Proof that counts

The group identifies at least three concrete defects. Keep the output visible
for the structured-prompt comparison.

## Recovery

If the agent stalls, use a rehearsed response labeled **prepared** and perform
the same critique. Never describe prepared output as live.

Next: [`02-investigation-contract.md`](02-investigation-contract.md).
