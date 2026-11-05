# Rendering the deck

## Contents

- [Choose the renderer](#choose-the-renderer)
- [UiPack deck player](#uipack-deck-player)
- [Portable fallback: one HTML file](#portable-fallback-one-html-file)
- [Shoot and inspect](#shoot-and-inspect)

`deck.md` stays the source of truth for words, figures, labels, sources and notes; the renderer
gives each shape a layout. Copy headlines and notes from `deck.md` verbatim, and add no figure,
date or ask on a rendered slide that its `deck.md` slide lacks (tiles, deltas, footnotes and
"so what" panels included): put it in `deck.md` first. `check_deck.py deck.md --rendered
shots/slides.json` flags any that slip through.

## Choose the renderer

1. **UiPack deck player** (`uipack/deck`) when a UiPack checkout or `node_modules/uipack` with
   built `dist/deck.js` and Node are on the machine. Its consulting parts give decision decks what
   hand-made HTML usually lacks: real bar charts with a gate line, KPI tiles, option and owner
   tables, a "so what" strip, numbered footnotes and a source line, a section tracker, text never
   under 20 canvas px, a speaker view with notes, and one-click PDF. Its `lintDeck` also checks
   answer-first, a concrete closing ask and sourced numbers.
2. **Otherwise** a self-contained HTML file (below). Use Marp or Slidev only when the user asks for
   them or the deck must stay editable as Markdown; their default themes tend toward bullet slides,
   so apply the layout table in [visual-design.md](visual-design.md) either way.

Ask before installing anything. Without Node or a browser, deliver `deck.md` and say the deck was
not rendered.

## UiPack deck player

Read the checkout's `docs/deck.md` (player) and `docs/deck-consulting.md` (parts) before using a
prop; don't work from memory. Write `deck.tsx` beside `deck.md`:

```tsx
import { createRoot } from "react-dom/client";
import { DeckPlayer, ConsultingSlide, Panel, KpiTiles, BarChart, HarveyTable, SoWhat,
  lintDeck, formatter, type DeckSlide } from "uipack/deck";
import "uipack/deck.css";

const slides: DeckSlide[] = [/* one per deck.md slide: id, title, headline, role, render, notes */];
(window as any).__deckLint = lintDeck(slides, { minutes: 12 }); // presenting time, not the meeting
const view = new URLSearchParams(location.search).get("view") === "print" ? "print" : undefined;
createRoot(document.getElementById("root")!).render(
  <DeckPlayer id="deck" title="…" slides={slides} theme="light" view={view} minutes={20} />);
```

| deck.md shape | UiPack build |
|---|---|
| `title` | `ConsultingSlide` titled with the answer; one short `Panel` per part of the asked scope (Go / Not yet) beside a narrow `KpiTiles` column of the 2–3 deciding facts, with `rows` sized to content (`"auto"`), never one tall panel of centred tiles |
| `decision` | `HarveyTable` with text columns (condition, owner, by) and `showKey={false}`; `SoWhat` for "decided separately" and `If no:` |
| `results` | `KpiTiles` with `note` carrying label and source ("Measured · finance audit, 600 invoices") beside a `StackedBar` when the results are shares of one total |
| `chart` | `BarChart` with `reference={{ value, label }}` for the gate, `highlight` on the item the headline is about; `SoWhat` beside it |
| `table` | `HarveyTable` text columns; category tags ("Gate 1") in the row label, `highlight` on one row at most |
| `comparison` | `HarveyTable`, options as rows, the recommended row `highlight` with `tag: "Recommended"` |
| `plan` | `HarveyTable` rows by phase (when, what, gate, owner) beside a narrow `Panel` of rollback triggers, one per metric |
| money | `HarveyTable` rows (figure, volume base, label) or a `Waterfall` from fee to net, with the cash-or-capacity line as the `SoWhat` |
| `ask` | One `Panel` per decision-maker (`cols={4}` each for three people), `takeaway` for `If no:` |
| `architecture` | A UiPack figure per its `docs/system/` diagram rules, or the portable fallback for that slide |

Rules that keep it honest and readable:

- Show each claim's label in the item itself: a `note` on a KPI tile, a "Basis" column in a table,
  or the first word of a footnote. Put the label key once in the first labelled slide's subtitle
  or footnotes.
- A bound stays a bound: chart a reported ">98%" with a label that says so (`format` returning
  `>98%`), never as a measured 98.0. When a value has no measured equivalent, footnote it.
- Use `sticker` only for a true status ("Draft for discussion" before a pre-read, never on the
  final deck), `tracker` for 4–7 sections, and `notes` (numbered footnotes) for definitions and
  arithmetic. With a tracker, add `Appendix` as its last section and make it current on every
  backup slide. Skip `sectionSlide` dividers unless they carry an index of the backup slides.
- `highlight` bolds a whole row and adds its tag: use it on one row per table at most, and never
  with a tag that reads as already decided (`For decision today`, not `Decided today`).
- Panels in one row share a height; give a short `SoWhat` a narrow column or move it to
  `takeaway`, so no panel stands half empty. Use `takeaway` only where it carries the slide's so
  what, not on every slide; vary the frame (two panels, chart beside its so what, cards per
  person) so the deck does not read as one template. A thin table is better beside a second panel than
  alone at full width.
- Pass `lintDeck` the presenting time (the meeting less discussion). `notes.say` holds the cues from
  `deck.md` (say, point, bridge), not a script; its talk-time "under half" warning is expected for
  cues, and `shoot_deck.py` ignores it.
- Quote marks inside a JSX attribute or string are curly (“ ”); straight ones end the string.
- `uipack-cx-t` classes style SVG text only; for HTML text inside a panel use a table, a KPI
  `note`, a panel `unit` or a `SoWhat`.

Build to one file (esbuild ships in the UiPack checkout's `node_modules`; `UIPACK` is the checkout
path, and its folder must be named `uipack`, or point `NODE_PATH` at a parent that has one):

```bash
NODE_PATH="$(dirname "$UIPACK"):$UIPACK/node_modules" "$UIPACK/node_modules/.bin/esbuild" deck.tsx \
  --bundle --outdir=build --jsx=automatic --minify --define:process.env.NODE_ENV='"production"' \
  --loader:.woff2=dataurl --loader:.woff=dataurl --loader:.ttf=dataurl
python3 scripts/pack_html.py build/deck.js build/deck.css deck.html --title "…"
```

`deck.html` then opens offline: arrow keys to present, `S` for the speaker view, the PDF button
to print. `deck.html?view=print` shows every slide fully built, one per page.

## Portable fallback: one HTML file

One `deck.html` with inline CSS and SVG, no network requests:

- One `<section class="slide">` per slide, authored on a 1920×1080 canvas and scaled to the
  viewport with a CSS transform; print CSS gives one slide per landscape page; notes omitted.
- A light neutral theme, one accent, one warning colour; system fonts or the customer's.
- Build each shape from the layout table in [visual-design.md](visual-design.md): CSS grid for
  tiles and cards (`grid-template-rows: subgrid` to align rows), real `<table>`s for conditions,
  risks, options and asks, and inline SVG for bar charts (bars with values at their ends, the gate
  as a dashed line with its label).
- Mark cards and panels with `data-card` so `shoot_deck.py` can measure how full they are.

## Shoot and inspect

```bash
pip install playwright && python3 -m playwright install chromium   # once, if missing; ask first
python3 scripts/shoot_deck.py deck.html --out shots/
```

It loads the deck headless (UiPack in print view, otherwise each `section.slide`), writes one
1920×1080 PNG per slide and `shots/slides.json` with each slide's visible text, and flags:
placeholder words on a slide, text under 18 canvas px, content overflowing its box or the slide,
cards or panels less than 65% full, covering under half their height or holding an empty band over
30%, or spilling past their edge, layouts repeated by rendered structure (three in a row, one frame
on most slides, a strip on most slides, under four distinct layouts), tables with more than one
emphasised row, near-empty slides, page errors, and UiPack `lintDeck` errors and warnings. Exit 1
while flags remain. Then run `python3 scripts/check_deck.py deck.md --rendered shots/slides.json`
for figures missing from `deck.md`, appendix navigation and cross-slide consistency on the
rendered text.

Then open every PNG yourself. Claim fit only for what you looked at; without a browser, report
layout, overflow and contrast as **not measured**.
