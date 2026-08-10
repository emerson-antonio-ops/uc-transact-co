# Semana Engenharia Agentica - Facilitation and Delivery Plan

- Status: living facilitator plan
- Session: Day 1, 19:00-22:00, America/Sao_Paulo
- Case: TransactCo - "the analytics are killing the store"
Primary source: [`docs/semana-agentic-uc-transact-co-v2.pdf`](../docs/semana-agentic-uc-transact-co-v2.pdf)

## 1. Purpose

Day 1 must give participants enough concepts, data, and language to investigate
an unfamiliar system before asking them to build anything on top of it.

The teaching rule is:

> Nobody constructs with a concept that has not first been motivated, defined,
> grounded in data, and demonstrated.

Every teaching block follows the same progression:

```text
Why -> Concept -> Required material -> Demonstration -> Construction -> Proof -> Skill
```

By 22:00, participants should be able to explain how TransactCo works, distinguish
facts from inferences and decisions, construct an evidence-led investigation
prompt, select useful context, model the first business ontology, inspect the
agent's trajectory through telemetry, and produce a technical brief for human
review.

Day 1 is successful when understanding becomes an inspectable engineering
artifact. It is not measured by code volume.

## 1A. Base-project delivery contract and live alignment

This section is the release gate between "Claude implemented it" and "we can
teach from it." It separates the base project promised by the released Semana
material from the additional assets required to facilitate Day 1. A green base
project does not make an unfinished presentation or unimplemented telemetry
green by association.

### Released Semana base project

| Promised capability | Repository evidence | Validation gate | Status on 2026-08-10 |
| --- | --- | --- | --- |
| Postgres starts with the source schema applied | `docker-compose.yml`; `infra/postgres/init/01_schema.sql` | Fresh-volume `make up`; `make doctor` | **VALIDATED** |
| Correlated business data can be generated from a clean baseline | `src/transactco/seed.py` | `make seed`; baseline assertions; row-count inspection | **VALIDATED** |
| All 14 designed defect types can be injected | `src/transactco/defects.py` | Every injector run independently; `SCENARIO=all` produced 14 incident records | **VALIDATED** |
| Instructor truth is recorded in `_control.injected_incidents` | `infra/postgres/init/02_control.sql`; injection code | `make inject`; control-table inspection | **VALIDATED** |
| The analytical role cannot read the oracle or write to the source | `infra/postgres/init/03_roles.sql` | Explicit denied read and denied write checks | **VALIDATED** |
| `make land` carries `public.*` from Postgres to DuckDB through a read-only attachment | `src/transactco/land.py` | Four-table Postgres/DuckDB count parity | **VALIDATED** |
| Oracle data is not copied into DuckDB | landing allowlist; `src/transactco/verify.py` | `make verify` oracle-inventory check | **VALIDATED** |
| The raw layer is ready while student-built layers remain absent | `warehouse.duckdb` raw schema; empty dbt model tree | `dbt parse`; warehouse inventory | **VALIDATED** |
| The scoring contract can evaluate a detector without supplying one | `src/transactco/score.py` | Perfect-fixture score returned precision, recall, and F1 of 1.0 | **VALIDATED** |
| A clean machine has one documented construction-and-proof path | `make bootstrap` | Setup, health, clean warehouse, seed, land, tests, dbt shell, and verification complete; detector count is zero | **VALIDATED** |

Conclusion: the **released base-project functional contract is complete and
validated locally**. The code base may be used as the brownfield starting point
for Day 1 after the facilitator reruns `make bootstrap` on the presentation
machine. This does not yet mean that the baseline is versioned or published.

### Day 1 facilitation readiness

These items are not part of the released data-platform base, but they are part
of the Day 1 experience we have now chosen to deliver.

