---
name: uipack-design
description: >-
  Build or restyle a visual in the owner's UiPack design system: slides or a talk deck, a landing
  or product page, a diagram for a site or article, a motion explainer or a 3D hero. Use for "make
  slides", "landing page", "in our style", "on brand", "use uipack", "swap the style", "make it not
  look AI-generated", or any visual in a repo that depends on uipack. Not for: data charts alone
  (dataviz), a UX audit alone (ux-design), Blender installs.
---

# UiPack design

UiPack (`github:ong6/uipack`) draws explanations in three independent layers: **style** (how it
looks), **writing** (what it says) and **layout** (where things sit). Its spec lives in the repo's
`docs/system/`: `README.md` (philosophy, contract, recipes), `style.md`, `writing.md`,
`layout.md`. Each has a section per medium. Read the overview, then only your medium's section in
each of the three files. Jump by heading rather than reading whole files. They hold the values, so
don't work from memory. Find the docs in the consumer's `node_modules/uipack`, a local clone (look
for a `uipack` folder near the user's other projects), or GitHub.

"Our style", "house style", "our design system" and "on brand" in this user's projects mean
UiPack, even when it isn't named. Install it with `npm install github:ong6/uipack` if the project
lacks it.

## Workflow

Copy this checklist into the reply and tick it off:

```text
- [ ] 1. Medium and claim: one sentence the visual must make a reader conclude
- [ ] 2. Writing: content as data, per writing.md (given facts only, gaps pinned to the data or left out; "after", not "lifted"; exact qualifiers; verdict titles; notes that add why/so-what/bridge; each point once; reader's words; ask or one CTA)
- [ ] 2b. Reread as the audience against writing.md rule 11's checklist; revise once
- [ ] 3. Layout: archetype or pattern from layout.md that fits the claim's shape
- [ ] 4. Style: a named UiPack style through its swap API; roles only, no literals
- [ ] 5. Build with real exports (web: start from examples/web-starter; check the index/README before using a prop)
- [ ] 6. Review the three layers and the largest object; two screenshot-and-fix passes
```

1. **Claim.** If you can't write it in one sentence, ask or split the visual. For a deck, write
   the line leadership should repeat a week later.
2. **Writing.** Write the words as a typed object first (`DeckSlide[]`, a preset spec, a page
   content object), using only the facts given. A missing fact is never filled in, and finished
   copy never shows `TODO`. Never state a gap as a fact about the team ("we haven't costed a fix",
   "nothing else changed"): leave it out, or, only when the decision needs it, pin it to the data
   in the notes ("the brief has no cost for a fix"). A before/after says "after", "since", "went
   from… to", never "lifted", "cut" or "because", and says once that it is two windows, not a
   controlled test. Copy qualifiers exactly ("up to 15 minutes", "about"). A stated purpose gives
   the consequence ("so it ships in spring": later misses spring). Then run the medium's checks.
   Decks go through `lintDeck` and `storylineOf` from `uipack/deck`. Fix findings before layout; a
   `template-beats` gap the facts can't fill stays a gap. Words read as a person's: plain
   statements and numbers, none of writing.md's AI tells (corrective "X, not Y", kickers, triads,
   inline disclaimers). Slides are presented by default: a 2-5
   word spoken verdict title ("Android crashes down by two thirds", "Start time: 0.2 s slower"; a
   bare label only on agenda, section or mechanism slides), 2-4 fragment points carrying the
   numbers, no eyebrow or lede. Notes add what the slide can't hold: why it matters, the so-what
   for this audience, the trade-off if the answer is no, the bridge. Reason from the given facts;
   add none. A note restating its slide fails (`notes-echo`). The ask slide names action, object,
   cost, owner, date and what a no means (`ask-scope`). Each slide adds something: no point,
   number or ask repeated across slides or between a title and its points.
   Full-sentence titles only for a read-alone deck (`lintDeck` `mode`). Public and user copy uses
   the reader's words (no "main thread", no tool names, no internal metrics such as conversion or
   ticket counts: what the customer notices), keeps scope ("on Android") and has short plain
   section heads. A figure draws the system in at most six nodes, arrows along the flow saying what
   moves, results in a sub-label or the caption; a before/after figure draws both states.

   **2b. Review and revise.** Reread the draft cold as the person who must act on it, against
   rule 11's checklist in `writing.md` (titles that state a point and hide nothing, unambiguous
   points, notes beyond the slide, a full ask, exact qualifiers, nothing invented, no AI tells,
   both states in a before/after). Fix every miss in one pass, then lint again.
3. **Layout.** Choose from the medium's archetype or pattern table. A deck is a sequence of
   archetypes picked by slide role. A web page keeps its own section order in every style.
