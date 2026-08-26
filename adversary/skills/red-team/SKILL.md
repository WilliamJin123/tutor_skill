---
name: adversary:red-team
description: >
  Recurring adversarial sweep-and-upgrade loop for a codebase and its design
  decisions. Default: diff-scoped report since the last audit/* git tag —
  parallel finder agents, adversarial verification, dated audit doc + tag.
  `fix` orchestrates remediation on a branch. `cron weekly` schedules the
  report. Trailing free text after the mode is a focus prompt threaded into
  every finder. Subagents run on cheap models; synthesis stays with the
  orchestrator. Report mode never edits code; fix mode never touches main.
version: 0.3.0
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion, Artifact, CronCreate, CronDelete, CronList, SendMessage, ToolSearch
---

# Adversary Red-Team

The loop: audit → tag → user approves a fix batch → fix on a branch → user merges → next audit diffs from the new tag.

| Args | Mode |
|---|---|
| (none) | Report, scoped to changes since the last `audit/*` tag |
| `full` | Report, whole repo |
| `fix` | Remediate the newest audit, on a branch |
| `cron weekly` | Install a weekly report cron (Monday 09:00) |
| `cron off` | Remove that cron |

Any trailing text after the mode keyword is a **focus prompt**: `/adversary:red-team full lead quality, extensibility`. After `fix`, trailing text names the batch (`fix F2 F5`) and replaces the confirm question. After `cron weekly`, it becomes every scheduled run's focus.

## Focus

A focus prompt shifts emphasis, never scope or rules: all six lenses still attack everything in scope, still read-only.

- Paste it verbatim into every finder brief under `Focus for this run:`.
- If it names a concern no lens covers, spawn one extra finder for that concern, same output contract.
- Rank focus-relevant findings above equal-severity ones; open the report by restating the focus.

## Models

Subagents are volume; synthesis is judgment.

- Finders, refuters, and fix-mode lane agents: spawn with `model: sonnet` (`haiku` for purely mechanical checks). Never the orchestrator's top-tier model.
- Scope, merging, severity calls, reproducing numbers, the report, and fix-mode waves 0/2: the orchestrator, in the main session. Never delegated.
- Escalate a single subagent to `opus` only when its cheap-model result proved inadequate for a genuinely subtle brief.

## Hard rules

1. Report mode edits NO source code. It may write exactly: one audit doc, one commit containing only that doc, one `audit/*` tag, one artifact. Cron runs report mode, so cron never edits code.
2. Fix mode NEVER commits to main. All work on `red-team/fixes-YYYY-MM-DD`. The user merges; you do not.
3. All DB access in report mode is SELECT-only.
4. No finding without a concrete breaking scenario. No number in the report you did not reproduce yourself.

## Report mode

### 1. Scope

```bash
base=$(git tag -l 'audit/*' | sort | tail -1)
```

- No tag, or args = `full` → whole repo.
- Else scope = `git diff --name-only $base..HEAD` + `git log --oneline $base..HEAD` + decision-log rows added since `$base`. Empty scope → tell the user "nothing new since $base" and stop. No doc, no tag.
- Decision log, by convention: a decision table in `designs/*spec*.md`; else `ADR*` / `DECISIONS*` / `docs/decisions/`; else audit code only.

### 2. Find

Read `references/finder-lenses.md`. Spawn one read-only subagent per lens — all six in one message, in parallel. Each brief = that lens's section verbatim + the scope (file list, decision rows) + the output contract from that file. Finders may read anything in the repo; in diff scope, every finding must trace to a changed file or a new decision.

### 3. Verify

- Merge: the same defect found through two lenses is one finding; keep the stronger scenario.
- Per surviving finding, spawn 2–3 refuter subagents with distinct angles: (a) the claim is factually wrong, (b) the severity is inflated, (c) it is already handled elsewhere. Majority refuted → dead.
- Yourself: re-run every alarming quantitative claim against live data (SELECT-only) before it enters the report.

### 4. Report

Write `designs/YYYY-MM-DD-audit.md` (no `designs/` dir → `docs/audits/YYYY-MM-DD-audit.md`):

1. Findings ranked F1..Fn — severity, the assumption in one sentence, breaking scenario, cheapest structural fix.
2. "Pressure-tested and held up" — what was attacked and survived. Required.
3. One-sentence core — the single habit behind the top findings.
4. Recommended fix batch.
5. Appendix, one line each: findings killed by refuters.

Then: commit the doc (nothing else in the commit), publish it as an artifact, `git tag audit/YYYY-MM-DD`, `git push --tags` if a remote exists. Report to the user; recommend `/adversary:red-team fix`. Stop.

## Fix mode

Read `references/fix-orchestration.md`. Follow it exactly.

## Cron mode

- `cron weekly`: use CronCreate (load via ToolSearch if deferred). Monday 09:00 local, prompt = run `/adversary:red-team` in this project directory. Tell the user it is report-only by construction. No cron tool available → hand the user the schedule to install manually and stop.
- `cron off`: CronList, CronDelete the matching job, confirm.
