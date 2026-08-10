# Semana Engenharia Agentica - Facilitation and Delivery Plan

- Status: living facilitator plan
- Session: Foundation Investigation, 19:00-22:00, America/Sao_Paulo
- Case: TransactCo - "the analytics are killing the store"

Historical source, preserved verbatim:
[`docs/semana-agentic-uc-transact-co-v2.pdf`](../docs/semana-agentic-uc-transact-co-v2.pdf)

## 1. Purpose

Foundation Investigation must give participants enough concepts, data, and language to investigate
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

Foundation Investigation is successful when understanding becomes an inspectable engineering
artifact. It is not measured by code volume.

## 1A. Base-project delivery contract and live alignment

This section is the release gate between "Claude implemented it" and "we can
teach from it." It separates the base project promised by the released Semana
material from the additional assets required to facilitate Foundation Investigation. A green base
project does not make an unfinished presentation or unimplemented telemetry
green by association.

### Released Semana base project

| Promised capability | Repository evidence | Validation gate | Current status |
| --- | --- | --- | --- |
| Postgres starts with the source schema applied | `docker-compose.yml`; `infra/postgres/init/01_schema.sql` | Fresh-volume `make up`; `make doctor` | **VALIDATED** |
| Correlated business data can be generated from a clean baseline | `src/transactco/operational/seed.py` | `make seed`; baseline assertions; row-count inspection | **VALIDATED** |
| All 14 designed defect types can be injected | `src/transactco/control/evaluation/injection.py` | Every injector run independently; `SCENARIO=all` produced 14 incident records | **VALIDATED** |
| Instructor truth is recorded in `_control.injected_incidents` | `infra/postgres/init/02_control.sql`; injection code | `make inject`; control-table inspection | **VALIDATED** |
| The analytical role cannot read the oracle or write to the source | `infra/postgres/init/03_roles.sql` | Explicit denied read and denied write checks | **VALIDATED** |
| `make land` carries `public.*` from Postgres to DuckDB through a read-only attachment | `src/transactco/analytical/landing.py` | Four-table Postgres/DuckDB count parity | **VALIDATED** |
| Oracle data is not copied into DuckDB | landing allowlist; `src/transactco/control/verification.py` | `make verify` oracle-inventory check | **VALIDATED** |
| The raw layer is ready while student-built layers remain absent | `warehouse.duckdb` raw schema; empty dbt model tree | `dbt parse`; warehouse inventory | **VALIDATED** |
| The scoring contract can evaluate a detector without supplying one | `src/transactco/control/evaluation/scoring.py` | Perfect-fixture score returned precision, recall, and F1 of 1.0 | **VALIDATED** |
| A clean machine has one documented construction-and-proof path | `make bootstrap` | Setup, health, clean warehouse, seed, land, tests, dbt shell, and verification complete; detector count is zero | **VALIDATED** |

Conclusion: the **released base-project functional contract is complete,
validated locally, and versioned on `main`**. The code base may be used as the
brownfield starting point for the Foundation Investigation after the facilitator
reruns `make bootstrap` on the presentation machine.

### Foundation Investigation facilitation readiness

These items are not part of the released data-platform base, but they are part
of the Foundation Investigation experience we have now chosen to deliver.

