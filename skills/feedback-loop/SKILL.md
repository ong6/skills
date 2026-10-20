---
name: feedback-loop
description: >-
  Log the owner's feedback on how the agent, a skill, hook, rule or reply behaved in feedback.md,
  and patch its target in the same session. Fires on "don't do X", "stop doing", "next time", "I
  prefer", "that was wrong", "always"/"never" about the agent. Not for: feedback on the owner's
  writing or a one-off instruction.
---

# Feedback loop

Feedback is a change request. Log it, then change the thing it is about, in this session. The
owner never repeats feedback and never maintains the log.

## Procedure

1. **Quote it.** Keep the owner's words, trimmed of filler. Do not sharpen them into a stronger claim.
2. **Name the target.** One row of this table. When two fit, take the narrower one.

   | Feedback is about | Target | What "applied" means |
   |---|---|---|
   | What a skill did or failed to do | that skill's `SKILL.md` | smallest edit that changes behaviour: a checklist line, a ❌/✅ row, a trigger phrase in `description` |
   | How every reply should read, or a rule for the whole repo | the root `AGENTS.md` (never create a `CLAUDE.md` for it) | one line in the section that already covers it |
   | Something that should happen automatically on an event | the hook script and its registration | edit script, mirror registration for every client, run its tests |
   | A tool's own behaviour (Claude Code, the IDE, a CLI) | that tool's config | make the config change; note if it is per-machine |
   | This loop itself | this `SKILL.md` | same as any skill |
   | Only this task, or the owner's own content | none | log it, change nothing |

3. **Apply it.** Edit the target now. Do not ask permission for in-repo edits. Do not add a
   "feedback" section to a skill; fold the change into the step it affects. If the new feedback
   contradicts an earlier entry, apply the new one and mark every entry in that supersede chain
   `superseded by YYYY-MM-DD` (the new entry's date).
4. **Verify.** Run the repo's skill validator (the `skillsmith` linter, or whatever check the repo's
   agent manual names) after a skill edit, the hook tests after a hook edit. A failing check means go back to step 3.
5. **Log it** in `feedback.md` at the repo root: append the entry in date order and add its row
   to the **Live rules** table. Create the file from the skeleton below if it is missing. Never
   alter the owner's quoted words.
6. **Keep it lean.** Move superseded entries, and entries applied more than 30 days ago, verbatim
   to `archive/feedback/YYYY-MM.md` (the entry's month) in the host repo. **Live rules** keeps one
   row per rule still in force, wherever its entry now sits; a superseded entry loses its row.
7. **Reply in one or two lines:** what changed and the absolute path of the file.

## Log entry

```markdown
## YYYY-MM-DD · short label
- **Said:** "owner's words"
- **About:** target from the table (skill name, AGENTS.md, hook name, tool)
- **Applied:** what was edited, one line; or "nothing, one-off"
- **Status:** applied | pending | superseded by YYYY-MM-DD
```

`pending` is for a target that cannot be edited from this session (another machine's config, a
locked file). Say so in the reply and leave the entry pending until it is done.

## Skeleton for a new `feedback.md`

```markdown
# Feedback log

What the owner said about how the agent, a skill, a hook, or a reply behaved, and what changed
because of it. The `feedback-loop` skill writes here; superseded and older applied entries move to
`archive/feedback/`.

## Live rules

| Date | Rule | Where it lives | Status |
|---|---|---|---|

## Entries
```

Add the repo's usual frontmatter above the heading if its notes require one.

## Examples

| ❌ | ✅ |
|---|---|
| "Noted, I'll keep that in mind." (nothing edited) | Edit the skill, log the entry, reply with the path. |
| Append "Owner feedback 2026-09-15: be shorter" to the end of a skill | Change the line in the skill that produced the long output. |
| Paraphrase "why does it do X" as "owner hates X" | Quote it and log the actual question. |
| Ask "should I update the skill?" | Update it. Feedback is the instruction. |
| Log a one-off ("use the other branch this time") as a rule | Log it with `About: none`, change nothing. |

## Where edits land

This skill ships in the public [`ong6/skills`](https://github.com/ong6/skills) collection and is
linked into each host repo, so an edit made through the link changes the shared checkout. Tell
the owner which checkout changed, then commit and publish it only the way the host repo's manual
says (after the guard and linter pass); if it says nothing, leave the commit to the owner. Edit in
place; never keep a second copy.
