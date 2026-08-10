# Frontier grill

The grill converts an appealing but vague request into an investigable question. It is firm, brief, and evidence-oriented.

## Technique

1. First inspect what is already available. Separate discoverable facts from human decisions.
2. Ask every currently unblocked decision question in one numbered batch.
3. Give a recommended default and its consequence when a real choice exists.
4. Use each answer to expose the next frontier. Do not ask later questions whose premises are not yet established.
5. Push an ambiguous answer once with a concrete contrast. If ambiguity remains, assign an owner and record an open question.

## Frontier rounds

### Consequence

- What pain or risk triggered this investigation?
- What is the measurable cost of doing nothing?
- Who experiences that consequence?

If the consequence is immaterial, recommend a no-go or park decision.

### Outcome

- What exact question must the evidence answer?
- What changes when the answer is known?
- What would count as a useful negative result?

### Boundary

- Which systems, time range, environments, and business processes are in scope?
- What is explicitly out of scope?
- Which actions are allowed, and which are prohibited?

### Proof

- Which sources are authoritative?
- What evidence would support or falsify the answer?
- How fresh must the evidence be?

### Delivery

- Who will review the result?
- Which open decisions belong to which owner?
- What output is required, and what condition ends the investigation?

## Classification examples

| Statement | Classification | Treatment |
|---|---|---|
| `payments.amount` is a numeric column | Fact | Discover and cite schema evidence |
| Payments probably settle orders | Inference | Cite inputs and keep the reasoning visible |
| Revenue is recognized when payment succeeds | Decision | Ask Finance; never infer from naming |
| Which statuses count as successful? | Question | Assign owner and next action |

## Recommended-default pattern

> Which environment is in scope? I recommend the local seeded environment because it is safe and reproducible. Choosing production would require separate authorization and privacy controls.

Do not manufacture multiple-choice options when the answer is a discoverable fact.

