---
name: write-a-brief
description: Write or tighten a one-to-two-page meeting brief for a professional (contractor, consultant, doctor, vendor), including what to ask about their quote. Use for "meeting brief", "prep doc", "questions to ask", "check this quote", or fixing a brief that is too long or AI-sounding; not for email drafts or general notes.
---

# Write Brief

The reader is the owner, in a room, under time pressure, with a professional waiting. A thing
you glance at, not a report.

## Step 0: frame it

Answer three questions from the background note or by asking:

1. **What does the owner walk out holding?** A quote, a drawing, a date, a decision. The
   decision goes in the first three lines; the artefacts go in *Leave with*.
2. **How good is this person?** Assume competent and experienced until shown otherwise.
3. **What expires?** Anything that gets expensive or impossible after a date: a roof closing,
   a membrane going down, an application still open, a return window. Usually the real reason
   the meeting is now; it gets its own block.

## Step 1: the competence split

This is the whole skill. Every candidate item goes in exactly one bucket:

| Bucket | Contains | Written as |
|---|---|---|
| **Where I stand** | Decisions the owner has made and intends to hold, with the one-line reason. | Plain statements, no bold lead-ins. Include what a pushback must contain to change the answer. Only decisions the owner actually stated; never a verdict they didn't give ("I wouldn't sign this"). |
| **Ask them** | Only items passing the test below. | Numbered questions. **Hard cap ~8.** |
| **Should be in the quote anyway** | Everything a competent pro does by default, drawn from the quote or background, not a generic trade checklist. | One short paragraph the owner can scan; say it aloud only if an item is missing from the quote. |

**A question earns a slot only if it is one of:**

- **Site-specific**: unanswerable without seeing our drawings, our bills, our roof.
- **A position to hold**: the answer is a decision the owner might be talked out of.
- **Expiring**: cheap now, expensive later.
- **A quiet upsell or a quiet corner-cut**: never comes up unless asked.

Everything else is hand-holding. Reciting standards at a tradesperson signals distrust, burns
minutes, and buries the questions that matter. Over ~8 questions, cut; don't reformat. A
30-question sheet is an unsorted one.

**Name the one question that matters most and say why**, one plain line under the list, stating
the consequence, not a verdict the owner hasn't given. It's what the owner falls back on when
the meeting runs short.

## When the meeting is about a quote

Before sorting questions, check the commercial frame; it decides which line items are worth asking
about. Trace every number to the quote's extracted text (`pdftotext -layout`), never memory.

- **Do the sums the owner would do in their head**, from the given figures only: price per unit
  against the other quote, how much of their use an estimate covers, the gap in money between two
  options. Show the inputs in the table. A benchmark or product fact from outside the papers goes
  in as a question ("is 1,200 kWh per kWp realistic for this roof?"), never as a stated fact.
- **Check the papers themselves**: weekday against date, totals against line items, units. A
  mismatch is the first line of the brief, as a `TODO:`.

- **Allowance:** quote against the budget line or PC sum, with GST stated in or out.
- **Who keeps a saving:** under a PC sum it may credit the main contract, not the owner. Unknown
  means it is the first question.
- **Bundle terms:** a bundle-conditional discount means ask for a revised bundle quote, never
  delete lines. A price exactly list × discount is a spec question, not a discount one.
- **Timeline:** validity against the decision date and lead times. A quote lapsing first is an ask.
- **Like for like:** compare items by function, not price bracket, and check finishes against the
  packages already decided.

Only decisions and blocking questions go in *Ask them*. Typos, stale rates and payment terms are
parked in the background note until the revised quote arrives.

## Step 2: write it like a person

The failure mode is a doc that is correct and obviously machine-made. Fixes, by payoff:

- **Bottom line up front.** First three lines: what the meeting is, what to walk out with. No
  restating the background note.
- **Bold only what the eye should catch**: a number, a position, a deadline.
- **Kill decoration.** ✅/🚩 legends, emoji headers, "The Three Numbers" capital-letter framing.
- **A table needs two real columns.** A second column of sentences is a list in costume.
  Numbers, ranges and comparisons stay in tables; reasoning becomes prose.
- **Let length follow content.** Most lines short; a longer one where the reasoning needs it. A
  short line carries a fact or a position, never a slogan.
- **Short Anglo-Saxon words.** Use not utilise, start not commence, buy not procure. Cut just,
  really, simply, actually, basically.
- **Say it once.** A fact in the background note and the brief stays in one.
- **Contractions are fine.** This is the owner talking to themselves.
- **Positions as plain statements.** "Keeping the existing boiler." beats an argued paragraph. Cut
  corrective framing ("it's a timing question, not a price one"), triads where one item carries
  it, and a neat closing line.
- **A gap is a fact about the paper, said once.** "The quote doesn't say whether
  disposal is included" goes under *Ask them*; never a disclaimer like "to be transparent" or "we can't
  confirm".
- **Dashes aren't the problem.** Use them where they read naturally; don't swap each one for a
  hyphen.

## Step 3: standard shape

Adapt freely, but this order works:

```
Title, date, what this is                    2 lines
The one decision this meeting settles        1 sentence
Link to the background note                  1 line; brief ≠ background
Where I stand                                as many bullets as decisions
The numbers                                  small table with the sums, only if there are numbers
Ask them                                     ≤8 numbered, + which one matters most and why
Expires on <event>                           one line if an Ask already covers it
Should be in the quote anyway                one short paragraph
Bring                                        tick-boxes, only what isn't already in the room
Leave with                                   tick-boxes: the artefacts, listed once
Related                                      links back to the background notes
```

**Each item appears once.** The artefacts live in *Leave with*, not also in a top line; the expiry
lives in its question, with the block only saying why it's now. Drop any section with nothing real
in it (no "Also worth saying" filler). **Leave with survives contact with a real meeting.**
Tick-boxes, kept last so a thumb finds them. The whole brief fits about two phone screens.

## Step 4: check before handing over

Return to Step 1 on any fail.

- [ ] Count the questions. Over 8 → cut, don't merge.
- [ ] Every question passes one of the four tests. Any that don't → move to *Assume*.
- [ ] The first three lines alone say what the meeting decides.
- [ ] No item appears twice (top line, Ask, Expires, Leave with).
- [ ] No bold lead-in bullets, no "X, not Y" line, no kicker after the "matters most" line.
- [ ] Bold spans in the longest section ≤ ~5.
- [ ] Every fact traces to the background note or a source. Never invent a price, a
      standard, a lead time.
- [ ] Two pages or fewer at print size.
- [ ] One paragraph read aloud sounds like the owner.

Then cut generic framing and filler while preserving every fact, number, link, and owner-authored
word.

## Afterwards

- Fix inbound links: the parent `README.md` and the background note both describe the brief,
  and a question count or subtitle there goes stale the moment you cut.
- If a PDF was built from the old version, mark it stale in the README and offer to rebuild
  with the `markdown-to-pdf` skill. Don't rebuild unasked.
- After the meeting the brief is a record: append what they answered, don't overwrite the
  questions.