| Day 1 asset or capability | Current evidence | Gate before 19:00 | Status |
| --- | --- | --- | --- |
| Business, data, investigation, ontology, telemetry, brief, and reflection context | `docs/day-01/` | Facilitator content review and link check | **VALIDATED** |
| Safe student investigation paths | `make psql-ro`; `make query-ro` | Prove reads succeed and writes fail | **VALIDATED** |
| Recoverable versioned baseline | Current Git worktree contains untracked base-project files | Review intended file set, commit deliberately, and record the revision used for class | **NOT VERSIONED** |
| Minimal 12-slide story | Section 6 of this plan | Editable deck opens and rendered slides are inspected | **CONTENT READY; DECK NOT BUILT** |
| Live telemetry | `docs/day-01/telemetry-contract.md` defines the contract | A real emitter produces a rehearsed trace, or the session explicitly teaches only the manual contract | **CONTRACT ONLY; NOT IMPLEMENTED** |
| Weak-versus-structured prompt comparison | Planned in Acts 2 and 5 | Rehearse both paths; save known-good outputs | **REHEARSAL REQUIRED** |
| Ontology v1 and technical-brief fallbacks | Templates and expected structures exist | Save presenter fallback artifacts | **FALLBACKS REQUIRED** |
| Presentation-machine recovery | `docs/facilitator/day-01-runbook.md` | Cold rehearsal plus recovery rehearsal | **RUNBOOK READY; REHEARSAL REQUIRED** |

Therefore, do not call the **entire Day 1 delivery** 100% ready yet. It becomes
ready only when one of these telemetry decisions is made and recorded:

1. Implement and validate a live telemetry emitter before the session; or
2. Deliberately scope Day 1 to constructing and inspecting the telemetry
   contract manually, and remove any wording that claims live collection.

The versioned snapshot, PowerPoint, fallback artifacts, and rehearsal gates must
also be closed. These are delivery/facilitator-readiness gaps, not functional
base-project implementation gaps.

### Intentional adaptations from the released wording

- The released Day 1 description mentions reading foreign keys. The source
  database intentionally has no foreign-key or check constraints because the
  teaching fixture must admit invalid states. Participants will infer and test
  **candidate logical relationships** from names, values, cardinalities, and
  samples. We must not claim that physical foreign keys exist.
- "Sealed oracle" means isolated from the `analytics_ro` role and excluded from
  DuckDB. It is not secret from the owner or administrator of the laptop. A
  genuinely private Day 4 holdout requires a separate instructor-controlled
  environment or context boundary.
- The released outline leans toward roughly 20% theory and 80% construction.
  This plan deliberately uses about 45-50 minutes of framing because the Day 1
  brief added prompts, context, ontology, telemetry, and Agentic Development.
  The deck remains braided into live work rather than delivered as a one-hour
  lecture.

### Scope that must remain absent before Day 1

Do not "complete" the project by adding the work participants are meant to
construct: dbt staging/intermediate/mart models, the agent harness, detector,
task loop, serving layer, or canonical ADR set. Their absence is a delivery
condition, not a defect.

## 2. Position in the learning and product journey

| Experience | What participants do | Intended belief |
| --- | --- | --- |
| Semana | Perform canonical practices manually | "I can do this." |
| Bootcamp | Turn practices into reusable skills, gates, and evals | "I can systematize this." |
| Converge Bootcamp | Compose the skills into an end-to-end operating method | "I can build and operate the machine." |

The Semana teaches the generic practices underneath Converge without exposing
the protected machinery during Days 1-4. Use verbs such as understand, ground,
model, specify, decide, decompose, verify, execute, and learn. Do not teach pass
counts or internal names on Day 1.

Presenter-only mapping:

| Semana practice | Underlying methodological idea |
| --- | --- |
| Frame the prompt | Intent |
| Select context | Grounding |
| Interview the system | Evidence-backed discovery |
| Model the ontology | Structure and semantic contracts |
| Produce the technical brief | Falsifiable requirements |
| Identify ADR candidates | Explicit decision boundaries |
| Capture telemetry | Execution evidence |
| Reflect and distill | Learning loop |

Day 1 may identify ADR candidates. It must not silently manufacture canonical
ADRs. A decision becomes an ADR only when the choice, alternatives, trade-offs,
evidence, and accountable owner are explicit.

## 3. Curriculum and reveal boundaries

### Available on Day 1

