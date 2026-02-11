# Tutor — Claude Code Plugin Draft

> Self-contained design doc for a Claude Code plugin that writes project tutorials
> tailored to a configured audience and focus. Transfer this file to a new repo
> and use it as the spec to build from.

## Plugin Structure

```
tutor/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── init/
│   │   └── SKILL.md          # /tutor:init — one-time setup, ~350 words
│   ├── write/
│   │   └── SKILL.md          # /tutor:write — generate tutorials, ~100 words
│   └── ask/
│       └── SKILL.md          # /tutor:ask — Q&A grounded in tutorials, ~100 words
└── README.md
```

### plugin.json

```json
{
  "name": "tutor",
  "description": "Audience-aware tutorial generation and Q&A for any codebase",
  "author": {
    "name": "",
    "email": ""
  }
}
```

---

## Design Principles

1. **Three skills, one namespace.** `tutor:init`, `tutor:write`, and
   `tutor:ask` share config but have separate descriptions optimized for
   their own trigger conditions. Only the one that matches loads.

2. **Generated guide, not baked-in rules.** The behavioral instructions
   (audience adaptation, section weights, style rules) live in a generated
   `.tutor/GUIDE.md` file, not in the skill definitions. Read on-demand
   via the Read tool, not loaded into every conversation.

3. **Config is data, guide is behavior.** `.tutor/config.yaml` stores
   settings (audience level, focus weights, presets). `.tutor/GUIDE.md`
   stores prose instructions derived from that config. Both are human-editable.

4. **Outline before prose.** The writing flow always presents a section
   outline for user approval before generating the full tutorial. This is
   the highest-leverage quality gate.

5. **Questions become gap signals.** When `/tutor:ask` can't answer from
   existing tutorials, it flags the gap and offers to write a new one. This
   creates a feedback loop: questions reveal what's missing.

6. **Configurable triggers.** Tutorial writing can be manual-only, or
   automatically triggered before/after implementation via a generated
   CLAUDE.md snippet. The trigger mode is a project-level setting.

---

## Skill 1: `init/SKILL.md`

Invoked once per project via `/tutor:init`. Asks questions, writes config,
generates a tailored writing guide, and optionally injects CLAUDE.md triggers.

```markdown
---
name: init
description: Use when setting up tutorial conventions for a project
  for the first time, or reconfiguring tutorial preferences.
version: 0.1.0
---

# Tutor Init

Set up tutorial writing config for this project.

## Step 1: Gather context

Read README, CLAUDE.md, or package metadata to infer project summary.
Confirm with user.

## Step 2: Ask preferences

Use AskUserQuestion for each (batch where possible):

**Audience** — Who reads these?
- Developers on my team | OSS contributors | Non-technical | (Other)

**Baseline knowledge** (if technical audience) — Multi-select from
project-relevant topics inferred from codebase.

**Focus areas** — Multi-select:
- Why decisions were made (design_choices)
- How the code works (implementation)
- How to use it (examples)
- How it fits together (connections)

**Style** — Narrative walkthrough | Reference docs | FAQ format

**Trigger mode** — When should tutorials be written?
- Manual only (call /tutor:write yourself)
- Before implementation (write tutorial first, then code)
- After implementation (write tutorial after code is done)
- Both (before and after — plan then update)

## Step 3: Write config

Write `.tutor/config.yaml` (see Config Schema below).

## Step 4: Generate GUIDE.md

Write `.tutor/GUIDE.md` — a tailored writing guide. NOT a generic
template. Generate specifically for this project's audience and focus:

- Audience adaptation rules (what to define, what to skip, tone)
- Section expectations per focus weight (skip/light/normal/heavy)
- Style rules for the chosen format
- Frontmatter requirements
- Naming convention with examples using actual project topics
- Quality bar for the target reader

## Step 5: Generate CLAUDE.md snippet

If trigger mode is NOT "manual only", append a section to the
project's CLAUDE.md (or create one). The snippet references
/tutor:write at the appropriate point in the workflow.

See "Trigger Mode" section below for the exact snippets.

## Step 6: Create directory

Create `tutorials/` if it doesn't exist. Done.
```

---

## Skill 2: `write/SKILL.md`

The primary writing skill. Must be lean.

```markdown
---
name: write
description: Use when creating or updating tutorials, documentation,
  or explanatory writeups for project code.
version: 0.1.0
---

# Tutor Write

1. Read `.tutor/config.yaml` and `.tutor/GUIDE.md`
   - If missing, tell the user to run `/tutor:init` first and stop
2. If no topic given, ask what to write about (current work,
   a module, a concept, or a phase)
3. Read relevant source files and existing tutorials
4. Present a section outline for approval
5. Write the tutorial following GUIDE.md instructions exactly
6. Support `--preset <name>` to override focus weights from config
7. Support `--audience <level>` for one-off audience override
```

