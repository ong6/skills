# What the current guides say

This file is the fetch. A pass reads the digest and does not open the web; fetching the pages on
every run costs more than the rest of the pass. Refresh it only when the user asks ("refresh
guides"): read the sources below for the model in use, update the digest, and keep the covered
line current.

Covered: Claude Fable 5.2 and Claude Opus 5.5 in Claude Code, and Codex with the GPT-6.2 family,
read in November 2026. On another model, use the digest as it stands and say in the report that
the model is not covered.

## Contents

- [Digest](#digest)
- [Where the guides disagree or are silent](#where-the-guides-disagree-or-are-silent)
- [Sources](#sources), for a refresh

## Digest


**Manuals**
- Keep/cut test: could the agent find this by reading the code, and would it go and look? If
  both, leave it out. Keep commands, traps in the code, decisions written nowhere else, and
  anything corrected twice. Architecture tours and file listings go stale and are discoverable.
- Claude Code suggests under 200 lines per manual; `@path` imports load in full and nest up to
  four hops. Codex reads one manual per directory from the root down and stops at 32 KiB in total.
- Claude Code reads `AGENTS.md` only when no `CLAUDE.md` exists at or above the working directory.
  A `CLAUDE.md` that says "see AGENTS.md" in words loads nothing; `@AGENTS.md` or a symlink does.
- Contradictions cost more than length: one model picks a side arbitrarily, another burns
  reasoning trying to reconcile them.
- A line that needs ever more emphasis to be obeyed belongs in a hook, linter or CI check.

**Prompt style on current models**
- Give the reason with the instruction; say what to do in preference to what not to do; a few
  varied examples beat a list of edge cases; general instructions beat prescriptive steps.
- Emphasis ("CRITICAL", "MUST", capitals) makes current models over-apply the rule. Plain
  wording works. An absolute "never" is read as absolute, so state its scope and exception.
- Habits the guides now list as costly or dead weight: personas, "think step by step" and "think
  hard", "don't be lazy" and keep-going lines, self-verification boilerplate, token budgets shown
  to the model, standing orders to delegate, strict style limits, accumulated cautions whose
  reason is gone. Which apply depends on the model, which is why the per-model page matters.

**Skills**
- `name` up to 64 characters, lowercase with hyphens, matching the folder; `description` up to
  1,024 characters, third person, trigger words first, saying when it should and should not fire.
- Body under 500 lines with references one level deep. After compaction only the start of a
  skill may survive, so what matters most goes first.
- Skill listings share a small slice of the context window and the least-used descriptions are
  dropped first; a skill with side effects is better made explicit-only.

**Session start**
- Hook output added to context is capped (10,000 characters in Claude Code; beyond that the model
  gets a preview and a file path) and is summarised away at compaction, while the root manual is
  re-read from disk.

**Delegation briefs**
- A subagent sees only the brief and the manuals, not the conversation. A brief wants an
  objective, the output format, guidance on sources and tools, and task boundaries.
- Write for an intelligent reader with no context; working shorthand does not carry over.

## Where the guides disagree or are silent

- **Persistence lines.** OpenAI's current guidance recommends "keep going" blocks; Anthropic's
  says they cause over-work on current Claude models. Follow the page for the model that runs the
  prompt, and for a manual shared across harnesses keep such lines out of the shared file.
- **Delegation.** Codex delegates when asked; newer Claude models delegate on their own, and a
  standing "use subagents" line can cause over-delegation there.
- **Project structure in the manual.** Sources differ. Default to leaving it out unless the
  layout is misleading.
- **READMEs, repo layout and fresh-session handoffs** have no official guide. The defaults in
  surfaces.md and prompts.md are judgment; the repository's existing convention outranks them.

## Sources

| Area | URL | Applies to |
|---|---|---|
| Prompting, general and per-model table | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | Claude |
| Manuals: CLAUDE.md, AGENTS.md, rules, imports, limits | https://code.claude.com/docs/en/memory | Claude Code |
| What belongs in a manual; habits to stop | https://code.claude.com/docs/en/best-practices | Claude Code |
| Skills: frontmatter, listing budget, lifecycle | https://code.claude.com/docs/en/skills | Claude Code |
| Subagents: what they see, descriptions | https://code.claude.com/docs/en/sub-agents | Claude Code |
| Hooks: session-start context and its cap | https://code.claude.com/docs/en/hooks | Claude Code |
| What loads when; what survives compaction | https://code.claude.com/docs/en/context-window | Claude Code |
| Skill authoring | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Claude |
| Agent Skills spec | https://agentskills.io/specification | any |
| AGENTS.md format | https://agents.md | any |
| Writing an effective AGENTS.md (format steward's blog) | https://aaif.io/blog/writing-an-effective-agents-md | any |
| Codex AGENTS.md: discovery order, byte cap | https://developers.openai.com/codex/guides/agents-md | Codex |
| Codex skills | https://developers.openai.com/codex/skills | Codex |
| Current OpenAI model guidance | https://developers.openai.com/api/docs/guides/latest-model | OpenAI |
| Context engineering; delegation briefs | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents and https://www.anthropic.com/engineering/multi-agent-research-system | any |
| Indexes | https://code.claude.com/docs/llms.txt, https://platform.claude.com/llms.txt, https://developers.openai.com/llms.txt | |

Most of these sites serve Markdown when `.md` is appended to the URL. For Claude, the prompting
page has a table that maps each model to its own page; for OpenAI, the latest-model guide names
the current family. Some URLs redirect; use the page they land on. Hosts may also ship
their own auditors (Claude Code has `/doctor`, a prompt audit and `claude plugin validate`; the
skills spec has `skills-ref validate`). When one exists, suggest it or run it rather than
re-deriving its checks.