| Foundation Investigation asset or capability | Current evidence | Gate before 19:00 | Status |
| --- | --- | --- | --- |
| Business, data, investigation, ontology, telemetry, brief, and reflection context | Appendix A of this plan | Facilitator content review and distribution check | **VALIDATED** |
| Safe student investigation paths | `make psql-ro`; `make query-ro` | Prove reads succeed and writes fail | **VALIDATED** |
| Recoverable versioned baseline | Base project is committed to `main` | Record the exact revision used for the presentation | **VALIDATED** |
| Minimal 12-slide story | Section 6 of this plan | Editable deck opens and rendered slides are inspected | **CONTENT READY; DECK NOT BUILT** |
| Live telemetry | Appendix A5 of this plan defines the contract | A real emitter produces a rehearsed trace, or the session explicitly teaches only the manual contract | **CONTRACT ONLY; NOT IMPLEMENTED** |
| Weak-versus-structured prompt comparison | Planned in Acts 2 and 5 | Rehearse both paths; save known-good outputs | **REHEARSAL REQUIRED** |
| Ontology v1 and technical-brief fallbacks | Templates and expected structures exist | Save presenter fallback artifacts | **FALLBACKS REQUIRED** |
| Presentation-machine recovery | Appendix B of this plan | Cold rehearsal plus recovery rehearsal | **RUNBOOK READY; REHEARSAL REQUIRED** |

Therefore, do not call the **entire Foundation Investigation delivery** 100% ready yet. It becomes
ready only when one of these telemetry decisions is made and recorded:

1. Implement and validate a live telemetry emitter before the session; or
2. Deliberately scope Foundation Investigation to constructing and inspecting the telemetry
   contract manually, and remove any wording that claims live collection.

The versioned snapshot, PowerPoint, fallback artifacts, and rehearsal gates must
also be closed. These are delivery/facilitator-readiness gaps, not functional
base-project implementation gaps.

### Intentional adaptations from the released wording

- The released Foundation Investigation description mentions reading foreign keys. The source
  database intentionally has no foreign-key or check constraints because the
  teaching fixture must admit invalid states. Participants will infer and test
  **candidate logical relationships** from names, values, cardinalities, and
  samples. We must not claim that physical foreign keys exist.
- "Sealed oracle" means isolated from the `analytics_ro` role and excluded from
  DuckDB. It is not secret from the owner or administrator of the laptop. A
  genuinely private Incident Exercise holdout requires a separate instructor-controlled
  environment or context boundary.
- The released outline leans toward roughly 20% theory and 80% construction.
  This plan deliberately uses about 45-50 minutes of framing because the Foundation Investigation
  brief added prompts, context, ontology, telemetry, and Agentic Development.
  The deck remains braided into live work rather than delivered as a one-hour
  lecture.

### Scope that must remain absent before Foundation Investigation

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
the protected machinery during the opening modules. Use verbs such as understand, ground,
model, specify, decide, decompose, verify, execute, and learn. Do not teach pass
counts or internal names during the Foundation Investigation.

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

Foundation Investigation may identify ADR candidates. It must not silently manufacture canonical
ADRs. A decision becomes an ADR only when the choice, alternatives, trade-offs,
evidence, and accountable owner are explicit.

## 3. Curriculum and reveal boundaries

### Available on Foundation Investigation

- The TransactCo business problem.
- The context pack from Appendix A, distributed by the facilitator rather than
  read from a repository path.
- Approved operational source code: `infra/postgres/init/01_schema.sql` and
  read-only inspection surfaces. Add other paths only when the facilitator has
  confirmed they do not reveal later-module material.
- The clean Postgres baseline.
- The four-table data model.
- Read-only investigation access.
- The prompt worksheet.
- The context inventory.
- The ontology worksheet.
- The telemetry contract.
- The technical-brief template.

### Deliberately not taught or revealed on Foundation Investigation

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

The minimum Foundation Investigation authority is:

- read repository files;
- run approved read-only queries;
- write the Foundation Investigation documentation artifacts;
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

Foundation Investigation Trace.

### Proof

The facilitator can reconstruct which sources, tools, evidence, and decisions
produced the technical brief.

## 12. Act 6 - Why documentation and reflection matter

Time: 21:35-22:00

### Why

Knowledge that exists only in a chat session cannot reliably guide the next
module. Documentation makes evidence, decisions, ownership, and remaining
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

### End-of-session reflection

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

### Next Module hook

> The investigation established understanding before execution. Next, we build
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

## 14. Foundation Investigation learner material to prepare

