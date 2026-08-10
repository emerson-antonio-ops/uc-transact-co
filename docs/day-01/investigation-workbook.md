# Day 1 Investigation Workbook

## 1. Prompt as a work contract

Start with the deliberately weak request:

> Analyze this database and explain revenue.

Record what is missing:

- objective;
- scope;
- context;
- tools;
- authority;
- evidence standard;
- output format;
- stopping and escalation conditions.

Now construct the investigation contract:

> Investigate how TransactCo represents revenue. Use the approved repository
> context and read-only database access. Identify the relevant entities,
> relationships, business invariants, operational risks, and unresolved business
> questions. Support every important claim with a repository path, schema object,
> or query. Clearly label facts, inferences, decisions, and open questions. Do not
> modify the database or application code. Stop and ask when a conclusion requires
> business authority rather than technical evidence.

## 2. Context inventory

| Source | Why selected | Questions it can answer | Questions it cannot answer | Provenance |
| --- | --- | --- | --- | --- |
| Business brief |  |  |  |  |
| Data guide |  |  |  |  |
| Operational DDL |  |  |  |  |
| Representative queries |  |  |  |  |
| Day 1 context-pack README |  |  |  |  |

Context is selected, not dumped. Exclude a source when it does not help answer
the mission, when its authority is unclear, or when it would reveal later-day
instructor material.

## 3. Evidence ledger

| ID | Statement | Status | Evidence | Owner | Next action |
| --- | --- | --- | --- | --- | --- |
| C-01 |  | fact / inference / decision / question |  |  |  |

Status definitions:

- **Fact:** directly supported by evidence.
- **Inference:** reasonable but not conclusively established.
- **Decision:** chosen by someone with authority.
- **Question:** requires more evidence or an accountable owner.

## 4. Ontology worksheet

Vocabulary:

- Entity: something the business cares about.
- Relationship: how entities connect.
- Rule: what must remain true.
- Event: something that happened in business time.
- Provenance: the source supporting the statement.
- Owner: the person or system authorized to decide meaning.

| Subject | Relationship | Object | Status | Evidence | Owner/question |
| --- | --- | --- | --- | --- | --- |
| Customer |  | Order |  |  |  |
| Product |  | Order |  |  |  |
| Order |  | Payment |  |  |  |
| Payment |  | Revenue |  |  |  |

Do not promote a candidate relationship to a confirmed rule until its evidence
and scope are explicit.

## 5. ADR candidate register

Day 1 identifies decisions; it does not silently approve them.

| Candidate | Decision required | Alternatives | Evidence available | Missing owner/input |
| --- | --- | --- | --- | --- |
| ADR-C01 | Define the analytical system boundary |  |  |  |
| ADR-C02 | Define revenue recognition time |  |  |  |
| ADR-C03 | Define late-arrival treatment |  |  |  |

## 6. Investigation gate

- [ ] Every important claim has evidence or an explicit uncertainty label.
- [ ] The operational investigation remained read-only.
- [ ] Ontology edges show status, evidence, and ownership.
- [ ] Business decisions were not invented by the agent.
- [ ] ADR candidates are proposals, not approved records.
- [ ] The technical brief can be reviewed without replaying the chat.
