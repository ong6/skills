---
name: repo-cleanup
description: >-
  Reviews and cleans up what agents read in a repository: AGENTS.md and CLAUDE.md manuals, skills,
  prompts, READMEs, docs layout and folder structure, checked against the current official guides
  for the running model, then fixed. Also trims what every session loads, and writes or shortens a
  kickoff prompt, brief or handoff for another session. Use for "clean up this repo", "tidy the
  agent docs", "audit AGENTS.md", "make the repo easier for agents", "session context is too
  heavy", "clean up this prompt", "write a prompt for a new session", "write a handoff". Not for:
  freeing disk space, tidying downloads, lists or note content, closing shells and worktrees, a
  code refactor with no docs angle, writing a new skill, or logging feedback about agent behaviour.
---

# Repo cleanup

Make a repository cheap and unambiguous for an agent to work in: a short manual that says what
cannot be inferred, one home for each fact, docs an agent can find, prompts that give a goal and
trust the reader. Most of this is judgment, and the notes here are defaults to weigh, not rules.
Four things are worth holding to, because getting them wrong costs more than a messy repo does:

- **The repository's own rules come first.** Read its manuals and any maintenance or contributing
  procedure before changing anything; where they disagree with a guide or with this skill, they
  win. If the repo has its own cleanup routine, run that and add only what it does not cover.
- **Cut words, keep meaning.** Every live constraint survives a rewrite, with its reason. A rule
  that looks arbitrary but specific ("retries capped at 5") was probably a correction someone
  paid for: keep it, and ask if it still applies instead of dropping it.
- **Records stay as written.** Changelogs, decision logs, worklogs, journals, feedback logs, dated
  notes and anything a person wrote in their own voice are history, and dates and quotes are the
  point of them. That covers the whole record folder, its index included. Fix a manual; leave a
  record alone even when it has the same symptoms, and report what you saw there.
- **Stay inside the request and keep changes recoverable.** Fix what was asked about; anything
  else you notice (code, build config, tests, a gap in some other folder) goes in the report as a
  lead. Remove files only when version control or the repo's archive convention can bring them
  back.

## Pick the pass

| The request is about | Do |
|---|---|
| The repository: manuals, skills, docs, READMEs, structure | [Repo pass](#repo-pass) |
| What every session starts with, or token cost per session | Repo pass with [references/session-context.md](references/session-context.md) as the focus |
| One prompt, brief or handoff for another session or subagent, or a rough prompt to tidy | [references/prompts.md](references/prompts.md) alone; skip the survey and the guides |

## Repo pass

1. **Read the repo's own rules** (first point above), then survey the surface:
   `python3 scripts/survey.py <repo>` (read-only, standard library, path relative to this skill).
   It lists what loads every session, each agent-facing file with its size, and mechanical leads:
   broken links, paths that do not exist, text duplicated across manuals, emphasis and older-model
   phrasing, dated attributions, folders without an index. A lead is something to check, and
   only the ones inside the request are yours to fix. Keep the numbers for the report.
2. **Fetch the current guides for the model and harness you are running on**, from
   [references/guides.md](references/guides.md). Guidance changes with each model generation and
   habits that helped one hurt the next, so read the live pages instead of working from memory.
   Two pages are usually enough: the one for your model and the one on manuals. Add the skills,
   hooks or subagent page only when the repo has those; the digest in that file covers the rest.
   Fetch them together in one step, and where the host has subagents, have one read the pages
   and return only what differs from the digest, so the pages stay out of your own context.
3. **Ask once, up front,** only what changes the work and cannot be read from the repo: whether
   code is in scope, whether to delete or archive, which of two contradicting rules is live.
   When nobody can answer, take the reversible reading and list the calls you made.
4. **Fix it.** [references/surfaces.md](references/surfaces.md) says what good looks like for
   each surface and what tends to go wrong. Verify a fact against the tree before writing it: the
   command exists, the path resolves, the number matches the code. In a large repository split
   the work across subagents by surface or folder, give each a short brief (see
   references/prompts.md) and its own files, and run moves and renames alone afterwards, since
   they touch everyone's links. Read their diffs before accepting them.
5. **Verify** once, at the end: rerun the survey and compare; links resolve from both ends after
   a move; commands named in the manuals exist; the repo's own checks pass. Go back to step 4
   for anything that fails. What you could not check (a live session loading the manual, say)
   goes in the report as unchecked.
6. **Report** in a reply that fits on one screen, outcome first: what changed (grouped, not
   file by file), the before and after size of what every session loads, what was verified, the
   judgment calls worth reversing, and the decisions that belong to the user. The diff holds the
   detail. If the same defect will recur, suggest the check or hook that prevents it.

## Where passes go wrong

| Tempting | Better |
|---|---|
| Rewriting a manual from taste or memory | Fetch the guide, then change what it and the tree give a reason to change |
| Trimming a rule along with the shouting around it | Lower the volume, keep the constraint and its reason |
| Scrubbing dates and quotes from a decision log | Records are exempt; only live instructions lose their history |
| Copying "the owner said" or a dated story into a manual | State the current rule; history goes to the log that already holds it |
| Turning one remark into a broad hard rule | Record what was said at its real scope, as a default when it is one |
| Fixing the three instances found | Fix the cause: the duplicate source, the missing index, the absent check |
| Keeping two variants "in case" | One canonical version; the other is in version control |
| Fixing whatever the survey flags, wherever it is | Fix what was asked about; report the rest as leads |
| A report that lists every edit | One screen: outcome, numbers, open decisions |