- The TransactCo business problem.
- Approved repository paths and operational source code: `docs/day-01/`,
  `infra/postgres/init/01_schema.sql`, and read-only inspection surfaces. Add
  other paths only when the facilitator has confirmed they do not reveal
  later-day material.
- The clean Postgres baseline.
- The four-table data model.
- Read-only investigation access.
- The prompt worksheet.
- The context inventory.
- The ontology worksheet.
- The telemetry contract.
- The technical-brief template.

### Deliberately not taught or revealed on Day 1

- Injected incidents or their exact mechanics.
- The oracle reveal.
- The detector implementation.
- dbt transformation models.
- The serving API or MCP layer.
- Agent harness scaffolding.
- Task creation or Task-Spec machinery.
- Evals and the execution loop.
- Converge passes, internal gates, Fork terminology, or HMAC.
- Claims of a production-ready autonomous fleet.

### Information design

Separate the learning material into three categories:

| Category | Examples | Teaching purpose |
| --- | --- | --- |
| Given upfront | Business problem, four tables, system boundary, read-only access | Prevent irrelevant confusion |
| Discovered from evidence | Relationships, invariants, reconciliation rules, data risks | Create the investigative experience |
| Deliberately unresolved | Revenue recognition time, refund policy, decision ownership | Teach when an agent must ask a human |

Do not document every business rule in the initial context pack. Give participants
enough information to investigate, while preserving meaningful discoveries and
real business ambiguities.

## 4. Storytelling grammar

The session is not "PowerPoint, then demo." It is a braided story:

```text
PPT: create the question
  -> Demo: test the question against TransactCo
  -> Evidence: inspect what actually happened
  -> PPT: name the concept and reusable skill
  -> Reflection: decide what became true
```

Recommended transition into a demo:

> We could debate this, but let's test it.

Recommended transition back to the deck:

> Now let's separate what looked impressive from what became provably true.

Do not narrate every click. Before each demo, state the question, the expected
artifact, the authority boundary, and the proof that will count.

## 5. Complete three-hour run of show

| Time | Mode | Segment | Outcome |
| --- | --- | --- | --- |
| 19:00-19:15 | PPT + demo | Why this system matters | The room understands the business tension and available data |
| 19:15-19:40 | PPT + demo | Why prompts matter | The room constructs an investigation contract |
| 19:40-20:15 | PPT + demo | Why context matters | The agent receives a deliberate, traceable context package |
| 20:15-20:25 | Break | Reset | Facilitator checks environment and next checkpoint |
| 20:25-21:00 | PPT + demo | Why ontology matters | The room constructs and validates ontology v1 |
| 21:00-21:35 | PPT + demo | Why Agentic Development and telemetry matter | The investigation becomes an inspectable trajectory |
| 21:35-21:55 | Demo + review | Why documentation matters | Evidence becomes a durable technical brief |
| 21:55-22:00 | PPT + reflection | Distill the skill | Participants name what they learned and what remains manual |

Target mix, excluding the break:

- Approximately 45-50 minutes of explanatory slides and guided concept framing.
- Approximately 115-120 minutes of repository work, investigation, construction,
  validation, and reflection.

## 6. Minimal PowerPoint structure

The deck should contain no more than 12 audience-facing slides. Each slide has
one narrative job.

| Slide | Audience-facing title | Narrative job | Transition |
| --- | --- | --- | --- |
| 1 | Semana Engenharia Agentica | Establish the session and case | Open with the CFO's question |
| 2 | The report can be precise and still be wrong | Create business tension | Ask what makes a number trustworthy |
| 3 | The system we are inheriting | Introduce the four entities and brownfield boundary | Open the repository |
| 4 | A prompt is a contract for the next piece of work | Explain why prompts matter | Run a weak prompt |
| 5 | A useful prompt defines objective, authority, evidence, and stopping | Give the prompt anatomy | Construct the investigation prompt |
| 6 | The prompt defines the work; context supplies the world | Explain why context matters | Inspect available context sources |
| 7 | Context must be selected, not dumped | Teach context categories and provenance | Build the context inventory |
| 8 | Ontology preserves meaning while systems change | Explain why ontology bridges systems | Construct ontology v1 |
| 9 | Entities, relationships, rules, events, and provenance | Give the ontology vocabulary | Validate relationships with data |
| 10 | Agentic development is controlled work, not a longer chat | Introduce objective, tools, authority, feedback, and human gates | Run the structured investigation |
| 11 | Telemetry makes the trajectory inspectable | Explain why the final answer is insufficient | Inspect the event and claim trail |
| 12 | Evidence becomes valuable when it survives the session | Close through documentation and skill distillation | Review the brief and reflect |

