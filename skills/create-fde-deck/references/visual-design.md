# Visual design for customer decks

## Contents

- [Pick the layout from the claim](#pick-the-layout-from-the-claim)
- [Density](#density)
- [Craft checks on every render](#craft-checks-on-every-render)
- [Finished, not drafted](#finished-not-drafted)

A senior reader judges a deck in the first three slides: is the answer there, does it look
finished, can I find the money and the risks. Layout serves those three questions.

## Pick the layout from the claim

| The slide says | Layout | Not |
|---|---|---|
| The answer to what was asked | Split cards, one per part of the asked scope ("Go: north region", "Not yet: the two sites on the old ERP"), each with its reason and what brings it back; the deciding numbers beside them | One tall panel of three centred numbers |
| The conditions | A conditions table (condition, owner, by when) + one "decided separately" line + `If no:` | The conditions first appearing on slide 6 |
| Where the volume went (handled, no reply, declined, unexplained) | One stacked bar that adds to 100%, the unexplained remainder shown | Four separate tiles that do not visibly add up |
| Results against a target | Two to four number tiles, each with its label, unit, basis and source, plus a "so what" strip | Tiles with a third of their height empty |
| Segments against a gate (sites, cohorts, document types) | A bar chart with the gate drawn as a line, values on the bars, bounds shown as bounds (`>98%` as reported, not `98.0%`) | Three big-number cards |
| Our result against a baseline that was never measured | Two columns, "measured" and "reported", with the comparability caveat between them | A single number implying improvement |
| Risks, blockers, open items | A table: item, why it matters, mitigation or next step, owner, when | Four slides of bullets, one risk each |
| Cost | A table with one row per figure (fee, net a year, break-even), each with its volume base and label, a named `Sensitivity:` row, and a cash-or-capacity line; or a waterfall from fee to net | Four equal tiles, two showing the same number |
| Options | One table: options as rows, the same criteria as columns, the recommendation highlighted, "do nothing" included | Three equal cards with three one-line rows each |
| Rollout | Phases as columns or rows, each with its gate and a duration or anchored date | Phases with no time |
| The ask | One card per decision-maker with their two or three actions and dates, and an `If no:` strip | One numbered list with every owner mixed together |

A labelled bullet list (`findings`) suits at most a third of the deck; use it where the evidence
really is a set of separate observations.

## Density

- Count layouts as rendered, not as declared: a `results`, a `table` and a `plan` slide all drawn
  as one full-width panel over a strip are one layout. No three in a row alike, no frame on more
  than half the presented slides, a "so what" strip on at most 60%, at least four layouts in
  8–12 slides.
- A card, panel or column whose content reaches less than about two thirds of its height, covers
  less than half of it (three numbers centred in a tall box), leaves an empty band over 30%, or
  spills past its edge, is a defect:
  enlarge the figure, merge it with its neighbour, add the "so what", or pick a denser layout.
  `scripts/shoot_deck.py` measures this.
- Fill the frame: content in the top half of a slide reads as unfinished. Never cap a grid's height
  so a two-line heading grows into the figure.
- One idea per slide, but a slide with one sentence and one number is usually two slides that
  should be merged.
- About one presented slide per two minutes; backup slides follow the ask, the first marked `<!-- appendix -->`.

## Craft checks on every render

- **Align across a row.** Cards side by side share their row lines (labels, figures, headings,
  subtitles); in HTML use CSS subgrid and size the heading row `minmax(max-content, 1fr)`.
- **Small text survives a screen share.** Body text at least 24px and footers, sources and chart
  labels at least 18px on a 1920×1080 canvas; split a diagram rather than shrink it.
- **Labels on the data.** Values sit at the end of their bars, not in a far column; a legend only
  when labels cannot sit on the marks.
- **No orphaned units.** Keep a number with its unit (`4 min`, non-breaking space).
- **No widows in headlines.** A headline never leaves one word on its last line; rebalance or
  rewrite it.
- **Colour has one job per slide.** Accent on the recommended or measured item, the warning colour
  only on the problem, never meaning by colour alone.
- **Illustrations earn their place.** No decorative icons or clip art; a figure must be evidence
  for the headline.
- **Borrow the customer's style** when they have a recognisable one; otherwise a neutral light
  theme reads best on projectors and prints.
- **Sources the audience recognises** ("finance audit, 600 invoices, weeks 1–4"); file paths go in
  the notes.
- **Numbers a listener can check.** Columns add up when read aloud; say the arithmetic in a
  footnote when two numbers look contradictory.
- **Open and close the frame.** The last presented slide is the ask; backup slides follow, marked
  as appendix in their eyebrow and navigation. No near-empty divider slide.
- **Emphasis is scarce.** Bold or highlight one row per table at most, the one the headline is
  about; status tags ("Gate 1") sit in the row label in normal weight.
- **Get an outside review.** A fresh reviewer looks at every rendered slide before it ships.

## Finished, not drafted

Nothing visible may read as a note to self: no `TBD`, `TODO`, `confirm`, `sample size TBD`,
`Source: TBD`, bracketed placeholders, "wait a minute" cues or questions to the team. Each open
item is an owned ask, a `Gap ·` line, or moves to the notes or the pre-read (SKILL.md, "Open items
never show as placeholders"). `check_deck.py` and `shoot_deck.py` both flag placeholder words.
