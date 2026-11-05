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
- [ ] 2. Writing: content as data, per writing.md (claims, captions, ask or one CTA, budgets)
- [ ] 3. Layout: archetype or pattern from layout.md that fits the claim's shape
- [ ] 4. Style: a named UiPack style through its swap API; roles only, no literals
- [ ] 5. Build with real exports (check the package's index/README before using a prop)
- [ ] 6. Review the three layers; on a failure go back to that layer's step
```

1. **Claim.** If you can't write it in one sentence, ask or split the visual. For a deck, write
   the line leadership should repeat a week later.
2. **Writing.** Write the words as a typed object first (`DeckSlide[]`, a preset spec, a page
   content object). Then run the medium's checks. Decks go through `lintDeck` and `storylineOf`
   from `uipack/deck`. Fix findings before layout. Words read as a person's: plain statements
   and numbers, none of writing.md's AI tells (corrective "X, not Y", kickers, triads, inline
   disclaimers).
3. **Layout.** Choose from the medium's archetype or pattern table. A deck is a sequence of
   archetypes picked by slide role. A web page follows the section sequence its style recommends.
4. **Style.** Pick from the style list in `style.md` and apply it with the `uiStyle` prop (`Figure`,
   `DeckPlayer`, `SlideStarter`, `WebSurface`, `Section`), `<WebPage uiStyle sections>` for a whole
   page, or `data-ui-style`. Technical is the
   default for every medium and is the owner's own look. Graphical is for a bold poster page.
   Landing is the generic SaaS look, used only when asked for. On the web, follow the section
   sequence the chosen style recommends (`uiStyles[].prefers`; `WebPage` applies it). Colours, faces and radii come from roles. A one-off literal means the style is missing
   a role, so say so instead of hard-coding it.
5. **Build.** Use the executor for the medium, plus this spec:

   | Medium | Executor |
   | --- | --- |
   | Diagram | `system-diagram` (its targets and review), values from `style.md#diagrams` |
   | Deck | `uipack/deck` per `docs/deck.md`; customer FDE decks via `create-fde-deck` |
   | Web page | `uipack/web` parts; `frontend-design` for direction, `ux-design` for the usability pass |
   | 3D | `3d-design`, then `blender-authoring` if it picks Blender |

6. **Review.** For each layer, does a swap of the other two leave it intact? Then render it at
   1440 and 390, light and dark, and with reduced motion. Use a headless browser you launch
   yourself (a Playwright script against a preview you started). Never drive or resize a browser
   or tab the user has open. If you can't render, say so plainly instead of guessing.

## Bad and required

| Bad | Required |
| --- | --- |
| `color: #205f49`, `font-family: "IBM Plex Sans"` in consumer code | A style role or the `uiStyle` prop |
| Slide titled "Results" or "Q&A" | An action title: "Index freshness fell from 40 to 6 minutes"; the deck ends on an ask with owner and date |
| Indigo accent, centred hero, three icon cards, logo strip, pricing, FAQ for the owner's own page | The owner's style and its section sequence, led by a real mechanism figure |
| Sentences inside diagram nodes, unlabelled arrows | 2–3 word labels, labelled arrows, the claim in the caption |
| Restyling a figure to fit a slide | The figure keeps the diagram style; the slide gives it the body region |
| An invented prop because it seems likely | Check the export first; if it's missing, extend UiPack per its `docs/contributing.md` |
| "Looks good" with nothing rendered | Screenshots, or a plain statement that it wasn't rendered |