| Material | Audience | Purpose | Spoiler policy |
| --- | --- | --- | --- |
| Business brief | Student | Explain the company, CFO problem, and constraints | No incident details |
| Repository map | Student | Show where operational code and data definitions live | Exclude instructor-only assets |
| Data dictionary | Student | Define columns and timestamps | Do not state every hidden invariant |
| Investigation-prompt worksheet | Student | Construct the task contract | Safe |
| Context-inventory worksheet | Student | Select and cite context | Safe |
| Ontology worksheet | Student | Model entities, relationships, rules, provenance, owners | Safe |
| Technical-brief template | Student | Produce the Foundation Investigation artifact | Safe |
| Telemetry contract | Student | Make the trajectory inspectable | Must prohibit secrets and PII |
| Facilitation runbook | Instructor | Commands, timing, answers, fallbacks, recovery | Instructor only |
| Oracle/injection guide | Instructor | Incident Exercise setup and scoring | Instructor only |

## 15. Repository readiness contract

The implementation is not Foundation Investigation ready because files exist. It is ready only when
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
- Status output reveals no Incident Exercise spoilers.
- Reset and recovery commands work as documented.
- Student documentation contains no required command that has not been executed
  successfully during rehearsal.

### Defect/scoring rehearsal

Before the Incident Exercise, test every defect in isolation from a clean baseline:

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
- Do not give the Incident Exercise detector agent repository-wide access to instructor code.
- For a genuinely private holdout, distribute instructor injection/scoring as a
  separate service, private repository, or instructor-controlled environment.
- Keep student context and instructor truth physically separate before making a
  strong claim that the oracle is hidden.

This boundary must be decided before the Incident Exercise. It does not block the Foundation Investigation if the
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
- Create Foundation Investigation learner documents and facilitator runbook from this plan.
- Update wording only after behavior is verified.
- Re-run checks after every meaningful correction.

### Documentation truth rules

- "Implemented" means the code exists and has been inspected.
- "Validated" means the behavior was executed successfully in this checkout.
- "Foundation Investigation ready" means the complete clean-room rehearsal passed.
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

Each session ends with the same reflection:

```text
What did we believe?
What did we observe?
What artifact changed?
What evidence made it trustworthy?
What reusable skill did we practice?
What remains manual?
What would the later machine automate?
```

## 19. Final Foundation Investigation gate

Foundation Investigation closes only when:

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
- The Next Module hook is explicit: understanding now needs a controlled harness.

## 20. Appendix A - Participant context pack

These handout-ready sections are consolidated here so the facilitation plan
remains the canonical source. Distribute only the relevant sections to
participants or paste them into the approved agent context. Keep instructor
truth and later-module mechanics outside that context.

### A1. Context pack entry point

This is a controlled investigation of an unfamiliar brownfield. The goal is not
to build transformation models or autonomous agents. The goal is to understand
TransactCo well enough to produce an evidence-backed technical brief through
prompt design, context selection, ontology, and evidence.

#### Learning outcome

By the end of the session, you should be able to:

- explain why a prompt is a work contract rather than a knowledge base;
- select context deliberately instead of dumping files;
- interview a system through documentation, schema, and read-only queries;
- model entities, relationships, rules, events, provenance, and owners;
- distinguish facts, inferences, decisions, and open questions;
- inspect the work trajectory through safe telemetry;
- produce a durable technical brief for human review.

#### Context pack

Read these in order:

1. Business brief (A2)
2. Data guide (A3)
3. System investigation workbook (A4)
4. Investigation telemetry contract (A5)
5. Technical brief template (A6)
6. Investigation reflection (A7)

The repository contains material for the entire Semana. The foundation
investigation intentionally uses only this context pack, the operational schema,
representative data, and approved read-only commands. Incident injection,
scoring, dbt models, the harness, and the execution loop belong to later modules.

#### Working agreement

