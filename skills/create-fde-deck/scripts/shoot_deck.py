#!/usr/bin/env python3
"""Screenshot every slide of a rendered deck and flag what a reviewer would send back.

Usage: python3 shoot_deck.py deck.html [--out shots/] [--min-fill 0.65] [--min-px 18]

Loads the deck in its own headless Chromium (never an existing browser). A UiPack deck is opened
with ?view=print; any other deck is read as one `section.slide` (or `section`) per slide on a
1920x1080 canvas. Writes shots/slide-NN.png at 1920x1080 and shots/slides.json, and prints:
  placeholder words in visible text (TBD, TODO, confirm, {{...}}), text under --min-px canvas px,
  elements overflowing their box or the slide, cards or panels filled below --min-fill of their
  height, covering under --min-cover of it, or holding an empty band over 30% (centred tiles in a tall
  panel), or spilling out of it, layouts repeated by rendered structure (three in a row, one frame on
  most slides, a strip on most slides, fewer than four distinct layouts), tables with more than one emphasised row, near-empty slides, page
  errors, and UiPack lintDeck errors and warnings (window.__deckLint). slides.json also records each
  slide's current navigation item for `check_deck.py --rendered`.
Exit 1 while any FLAG remains. Requires: pip install playwright && python3 -m playwright install chromium
"""
import argparse
import json
import pathlib
import re
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("shoot_deck.py needs Playwright: pip install playwright && python3 -m playwright install chromium")

PLACEHOLDER = re.compile(
    r"\b(TBD|TBC|TODO|FIXME|XXX|lorem ipsum)\b|\?\?|\{\{|\}\}|\bto confirm\b|[-–—:]\s*confirm\b",
    re.I)
CARDS = ".uipack-cx-panel__inner, .uipack-cx-sowhat, [data-card]"

