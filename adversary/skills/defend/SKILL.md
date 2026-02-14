---
name: adversary:defend
description: >
  Use after adversary:critique to push back on findings. Spawns an independent
  defense agent that reads the original source material and the critique findings
  without the attacker's reasoning context. Filters out overblown, invalid, or
  already-handled issues and produces a reconciled report of what actually matters.
version: 0.1.0
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, Task, AskUserQuestion
---

# Adversary Defend

Run a defense pass against a prior adversary:critique. The defense agent operates
in an isolated context — it never sees the attacker's chain of thought, only the
raw findings and the original source material.

## Step 1: Locate the critique

Find the most recent adversary:critique output in the conversation. Extract:

1. **The target** — what was critiqued (files, directories, diffs, plan documents).
2. **The raw findings** — the full critique report (every finding with its severity, evidence, and proposed fix).
3. **User constraints** — any guidance the user gave during or before the critique (e.g., "focus on security", "ignore styling", "I know X is rough"). These will be forwarded to the defense agent as context.

If no critique output is found in the conversation, ask the user to either run `adversary:critique` first or paste the findings they want defended against.

## Step 2: Build the file manifest

Do NOT read source files yourself. Instead, extract the list of file paths and
diff commands from the critique findings. The subagent will read them directly
with its own tools — this avoids duplicating file contents across two contexts.

Collect:
- **File paths**: Every `file:line` reference in the critique, plus any files
  mentioned as context (imports, callers, tests).
- **Diff commands**: If the critique targeted git changes, note the exact diff
  command(s) used (e.g., `git diff main...HEAD`).
- **Plan paths**: If the critique targeted plan documents, list those paths.

The output of this step is a compact manifest — a list of paths and commands,
not file contents.

## Step 3: Spawn the defense agent

Use the Task tool to spawn a **single subagent** (`subagent_type: "general-purpose"`).

Pass it ONLY:
- The file manifest from Step 2 (paths and diff commands — NOT file contents)
- The critique findings (the report text only — not the attacker's reasoning)
- Any user constraints from Step 1

The subagent will use its own Read/Grep/Bash tools to gather source material.
This keeps the parent context lean and avoids paying for file contents twice.

**Defense agent prompt template:**

```
You are the author's advocate. Your job is to defend this code/plan against
a set of critique findings. You believe the work is sound until proven otherwise.

## Step A: Read the source material

Read the following files and/or run the following commands to understand the
code/plan being defended. Read them yourself — do not ask for them to be
provided.

Files to read:
{file_manifest — list of absolute paths}

Diff commands to run (if any):
{diff_commands or "None — this is not a diff-based critique."}

## Step B: Evaluate each finding

For each finding, deliver one of three verdicts:
  - STANDS: The finding is legitimate. You have no credible defense.
  - DOWNGRADED: The finding has merit but the severity is inflated. State the
    correct severity (Critical → Serious, Serious → Minor, etc.) and why.
  - DISMISSED: The finding is wrong, irrelevant, or already handled. Provide
    a concrete, evidence-based rationale — quote the code/plan that disproves it.

Rules:
- You MUST evaluate every single finding. Do not skip any.
- Do NOT dismiss findings to be agreeable. Only dismiss what you can genuinely
  defend with evidence from the source material.
- Do NOT invent defenses. If the code is actually broken, say STANDS.
- Valid defenses cite specific evidence: caller validates at line N, framework
  guarantees this invariant, this is a cold path, the handling exists in file X
  at line Y, etc.
- Invalid defenses are speculation: "probably fine", "author likely intended
  this", "could be fixed later".

## User constraints
{user_constraints or "None provided."}

## Critique findings to defend against
{paste the critique report text only}

## Output format

For each finding, respond with:

### Finding N: <one-line summary>
- **Original severity**: Critical | Serious | Minor
- **Verdict**: STANDS | DOWNGRADED (→ new severity) | DISMISSED
- **Defense**: <evidence-based rationale, 1-3 sentences, cite file:line>
```

## Step 4: Reconcile

When the defense agent returns, review each verdict as the **final arbiter**. You are
not bound by the defender's conclusions. For each finding:

- **Defender said DISMISSED and the rationale is sound** → Accept. Move finding to dismissed.
- **Defender said DISMISSED but the rationale is weak or wrong** → Override. Finding STANDS. Note why the defense failed.
- **Defender said DOWNGRADED and the rationale holds** → Accept the new severity.
- **Defender said DOWNGRADED but you disagree** → Keep original severity with a note.
- **Defender said STANDS** → Finding stands. No further action.

## Step 5: Present the reconciled report

Output the final report with surviving and dismissed findings clearly separated.

```
## Defense Report: <target name>

### Surviving findings

#### Critical (must fix)
- **[Category]** `file:line` — <description>
  Evidence: <quote>
  Fix: <specific correction>

#### Serious (should fix)
- **[Category]** `file:line` — <description>
  Evidence: <quote>
  Fix: <specific correction>

#### Minor (consider fixing)
- **[Category]** `file:line` — <description>
  Fix: <specific correction>

### Dismissed by defense
- **[Category]** `file:line` — <one-line finding description>
  Defense: <evidence-based rationale for dismissal>

### Downgraded
- **[Category]** `file:line` — <one-line finding description>
  Original: <old severity> → New: <new severity>
  Rationale: <why the severity was reduced>

### Summary
- Original findings: N
- Survived: Critical: N | Serious: N | Minor: N
- Dismissed: N | Downgraded: N
- Defense quality: <how well the defense held up — did it catch real overcalls, or was it mostly unable to defend?>
- Final assessment: <1-2 sentence honest verdict on the actual state of the target>
```

Rules for the report:
- Omit any section with zero entries.
- Every surviving finding must include a concrete fix.
- The dismissed section exists for transparency — the user should be able to verify each dismissal.
- "Defense quality" is your meta-assessment of how much noise the original critique contained. If most findings survived, say so. If the defense filtered out a lot of chaff, note that too.

## Step 6: Walk through fixes

Iterate through each **surviving** finding (highest severity first). For each issue, use AskUserQuestion with:
- Concrete fix options
- A **"Skip"** option to reject the fix and move on

After walking through surviving findings, ask once:
> "Any dismissed findings you want to reinstate?"

with options listing the dismissed findings plus a "None — dismissed findings look correct" option.

Apply all accepted fixes after completing the full walkthrough.