- Read before changing.
- Use read-only access during the investigation.
- Support important claims with a path, schema object, or query.
- Label inference as inference.
- Do not invent business decisions.
- Escalate questions that require an accountable owner.
- Never put credentials, personal data, or complete rows in telemetry or notes.

#### Investigation gate

The investigation closes when the technical brief, ontology, evidence ledger,
telemetry summary, and open questions have been reviewed by a human.

### A2. Business brief


#### Situation

TransactCo is a high-volume e-commerce company. Store operations and analytical
queries currently share the same Postgres database. The operational workload
creates and updates customers, products, orders, and payments. The analytical
workload scans and aggregates those records for reporting.

The two workloads compete for the same resources. Heavy analytical work can
affect store operations, while transactional traffic can make reporting slow or
unpredictable.

#### The CFO's question

> How much revenue did we make yesterday, and why should I trust that number?

The request contains two different problems:

1. Calculate a number.
2. Establish the meaning and evidence that make the number trustworthy.

The foundation investigation focuses on the second problem before implementing
a new analytical system.

#### Known system boundary

- Postgres is the operational source.
- The relevant public tables are `customers`, `products`, `orders`, and
  `payments`.
- The initial investigation is read-only.
- The supplied analytical crossing lands operational data into DuckDB; this
  investigation examines that boundary rather than extending it.
- Business meaning must survive that system crossing.

#### Known stakeholders

| Stakeholder | Concern |
| --- | --- |
| CFO | A revenue number with defensible meaning |
| Store operations | Transactional reliability and responsiveness |
| Data team | Reproducible transformations and quality evidence |
| Engineering | Clear interfaces, permissions, and recovery paths |

#### What is not decided for you

The following are intentionally open until evidence or an accountable owner
resolves them:

- Which business event recognizes revenue?
- Which payment and order statuses count?
- How should refunds affect the metric?
- Which timezone defines "yesterday"?
- How should late-arriving data change a previously published number?
- Who owns each semantic decision?

These are not trivia questions. They are examples of the boundary between
technical discovery and business authority.

#### Investigation mission

Understand the existing system, identify the evidence available, map its first
ontology, document confirmed rules and unresolved decisions, and propose the
questions that must be answered before building a trustworthy revenue model.

### A3. Data guide


This guide describes what the supplied columns are intended to represent. It
does not give away every relationship or business invariant; validating those is
part of the investigation.

The executable source of schema truth is
[`infra/postgres/init/01_schema.sql`](../infra/postgres/init/01_schema.sql).

#### `public.customers`

| Column | Intended meaning |
| --- | --- |
| `customer_id` | Internal customer identifier |
| `full_name` | Display name |
| `email` | Contact email as received from the source |
| `country`, `city` | Customer location attributes |
| `segment` | Commercial customer segment |
| `signup_date` | Business date of registration |
| `is_active` | Current active flag |
| `created_at`, `updated_at` | Source lifecycle timestamps |
| `ingested_at` | Time the row reached this database |

#### `public.products`

| Column | Intended meaning |
| --- | --- |
| `product_id` | Internal product identifier |
| `sku` | Commercial stock-keeping identifier |
| `product_name`, `category` | Catalog description |
| `price` | Current selling price in the source catalog |
| `cost` | Current product cost in the source catalog |
| `is_active` | Current catalog availability flag |
| `created_at`, `updated_at` | Source lifecycle timestamps |
| `ingested_at` | Time the row reached this database |

#### `public.orders`

| Column | Intended meaning |
| --- | --- |
| `order_id` | Internal order-row identifier |
| `customer_id` | Customer reference supplied by the source |
| `product_id` | Product reference supplied by the source |
| `quantity` | Ordered quantity |
| `unit_price` | Price recorded on the order |
| `discount` | Discount recorded on the order |
| `total_amount` | Total recorded by the order system |
| `status` | Current order status supplied by the source |
| `channel` | Order acquisition channel |
| `ordered_at` | Business time of the order |
| `updated_at` | Last source update time |
| `ingested_at` | Time the row reached this database |