MEASURE = r"""
([cardSel, minPx]) => {
  const slides = [...document.querySelectorAll('.uipack-deck-print__slide')];
  const list = slides.length ? slides : [...document.querySelectorAll('section.slide')].length
    ? [...document.querySelectorAll('section.slide')] : [...document.querySelectorAll('section')];
  return list.map((slide) => {
    const box = slide.getBoundingClientRect();
    const text = slide.innerText.replace(/\s+\n/g, '\n').trim();
    const small = [], overflow = [], thin = [];
    for (const el of slide.querySelectorAll('*')) {
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height || el.closest('[aria-hidden="true"] title')) continue;
      if (own && el.tagName.toLowerCase() !== 'title') {
        const px = parseFloat(getComputedStyle(el).fontSize);
        if (px < minPx) small.push(`${px}px "${el.textContent.trim().slice(0, 40)}"`);
      }
      const cs = getComputedStyle(el);
      if (/(hidden|clip|auto|scroll)/.test(cs.overflow + cs.overflowY) &&
          (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) && own)
        overflow.push(`clipped: "${el.textContent.trim().slice(0, 40)}"`);
      if (own && (r.right > box.right + 1 || r.bottom > box.bottom + 1 || r.left < box.left - 1))
        overflow.push(`off-slide: "${el.textContent.trim().slice(0, 40)}"`);
    }
    for (const card of slide.querySelectorAll(cardSel)) {
      const c = card.getBoundingClientRect();
      if (c.height < box.height * 0.18) continue;
      let top = Infinity, bottom = -Infinity;
      const spans = [];
      for (const el of card.querySelectorAll('*')) {
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
        const r = el.getBoundingClientRect();
        const leaf = !el.children.length || el.tagName.toLowerCase() === 'svg';
        if (!leaf || !r.height) continue;
        top = Math.min(top, r.top); bottom = Math.max(bottom, r.bottom);
        spans.push([Math.max(r.top, c.top), Math.min(r.bottom, c.bottom)]);
      }
      if (bottom < top) continue;
      const fill = (bottom - c.top) / c.height;
      if (fill < 0) continue;
      // Covered height: the union of content rows, so centred tiles in a tall panel read as empty.
      spans.sort((a, b) => a[0] - b[0]);
      let covered = 0, end = -Infinity, gap = 0, last = c.top;
      for (const [a, b] of spans) {
        if (b <= a) continue;
        if (a > end) { gap = Math.max(gap, a - Math.max(end, last)); covered += b - a; end = b; }
        else if (b > end) { covered += b - end; end = b; }
      }
      gap = Math.max(gap, c.bottom - end);
      thin.push({ fill: Math.round(fill * 100) / 100, cover: Math.round(covered / c.height * 100) / 100,
                  gap: Math.round(gap / c.height * 100) / 100,
                  text: card.innerText.replace(/\s+/g, " ").trim().slice(0, 60) });
    }
    // Rendered structure: top-level panels, what they hold, and whether a strip sits under them.
    const all = [...slide.querySelectorAll('.uipack-cx-panel, [data-card]')];
    const panels = all.filter((el) => !all.some((o) => o !== el && o.contains(el)));
    const kinds = new Set();
    for (const el of panels) {
      if (el.querySelector('table')) kinds.add('table');
      if (el.querySelector('svg rect, svg path.uipack-cx-bar, .uipack-cx-chart svg')) kinds.add('chart');
      if (el.querySelector('.uipack-cx-kpi, [data-kpi]')) kinds.add('tiles');
    }
    if (!panels.length && slide.querySelector('table')) kinds.add('table');
    const strip = !!slide.querySelector('.uipack-cx-takeaway, .uipack-cx-sowhat, [data-strip]');
    const wide = panels.filter((el) => el.getBoundingClientRect().width > box.width * 0.8).length;
    const layout = { panels: panels.length, wide, strip, kinds: [...kinds].sort() };
    const cur = slide.querySelector('nav [aria-current], .uipack-cx-tracker [aria-current], [data-nav-current]');
    const nav = cur ? cur.textContent.trim() : '';
    const tables = [...slide.querySelectorAll('table')].map((t) => {
      const rows = [...t.querySelectorAll('tbody tr')];
      const loud = rows.filter((tr) => tr.hasAttribute('data-highlight') || (() => {
        const cells = [...tr.querySelectorAll('td')].filter((td) => td.innerText.trim());
        return cells.length > 0 && cells.every((td) => parseInt(getComputedStyle(td).fontWeight, 10) >= 600);
      })());
      return { rows: rows.length, loud: loud.length, text: t.innerText.replace(/\s+/g, ' ').trim().slice(0, 50) };
    });
    let words = 0;
    for (const el of slide.querySelectorAll('h1, h2, h3, p, li, td, th, figure, svg text, [data-card]'))
      if (!el.closest('nav') && !el.closest('footer')) words += (el.innerText || el.textContent || '').split(/\s+/).filter(Boolean).length;
    return { text, small: small.slice(0, 5), overflow: overflow.slice(0, 5), cards: thin,
             width: box.width, nav, tables, words, layout };
  });
}
"""


def frame(layout):
    if layout["panels"] == 1 and layout["wide"]:
        return "one full-width panel" + (" with a strip" if layout["strip"] else "")
    return "%d panels%s" % (layout["panels"], " with a strip" if layout["strip"] else "")