Speaker notes should contain the timing, facilitation prompts, demo commands,
fallbacks, and internal Converge mapping. None of those production notes should
appear as audience-facing slide copy.

## 7. Act 1 - Why this system matters

Time: 19:00-19:15

### Why

Participants need a concrete business tension before technical concepts have
meaning. The CFO does not merely need a revenue number; the CFO needs confidence
that the number describes the business correctly without harming the store.

### Concepts to explain

- Brownfield: a system with history, implicit rules, constraints, and existing
  users; not an empty repository.
- Operational workload: work that runs the store.
- Analytical workload: work that scans, aggregates, and explains the store.
- Trustworthy metric: a number with defined meaning, provenance, and validation.
- Business time versus ingestion time.

### Data and material supplied

- TransactCo is a high-volume e-commerce company.
- The operational source is Postgres.
- The four primary entities are customers, products, orders, and payments.
- The store and analytics currently share resources.
- The CFO asks: "How much revenue did we make yesterday, and why should I trust
  that number?"

### Demonstration

1. Open the repository at its root.
2. Show only the top-level structure.
3. Start or verify the clean environment.
4. Show table names and safe row counts.
5. Do not interpret all relationships yet.

### Proof

The audience can restate the business problem, identify the four entities, and
explain why a plausible query is not yet a trustworthy revenue definition.

## 8. Act 2 - Why prompts matter

Time: 19:15-19:40

### Why

A prompt is the contract for the next piece of work. Without understanding the
prompt, participants cannot distinguish a vague request from an executable
assignment, an output preference from a requirement, or permission to inspect
from permission to modify.

### Concepts to explain

An investigation prompt should define:

```text
Objective
Context available
Questions to answer
Tools permitted
Authority boundary
Evidence required
Output format
Stop and escalation conditions
```

The prompt does not contain all domain knowledge. It tells the agent what work to
perform with the context and tools it receives.

### Demonstration A - weak prompt

Use:

> Analyze this database and explain revenue.

Ask the audience to find:

- assumptions presented as facts;
- missing evidence;
- undefined revenue semantics;
- absent authority boundaries;
- no stopping condition.

### Demonstration B - construct the investigation contract

Build this with the audience:

> Investigate how TransactCo represents revenue. Use the repository and
> read-only database access. Identify the relevant entities, relationships,
> business invariants, operational risks, and unresolved business questions.
> Support every important claim with a repository path, schema object, or query.
> Clearly label facts, inferences, decisions, and open questions. Do not modify
> the database or application code. Stop and ask when a conclusion requires
> business authority rather than technical evidence.

### Artifact

Investigation Prompt v1.

### Proof

The audience can explain why each clause exists and predict what failure it
prevents.

## 9. Act 3 - Why context matters

Time: 19:40-20:15

### Why

The model may know what an order usually means. It does not automatically know
what TransactCo recognizes as revenue, which timestamps are authoritative, which
payment statuses matter, or which system owns each decision.

### Concepts to explain

| Context layer | Question it answers |
| --- | --- |
| Business | Why does the work matter? |
| Domain | What do the terms mean here? |
| System | Where do code, data, and interfaces live? |
| Operational | What must remain safe and available? |
| Evidence | What can support or refute a claim? |
| Authority | What may the agent inspect, change, or decide? |

Context engineering is selection, ordering, and provenance. It is not copying
every file into a model window.

### Context package

- Business brief.
- Repository map.
- Postgres DDL.
- Data dictionary.
- Representative, non-sensitive sample rows.
- Operational constraints.
- Read-only connection instructions.
- Technical-brief template.
- Telemetry contract.