#### `public.payments`

| Column | Intended meaning |
| --- | --- |
| `payment_id` | Internal payment-attempt identifier |
| `order_id` | Order reference supplied by the payment source |
| `amount` | Payment amount reported by the source |
| `method` | Payment method |
| `status` | Payment status |
| `paid_at` | Business time associated with the payment event |
| `ingested_at` | Time the row reached this database |

#### Time vocabulary

- **Business time** describes when something happened in the domain, such as
  `ordered_at` or `paid_at`.
- **Source lifecycle time** describes when a record was created or updated in an
  operational system.
- **Ingestion time** describes when the row reached the database being inspected.

These timestamps answer different questions and must not be silently substituted
for one another.

#### Investigation questions

- Which references behave like real relationships in the current data?
- Which statuses appear, and how frequently?
- Which timestamps are relevant to the CFO's question?
- Which numerical fields reconcile, and under what conditions?
- Which statements are supported by schema alone?
- Which statements require queries or business ownership?

### A4. System investigation workbook


#### 1. Prompt as a work contract

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

#### 2. Context inventory

| Source | Why selected | Questions it can answer | Questions it cannot answer | Provenance |
| --- | --- | --- | --- | --- |
| Business brief |  |  |  |  |
| Data guide |  |  |  |  |
| Operational DDL |  |  |  |  |
| Representative queries |  |  |  |  |
| Foundation context pack (A1) |  |  |  |  |

Context is selected, not dumped. Exclude a source when it does not help answer
the mission, when its authority is unclear, or when it would reveal later-module
instructor material.

#### 3. Evidence ledger

| ID | Statement | Status | Evidence | Owner | Next action |
| --- | --- | --- | --- | --- | --- |
| C-01 |  | fact / inference / decision / question |  |  |  |

Status definitions:

- **Fact:** directly supported by evidence.
- **Inference:** reasonable but not conclusively established.
- **Decision:** chosen by someone with authority.
- **Question:** requires more evidence or an accountable owner.

#### 4. Ontology worksheet

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

#### 5. ADR candidate register

The investigation identifies decisions; it does not silently approve them.

| Candidate | Decision required | Alternatives | Evidence available | Missing owner/input |
| --- | --- | --- | --- | --- |
| ADR-C01 | Define the analytical system boundary |  |  |  |
| ADR-C02 | Define revenue recognition time |  |  |  |
| ADR-C03 | Define late-arrival treatment |  |  |  |

#### 6. Investigation gate

- [ ] Every important claim has evidence or an explicit uncertainty label.
- [ ] The operational investigation remained read-only.
- [ ] Ontology edges show status, evidence, and ownership.
- [ ] Business decisions were not invented by the agent.
- [ ] ADR candidates are proposals, not approved records.
- [ ] The technical brief can be reviewed without replaying the chat.

### A5. Investigation telemetry contract


Telemetry makes the investigation trajectory inspectable. It should help answer
what the agent inspected, which tools it used, what it claimed, how claims were
verified, where it became uncertain, and which artifacts changed.

Telemetry does not make an answer correct by itself. It provides evidence about
the process that produced the answer.

#### Minimum event types

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

#### Minimum event fields

| Field | Purpose |
| --- | --- |
| `timestamp` | When the event occurred |
| `run_id` | Which investigation run produced it |
| `actor` | Human or agent responsible for the action |
| `phase` | Current investigation phase |
| `action` | Event type |
| `ontology_entity` | Optional business entity affected |
| `evidence_reference` | Path, schema object, or safe query identifier |
| `outcome` | Success, failure, rejection, escalation, or open |
| `duration_ms` | Optional elapsed time |

#### JSONL example