---

## Skill 3: `ask/SKILL.md`

Q&A skill grounded in existing tutorials. Lean, separate trigger.

```markdown
---
name: ask
description: Use when asking questions about project architecture,
  design decisions, or how code works — answers grounded in existing
  project tutorials.
version: 0.1.0
---

# Tutor Ask

Answer questions using existing tutorials as primary source.

1. Read `.tutor/config.yaml` and `.tutor/GUIDE.md`
   - If missing, tell the user to run `/tutor:init` first and stop
2. Search `tutorials/` directory for content relevant to the question
3. Read matching tutorials fully
4. Read related source files for additional context if needed
5. Answer grounded in tutorial explanations first, source code second
   - Match the audience level and style from config
   - Cite which tutorial the answer draws from
6. If tutorials don't cover the question:
   - Say so explicitly
   - Answer from source code with a caveat
   - Offer: "This isn't covered yet. Run `/tutor:write <topic>`?"
```

---

## Trigger Mode

The trigger setting controls whether tutorials are written automatically
as part of the development workflow, or only when manually invoked.

### How it works

`/tutor:init` generates a CLAUDE.md snippet based on the chosen mode.
This uses Claude Code's native instruction system — no special hook
infrastructure needed. The snippet is clearly marked so users can
edit or remove it.

### Generated CLAUDE.md snippets by mode

**`manual`** — no snippet generated.

**`pre`** — tutorial before implementation:
```markdown
<!-- tutor:triggers — auto-generated by /tutor:init, edit freely -->
## Tutorial-First Development
Before implementing any new feature, phase, or significant code change,
run `/tutor:write` to create a tutorial covering the planned work.
The tutorial should explain the design, approach, and reasoning BEFORE
code is written. This ensures clarity of thought and creates documentation
as a side effect of planning.
<!-- /tutor:triggers -->
```

**`post`** — tutorial after implementation:
```markdown
<!-- tutor:triggers — auto-generated by /tutor:init, edit freely -->
## Post-Implementation Tutorials
After completing a new feature, phase, or significant code change,
run `/tutor:write` to create or update a tutorial covering what was
built. The tutorial should explain the final design, key decisions
made during implementation, and how the code works.
<!-- /tutor:triggers -->
```

**`both`** — plan tutorial before, update after:
```markdown
<!-- tutor:triggers — auto-generated by /tutor:init, edit freely -->
## Tutorial-Driven Development
Before implementing any new feature or significant change, run
`/tutor:write` to draft a tutorial covering the planned approach.
After implementation is complete, run `/tutor:write --update` to
revise the tutorial to reflect what was actually built.
<!-- /tutor:triggers -->
```

### Changing trigger mode

Run `/tutor:init` again to reconfigure. It will find and replace the
existing `<!-- tutor:triggers -->` block in CLAUDE.md, or remove it
if switching to `manual`.

---

## Config Schema: `.tutor/config.yaml`

Generated by `/tutor:init`. Human-editable after generation.

```yaml
# Generated by /tutor:init — edit freely
project:
  summary: "One-line project description for tutorial context"

audience:
  profile: "developers on my team"       # free text
  technical_level: intermediate           # beginner | intermediate | expert
  assumed_knowledge:                      # list of things NOT to explain
    - Python
    - git basics

focus:
  conceptual: normal          # skip | light | normal | heavy
  design_choices: heavy       # "why was this approach chosen?"
  implementation: heavy       # "how does the code work?"
  connections: normal         # "how does this fit the bigger picture?"
  examples: heavy             # "show me runnable code"

triggers:
  mode: pre                   # manual | pre | post | both

output:
  directory: tutorials/
  style: narrative            # narrative | reference | faq
  naming: "{nn}-{slug}.md"   # nn = number, slug = kebab-case
  frontmatter: true
  frontmatter_fields:
    - date
    - summary
    - audience

presets:
  quick:
    focus_override:
      conceptual: light
      implementation: skip
    length: brief
  deep-dive:
    focus_override:
      conceptual: heavy
      design_choices: heavy
      implementation: heavy
      connections: heavy
      examples: heavy
    length: comprehensive
```

---

## Generated Guide: `.tutor/GUIDE.md`

This is what `/tutor:init` produces — tailored to the specific project.
Below is an **example** for a Python library project with intermediate
developer audience, heavy design + implementation focus, narrative style.

