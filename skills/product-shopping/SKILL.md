---
name: product-shopping
description: >-
  Recommend what to buy, judge an item the owner is looking at in a shop (a photo of a price tag,
  shelf card or product counts), find the best legitimate price or price history for a chosen
  model, compare landed cost across countries in SGD, or say where to buy it. Use for "which X
  should I get", "is X worth it", "I'm in the shop looking at X", "is this a good deal", "should I
  buy this overseas", "where can I buy X". Not for: property (evaluate-condo).
---

# Compare Products

Decide **what** to get (Track A), then find the best **price** (Track B), or compare it **across
countries** (Track C); judge an item **in a shop** (In-shop mode). Run whichever the ask needs.

- **In a shop** (a photo of a price tag, shelf card or product taken in a store, or "I'm in the
  shop looking at X") → In-shop mode, below. No Track A interview.
- **Model not pinned down** ("what should I get", "compare these", "is X worth it") → Track A,
  which hands the winner to Track B for the **Before you buy** line.
- **Exact model known** ("where's it cheapest", "is this deal good", "price history", "good time
  to buy") → Track B directly. Skip Track A's interview.
- **Several countries** ("SG vs US price", "where in the world is it cheapest", "should I buy this
  overseas", a trip abroad) → Track C: read
  [references/cross-country.md](references/cross-country.md) and follow it.
- **"Where can I buy X"** → Where to buy, below; then offer Track A or B.

**Start from what the owner already has.** Before the first question or search, read the host
repo's shopping notes (its folder manual, e.g. `AGENTS.md`, or shopping index says where notes go):
brand exclusions and buying preferences; the category's note of what is **owned, wanted, tried and
considered** (a wardrobe, skincare or devices note), with any recorded **criteria** for an item;
and recorded **sizes**. Then:

- Never recommend an excluded brand, even as a budget backup.
- Don't re-recommend something owned; pick what fills a listed gap or pairs with owned items, and
  say which owned item it pairs with or replaces. Don't ask what the notes already answer.
- Give sizes from the recorded measurements and fit notes, not a generic chart.
- When the owner reports buying or trying something, write it to the category note in the same
  session: a purchase is marked bought in the wanted list and added to owned; a try-on is a dated
  line with the size and the fit they reported. Tell them where you wrote it.

If the repo keeps none of these notes, ask about owned items and sizes in the Step 1 question.

# In-shop mode

The owner is standing in the shop reading on a phone: verdict first, short enough to take in at the
shelf, as plain lines rather than tables; leave out source lists and side tips (tax refunds, care)
unless asked.

1. **Pin the model** from the tag: model code, variant, colourway. If the photo doesn't settle it,
   ask for the code on the tag; don't guess.
2. **Read the notes** above, then reply in this shape:
   - **Verdict:** buy, skip, or try it on first.
   - **Criteria:** one line per recorded criterion: pass / fail / can't tell, and why.
   - **Size to ask for:** from recorded measurements and fit notes.
   - **Price:** the in-shop price check the host's preferences note defines, if it has one (follow
     it there); otherwise the shown price against the home-country price for the same model. One
     line per price, with its source and date inline.
3. **Source every size, fit and tried statement**: "you said, <date>", the note it is recorded in,
   or "not recorded" plus a question. A photo, even of the owner wearing the item, is not a try-on
   report.

   | Bad | Required |
   |---|---|
   | "M fits you well" (from a mirror photo) | "Ask for M (sizes note). No try-on of this model recorded: how does it fit?" |
   | "You tried these last week" (it was a photo) | "Considered list: photo on <date>, not tried." |
4. **Write back before finishing:** record the shown price (Track B step 3), and write any reported
   try-on or purchase to the category note (above).

# Track A: decide what to buy

Interview before researching. Generic research disappoints because it searches before it
understands the decision. **No searching until the Step 3 gate passes.** If the ask isn't a
purchase recommendation, say so and stop.

### 1 · Opening question (one message)
Ask for a brain-dump in their own words: what they're buying (category, models in mind), what for
(the real job, where/how/how often), what they already know or ruled out and why, budget and where
they'll buy (country/currency), what "good" looks like. Close with "...and anything else you think
matters." One friendly block, not a form; say a sentence or just the product name is plenty
because the next step is tap-to-answer.

### 2 · Gap analysis (internal)
Score the request against the decision-dimension checklist in `REFERENCE.md` §1: each dimension
known / unknown / not-applicable. Keep only the unknowns that would change the recommendation.
Those blind spots are the main value-add.

### 3 · Clarify the gaps (gate)
Ask the **2–4 highest-leverage unknowns in one round** with the structured user-input tool when
available, else one compact message. Every question has concrete pre-filled options; never force a
long typed answer.
- Most-likely / recommended option first.
- Allow multiple selections when several answers can be true at once.
- For a factor the buyer likely didn't know mattered, fold a one-line *why it matters* into the
  question.
- Second round only if an answer opens a fork that changes the shortlist.
- Don't ask what they already answered or anything irrelevant to the category.
- "Other" and "just go" are always available; on "just go", state your assumptions and proceed.

### 4 · Research
Triangulate; never trust a single source.
- Independent hands-on tests, aggregated owner reviews, forum sentiment, spec sheets.
- Hunt failure modes, reliability, common complaints, not just praise.
- Check recency: current model? refresh or seasonal sale imminent?
- Discount affiliate listicles, sponsored placements, astroturf; weight independent testing.
- **Marketing is a claim, not evidence.** For each claim ask "what spec, test, or mechanism backs
  this?" and find it. For measurable products lead with independent measurements, standards,
  teardowns, datasheets; decode buzzwords into the spec that matters (`REFERENCE.md` §3). Scale
  depth to stakes: full workup for spec-driven, expensive or health items, light touch for a mug.
- Narrow to 2–4 contenders scored on *the buyer's ranked priorities*. Never a generic "best overall".

### 5 · Deliver
Use the template in `REFERENCE.md` §4: top pick and why it fits *them*, runner-up ("pick this
instead if you weigh X more"), trade-off table across their priorities, what to avoid / common
regrets, pre-purchase checks, confidence and what would change the call. Then hand off to Track B.

# Track B: find the best price

Lowest legitimate price for a **specific** model/variant, not a category.

### 1 · Pin the exact item
Model number, variant, size/colour where price differs, region and currency. Ask only if missing.

### 2 · Check the local cache first
`price-cache.py`, in this skill's base directory (run it; `--help` lists commands), holds prices
already gathered, dated, with currency, url and condition. The cache is the host repo's data, not
the skill's: it defaults to `resources/shopping/price-cache.json` under the host repo root
(`$HOST_REPO`, else the Git toplevel of the working directory); `--cache` or `PRICE_CACHE`
overrides it. Below, `PC` is `python3 <skill dir>/price-cache.py`.
- `$PC cheapest "<model>" [--currency <CUR>] --available` gives an instant answer if we've seen it, and warns when results span currencies.
- `$PC stale --days 30` lists what to re-fetch. Re-fetch only stale/missing items; trust the rest.

### 3 · Sweep current listings, structured sources first
Start from the host repo's venue directory if it keeps one (the shopping notes above), then
widen. A CAPTCHA or bot-wall means you're using the hard door; an allowed one almost always
exists. In order:
1. **Official / aggregator data**: retailer or brand API, product feed, RSS, sitemap; aggregators
   (Google Shopping, PriceSpy, PriceRunner, Idealo) and trackers (Keepa, camelcamelcamel). Stable,
   no walls, history for free.
2. **Live web search** across the region's major retailers.
3. **`web-extract`** for prices behind JS; it picks Firecrawl or a plain fetch by credit balance.
4. **Your own logged-in session** (Playwright) where the owner has an account. Legitimate access,
   not evasion.

**Record first-hand prices only:** a tag or shelf photo, or a page loaded this session; never an
approximate, converted or recalled figure. `$PC record "<shop, branch or site>" <category> "<brand
model code variant>" <lo> <hi> --currency <CUR> [--url <link>] [--condition new|refurb|used] [--date
YYYY-MM-DD]`. The source is the actual shop and branch, never "a shop in <city>"; the title carries
the exact model code; `--currency` always; `--date` when the observation is older than today.

On CAPTCHA / bot-detection / paywall, stop and report (`web-extract`'s hard stop) and try another
source. Never auto-solve CAPTCHAs or rotate identities/proxies.

### 4 · Price history
Amazon: camelcamelcamel / Keepa. Elsewhere: PriceSpy / PriceRunner / Idealo / Google Shopping or the
category's known tracker (`REFERENCE.md` §6.4).

### 5 · Landed cost
Add shipping, taxes/import/duty, subtract valid coupons/cashback. Rank by what you actually pay
(`REFERENCE.md` §6.1).

### 6 · Verify the winner
Open the listing: price, right model, in stock, ships to region, reputable seller (not grey-market
or counterfeit).

### Price report
- **Cheapest legit option:** price, landed cost, retailer, condition, link.
- **Runner-up(s):** especially a more trusted seller if the cheapest is risky.
- **Deal verdict:** *good now / wait / average* against typical and recent low (`REFERENCE.md` §6.5).
- **Watch-outs:** fake "was" prices, expired or region-locked coupons, refurb vs new, model-year
  confusion (`REFERENCE.md` §6.2–6.3).

# Where to buy

List the venues that fit the item and the buyer's region, not a generic web search.
- Start from the host repo's venue directory (the shopping notes above). If it has none, say so
  and offer to start one; if nothing in it fits, say so and search broadly (Track B step 3).
- Pin the item category and where they will buy (home, online to home, a trip). Ask one short
  question only if either is unclear.
- Order venues by fit for this item, each with what it is best for and the practical note
  (location for a shop; shipping, warranty or authenticity caveat online). For
  authenticity-critical items, prefer brand stores and authorised retailers over marketplaces.
- Give the trade-off in one line ("marketplace cheapest but slow and no warranty; brand store
  faster with returns"). Respect timing: never suggest an overseas shop for something needed at
  home next week.
- When the buyer names a new venue worth keeping, add it to the directory. Never invent an
  address or a detail; leave a `TODO:`.

# Rules

- Honor the buyer's region, currency, and what's actually available to them.
- Cite sources; separate measured fact from reviewer opinion; flag thin evidence.
- Date every price; if unconfirmed, say "verify at checkout".
- Surface refurbished/open-box when the buyer is open to it.
- **Legitimate sources only:** real retailers, official refurb/used marketplaces, valid public
  coupons. No leaked keys, dubious grey-market, coupon fraud, or scraping against a site's terms.

Companion skills: **`web-extract`** for web search and page reads; **`youtube-transcript`** to mine
video reviews for real-world failure modes (Track A). See [references/cross-country.md](references/cross-country.md) for Track C and
[REFERENCE.md](REFERENCE.md): §1 dimension checklist, §2 category blind spots, §3 source
rubric, §4 output template, §5 worked example, §6 pricing reference.