```json
{"timestamp":"2026-08-10T22:05:00Z","run_id":"foundation-demo","actor":"agent","phase":"context","action":"context_loaded","ontology_entity":null,"evidence_reference":"context-pack/business-brief","outcome":"success","duration_ms":18}
```

#### Safety rules

Never record:

- passwords or secret-bearing connection strings;
- `.env` contents;
- personal customer data;
- complete database rows;
- private instructor material;
- full prompts containing secrets;
- the later-module oracle or incident details.

Prefer query identifiers, aggregate counts, hashes, and file paths over raw data.

#### End-of-session summary

Report:

- time to first verified claim;
- context sources used;
- read-only queries executed;
- verified and rejected claims;
- open questions and escalations;
- artifacts updated;
- gate outcome.

#### Implementation status

This section defines the investigation contract. A live emitter or tracing adapter
must be implemented and rehearsed separately before the facilitator promises
live telemetry collection. Manual event capture can demonstrate the schema, but
must not be presented as automated instrumentation.

### A6. Technical brief template


- Status: draft / reviewed / approved
- Authors:
- Review owner:
- Evidence window:

#### 1. Business problem

What decision or outcome is required, and why does it matter?

#### 2. Current system boundary

Describe the operational system, analytical pressure, interfaces, and authority
boundaries.

#### 3. Data inventory

| Source/table | Purpose | Business time | Ingestion time | Evidence |
| --- | --- | --- | --- | --- |

#### 4. Ontology v1

| Subject | Relationship | Object | Status | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |

#### 5. Confirmed rules

| Rule | Scope | Evidence | Validation query/reference |
| --- | --- | --- | --- |

#### 6. Facts, inferences, decisions, and questions

| ID | Statement | Status | Evidence | Owner | Next action |
| --- | --- | --- | --- | --- | --- |

#### 7. Risks and constraints

- Operational safety:
- Data quality:
- Semantic ambiguity:
- Freshness:
- Privacy/security:
- Recovery:

#### 8. Proposed analytical boundary

Describe what should cross from Postgres into DuckDB, in which direction, and
which meanings and constraints must survive.

#### 9. Success measures

Define observable, falsifiable outcomes. Avoid "works correctly" without a
measurement or evidence source.

#### 10. Non-goals

State what this investigation is not authorizing or implementing.

#### 11. ADR candidates

| Candidate | Decision required | Alternatives | Evidence | Missing owner/input |
| --- | --- | --- | --- | --- |

#### 12. Open questions

| Question | Why it blocks or changes the design | Owner | Due/next step |
| --- | --- | --- | --- |

#### 13. Evidence appendix

List repository paths, schema objects, safe query identifiers, and telemetry run
IDs. Do not paste credentials, personal data, or complete rows.

#### Review gate

- [ ] Important claims are evidenced or explicitly uncertain.
- [ ] Business decisions have accountable owners.
- [ ] The proposed boundary is read-only and one-directional where required.
- [ ] The brief does not authorize later-module implementation.
- [ ] Human review is recorded.

### A7. Investigation reflection


Use the technical brief, evidence ledger, ontology, and telemetry summary. Do not
answer from memory alone.

1. What did we initially believe?
2. What did we actually observe?
3. Which assumption failed?
4. Which context source changed the result?
5. What did the ontology make visible?
6. What did telemetry reveal that the final answer did not?
7. Which conclusion still requires a human owner?
8. What artifact will the next module's work rely on?
9. What remains manual?
10. What would a later machine automate?

#### Skill card

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

#### Next-module hook

> The investigation established understanding before execution. Next, we build
> the rails that turn that understanding into controlled work.

## 21. Appendix B - Facilitation runbook

Operational evidence, readiness gates, and recovery guidance for the foundation
investigation.

### B1. Validated baseline

Validated locally from a newly recreated Docker volume:

```bash
make bootstrap
make status
```

Observed clean baseline with the default `.env.example` settings:

