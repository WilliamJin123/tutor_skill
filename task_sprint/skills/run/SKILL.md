---
name: task-sprint:run
description: "User-initiated parallel task execution from .task-sprint/ checklist files."
version: 0.1.0
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task
---

# Task Sprint Runner

Execute all pending tasks from `.task-sprint/TASKS_*.md` files in parallel batches. Loop continuously until the user interrupts.

You are an orchestrator. You do NOT do the tasks yourself. You dispatch agents and manage state.

## Step 1: Validate workspace

Check that `.task-sprint/` exists in the current working directory.

- If it does not exist, create it and tell the user: "Created `.task-sprint/`. Add a task file like `TASKS_2026_02_12_0.md` with `- [ ]` checkboxes and run `/task-sprint:run` again." Then STOP.
- If the directory exists but contains no `TASKS_*.md` files, tell the user the same. Then STOP.

## Step 2: Load optional context

Check if `.task-sprint/CONTEXT.md` exists. If it does, read its full contents and store it. This will be prepended to every agent prompt as shared project context.

## Step 3: Begin the main loop

This is an infinite loop. It runs until the user sends a keyboard interrupt (Ctrl+C).

### 3a: Scan for pending tasks

Use Glob to find all `.task-sprint/TASKS_*.md` files. Read every file. Parse all lines matching the pattern `- [ ]` (unchecked checkboxes). **Only match lines where `- [ ]` starts at the beginning of the line (no leading whitespace).** Indented checkboxes are sub-items and must be ignored.

Collect matches into a work queue as tuples of `(file_path, line_number, task_text, previous_line)`. Store the previous line to use as disambiguation context when editing (see 3c).

Also track a `retry_count` dictionary keyed by task text, initialized to 0 for new tasks.

Skip lines matching `- [x]` (completed) and `- [!]` (permanently failed — not used by default, but the user may manually mark these).

If the work queue is empty, print:
```
All tasks complete. Watching for new tasks... (Ctrl+C to stop)
```
Then sleep 5 seconds using Bash (`sleep 5` on Unix, `powershell -command "Start-Sleep -Seconds 5"` on Windows) and go back to **3a**.

### 3b: Dispatch a batch

Take up to 5 tasks from the work queue. For each task, launch a Task agent using `run_in_background: true` with `subagent_type: "general-purpose"`.

Maintain up to 5 concurrent agents. As each agent completes, immediately dispatch the next task from the queue while other agents are still running.

The prompt for each agent MUST follow this exact structure:

```
{CONTEXT.md contents, if it exists}

## Working Directory

{absolute path to the current working directory}

## Your Task

{the task text from the checkbox}

## Rules

- Complete this task fully. Make all necessary code changes.
- Do NOT edit any file inside `.task-sprint/`.
- If you need to understand code before changing it, read it first.
- When done, respond with a brief summary of what you changed (files modified, what was done).
- If you cannot complete the task, your FINAL line of output must be exactly: @@TASK_FAILED: {reason}
```

After launching the batch, print a status line:
```
Dispatched batch: {N} tasks ({M} remaining in queue)
```

### 3c: Collect results

Wait for each background agent in the batch to finish. Use TaskOutput with appropriate timeouts (10 minutes per agent).

For each agent result:

**If the agent succeeded** (response does NOT contain `@@TASK_FAILED:` on its final line):
- Use Edit to change the task's `- [ ]` to `- [x]` in the source file. To avoid ambiguity with duplicate task text, use the `previous_line + \n + task_line` as the `old_string` and replace with `previous_line + \n + checked_line`. If the task is the first line in the file (no previous line), use just the task line.
- Print: `[DONE] {task_text}`

**If the agent failed** (final line contains `@@TASK_FAILED:` or agent timed out):
- Increment `retry_count` for this task
- Print: `[RETRY x{retry_count}] {task_text} — {reason}`
- Add the task back to the END of the work queue for retry in a future batch
- Do NOT edit the checkbox — it stays `- [ ]`

### 3d: Next batch or re-scan

If the work queue still has tasks, go to **3b**.

If the work queue is empty, go to **3a** (re-scan all files for new tasks).

## Important rules

- **You are the only one who edits task files.** Agents do the coding work and report back. You update checkboxes.
- **Never skip a task.** Every `- [ ]` gets attempted. Failed tasks get retried indefinitely.
- **Preserve file contents exactly.** When editing checkboxes, only change `- [ ]` to `- [x]` on the specific line. Do not reformat, reorder, or modify anything else in the file.
- **The loop never stops on its own.** After all tasks complete, keep watching. The user may add new tasks to existing files or drop new `TASKS_*.md` files at any time.
- **Be concise.** Your status output should be scannable. No walls of text between batches. Stick to the `[DONE]` / `[RETRY]` format with brief summaries.
