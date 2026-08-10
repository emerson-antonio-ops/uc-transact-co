# Live - Follow-Along Process

This folder is the live spine of each session, one file per demo checkpoint.
Each file bundles everything one checkpoint needs: the slide question, the
authority boundary, the exact prompt or commands, and the proof that counts.
The deck creates a question, a checkpoint file tests it, and a skill card in
[`../skills/`](../skills/) records what became reusable.

## The loop, every act

```text
Slide ends with a question
  -> Open the numbered checkpoint file for the current checkpoint
  -> Read the header aloud: question, authority boundary, proof that counts
  -> Paste the prompt into the agent (or run the commands) live
  -> Inspect the evidence produced
  -> Return to the deck and name the concept
  -> Fill the matching skill card in ../skills/
```

Transition into a file: "We could debate this, but let's test it."
Transition back to the deck: "Now let's separate what looked impressive from
what became provably true."

## File anatomy

Every checkpoint file has the same four sections, in this order:

1. **Question** - what the slide just asked. State it before switching apps.
2. **Authority boundary** - what the agent may and may not do in this step.
3. **Run this** - the exact prompt to paste, or the exact commands to run.
4. **Proof that counts** - the evidence that closes the checkpoint. If the
   live run fails, keep the failure visible; do not present a prepared
   artifact as live output.

## Rules for every day

- Investigation steps are read-only. Never run `make inject`, `make reveal`,
  or `make score` during a foundation session.
- Every important claim needs a repository path, schema object, or query.
- The agent receives the distributed context pack, not this folder. These
  files are for the humans following along.
- Each act ends by distilling one skill card. Participants leave with the
  full set for the day, not one summary card.

## Day 1 - Foundation Investigation

| Order | File | Checkpoint | Skill distilled |
| --- | --- | --- | --- |
| 0 | [`d1/00-setup.md`](d1/00-setup.md) | A - Environment | - |
| 1 | [`d1/01-weak-prompt.md`](d1/01-weak-prompt.md) | B - Prompt contrast | [`S1`](../skills/d1/S1-prompt-as-contract.md) |
| 2 | [`d1/02-investigation-contract.md`](d1/02-investigation-contract.md) | B - Prompt contrast | [`S1`](../skills/d1/S1-prompt-as-contract.md) |
| 3 | [`d1/03-context-inventory.md`](d1/03-context-inventory.md) | C - Context inventory | [`S2`](../skills/d1/S2-context-selection.md) |
| 4 | [`d1/04-ontology.md`](d1/04-ontology.md) | D - Ontology | [`S4`](../skills/d1/S4-ontology-modeling.md) |
| 5 | [`d1/05-agentic-investigation.md`](d1/05-agentic-investigation.md) | E - Agentic investigation | [`S3`](../skills/d1/S3-system-interviewing.md), [`S5`](../skills/d1/S5-trajectory-inspection.md) |
| 6 | [`d1/06-technical-brief.md`](d1/06-technical-brief.md) | F - Technical brief | [`S6`](../skills/d1/S6-technical-brief.md) |

The canonical facilitation plan remains
[`../plan/semana.md`](../plan/semana.md). If a prompt here and the plan
disagree, fix the disagreement; do not improvise a third version live.
