# Prompts, briefs and handoffs

For a prompt another session or subagent will run: a kickoff prompt, a delegation brief, a
handoff, a stored prompt template, or a rough or dictated prompt to tidy before it is sent.

## The shape

The reader is capable and has none of your context. Tell it what it cannot work out, and leave
the rest to it.

1. **Goal**, and why it matters when that changes the choices.
2. **Context it lacks**: where things are (paths and links, not pasted content), what has been
   decided, what was tried and ruled out.
3. **Constraints**, each with its reason, at their real scope.
4. **Finish line**: what done means and how it is checked.
5. **What to send back**, and in what form, when someone is waiting on the result.

Method stays with the reader unless a step is fragile, order-dependent or destructive; then give
that step exactly. A step list for ordinary work makes a capable model worse and the prompt
longer. Short is the default: when the detail is real, put it in a file and point to it.

## Tidying a rough or dictated prompt

- Keep the author's intent and every constraint. Add no requirement they did not state; if
  something seems missing, raise it after the prompt instead of writing it in.
- When they corrected themselves mid-thought, the later statement wins. Drop the earlier one, or
  name it only where the reader would otherwise meet the stale version in the repository.
- Make optional things optional ("use subagents if they help"), not orders.
- Where the prompt names commands, paths or values and a repository is at hand, check them, and
  warn about anything in the repository that would mislead the new session.
- Return the prompt in one copyable block, each paragraph on one line, with at most a few lines
  after it for the calls you made and questions worth answering. The prompt is the deliverable.

## Handoffs

A handoff lets a fresh session continue without replaying this one. State where things stand,
not how the session went: goal, what is done and how it was verified, what is in flight, next
steps in order, decisions waiting on someone, where the files and branches are. Leave out the
narrative, dead ends that teach nothing, and working shorthand the next reader cannot decode.
If the repository keeps handoffs in a known place, write it there.

## Delegating to subagents

A subagent sees the brief and the manuals, not the conversation. Give each one the goal, the
files it owns, the constraints that apply to its part, and what to return. Keep two writers off
the same file. Ask for conclusions and diffs, not transcripts. A brief that hands over your
hypothesis tends to get it back confirmed, so ask the question, not the answer.

## Stored prompts and templates

Treat a prompt file in the repository as a manual for one task: the style points in
surfaces.md apply, facts in it are checked against the tree, placeholders are kept, and
constraints stated only there are preserved because nothing else records them.

## Common misses

| Tempting | Better |
|---|---|
| Twenty-eight numbered steps | Goal, constraints, finish line |
| A persona, capitals, "think step by step" | Plain direct sentences |
| Pasting file contents into the prompt | The path |
| Rules with no reason | The reason in a clause, so the reader can judge the edge case |
| Adding sensible-sounding requirements | Only what was asked; questions go after the block |
| Paragraphs of commentary around the prompt | The block, then a few lines |