def layout_flags(slides):
    """Layout variety by rendered structure, not the declared shape."""
    flags = []
    main = [s for s in slides if not re.search(r"appendix|backup", s.get("nav") or "", re.I)] or slides
    sigs = [(frame(s["layout"]), tuple(s["layout"]["kinds"])) for s in main]
    for i in range(2, len(sigs)):
        if sigs[i] == sigs[i - 1] == sigs[i - 2]:
            flags.append("slides %d-%d render the same layout (%s, %s); vary it" % (
                i - 1, i + 1, sigs[i][0], "+".join(sigs[i][1]) or "text"))
    if len(main) >= 6:
        frames = [f for f, _ in sigs]
        common = max(set(frames), key=frames.count)
        wide = sum(1 for s in main if s["layout"]["panels"] == 1 and s["layout"]["wide"])
        if frames.count(common) > len(main) / 2:
            flags.append("%d of %d presented slides use the same frame (%s); use at least four frames: a chart "
                         "beside its so-what, split panels, tiles over a table, cards per person" % (
                             frames.count(common), len(main), common))
        elif wide > len(main) / 2:
            flags.append("%d of %d presented slides are one full-width panel; give some slides two panels side "
                         "by side or a chart beside its so-what" % (wide, len(main)))
        strips = sum(1 for s in main if s["layout"]["strip"])
        if strips > len(main) * 0.6:
            flags.append("%d of %d presented slides end in the same strip; keep it where it carries the so-what" % (
                strips, len(main)))
        if len(set(sigs)) < 4:
            flags.append("only %d distinct layouts across %d presented slides; use at least four" % (
                len(set(sigs)), len(main)))
    return flags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("deck")
    parser.add_argument("--out", default="shots")
    parser.add_argument("--min-fill", type=float, default=0.65)
    parser.add_argument("--min-px", type=float, default=18)
    parser.add_argument("--min-cover", type=float, default=0.5)
    args = parser.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    target = args.deck if re.match(r"^https?://", args.deck) else pathlib.Path(args.deck).resolve().as_uri()
    flags, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(target)
        page.wait_for_timeout(800)
        url = target
        if page.locator(".uipack-deck").count():
            url = target + ("&" if "?" in target else "?") + "view=print"
            page.goto(url)
            page.wait_for_selector(".uipack-deck-print__slide")
            page.wait_for_timeout(1500)
        slides = page.evaluate(MEASURE, [CARDS, args.min_px])
        if not slides:
            sys.exit("no slides found: expected UiPack print pages or <section class=\"slide\">")
        scale = 1920 / slides[0]["width"]
        page.close()
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale)
        page.goto(url)
        page.wait_for_timeout(1500)
        nodes = page.locator(".uipack-deck-print__slide")
        if not nodes.count():
            nodes = page.locator("section.slide")
        if not nodes.count():
            nodes = page.locator("section")
        for i in range(nodes.count()):
            nodes.nth(i).screenshot(path=str(out / ("slide-%02d.png" % (i + 1))))
        lint = page.evaluate("window.__deckLint || []")
        browser.close()
    for number, slide in enumerate(slides, 1):
        where = "slide %d" % number
        for line in slide["text"].splitlines():
            if PLACEHOLDER.search(line):
                flags.append("%s: placeholder on the slide: %s" % (where, line.strip()[:70]))
        for item in slide["small"]:
            flags.append("%s: text under %gpx: %s" % (where, args.min_px, item))
        for item in slide["overflow"]:
            flags.append("%s: %s" % (where, item))
        for table in slide["tables"]:
            if table["loud"] > 1:
                flags.append("%s: %d of %d table rows emphasised; emphasise at most one (tags go in the "
                             "row label): %s" % (where, table["loud"], table["rows"], table["text"]))
        if slide["words"] < 25:
            flags.append("%s: near-empty slide (%d words); cut it or give it content" % (where, slide["words"]))
        for card in slide["cards"]:
            if card["fill"] > 1.02:
                flags.append("%s: content spills out of its card: %s" % (where, card["text"]))
            elif card["fill"] < args.min_fill:
                flags.append("%s: card only %d%% full: %s" % (where, card["fill"] * 100, card["text"]))
            elif card["cover"] < args.min_cover or card["gap"] > 0.3:
                flags.append("%s: content covers %d%% of the card's height (largest empty band %d%%); size the "
                             "panel to its content, enlarge the figure or add the so-what: %s" % (
                                 where, card["cover"] * 100, card["gap"] * 100, card["text"]))
    flags += layout_flags(slides)
    for item in lint:
        # Notes are cues, not a script: a short talk track is intended.
        if item.get("rule") == "talk-time" and "under half" in str(item.get("message")):
            continue
        if item.get("severity") in ("error", "warn"):
            flags.append("lintDeck %s %s: %s" % (item.get("severity"), item.get("slideId", ""),
                                                  item.get("message", item)))
    flags += ["page error: %s" % e for e in errors]
    (out / "slides.json").write_text(json.dumps(slides, indent=2), encoding="utf-8")
    for line in flags:
        print("FLAG  " + line)
    print("%d flags, %d slides, screenshots in %s. Open every PNG before claiming fit." % (
        len(flags), len(slides), out))
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main())