### Demonstration

1. Inventory the available context sources.
2. Explain why each source is included or excluded.
3. Ask the agent to inspect them in a deliberate order.
4. Require a source reference for every important claim.
5. Maintain a claim ledger with fact, inference, decision, and question labels.

### Artifact

Context Inventory and Evidence Ledger.

### Proof

The audience can point to the context source that changed or supported a specific
conclusion.

## 10. Act 4 - Why ontology matters

Time: 20:25-21:00

### Why

Postgres and DuckDB may represent data differently. Column-to-column copying is
not enough; business meaning and constraints must survive the crossing.

### Concepts to explain

- Entity: something the business cares about.
- Relationship: how entities are connected.
- Rule: what must remain true.
- Event: something that happened at a point in business time.
- Provenance: the source that supports the statement.
- Owner: the person or system authorized to decide meaning.

Starting ontology:

```text
Customer --places--> Order
Product --appears in--> Order
Order --settled by--> Payment
Payment --may contribute to--> Revenue
```

The final edge is deliberately conditional. Whether and when a payment becomes
recognized revenue is a business decision, not something the model should invent.

### Demonstration

1. Derive candidate entities from the schema and business brief.
2. Derive relationships from columns and observed data.
3. Test cardinality and reconciliation claims with read-only queries.
4. Attach evidence to every confirmed relationship.
5. Mark unresolved semantics as questions with owners.
6. Show how the future Postgres-to-DuckDB crossing must preserve the same meaning.

### Artifact

TransactCo Ontology v1.

### Proof

Every ontology edge is either evidenced, explicitly inferred, or marked as an
unresolved business decision.

## 11. Act 5 - Why Agentic Development and telemetry matter

Time: 21:00-21:35

### Why

Ordinary chat produces a response. Agentic development produces controlled work
through tools, observations, feedback, evidence, and human gates. The final
answer alone cannot prove how the work was performed.

### Concepts to explain

```text
Objective
  -> Context
  -> Tool use
  -> Observation
  -> Claim
  -> Verification
  -> Human decision
  -> Durable artifact
```

The minimum Day 1 authority is:

- read repository files;
- run approved read-only queries;
- write the Day 1 documentation artifacts;
- do not modify operational data;
- do not make business decisions;
- escalate ambiguity to the facilitator or named owner.

### Telemetry contract

Minimum events:

```text
session_started
phase_started
context_loaded
repository_inspected
query_executed
claim_proposed
claim_verified
claim_rejected
question_opened
artifact_updated
gate_evaluated
session_completed
```

Minimum fields:

```text
timestamp
run_id
actor
phase
action
ontology_entity
evidence_reference
outcome
duration_ms
```

Never record passwords, connection strings with secrets, personal data, complete
database rows, or secret-bearing prompts.

### Demonstration

1. Run the structured investigation with read-only authority.
2. Display the event stream or terminal summary.
3. Connect claims to evidence and ontology entities.
4. Show one rejected assumption.
5. Show one escalation to human authority.
6. Compare the trajectory with the final response.

### Artifact

Day 1 Investigation Trace.

### Proof

The facilitator can reconstruct which sources, tools, evidence, and decisions
produced the technical brief.

## 12. Act 6 - Why documentation and reflection matter

Time: 21:35-22:00

### Why

Knowledge that exists only in a chat session cannot reliably guide tomorrow's
engineering. Documentation makes evidence, decisions, ownership, and remaining
uncertainty durable.

### Documentation categories

| Category | Definition |
| --- | --- |
| Fact | Directly supported by evidence |
| Inference | Reasonable but not conclusively established |
| Decision | Chosen by someone with authority |
| Open question | Requires more evidence or an accountable owner |

### Technical-brief content

- Business problem.
- Current system boundary.
- Data inventory.
- Ontology v1.
- Confirmed business rules.
- Evidence ledger.
- Risks and constraints.
- Assumptions.
- Open questions and owners.
- Proposed analytical boundary.
- Success measures.
- Non-goals.
- ADR candidates.

