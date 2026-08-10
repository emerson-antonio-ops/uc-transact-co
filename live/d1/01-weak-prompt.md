# 01 - Weak Prompt (Checkpoint B: Prompt contrast)

Act 2 - Why prompts matter (19:15-19:40)

## Question

What happens when we give an agent the request most people would actually
type?

## Authority boundary

- The agent has minimal context and read-only access.
- We run this expecting it to be inadequate. The failure is the lesson.

## Run this

Paste exactly, with nothing else:

```text
Analyze this database and explain revenue.
```

## Proof that counts

While the output streams, the room hunts for:

- assumptions presented as facts;
- claims with no evidence reference;
- undefined revenue semantics (which statuses? which timestamp? refunds?);
- no authority boundary (could it have modified data?);
- no stopping condition (when is it done? when should it ask a human?).

The checkpoint closes when the room can name at least three concrete failures
in the output. Do not fix the prompt yet - that is the next file.

## If it fails

If the live run stalls, use the saved weak-prompt output from the speaker
notes and run the same hunt against it. Label it as prepared, not live.

## Skill distilled

After returning to the deck, start filling
[`../../skills/d1/S1-prompt-as-contract.md`](../../skills/d1/S1-prompt-as-contract.md).
