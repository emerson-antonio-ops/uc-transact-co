# Day 1 — Interview the System Before You Build

The question carried through the session is:

> How much Revenue did TransactCo make yesterday, and why should the CFO trust
> that number?

The audience should leave understanding that prompts define work, context
selects evidence, ontology governs meaning, and agentic systems remain bounded
by observable actions and human decisions.

## The complete story

```mermaid
flowchart LR
    S0[00 Baseline] --> S1[01 Weak prompt]
    S1 --> S2[02 Contract]
    S2 --> S3[03 Context and evidence]
    S3 --> S4[04 Ontology]
    S4 --> S5[05 Telemetry]
    S5 --> S6[06 Brief]
    S6 --> S7[07 Skill]
    S7 --> S8[08 Reflection]

    classDef setup fill:#E5E7EB,stroke:#4B5563,color:#111827
    classDef prompt fill:#EDE9FE,stroke:#7C3AED,color:#3B0764
    classDef evidence fill:#DCFCE7,stroke:#16A34A,color:#14532D
    classDef meaning fill:#DBEAFE,stroke:#2563EB,color:#172554
    classDef human fill:#FEF3C7,stroke:#D97706,color:#78350F
    class S0 setup
    class S1,S2 prompt
    class S3,S5,S6 evidence
    class S4,S7 meaning
    class S8 human
```

## Sequence and deck switches

| Step | Session | Deck cue | Demo evidence | Durable result |
| ---: | --- | --- | --- | --- |
| [`00`](00-setup.md) | No agent | The inherited system | Health and four entities | Baseline only |
| [`01`](01-weak-prompt.md) | **NEW A** | Ambiguity creates hidden choices | Three prompt failures | None |
| [`02`](02-investigation-contract.md) | **NEW B** | Prompt becomes contract | Human-confirmed boundary | None |
| [`03`](03-context-inventory.md) | **NEW C** | Context selects evidence | Source table and reconciliation | `1-context.md` |
| [`04`](04-ontology.md) | Continue C | Data is not meaning | Postgres versus ontology | `2-ontology.md` |
| [`05`](05-agentic-investigation.md) | Continue C | Trajectory is observable | Six telemetry events | Temporary trace |
| [`06`](06-technical-brief.md) | Continue C | Evidence survives chat | Human-review gate | `3-technical-brief.md` |
| [`07`](07-skill-reveal.md) | **NEW D** | Practice becomes automation | Validator and human stop | Temporary skill package |
| [`08`](08-reflection.md) | No agent | Distill the practice | Participant commitment | Team learning |

Switch in the same rhythm every time:

```text
DECK: explain why
  -> DEMO: perform one bounded action
  -> EVIDENCE: show only the named proof
  -> DECK: state what changed
  -> GATE: continue or keep the failure visible
```

## Output budgets

| Checkpoint | Visible agent response | Artifact budget |
| ---: | --- | --- |
| 01 | 6 bullets, 180 words | None |
| 02 | One 8-row table, 300 words | None |
| 03 | 120-word summary | 1,500 prose words, 8 evidence IDs, 16 ledger rows |
| 04 | 100-word summary | 700 words, one comparison table |
| 05 | One sentence | Exactly six JSONL events |
| 06 | 5 bullets, 100 words | 800 words |
| 07 | 6 bullets, 150 words | Validated package; inspect only selected fields |

Output budgets protect audience attention. Exact SQL and complete machine
artifacts remain available for review but are not read aloud.

## Artifact workspace

```text
storage/specs/
├── 1-context.md
├── 2-ontology.md
└── 3-technical-brief.md

tmp/foundation-investigation/
├── manual/
│   └── trace.jsonl
└── skill/
    ├── investigation.json
    ├── technical-brief.md
    └── trace.jsonl
```

Create directories with:

```bash
mkdir -p storage/specs
mkdir -p tmp/foundation-investigation/manual
mkdir -p tmp/foundation-investigation/skill
```

Move previous rehearsal artifacts to a uniquely named directory before a clean
run. Prepared and live evidence must never be mixed.

## Shared boundaries

- Postgres access is read-only.
- Each checkpoint authorizes only its named output.
- Session A demonstrates failure and is discarded.
- Session B designs the contract and stops.
- Session C carries the manual investigation through the brief.
- Session D proves the skill without inherited chat memory.
- Browser/Playwright MCP is disconnected during repository-only checkpoints.
- Structural validation never approves business meaning.

## Completion gate

- [ ] The baseline was healthy without being mistaken for semantic trust.
- [ ] Weak-prompt failures were visible.
- [ ] A human confirmed the investigation contract.
- [ ] Context and exact evidence were selected deliberately.
- [ ] Postgres measurements remained separate from ontology meaning.
- [ ] The trajectory showed evidence, rejection, and escalation.
- [ ] The brief remained `pending human review`.
- [ ] The skill reproduced the method and the human stop.
- [ ] The room named one reusable practice.

If a gate fails, preserve the failure and use the checkpoint recovery. Do not
widen authority or substitute prepared output without labeling it.