### End-of-day reflection

Use telemetry and artifacts, not memory or vibes:

1. What did we initially believe?
2. What did we actually observe?
3. Which assumption failed?
4. Which context source changed the result?
5. What did the ontology make visible?
6. What did telemetry reveal that the final answer did not?
7. Which decision still requires a human?
8. What reusable skill did we practice?
9. What remains manual?
10. What would a later machine automate?

### Skill card

```text
Skill: System interviewing and context synthesis
When to use:
Inputs:
Questions to ask:
Method:
Artifact produced:
Evidence required:
Human decision:
What remains manual:
```

The skill card is a learning artifact, not an installable automation package.

### Day 2 hook

> Today the agent learned to understand before it executed. Tomorrow we build
> the rails that turn that understanding into controlled work.

## 13. Demo choreography

### Demo checkpoints

| Checkpoint | Start state | Live action | Expected proof | Recovery |
| --- | --- | --- | --- | --- |
| A - Environment | Clean seeded Postgres | Open repo and run health/status commands | Four tables available; baseline healthy | Use pre-seeded backup or reset script |
| B - Prompt contrast | Agent has minimal context | Run weak prompt, then structured prompt | Unsupported assumptions become visible | Use saved outputs in speaker notes |
| C - Context inventory | Approved source bundle exists | Inspect sources and construct claim ledger | Claims point to sources | Use prepared inventory snapshot |
| D - Ontology | Claim ledger exists | Build and query relationships | Edges have evidence or explicit status | Use ontology v1 backup |
| E - Agentic investigation | Read-only authority and telemetry enabled | Run investigation and inspect trace | Tools, claims, evidence, and escalations visible | Use recorded JSONL trace |
| F - Technical brief | Artifacts from prior checkpoints | Generate and review brief | Gate passes or failures are explicit | Use prepared draft and review live |

### Switching rules

- End every explanatory slide with a question the demo will answer.
- Put the exact task and authority boundary on the transition slide or in the
  speaker notes before switching applications.
- Return to the deck only after producing visible evidence or a visible failure.
- Name the concept after the audience has experienced its need.
- Keep a prepared artifact for every demo, but do not present it as live output
  if the live run failed.

## 14. Day 1 learner material to prepare

| Material | Audience | Purpose | Spoiler policy |
| --- | --- | --- | --- |
| Business brief | Student | Explain the company, CFO problem, and constraints | No incident details |
| Repository map | Student | Show where operational code and data definitions live | Exclude instructor-only assets |
| Data dictionary | Student | Define columns and timestamps | Do not state every hidden invariant |
| Investigation-prompt worksheet | Student | Construct the task contract | Safe |
| Context-inventory worksheet | Student | Select and cite context | Safe |
| Ontology worksheet | Student | Model entities, relationships, rules, provenance, owners | Safe |
| Technical-brief template | Student | Produce the Day 1 artifact | Safe |
| Telemetry contract | Student | Make the trajectory inspectable | Must prohibit secrets and PII |
| Facilitation runbook | Instructor | Commands, timing, answers, fallbacks, recovery | Instructor only |
| Oracle/injection guide | Instructor | Day 4 setup and scoring | Instructor only |

## 15. Repository readiness contract

The implementation is not Day 1 ready because files exist. It is ready only when
the documented workflow succeeds from a clean environment and the documentation
matches observed behavior.

### Required operator flow

```bash
make setup
make up
make doctor
make seed
make land
make status
```

### Required evidence

- Dependency installation succeeds from the lock file.
- Postgres becomes healthy.
- All four operational tables exist.
- The deterministic baseline passes its integrity checks.
- The read-only role can query `public.*`.
- The read-only role cannot query `_control.*`.
- DuckDB contains the four `raw.*` tables and landing manifest.
- DuckDB does not contain `_control` or injected-incident tables.
- Postgres and DuckDB row counts match after landing.
- Re-landing does not delete student detections.
- Status output reveals no Day 4 spoilers.
- Reset and recovery commands work as documented.
- Student documentation contains no required command that has not been executed
  successfully during rehearsal.

