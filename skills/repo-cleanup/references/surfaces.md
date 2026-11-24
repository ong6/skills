# What good looks like, by surface

Defaults to weigh against the fetched guides and the repository's own conventions. Each says why,
so that the exception is recognisable when it comes up.

## Contents

- [Manuals](#manuals) (AGENTS.md, CLAUDE.md, rules files, folder manuals)
- [Skills, commands and agent definitions](#skills-commands-and-agent-definitions)
- [READMEs and docs](#readmes-and-docs)
- [Structure](#structure)
- [Records](#records)
- [Deleting, archiving, moving](#deleting-archiving-moving)

## Manuals

A manual is loaded into every session, so each line is paid for every time and competes with the
task for attention. It earns its place by saying what an agent cannot infer and would get wrong.

- **Keep:** commands that are not obvious, traps, constraints with their reason, decisions
  recorded nowhere else, where the real documentation lives, anything agents have got wrong twice.
- **Move out:** procedures for one kind of task (a skill, or a doc the manual links to), rules
  for one folder (a manual in that folder, loaded only when working there), reference material.
- **Drop:** what the code, linter config or README already says; generic engineering advice;
  personas; instructions about how to think; reply-format rules nobody asked for; history.
- **Current rules only.** A live instruction reads as the rule and its reason. "Sam asked on
  2025-06-11 that retries are capped at 5 after an incident" becomes "Retries are capped at 5;
  changing it needs payments on-call sign-off, because retried charges page them." The date and
  the name belong to the decision log, which usually has them already.
- **Suggestions over orders.** State a preference as a default with its reason, and reserve
  hard wording for constraints whose breach is expensive: data loss, production, money, secrets,
  other people's work. Lower the volume without loosening the rule: "NEVER EVER edit X" becomes
  "Don't edit X: <reason>". A hard rule with no findable reason stays and goes on the list of
  questions; it does not get softened or removed on a guess.
- **One manual, many readers.** When a repository serves more than one harness, keep one source
  (commonly `AGENTS.md`) and make the others an import or a symlink, not a copy: copies drift, and
  a drifted copy is a contradiction. Check the mechanism actually loads on each harness.
- **Verify every fact you keep or write.** Run or locate each command, resolve each path, compare
  each number with the code. Where two documents disagree, the code and the most recent record
  decide; say which you chose.
- **No absolute size target.** The guides give ceilings, not goals. Stop cutting when what is
  left would each be missed.

## Skills, commands and agent definitions

- The description decides whether the skill is ever used: what it does, the phrases that should
  reach it, the near-misses that should not. Check pairs of skills whose descriptions overlap.
- Dead references, retired names, hardcoded dates and versions, and steps written for an older
  model are fair to fix in place. A change to what a skill does is a different job: list it, or
  hand it to the repository's skill-authoring process if it has one.
- The same style points as manuals apply, since a loaded skill is a prompt.

## READMEs and docs

- The root README is the front door: what this is, how to run it, where things are. It routes;
  it does not hold the detail. A folder README indexes its folder in a line per entry.
- One home per fact. Where the same content lives in two places, pick the home by who needs it,
  link from the other, and delete the copy. Drifted duplicates are worse than missing docs because
  an agent cannot tell which is right.
- Docs that describe a past state in the present tense mislead. Fix them, mark them superseded,
  or remove them.
- Prefer a few accurate docs to many: merge fragments that only make sense together.
- Docs may be primarily for agents. Write them for a capable reader with no context: full
  sentences, defined terms, paths over descriptions of paths.
- Words written by a person in their own voice (notes, plans, preferences) are restructured and
  re-linked, not rewritten. An agent's opinion is labelled as the agent's, never as the user's.

## Structure

- An agent finds things by listing and searching, so names should say what is inside, each folder
  should have one obvious purpose, and related files should sit together (a doc beside the thing
  it documents) instead of being grouped by file type.
- Aim for progressive discovery: front door, then folder index, then file. Nothing important
  should be reachable only by knowing it exists.
- Follow the convention already in the repository, even where another would be nicer; mixed
  conventions cost more than a mediocre one.
- Typical leftovers: backup and scratch files, empty or single-file folders, `old/` and `misc/`
  directories, generated output committed by accident, several variants of something where one is
  in use. Keep the canonical one.
- Restructure only where it removes real confusion. A move breaks links, history and habits, so a
  small rename is cheap and a reshuffle needs a reason.
- Material for different audiences or under different confidentiality (an employer's and
  personal, public and private) belongs in separate places; flag a mix instead of moving it.

## Records

Changelogs, decision logs, worklogs, journals, meeting notes, feedback logs, dated reports and
anything append-only, together with the folder that holds them and its index. They carry dates,
names and quotes on purpose. Do not rewrite, reorder, trim or "fix" them, even for an
inconsistency or a missing index row: say what you found in the report. Add to a record only
when adding an entry is the task. When unsure whether a file is a record or a live instruction,
ask what reads it: a session that loads it to decide what to do is reading a manual; a person or
agent looking up what happened is reading a record. An archived copy of something retired is a
record too: it keeps its stale paths and old wording.

## Deleting, archiving, moving

- A repository with an archive convention archives. One without it deletes what version control
  can restore. Untracked files, ignored files and anything outside version control cannot be
  restored: list them and leave them unless told otherwise.
- Before removing a file, search for references to it, in this repository and in any sibling
  repository the manual says depends on it.
- A move is finished when links resolve from both ends and the index one level up is updated.
- Merged or abandoned local branches and stale worktrees are fair to remove. Git history rewrites,
  force pushes and anything published are the user's decision each time.
