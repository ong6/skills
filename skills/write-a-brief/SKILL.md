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

**Put the one question that matters most first and mark it "(ask first)"**, with its consequence
in the same line if it isn't obvious, never a verdict the owner hasn't given. It's what the owner
falls back on when the meeting runs short.

## When the meeting is about a quote

Before sorting questions, check the commercial frame; it decides which line items are worth asking
about. Trace every number to the quote's extracted text (`pdftotext -layout`), never memory.

- **Do the sums the owner would do in their head**, from the given figures only: price per unit
  against the other quote, how much of their use an estimate covers, the gap in money between two
  options. Show the inputs in the table. A benchmark or product fact from outside the papers goes
  in as a question ("is 1,200 kWh per kWp realistic for this roof?"), never as a stated fact.
- **Check the papers themselves**: weekday against date, totals against line items, units. A
  mismatch that changes an answer becomes a question; a plain slip is fixed in place.

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

## Step 3: shape

Lean and in the order the meeting runs. A typical brief is four or five headed parts:

```
Who, when, where                             title line
What I want from this meeting                one sentence: the decision and what I leave holding
Where I am                                   the facts the conversation turns on, the document
                                             wording that decides it quoted exactly, then my
                                             decisions (Where I stand) as plain statements
The numbers                                  small table with the sums, only if there are numbers
Questions                                    ≤8, grouped in the order the decision unfolds; the
                                             one that matters most comes first, marked "(ask first)"
Before I leave                               tick-boxes: the artefacts and answers, listed once
Bring                                        plain list, only what isn't already in the room
```

- **Headings in the owner's own plain words.** No slot labels ("Settles:", "Expires",
  "Also worth saying", "Matters most:" lines). An expiry lives in the question or position it
  affects ("pre-authorisation needs 10 working days, so for a December date who submits it
  today?"). For a quote meeting, add one line of things to check the quote covers, phrased as a
  check ("check the S$X install line covers…"), never as a fact about their scope; skip it
  otherwise. Name the checklist for where the meeting is ("Before he leaves" at home).
- **Questions can talk to the professional** ("what would make you change your mind?"); they are
  read aloud.
- **A slip in the background facts is fixed in place**, plainly ("physio since 6 Oct, so 7 weeks
  by today"), never as a `TODO:` at the top. `TODO:` is only for an unknown that blocks the
  meeting.
- **Inferences are questions, not facts.** A timing or cost guess the papers don't state becomes a
  question ("Does a December date clear the January busy period?").
- **Each item appears once.** The whole brief fits about two phone screens. Link the background
  note in one line under the title when there is one; a Related line at the end, if any.

## Step 4: check before handing over

Return to Step 1 on any fail.

- [ ] Count the questions. Over 8 → cut, don't merge.
- [ ] Every question passes one of the four tests. Any that don't → cut, or to the quote line.
- [ ] The first three lines alone say what the meeting decides.
- [ ] No item appears twice; no slot-label headings; no `TODO:` for something already known.
- [ ] No bold lead-in bullets, no "X, not Y" line, no kicker line under a position or question.
- [ ] No inference stated as fact: guesses about timing or cost are questions.
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