### Defect/scoring rehearsal

Before Day 4, test every defect in isolation from a clean baseline:

```text
reset -> seed -> inject one defect -> land -> assert oracle truth -> reset
```

Also test the live, deep, smoke, and all scenarios; a perfect detector fixture;
an empty detector; an unknown detection; and the decoy precision penalty.

## 16. Oracle truth boundary

The current local design can enforce that the `analytics_ro` connection and
DuckDB landing path cannot access `_control`. That is valuable and testable.

It does not by itself keep the oracle secret from the owner of the laptop or
container. A participant with repository access can inspect injection code, use
local admin credentials, run instructor commands, or enter the Postgres
container. Therefore:

- Describe the current design as a sealed analytical path or workflow seal.
- Do not describe it as an adversarial security boundary.
- Do not give the Day 4 detector agent repository-wide access to instructor code.
- For a genuinely private holdout, distribute instructor injection/scoring as a
  separate service, private repository, or instructor-controlled environment.
- Keep student context and instructor truth physically separate before making a
  strong claim that the oracle is hidden.

This boundary must be decided before Day 4. It does not block Day 1 if the
facilitator avoids exposing incident implementation details.

## 17. Validation and documentation workflow

This session acts as validator and documentation owner while Claude implements.

### Claude implementation responsibilities

- Operational schema and roles.
- Deterministic seeding.
- Incident injection.
- DuckDB landing.
- Scoring implementation.
- CLI and Make targets.
- Blocking code fixes found by validation.

### Validator/documentation responsibilities

- Reproduce every documented operator command.
- Separate implemented behavior from planned curriculum.
- Record commands, outputs, timings, and failures.
- Check student/instructor information boundaries.
- Keep README focused on project operation.
- Keep this file as the canonical facilitation/storytelling plan.
- Create Day 1 learner documents and facilitator runbook from this plan.
- Update wording only after behavior is verified.
- Re-run checks after every meaningful correction.

### Documentation truth rules

- "Implemented" means the code exists and has been inspected.
- "Validated" means the behavior was executed successfully in this checkout.
- "Day 1 ready" means the complete clean-room rehearsal passed.
- "Sealed" means the named role/path is denied; it does not imply a security
  boundary against the local environment owner.
- "Deterministic" must identify any intentionally time-relative fields.
- Timings are rehearsal evidence, not universal guarantees.

## 18. Daily skill distillation across Semana

| Day | Canonical concept | Reusable skill | Durable artifact | Proof |
| --- | --- | --- | --- | --- |
| 1 | Prompt, context, ontology, controlled investigation | System interviewing and context synthesis | Ontology, evidence ledger, technical brief, ADR candidates | Claims are evidenced or explicitly unresolved |
| 2 | Harness, roles, tools, authority | Harness and authority design | Role boundaries, tool policy, sketch plans | Agents operate within declared boundaries |
| 3 | Spec-driven execution and decomposition | Specification and task framing | Feature spec and atomic task descriptions | Work is bounded and dependencies are visible |
| 4 | Eval and loop engineering | Verification-driven execution | Detector, eval, execution trace, score | Result is measured against independent truth |
| 5 | External authority and reviewed learning | Evidence review and synthesis | Capability map, lessons, next-stage plan | Claims survive expert and human review |

Each day ends with the same reflection:

```text
What did we believe?
What did we observe?
What artifact changed?
What evidence made it trustworthy?
What reusable skill did we practice?
What remains manual?
What would the later machine automate?
```

## 19. Final Day 1 gate

Day 1 closes only when:

- The system is running and was investigated read-only.
- The prompt's objective, authority, evidence, output, and stopping conditions are
  understood.
- The context inventory explains why each source was selected.
- Ontology v1 connects business meaning to system evidence.
- Telemetry captures the investigation without secrets or PII.
- The technical brief separates facts, inferences, decisions, and questions.
- ADR candidates are identified without pretending they are approved decisions.
- The human owner retains authority over unresolved business semantics.
- Participants can name the skill they practiced.
- The Day 2 hook is explicit: understanding now needs a controlled harness.