4. **Style.** Pick from the style list in `style.md` and apply it with the `uiStyle` prop (`Figure`,
   `DeckPlayer`, `SlideStarter`, `WebSurface`, `Section`), `<WebPage uiStyle sections>` for a whole
   page, or `data-ui-style`. Technical is the
   default for every medium and is the owner's own look. Graphical is for a bold poster page.
   Landing is the product-marketing look (label stock: ivory, kraft, ledger green, ruled forms),
   used only when asked for. On the web, keep the page's own
   section order and layout in every style (`WebPage`'s default); a swap changes how parts are
   drawn (cards, numbering, stats, quote, cells, density), never where they sit. Don't pass
   `layout="style"` unless the owner asks. Colours, faces and radii come from roles. A one-off
   literal means the style is missing a role, so say so instead of hard-coding it.
5. **Build.** Use the executor for the medium, plus this spec:

   | Medium | Executor |
   | --- | --- |
   | Diagram | `system-diagram` (its targets and review), values from `style.md#diagrams` |
   | Deck | `uipack/deck` per `docs/deck.md`; customer FDE decks via `create-fde-deck` |
   | Web page | `uipack/web` parts; `frontend-design` for direction, `ux-design` for the usability pass |
   | 3D | `3d-design`, then `blender-authoring` if it picks Blender |

   **Web: show the product's real output.** Copy `node_modules/uipack/examples/web-starter/`
   (every block wired, sample rows) and replace its words and rows rather than discovering the API.
   The hero's largest object is the product doing its job with real-looking data: a
   `DemoPlayer` with no prompts (steps mode) whose step `screen`s hold `ScheduleGrid`,
   `DataTable`, `FileTable`, `ItemList` or `RecordCard`, the last screen the fullest; or a
   `ProductWindow` around one of them. When the product is a thing (a device, a kit, a label) or
   makes a picture (a scan, a map, a print), also pass `StarHero media={<ProductShot>}`: the thing
   or its picture, drawn from roles, above the demo (worked example:
   `examples/web-starter/device.tsx`). Show the mechanism as one `WorkedExample` with the brief's
   numbers (input, rule, arithmetic, result), not an icon flow, and a before/after as
   `Proof compare`. Bespoke markup is fine when no part fits, as long as it reads roles. Never an
   empty demo pane, a chat composer for a product that isn't a chat, or icon-in-a-box nodes.

   The starter's defaults are the ones to keep: `StarHero layout="split"` (copy beside the
   product, no empty half at 1440) with `stamp={{ value, label }}` holding the page's one measured
   number; `DemoPlayer`'s compact step rail (don't pass `rail="side"` when "How it works" lists
   the same steps); `GlassNav cta={{ label, short, href }}` so a phone keeps a short CTA beside
   Menu; a label per plan in `PricingPlans` (only the `featured` one repeats the goal);
   `ProductWindow source="Sample rates"` instead of a footer that only names the source;
   `priority: "low"` on supporting `DataTable` columns and `"key"` on the one the page is about;
   `WorkedExample` values with `unit`; `StarHero facts` for two or three plain facts under the
   actions; `FAQ intro` and `aside` so its head column isn't empty; `Proof caveat` for how the
   numbers were measured. Leave `theme` unset so the page follows the system; for `?style=1|2|3`
   style links, use `styleBootPlugin({ aliases })` in vite.config and `readStyle({ aliases })` in
   main, as the starter does, instead of a hand-written script.

6. **Review.** For each layer, does a swap of the other two leave it intact? Then render it at
   1440 and 390 (390 at device scale 2), light and dark, with reduced motion (the finished state),
   `waitUntil: "load"` and a 60-second timeout per shot; no slow scroll loops. Use a headless
   browser you launch yourself (a Playwright script against a preview you started). Never drive or
   resize a browser or tab the user has open. Then look at the shots and ask: is the largest object
   above the fold full and specific to this product, and could a stranger tell what the product is
   (a physical one shown, not only its table)? Does every figure show the brief's numbers?
   At 390, is the primary CTA in the header and does nothing wrap into narrow columns or crop the
   marked data? Fix and reshoot at least twice. If you can't render, say so plainly instead of
   guessing.

## Bad and required

| Bad | Required |
| --- | --- |
| `color: #205f49`, `font-family: "IBM Plex Sans"` in consumer code | A style role or the `uiStyle` prop |
| Slide titled "Results", "Crash rate" or "Slower starts?" | A spoken verdict: "Freshness: 40 → 6 min"; the deck ends on an ask with owner, date (year included) and what a miss costs |
| Indigo accent, centred hero, three icon cards, logo strip, pricing, FAQ for the owner's own page | The owner's style, led by the product's real output and a worked mechanism |
| A hero demo pane that is mostly empty, a chat prompt for a rota or a ledger, a four-box icon flow ("database, robot, wrench") | A filled `ScheduleGrid`/`DataTable` in the hero; the mechanism as `WorkedExample` ("84 covers ÷ 14 = 6 servers") |
| A different section order or hero per style to show range | One layout; range from each style's treatment of the same parts |
| Sentences inside diagram nodes, unlabelled or vague arrows ("user sessions"), metric nodes, nine boxes | At most six 2–3 word nodes drawing the system, arrows along the flow saying what moves ("decoded image"), results in a sub-label or the caption |
| A statistic on an arrow, a branch that ends nowhere | The statistic once, in the sub-label of the node it measures; every path ends at an outcome or a `Not yet known` node |
| A guessed reassurance, "we haven't costed a fix", "nothing else changed", or `TODO` in finished copy | Only the input's facts; a needed gap pinned to the data ("the brief has no cost for a fix"), else left out |
| "Cached cards lifted checkout", "a short while" for "up to 15 minutes" | "Checkout: 61.2% → 63.0% since caching", once "two windows, not a controlled test"; exact qualifiers |
| Notes that restate the slide ("Cost: one engineer for three weeks"); "Approve by 15 January 2027" | Notes with the why and the cost of a no ("If no, they meet the price change on the old bot"); "Approve Spanish and French by 15 January 2027" with "1 engineer ~3 weeks + 400-article review" |
| The same number on slide 1, slide 3, the hero and a section; "Crashlytics", "main thread" or ticket counts on a user page | Each fact once per piece; the reader's words and scope ("Images now load in the background", "on Android") |
| Restyling a figure to fit a slide | The figure keeps the diagram style; the slide gives it the body region |
| An invented prop because it seems likely | Check the export first; if it's missing, extend UiPack per its `docs/contributing.md` |
| "Looks good" with nothing rendered | Screenshots, or a plain statement that it wasn't rendered |
