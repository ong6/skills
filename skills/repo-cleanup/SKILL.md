---
name: repo-cleanup
description: >-
  Cleans up what agents read in a repository so each session loads less and finds more: AGENTS.md
  and CLAUDE.md manuals, skill descriptions, session-start hooks, stored prompts, READMEs and docs
  layout. Runs a free survey script, fixes what it finds and reports tokens loaded per session
  before and after. A routine run covers what changed since the last pass; "full" audits
  everything. Use for "clean up this repo", "repo cleanup", "tidy the agent docs", "audit
  AGENTS.md", "make the repo easier for agents", "session context is too heavy", "agents keep
  missing the right skill". Not for: writing or tidying one prompt, brief or handoff, freeing
  disk space, tidying downloads, lists or note content, closing shells and worktrees, a code
  refactor, writing a new skill, or logging feedback about agent behaviour.
---

# Repo cleanup

The aim is a repository an agent can work in cheaply: a short manual that says what cannot be
inferred, skills that fire when they should, one home for each fact, docs that can be found. The
measure is what a session loads before the user types, and whether what it loads is true.

Most of this is judgment; the defaults below come with reasons so the exception is recognisable.
Three things hold regardless, because getting them wrong costs more than a messy repo does:

- **The repository's own rules come first.** Read its manual and any maintenance procedure before
  changing anything. Where they disagree with a guide or with this skill, they win.
- **Cut words, keep meaning.** Every live constraint survives a rewrite, with its reason. A rule
  that looks arbitrary but specific was probably a correction someone paid for: keep it and ask
  whether it still applies. Moving a procedure out of the manual does not move its constraints:
  a rule an agent has to know before it starts stays where every session sees it.
- **Records and people's own words stay as written.** Changelogs, decision logs, journals,
  incident notes and feedback logs keep their dates, names and quotes; that covers the record
  folder and its index. A note someone wrote in their own voice is theirs too, however rough:
  link to it or index it, and do not merge, reword or delete it. Report what you see there.

Otherwise fix things without asking. Anything version control or the repo's archive convention
can bring back is yours to change, delete or move. Code, build config and tests are outside a
docs pass: report what you notice there.

## The pass

1. **Survey** (read-only, no model cost; path relative to this skill):
   `python3 scripts/survey.py <repo>`. It prints the tokens every session loads, what changed
   since the last recorded pass, and mechanical leads. If it reports a routine pass and the user
   did not say "full", work on the changed files and the leads; files that have not changed
   since the last pass stay as they are, even where they could be better. With no earlier
   pass, or on "full", cover the whole surface.
2. **Read the repo's own rules**, and [references/guides.md](references/guides.md) for what the
   current guides say. Do not fetch guides during a pass; that file is the fetch. Refresh it only
   when the user asks ("refresh guides"). If the model you are running on is not one it covers,
   say so in the report.
3. **Fix**, using the defaults below. Check every fact you keep or write against the tree: the
   command exists, the path resolves, the number matches the code. Where two documents disagree,
   the code and the latest record decide; say which you chose. Work inline; split across
   subagents only when the surface is too large for one context, with one writer per file and
   moves done last ([references/prompts.md](references/prompts.md) for the briefs).
4. **Verify and record**, once: `python3 scripts/survey.py <repo> --mark`. Links resolve from
   both ends after a move, commands named in the manual exist, the repo's own checks pass. What
   you could not check (a live session loading the manual, say) is reported as unchecked.
5. **Report** on one screen, outcome first: tokens loaded per session before and after, what
   changed (grouped), the judgment calls worth reversing, what is left for the user. If a defect
   will recur, name the check or hook that would stop it.

## Defaults

| Surface | Good looks like | Usual fixes |
|---|---|---|
| Root manual | Only what an agent cannot infer and would get wrong: non-obvious commands, traps, constraints with reasons, where the real docs are | Drop what code, linter config or README already say; drop personas, how-to-think lines, reply-format rules, history and layout tours |
| Rule wording | The current rule and its reason, in plain sentences; hard wording only where a breach is expensive | "X said on <date>" becomes the rule; capitals and "NEVER EVER" become "Don't …: <reason>"; a hard rule with no reason stays and becomes a question |
| Task procedures | Loaded on demand | A step list in the manual moves to a skill or a linked doc |
| Folder rules | In that folder's manual, loaded only when working there | Lines about one folder move out of the root manual |
| Several harnesses | One source; the others import or link it, and the mechanism really loads | A drifted copy is a contradiction: merge it, then replace it with the import |
| Skills | A description that says what it does, the phrases that reach it and the near-misses that do not; no two skills competing for the same request | Merge or sharpen overlapping descriptions; fix dead paths and retired names. A change to what a skill does is listed, not made |
| Session-start hooks | A line or two a session acts on, silent otherwise | Stop printing manuals, logs or status nobody uses ([references/session-context.md](references/session-context.md)) |
| Stored prompts | Goal, constraints with reasons, finish line; method left open | Cut step lists and shouting; fix stale commands; keep constraints recorded only there |
| READMEs and docs | Front door that routes; one home per fact; nothing describing the past in the present tense | Fix dead links, index what is missing, delete or mark superseded copies |
| Structure | Names say what is inside; related files together; the existing convention kept | Remove backups, scratch, empty and `old/` folders and unused variants; move only where it removes real confusion |

[references/surfaces.md](references/surfaces.md) has the longer reasoning for when a call is
unclear.

## Where passes go wrong

| Tempting | Better |
|---|---|
| Trimming a rule along with the shouting around it | Lower the volume, keep the constraint and its reason |
| Tidying a log, a journal, its index or someone's rough note | They are exempt; say what you saw |
| Copying "the owner said" or a dated story into a manual | The current rule; history is already in the log |
| Turning one remark into a broad hard rule | Its real scope, as a default when it is one |
| Fixing the instances found | The cause: the duplicate source, the missing index, the absent check |
| Asking before each deletion | Delete what version control restores; list only what it cannot |
| Fixing code or config noticed on the way | Report it |
| A report that lists every edit | One screen: numbers, outcome, open decisions |
