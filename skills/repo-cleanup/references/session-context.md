# Session context

What a session holds before the user types: it is paid for on every turn of every session, and
it dilutes attention to the task. This pass measures it, then moves what does not need to be
there.

## Measure

- **Manuals and imports.** `scripts/survey.py` totals the root manuals and everything they
  import. Add nested manuals for the folders where sessions usually start.
- **Hook output.** The survey lists session-start and prompt-submit hooks but does not run them.
  Read each script; run it to measure its output only when it is read-only. Output over the
  host's cap is replaced by a preview, so a long hook may already be losing its tail.
- **Skill and agent listings.** Every installed skill and custom agent contributes its name and
  description to each session. Count them, and look for ones that never fire.
- **Tool and MCP instructions.** Connected servers add tool definitions and instructions. Note
  servers that are configured but unused in this repository.
- **The host's own view.** Where the harness can report context use (Claude Code has `/context`),
  suggest the user run it; it sees what a script cannot.

## Decide, line by line

Ask of each item: does a typical session act on this?

| Answer | Home |
|---|---|
| Yes, most sessions | Stays, in as few words as carry it |
| Only for one kind of task | A skill or a linked doc, loaded on demand |
| Only in one folder | That folder's manual |
| Must hold on every action, and prose keeps failing | A hook, linter or CI check |
| It is a status line nobody acts on | Remove it, or print it only when there is something to act on |
| It duplicates another loaded source | One copy |

Hook-injected context is lost at compaction while the root manual is reloaded, so a rule that
has to survive a long session belongs in the manual, and volatile status belongs in the hook.

## Report

Give the before and after as numbers (tokens for manuals, characters for hook output and
listings), what moved where, and what you left because sessions do act on it.