| Table | Rows |
| --- | ---: |
| `public.customers` | 5,000 |
| `public.products` | 400 |
| `public.orders` | approximately 64,000 |
| `public.payments` | approximately 62,000 |

The exact timestamps and final partial-day row counts are relative to seed time.
Do not promise identical order/payment counts or wall-clock timestamps on every
laptop.

### B2. Pre-session checklist

- [ ] Docker is running.
- [ ] `uv` is installed.
- [ ] `make bootstrap` completed while network was reliable.
- [ ] The bootstrap output shows doctor readiness, passing unit contracts,
  seven passing delivery checks, and a passing dbt connection/parse.
- [ ] `make status` shows the expected clean row-count range and freshness.
- [ ] The reviewed baseline is committed, and the exact revision used for class
  is recorded.
- [ ] The Appendix A context pack is ready to distribute or paste into the
  approved agent context.
- [ ] The presentation opens without missing fonts or assets.
- [ ] Weak-prompt and structured-prompt fallback outputs are available.
- [ ] Ontology v1 and technical-brief fallback artifacts are available.
- [ ] Telemetry collection has been implemented and rehearsed, or is described
  honestly as a manual contract demonstration.

`make bootstrap` intentionally replaces the generated `warehouse.duckdb` file
so the presentation starts with zero detector rows. Do not run it over a
participant's later-module work without first preserving that generated artifact.

### B3. Safe investigation commands

```bash
make doctor
make status
make query-ro Q="select count(*) from raw.orders"
```

Use approved read-only SQL for live investigation. Do not run `make inject`,
`make reveal`, or `make score` during the foundation investigation.

### B4. Evidence already validated

- Fresh Docker-volume initialization applies the three Postgres init scripts.
- The baseline seeder completed and passed its clean-data assertions.
- `analytics_ro` could read the public path and was denied access to `_control`.
- `analytics_ro` was denied writes to `public.customers`.
- `make psql-ro` opened with the intended analytical role.
- `make query-ro` could read DuckDB and rejected a `CREATE TABLE` statement.
- DuckDB row counts matched Postgres for all four source tables.
- DuckDB contained no control/injected-incident tables.
- The all-defects scenario injected 14 incident records and landed successfully.
- Every named defect injector completed independently.
- The scorer returned 100% precision, recall, and F1 against a perfect validation
  fixture.
- Re-landing preserved existing `analytics.detections` rows.
- `dbt debug` connected to DuckDB and `dbt parse` validated the deliberately
  empty model shell.

### B5. Truth boundary

The current seal protects the `analytics_ro` and DuckDB landing path. It does not
hide instructor truth from the owner of the local laptop or repository. Keep the
investigating agent on the approved context pack and operational surfaces.
Before the Incident Exercise, choose whether a workflow seal is sufficient or
move the oracle and injection implementation into an instructor-controlled
environment.

### B6. Recovery paths

#### Postgres is unavailable

```bash
make up
make doctor
```

If the volume is disposable and initialization is suspect:

```bash
make reset
make doctor
make land
```

`make reset` destroys the local teaching database volume. Never use it against a
non-disposable database.

#### DuckDB landing is missing or stale

```bash
make land
make verify
```

#### DuckDB extension is unavailable

Run `make setup` with network access. Keep a pre-warmed facilitator environment
and prepared evidence screenshots/output for the live session.

#### The live agent run fails

- Keep the failure visible if it teaches a real boundary.
- Do not present a prepared output as if it were generated live.
- Switch to the prepared context inventory or ontology checkpoint.
- Continue the human review and skill distillation.

### B7. Current gap

The repository contains a telemetry contract but no verified live telemetry
emitter or tracing adapter yet. This does not block the Postgres/DuckDB
foundation investigation, but it blocks claiming that telemetry is being
collected automatically. Implement and rehearse that surface before putting it
in the live demo path.
