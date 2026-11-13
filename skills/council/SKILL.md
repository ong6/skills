---
name: council
description: >-
  Explicit-only. Put a deliverable (UI, code, draft, plan, design) through a council of fresh
  reviewer subagents that pick their own metrics, score it out of 10 against references, and drive
  fix-and-rescore rounds until every member meets the target and every stated constraint (default
  8/10, at most 3 rounds). Use only when the user says "council", "use the council" or "put this
  through the council". Not for a single quick edit, an ordinary PR or diff review,
  or feedback about agent behaviour (feedback-loop).
---

# Council

A hill climb with no programmatic scorer: several fresh reviewers score the work, you fix what they
flag, and fresh reviewers score it again. Variety comes from giving each member a different lens
and a clean context. On a single-model host that's the only source of variety, so don't skip the
lenses. Never score your own work and call it independent.

## Settings

| Setting | Default | Override when the user says |
|---|---|---|
| Target | every member scores every metric 8/10 or higher | "aim for 9", "9.5 in every category" |
| Rounds | at most 3 (one round = one full review pass; a fresh pass after fixes is a new round) | "up to 5 rounds", "until it passes" (confirm an unbounded climb first) |
| Members | 3 | "use 2", "add a security reviewer" |
| Mode | review then fix between rounds | "review only" or "just score it": one round, no edits |

## Procedure

Copy this checklist into the reply and tick it off as you go:

```text
[ ] 1 Brief and evidence   [ ] 2 Lenses   [ ] 3 Metrics frozen
[ ] 4 Round N scored       [ ] 5 Fix      [ ] 6 Stop and report
```

1. **Brief and evidence.** Write the goal in one sentence, in the user's terms ("the settings page
   should feel as clear as Linear's"). Then list every explicit constraint the user gave (length,
   tone, must-keep items, no new dependencies). Constraints outrank reviewer taste. The target is
   the most recent deliverable unless named. If it's unclear between two, take the latest and say
   so in one line. What counts as evidence depends on the project:
   - UI: screenshots of the real running app in every state that matters (light and dark, empty,
     error, narrow).
   - Code: the diff plus test, lint and benchmark output.
   - A draft or plan: the exact text plus what it has to achieve.

   Snapshot the starting version (v0) and collect a **reference**: a competitor, the best-in-class
   product or an earlier version the user rates. Scoring something in isolation inflates the
   numbers. With references next to it, the same work scores lower and more honestly.
2. **Lenses.** Choose one distinct lens per member to fit the goal:
   - UI: first-time user, daily power user, visual designer.
   - Code: correctness, future maintainer, on-call operator.
   - Writing: target reader, editor, skeptic.
   - Plan: sponsor, the person who executes it.

   Say which lenses you picked and why in one line.
3. **Metrics (members define them).** In round 1, each member proposes 3 to 6 metrics that decide
   quality for *this* goal and audience. Each metric says what a 6, an 8 and a 10 look like. Each
   member also names which metrics could be **measured instead of judged** (test pass rate, p95
   latency, contrast ratio, bundle size, word count, task steps). Merge the proposals into one
   rubric of 4 to 7 metrics. Keep any metric two members proposed, plus any single proposal that
   targets the goal directly. Turn every measurable one into a command you run each round; a
   measured number beats any opinion on that metric. Freeze the rubric: changing it mid-climb moves
   the goalposts. If it has to change, say so and restart the round count.
4. **Score a round.** Spawn fresh members with the host's native subagent mechanism, in parallel,
   with no inherited conversation; never reuse a member from an earlier round. Pass only the brief,
   the lens, the exact version under review (verbatim or an immutable path), v0, the references
   and, after round 1, the frozen rubric. Never pass your reasoning or earlier feedback. If the host
   can't give fresh subagents, say so and stop; don't fall back to self-review or launch another AI
   CLI. Member prompt:

   ```text
   You are an independent reviewer with this lens: {lens}. Do not edit files, launch agents or rewrite the work. Read-only checks (running tests, linters, opening links, taking screenshots) are allowed.
   Round 1 only: propose 3-6 metrics that decide quality for this goal and audience, each with what a 6, 8 and 10 look like, and say which could be measured instead of judged. Later rounds: use the given rubric unchanged.
   Score the work 1-10 on each metric with a quote, line reference or screenshot detail as evidence. Score each reference on the same rubric.
   Check every constraint in the brief separately: pass, fail or unknown, with evidence. A failed constraint is a critical issue; an unknown one is unresolved, not a pass.
   Return: the version reviewed, a rubric table, constraint checks, critical issues, and the 3 fixes that would help most, critical and unresolved constraints first.
   ```

   **Never tell members the target score or how many rounds remain.** The target leaks into the
   scores.
5. **Fix.** A version **passes** only when it has no critical issue, every constraint passes, and
   every member scores every metric at or above target. If it doesn't, fix critical and unresolved
   constraints first, then fixes several members raised, then the lowest metrics. Skip a fix that
   contradicts the brief and note why. Change only what the feedback targets; don't redesign what
   already passes. Snapshot the new version, rebuild the evidence (new screenshots, rerun the tests
   and measured metrics), then return to step 4.
6. **Stop and report.** Stop when a version passes, at the round bound, or early on a plateau. A
   plateau means two consecutive rounds each moved the lowest score by less than 0.5 and every
   compared version met all constraints; unresolved constraints are never a plateau. Keep the best
   version that meets every constraint (on a tie, the earlier one); a higher-scoring version that
   breaks a constraint never displaces it. If a fix made things worse, restore that snapshot with
   its own scores. Never attach one version's scores to another. Report:
   - a rounds table: rows are versions, with each member's per-metric minimum and overall,
     constraint status, measured metrics, reference scores and the fixes applied;
   - the retained version, its scores against the target, and the actual stop reason (passed,
     round bound, plateau, blocked);
   - remaining gaps, next fixes, and any fix declined with why. If the target was missed, say so
     and call the retained version an incomplete draft, not accepted;
   - an honest read of the result (next section).

## Reading the scores honestly

Council scores are model opinions, not a third-party evaluation. Feed the same evidence to the same
model three times and you can get three different scores. A council that has seen the work improve
round after round tends to drift upward, and reference scores can rise even though the references
never changed. So:

| Bad | Required |
|---|---|
| "The council rates it 9/10, so it's done" | "The council's opinion reached 9/10; take a look at the before/after yourself" |
| A final score with no reference beside it | The reference scores from the same round, so the gap is visible |
| Putting council scores in a PR or status update as proof of quality | Describe what changed; label any scores as AI-reviewer opinion |
| Judged scores overriding a measured number | The measured number wins; flag the disagreement |
| A high score cancelling a broken constraint | The version doesn't pass; fix the constraint first |
| Adding rounds silently because 9 is close to 10 | Stop at the bound; say what more rounds would buy. Each extra half point tends to cost several times more rounds than the last |

The user's own eye is the final judge. If the work clears the target but the user still thinks
it's not good enough, take their objection as new input: add a reference or tighten the goal,
then start a fresh climb. Don't argue from the scores. When the decision matters (a launch, a
redesign others will use), recommend real evidence beyond the council: a user test, analytics,
or a human reviewer.

## Limits

- Members review only and never edit; the main session makes every change.
- Edits stay in the working tree or a branch. Opening a PR, posting a comment or messaging anyone
  follows the host repo's rules for outward-facing writes.
- To save tokens, the user may ask to stage the council: run one member until it passes, then add
  the rest. Every member still has to pass in the same final round.
