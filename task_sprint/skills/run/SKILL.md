---
name: task-sprint:run
description: "User-initiated sequential task execution from .task-sprint/ checklist files."
version: 0.1.0
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Task Sprint Runner

Execute all pending tasks from `.task-sprint/TASKS_*.md` files in batches of up to 5. You implement each task yourself — no subagents.

## Step 1: Validate workspace

Check that `.task-sprint/` exists in the current working directory.

- If it does not exist, create it and tell the user: "Created `.task-sprint/`. Add a task file like `TASKS_2026_02_12_0.md` with `- [ ]` checkboxes and run `/task-sprint:run` again." Then STOP.
- If the directory exists but contains no `TASKS_*.md` files, tell the user the same. Then STOP.

## Step 2: Load optional context

Check if `.task-sprint/CONTEXT.md` exists. If it does, read its full contents and keep it in mind for all tasks.

## Step 3: Begin the main loop

This is an infinite loop. It runs until the user sends a keyboard interrupt (Ctrl+C).

### 3a: Scan for pending tasks

If the user specifies which task file to read (e.g. only the first one from today), read accordingly. Otherwise, use Glob to find all `.task-sprint/TASKS_*.md` files from today. Read those files.

**First, reset orphaned in-progress markers.** Any line matching `- [IP]` at the start of the line (no leading whitespace) is from a previous interrupted run. Use Edit to change each `- [IP]` back to `- [ ]`. Print `[RESET] {task_text}` for each one.

**Then, parse pending tasks.** Collect all lines matching `- [ ]` at the start of the line (no leading whitespace). Indented checkboxes are sub-items — ignore them.

Build a work queue of `(file_path, line_number, task_text, previous_line)`. The previous line is used for disambiguation when editing checkboxes.

Track a `retry_count` dictionary keyed by task text, initialized to 0 for new tasks.

Skip `- [x]` (completed) and `- [!]` (permanently failed).

If the queue is empty, print:
```
All tasks complete. Watching for new tasks... (Ctrl+C to stop)
```
Then sleep 17.5 seconds (`sleep 17.5` on Unix, `powershell -command "Start-Sleep -Seconds 17.5"` on Windows) and go back to **3a**.

### 3b: Execute a batch

Take up to 5 tasks from the work queue. For each task in the batch, sequentially:

1. **Mark in-progress.** Edit `- [ ]` to `- [IP]` in the source file. Use `previous_line + \n + task_line` as the `old_string` for disambiguation. If the task is the first line in the file, use just the task line.
2. **Implement the task.** Read relevant code, make changes, run commands — whatever the task requires. Do the work directly.
3. **Mark result.**
   - On success: Edit `- [IP]` to `- [x]` (same disambiguation). Print `[DONE] {task_text}`.
   - On failure: Edit `- [IP]` back to `- [ ]`. Increment `retry_count`. Print `[RETRY x{count}] {task_text} — {reason}`. Push the task to the end of the queue.

### 3c: Next batch or re-scan

If the work queue still has tasks, go to **3b**.

If the work queue is empty, go to **3a** (re-scan for new tasks).

## Important rules

- **You do all the work yourself.** No subagents. Read code, edit files, run tests — directly.
- **Never skip a task.** Every `- [ ]` gets attempted. Failed tasks get retried.
- **Task lifecycle: `[ ]` → `[IP]` → `[x]`.** Mark in-progress when starting, completed when done, or back to `[ ]` on failure. On scan, reset orphaned `[IP]` to `[ ]`.
- **Preserve file contents exactly.** Only change the checkbox marker on the specific line. Do not reformat or reorder anything else.
- **The loop never stops on its own.** After all tasks complete, keep watching for new ones.
- **Be concise.** Stick to `[DONE]` / `[RETRY]` output. No walls of text between tasks.
