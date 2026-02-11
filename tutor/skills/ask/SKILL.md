---
name: tutor:ask
description: >
  Use when asking questions about project architecture, design decisions,
  or how code works. Answers are grounded in existing project tutorials
  first, then source code. Identifies tutorial coverage gaps.
version: 0.1.0
user-invocable: true
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion
---

# Tutor Ask

Answer questions using existing tutorials as the primary source of truth.

## Step 1: Load configuration

Read `.tutor/config.yaml` and `.tutor/GUIDE.md`.
- If either file is missing, tell the user: "Tutorial config not found. Run `/tutor:init` first to set up your project." Then STOP — do not proceed.

## Step 2: Search tutorials

Search the `tutorials/` directory for content relevant to the user's question:
- Use Grep to find keyword matches across all tutorial files
- Use Glob to list all tutorials and read their frontmatter summaries
- Rank tutorials by relevance to the question

If no tutorials exist yet, skip to Step 5 (gap handling).

## Step 3: Read and synthesize

Read the most relevant tutorials fully (up to 3). If the question spans multiple topics, read tutorials covering each.

Also read the `.tutor/GUIDE.md` to understand the configured audience level and style — your answer should match these settings.

## Step 4: Answer the question

Construct an answer following these rules:
- **Primary source**: Tutorial explanations. Quote or paraphrase directly.
- **Secondary source**: Source code, only when tutorials don't fully cover it.
- **Audience match**: Use the tone, vocabulary, and depth appropriate for the configured audience level (beginner/intermediate/expert).
- **Style match**: Follow the configured style (narrative explanation / reference format / FAQ format).
- **Citations**: Always cite which tutorial(s) the answer draws from, e.g., "From `tutorials/03-caching-layer.md`:"
- If source code supplements the answer, note it: "This isn't covered in tutorials yet, but from the source code:"

## Step 5: Handle coverage gaps

If tutorials don't cover the question (or only partially):

1. **Say so explicitly**: "This topic isn't covered in existing tutorials."
2. **Answer from source code** with a clear caveat: "Based on reading the source code (not yet documented in tutorials):"
3. **Offer to fill the gap**: "Want me to create a tutorial covering this? Run `/tutor:write <suggested-topic>`"

Track the question topic mentally — repeated questions about uncovered topics are strong signals for what to write next.

## Step 6: Suggest related reading

If relevant tutorials exist that the user might not know about, mention them:
"You might also find these tutorials useful:"
- `tutorials/01-overview.md` — Project architecture overview
- `tutorials/04-auth-flow.md` — Authentication design decisions
