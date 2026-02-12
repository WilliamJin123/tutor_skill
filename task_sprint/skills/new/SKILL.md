---
name: task-sprint:new
description: "Create .task-sprint/ directory (if needed) and a new dated task file."
version: 0.1.0
user-invocable: true
allowed-tools: Bash, Write, Glob
---

# Task Sprint New

Create the `.task-sprint/` directory if it doesn't exist, then create a new dated task file with the next available suffix.

## Step 1: Ensure directory exists

If `.task-sprint/` does not exist, create it.

## Step 2: Determine file name

Get today's date using Bash (`date +%Y_%m_%d` on Unix, `powershell -command "Get-Date -Format 'yyyy_MM_dd'"` on Windows).

Use Glob to find all existing `.task-sprint/TASKS_{today's date}_*.md` files. Determine the next suffix number:
- If no files exist for today → suffix is `0`
- If `_0` exists → suffix is `1`
- If `_0` and `_1` exist → suffix is `2`
- And so on (find the max existing suffix and add 1)

## Step 3: Create the file

Write `.task-sprint/TASKS_{YYYY}_{MM}_{DD}_{suffix}.md` with:

```md
- [ ] Replace this with your first task
```

## Step 4: Confirm

Print:
```
Created .task-sprint/TASKS_{date}_{suffix}.md

Add your tasks as `- [ ]` checkboxes (one per line), then run /task-sprint:run.
Optional: create .task-sprint/CONTEXT.md with shared project context for all agents.
```

Only show the "Optional: create CONTEXT.md" line if `CONTEXT.md` does not already exist.
