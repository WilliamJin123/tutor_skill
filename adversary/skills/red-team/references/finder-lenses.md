# Finder Lenses

Six read-only finders, one per lens, spawned in parallel. Each agent's brief = the output contract + its lens section, verbatim, plus the scope.

The seeds are real findings from the 2026-08 emails_gen audit. They calibrate what "concrete" means — they are not a checklist. Attack the scoped code on the lens's core question.

## Output contract (paste into every brief)

You are a hostile reviewer of the scoped code and design decisions. Read-only: never Write or Edit; any SQL is SELECT-only.

For each finding return:

- Severity: HIGH / MEDIUM / LOW.
- The assumption, in one sentence.
- Breaking scenario: name the input, the code path, the wrong outcome, and when it fires. No scenario → not a finding.
- Recoverable? Can the lost or wrong data be reconstructed later, or is it gone?
- Cheapest structural fix. A schema or interface change beats process or vigilance.

Then a required **"Attacked and held"** list: every attack you ran that failed, one line each. An empty list means you did not attack hard enough.

## Lens 1 — Data narrowing & discard

Core: where is data dropped, truncated, summarized to a count, or stored somewhere unqueryable?

Hunt: rejected/error rows that keep only a reason string; fields parsed then thrown away; raw payloads not stored; counts where content should be; "invalid" silently meaning "not stored".

Seed: rows carrying platform URLs instead of domains were rejected wholesale — real firms discarded because they couldn't be keyed. Can't be keyed ≠ not worth storing.

## Lens 2 — Identity & keying

Core: what makes two records "the same entity" — and is that rule an identity, or a convenient join key promoted beyond its station?

Hunt: unique constraints doubling as identity; matching that prefers a display attribute over an authoritative id; shared values folding distinct entities into one row; first-writer-wins backfills that grant a row authority it never earned.

Seed: domain-first matching folded 375 distinct-registry-id firms into other firms' rows; `vimeo.com` was stored as "CIBC Private Wealth Advisors". Match on the official identifier alone; a value claimed by a different identifier is a recorded conflict, never a match.

## Lens 3 — Conflation

Core: one column, rule, or state serving two concepts.

Hunt: a lifecycle status doubling as a cached join; free-text columns feeding compliance gates; a single "reason" field for many causes; a validator doing both syntax and policy.

Seed: `status=suppressed` meant both "lifecycle state" and "a suppression row exists" — the two silently disagreed. `geo` mixed three formats and fed the legally required US-only gate.

## Lens 4 — Time & refresh

Core: the schema remembers only first encounters. What happens on second contact?

Hunt: re-encounters counted but not kept; facts without timestamps; verified/checked states with no re-check path; terminal states with no exit; refreshing sources with no churn detection.

Seed: a monthly roster refresh — new AUM discarded on match, deregistered firms stayed targetable forever, and VERIFIED had no legal decay transition, so stale leads would burn a warmed domain.

## Lens 5 — Source shape & encoding

Core: what does the code assume every future source will look like?

Hunt: encoding fallbacks that cannot fail loudly; ASCII/US-only validators silently shedding rows; alias maps guessing semantics; length limits that abort a whole batch on one row; "the first URL is the right URL".

Seed: encoding detection assumed not-UTF-8 = cp1252, so a UTF-16 file would crash mid-iteration — the exact failure the docstring promised couldn't happen; punycode domains were rejected as syntax errors.

## Lens 6 — Compliance & irreversibility

Core: which mistakes cannot be undone, or defended later?

Hunt: fail-open gates on legally required filters; destructive SQL with no pre-verified read-only twin; opt-out/suppression provenance that cannot hold two events for one value; data not captured at write time that is impossible to backfill; missing evidence links from an action to what triggered it.

Seed: `UNIQUE(kind, value)` plus a single reason column couldn't record that one address both opted out and complained; verifications never stored the email address they actually checked — trivial to add at insert, impossible to backfill.
