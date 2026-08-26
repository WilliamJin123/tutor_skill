# Fix Orchestration — the wave playbook

Parallel agents collide on shared files. Waves make collisions structurally impossible: everything shared is edited once, centrally, before any agent spawns.

## 0. Setup

- Read the newest audit doc. Unless the user already gave a finding list, confirm the batch with AskUserQuestion.
- `git status` must be clean; otherwise stop and tell the user.
- Branch off main: `red-team/fixes-YYYY-MM-DD`. Never work on main.

## 1. Wave 0 — spine (you, centrally)

- Everything shared, edited once: models/schema, ONE migration, shared enums and interfaces.
- Pre-add any field two lanes will both touch (one lane populates a column, another validates it → the column lands here, now).
- Migration and schema-drift tests green before any agent spawns.
- Commit: `wave 0: schema spine`.

## 2. Wave 1 — lanes (parallel subagents)

- Partition findings into lanes with strictly disjoint file ownership. Two lanes needing one file → move that change into Wave 0, or merge the lanes.
- Spawn lanes with `model: sonnet`; escalate a lane to `opus` only after its first attempt proves inadequate.
- Every brief states, explicitly:
  - Files you own — exhaustive list. Everything else is read-only.
  - No commits. No dev-DB writes.
  - The exact test command, including env (e.g. `TESTCONTAINERS_RYUK_DISABLED=true uv run pytest ...`).
  - Return: what changed, API notes the integrator needs, test results.
- An agent dying mid-flight on a transient API error loses nothing: check `git status` for partial edits, then resume that same agent via SendMessage. Do not respawn from scratch — its context survives.
- All lanes done → commit: `wave 1: <finding ids>`.

## 3. Wave 2 — integrate (you, centrally)

- Global wiring no lane could own: CLI, exports, config.
- Full test suite + lint. Failures are fixed here, not by reopening lanes.
- Data repair: for every destructive query, write and run its read-only twin first, eyeball the counts, only then execute. Re-verify the final counts after.
- Docs: decision-log rows for structural changes, a remediation note at the top of the audit doc, republish affected artifacts.
- Commit: `wave 2: integrate + repair + docs`. Push the branch.

## 4. Handoff

Report per-finding status and the final verified numbers. The user merges. You never merge, never touch main.
