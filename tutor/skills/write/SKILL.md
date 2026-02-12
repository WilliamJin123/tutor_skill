---
name: tutor:write
description: >
  Use when creating or updating tutorials, documentation, or explanatory
  writeups for project code. Generates audience-aware tutorials following
  the project's configured style and focus areas.
version: 0.1.0
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Task
---

# Tutor Write

Generate or update a tutorial for this project.

## Step 1: Load configuration

Read `.tutor/config.yaml` and `.tutor/GUIDE.md`.
- If either file is missing, tell the user: "Tutorial config not found. Run `/tutor:init` first to set up your project." Then STOP — do not proceed.

## Step 2: Parse arguments

Check for optional flags in the user's input:
- `--preset <name>` — Look up the preset in config.yaml's `presets` section. Override focus weights and length accordingly. If the preset doesn't exist, list available presets and ask the user to pick one.
- `--audience <level>` — Temporarily override the audience technical_level for this tutorial only (beginner/intermediate/expert). Adjust the writing style per the GUIDE.md audience rules for that level.
- `--update <slug>` — Find the existing tutorial matching the slug in the tutorials/ directory. Read it fully. The goal is to revise it based on current source code, not write from scratch.

If no topic is provided, ask the user: "What should this tutorial cover?" Suggest options based on recent git changes, current working branch, or modules that lack tutorial coverage.

## Step 3: Research the topic

Use subagents (Task tool with subagent_type "Explore") to research in parallel:
- Read relevant source files for the topic (use Glob and Grep to find them)
- Read any existing tutorials in the tutorials/ directory that relate to this topic
- Identify key concepts, data flows, design decisions, and public APIs

Synthesize the research into a mental model of what needs to be explained.

## Step 4: Present outline for approval

Present a structured section outline to the user. The outline should:
- Follow the section weights from config (skip/light/normal/heavy)
- Apply any preset overrides
- List each planned section with a 1-sentence description of what it will cover
- Estimate relative length (brief paragraph vs. detailed walkthrough)

Wait for user approval before proceeding. If the user requests changes to the outline, incorporate them.

## Step 5: Write the tutorial

Follow `.tutor/GUIDE.md` instructions exactly:
- Use the configured style (narrative/reference/faq)
- Apply audience adaptation rules for the configured technical level
- Include frontmatter as specified in config
- Weight each section according to focus settings
- Use the naming convention from config for the filename

For `--update` mode:
- Preserve the existing file's frontmatter date (add an "updated" date)
- Keep sections that are still accurate
- Revise sections where source code has changed
- Add new sections for new functionality
- Remove sections for deleted functionality

## Step 6: Write the file

Write the tutorial to the tutorials/ directory using the configured naming convention.
- Auto-assign the next available number prefix
- Use kebab-case slugs derived from the topic
- If updating, overwrite the existing file

Report what was written: filename, sections covered, word count estimate.

## Step 7: Commit

Commit the tutorial with a basic overview of it in the commit message.