```markdown
# Tutorial Writing Guide

## Audience

Intermediate Python developers. Assume fluency with Python, decorators,
context managers, dataclasses. Do NOT assume knowledge of project-specific
libraries (introduce on first use with a one-sentence explanation).

## Section Weights

| Focus Area     | Weight | What to write                                            |
|----------------|--------|----------------------------------------------------------|
| Conceptual     | normal | 1-2 paragraphs establishing the "why" and mental model   |
| Design choices | heavy  | Dedicated section. Alternatives considered, tradeoffs     |
| Implementation | heavy  | Walk through key functions and data flow with code        |
| Connections    | normal | Brief paragraph linking to related modules                |
| Examples       | heavy  | Runnable snippets with expected output shown              |

### Weight definitions

- **skip**: Omit entirely
- **light**: 1-2 sentences, no dedicated section
- **normal**: Standard paragraph-level coverage
- **heavy**: Dedicated section, go deep, this is a primary draw

## Style: Narrative

Write as a linear walkthrough. "First we... then we... because..."
Embed code blocks in explanatory prose. Avoid bullet-point-only sections.
Each section should flow into the next.

## Frontmatter

Every tutorial starts with:

```yaml
---
date: YYYY-MM-DD
summary: "One line describing what this tutorial covers"
audience: [intermediate, python]
---
```

## Naming Convention

`tutorials/{nn}-{slug}.md`

Use two-digit numbers for ordering. Use lowercase letters for sub-topics:
- `01-overview.md` — phase or feature overview
- `01a-data-models.md` — sub-topic deep dive
- `01b-storage-layer.md`

## Quality Bar

After reading, the target reader should be able to:
- Explain WHY each design decision was made
- Trace the data flow without reading source code first
- Ask informed questions about alternatives and tradeoffs
```

---

## Audience Adaptation Reference

These are the rules `/tutor:init` should bake into GUIDE.md based on
the selected audience level. NOT loaded into any skill — only used
during guide generation.

### Beginner
- Define every term on first use
- Use analogies to familiar concepts
- No unexplained jargon or acronyms
- Start every section with "why" before "how"
- Show complete, runnable examples (not fragments)
- Explain what the output means, not just what it is

### Intermediate
- Assume language fluency and standard library knowledge
- Introduce project-specific libraries on first use (one sentence)
- Focus on project-specific decisions and patterns
- Code examples can be fragments if context is clear
- Can reference external docs instead of re-explaining basics

### Expert
- Skip language and framework fundamentals entirely
- Focus on non-obvious design tradeoffs and edge cases
- Discuss architectural reasoning and alternatives in depth
- Code examples focus on subtle or surprising behavior
- Can assume familiarity with the problem domain

---

## Usage Examples

```bash
# First time setup — asks questions, writes config + guide
/tutor:init

# Write a tutorial on a topic
/tutor:write the caching layer

# Write about whatever you're currently working on
/tutor:write

# Quick version (lighter focus, shorter)
/tutor:write --preset quick the auth module

# Deep dive
/tutor:write --preset deep-dive state management

# One-off audience override (doesn't change saved config)
/tutor:write --audience beginner the API endpoints

# Update an existing tutorial after code changed
/tutor:write --update 01a-data-models

# Ask a question — answered from tutorials first
/tutor:ask why did we choose SQLite over Postgres?

# Ask about architecture
/tutor:ask how does the compile cache work?
```

---

## How the Three Skills Interact

```
/tutor:init ──writes──▶ .tutor/config.yaml
                        .tutor/GUIDE.md
                        tutorials/
             ──injects─▶ CLAUDE.md (trigger snippet, if not manual)

/tutor:write ──reads──▶ .tutor/config.yaml
                        .tutor/GUIDE.md
             ──reads──▶ source files, existing tutorials
             ──writes─▶ tutorials/{nn}-{slug}.md

/tutor:ask ──reads──▶ .tutor/config.yaml
                      .tutor/GUIDE.md
           ──reads──▶ tutorials/*.md (search + read)
           ──reads──▶ source files (if tutorials insufficient)
           ──offers─▶ /tutor:write (when gap detected)

CLAUDE.md trigger ──invokes──▶ /tutor:write (at configured point)
```

---

## Future Considerations

Not in v0.1, worth considering later:

1. **Gap detection** (`tutor:gaps`) — scan tutorials/ and source code,
   suggest modules or features that lack tutorial coverage.

2. **Staleness detection** (`tutor:update`) — diff source code against
   existing tutorials, flag sections referencing changed or removed APIs.

3. **Cross-references** — auto-insert "See also: 01a-data-models.md"
   links between related tutorials.

4. **Multi-audience variants** — generate beginner AND expert versions
   of the same tutorial from one outline, to separate subdirectories.

5. **CI integration** — a hook that warns when code changes touch modules
   that have tutorials, prompting a tutorial update.
