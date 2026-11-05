#!/usr/bin/env python3
"""Editorial check for a Markdown deck in the create-fde-deck format.

Usage: python3 check_deck.py deck.md [--rendered shots/slides.json]
Prints one line per finding. Exit 1 when any FLAG is found, 0 when only notes (or nothing) remain.
Checks structure, labels, placeholders, the decision and ask slides, an `Answer:` covering the
asked scope, a response to every `goals:` aim, one-claim headlines, the money frame (yearly net on a
stated volume base that matches its label, Derived not Assumption for arithmetic, cash or capacity,
named sensitivities), a gated segment's remedy and rollback, each condition's date and owner on
every slide, gate counts, decided-sounding tags, rollback coverage, multi-site sequencing, dividers,
table emphasis, cue-length notes, layout runs and a word-count density heuristic. With --rendered (the slides.json shoot_deck.py writes) it
also checks the rendered text: figures missing from deck.md, appendix navigation, and the same
consistency rules. It does not measure fit or check that claims are true. Stdlib only, Python 3.7+.
"""
import json
import re
import sys

LIMITS = {"decision": 4, "findings": 5, "results": 4, "chart": 8, "table": 5, "comparison": 3,
          "architecture": 5, "plan": 4, "ask": 9, "next-steps": 6}
TARGETS = {"findings": 4, "comparison": 2, "architecture": 4, "next-steps": 4}
SHAPES = {"title", "divider"} | set(LIMITS)
LABELS = ("Measured", "Reported", "Derived", "Assumption", "Proposal", "Gap")
LABEL = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\*\*(%s|Evidence)\*\*" % "|".join(LABELS), re.I)
ANY_LABEL = re.compile(r"\b(%s)\b" % "|".join(LABELS))
ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+\S")
COMMENT = re.compile(r"<!--.*?-->", re.S)
NOTES = re.compile(r"<!--\s*notes:(.*?)-->", re.S)
PLACEHOLDER = re.compile(
    r"\b(TBD|TBC|TODO|FIXME|XXX|lorem ipsum)\b|\?\?|\{\{|\}\}|\bto confirm\b|[-–—:]\s*confirm\b", re.I)
MONEY = re.compile(r"[$€£¥]\s?\d[\d,.]*\s?[kKmM]?\b|\b\d[\d,.]*\s?(?:USD|EUR|GBP|SGD|dollars)\b")
PAYBACK = re.compile(r"pay\s?back|pays back|break[- ]?even|\bROI\b", re.I)
IF_NO = re.compile(r"\bif no\b|\bno-go\b|\bif not\b", re.I)
DECIDED = re.compile(r"\b(decided|approved|agreed|confirmed|signed[- ]off|green-?lit)\s+(today|now|in the room)\b"
                     r"|^\s*(approved|decided|agreed|confirmed|go)\s*$", re.I)
ROLLBACK = re.compile(r"roll\s?back|stop rule|stop if|pause if|kill switch|revert", re.I)
SITES = re.compile(r"\b([A-Z][a-z]{2,})\s+(?:and|&)\s+([A-Z][a-z]{2,})\b"
                   r"|\b(?:both|all|every)\s+(?:\w+\s+)?(?:sites|centres|centers|regions|plants|stores|"
                   r"branches|offices|hospitals|warehouses|countries|markets|clinics|depots)\b")
SEQUENCED = re.compile(r"\b(first|then|followed by|stagger\w*|one (?:\w+ )?at a time|in parallel|"
                       r"at the same time|together because|weeks? later)\b", re.I)
MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
MON = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
DATE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+%s|\b%s\s+(\d{1,2})\b|\b20\d\d-(\d\d)-(\d\d)\b" % (MON, MON), re.I)
DATE_WORDS = re.compile(r"\b(by|date|when|due|on|before|until|deadline|method|20\d\d)\b|[:·,.()\s]", re.I)
STOP = set("""a an the and or of to in on for by with from at as is are be our your their its this that
these those into than then each every any all one two three four five gate gates condition conditions
check fix fixed sign signed accepted accept test tests evidence stronger method picked pick chosen owner
team data plan review approval approve before after weeks week days more less calls call agent staff
without human what which when where who will would could should must have has been being new rate per
target time line lines across patients affected group overall total people""".split())
NUMWORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}


def visible_words(text):
    text = COMMENT.sub(" ", text)
    text = re.sub(r"^\s*\|?\s*:?-{3,}.*$", " ", text, flags=re.M)  # table separator rows
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(re.findall(r"[^\W_]+(?:['’.-][^\W_]+)*|\d+(?:[.,]\d+)*%?", text))


def split_slides(source):
    if source.startswith("---\n"):
        end = source.find("\n---\n", 4)
        front, body = (source[4:end], source[end + 5:]) if end != -1 else ("", source)
    else:
        front, body = "", source
    return front, [s for s in re.split(r"^---[ \t]*$", body, flags=re.M) if s.strip()]


def decision_makers(front):
    match = re.search(r"^decision-makers:[ \t]*(.*)$", front, re.M)
    if not match:
        return None
    inline = match.group(1).strip()
    if inline:
        return [p.strip(" \"'") for p in inline.strip("[]").split(",") if p.strip(" \"'")]
    people = []
    for line in front[match.end():].splitlines()[1:]:
        item = re.match(r"^\s+-\s+(.+)$", line)
        if not item:
            break
        people.append(item.group(1).strip(" \"'"))
    return people


def matches(person, names):
    key = person.lower().strip()
    return any(key in n.lower() or n.lower().strip() in key for n in names if n.strip())


def dates(text):
    found = []
    for m in DATE.finditer(text):
        if m.group(1):
            found.append((MONTHS[m.group(2)[:3].lower()], int(m.group(1))))
        elif m.group(4):
            found.append((MONTHS[m.group(3)[:3].lower()], int(m.group(4))))
        else:
            found.append((int(m.group(5)), int(m.group(6))))
    return found


def show(date):
    return "%d %s" % (date[1], "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[date[0] - 1])


def words(text):
    return set(w for part in re.findall(r"[a-z][a-z-]+", text.lower()) for w in part.split("-") + [part]
               if len(w) >= 4 and w not in STOP)


def gate_refs(text):
    refs = set()
    for m in re.finditer(r"\b(?:gates?|conditions?)\s+((?:\d\s*(?:,|and|&|or)?\s*)+)", text, re.I):
        refs |= {int(d) for d in re.findall(r"\d", m.group(1))}
    return refs


def clauses(line):
    """Split one line or table row into clauses; each carries its own dates or the row's due date."""
    parts = [p.strip() for p in re.split(r";|\||\t|(?<=[.!?])\s+(?=[A-Z])", line) if p.strip()]
    pure = [d for p in parts for d in dates(p) if len(DATE_WORDS.sub(" ", DATE.sub(" ", p)).split()) <= 1]
    inherit = pure[0] if len(set(pure)) == 1 else None
    return [(p, dates(p) or ([inherit] if inherit else [])) for p in parts]


def conditions(slide):
    found = []
    for line in COMMENT.sub("", slide).splitlines():
        if not ITEM.match(line) or not re.search(r"\bOwner:", line):
            continue
        body = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", line)
        bold = re.match(r"\*\*(.+?)\*\*", body)
        number = re.match(r"(?:\*\*)?(?:gate|condition)\s+(\d)", body, re.I)
        name = bold.group(1) if bold else re.split(r"[.,;(]| — ", re.sub(
            r"^(?:gate|condition)\s+\d\s*[:·.-]\s*", "", body, flags=re.I))[0]
        name = re.sub(r"^(?:gate|condition)\s+\d\s*[:·.-]\s*", "", name, flags=re.I)
        owner = re.search(r"\bOwner:\s*([^.]+)", line)
        due = re.search(r"\b(?:By|When|Date):\s*(.+)$", line)
        found.append({"name": " ".join(name.split()[:5]), "terms": words(name), "line": line.strip(),
                      "number": int(number.group(1)) if number else None, "bold": bool(bold),
                      "owner": owner.group(1).strip() if owner else "",
                      "date": (dates(due.group(1)) or [None])[0] if due else None})
    for c in found:
        others = set().union(*[o["terms"] for o in found if o is not c]) if len(found) > 1 else set()
        c["unique"] = {t for t in c["terms"] - others if len(t) >= 6}
    return found


def mentions(clause, cond):
    low = clause.lower()
    if cond.get("bold") and cond["name"].lower() in low:
        return True
    hit = {t for t in cond["terms"] if re.search(r"\b%s\b" % re.escape(t), low)}
    if cond["number"] and cond["number"] in gate_refs(clause):
        return True
    return len(hit) >= 2 or bool(hit & cond["unique"])


def consistency(where, text, conds, owners, flags, skip=()):
    """Flag any clause that names a condition with a different date or owner from the decision slide."""
    heading_owner = None
    rows = re.sub(r"\n(?=\t)", "\t", text).splitlines()
    for line in rows:
        if line.strip() in skip:
            continue
        head = re.match(r"^\s*###\s+(.+)$", line)
        if head:
            heading_owner = head.group(1)
            continue
        if line.strip() and not ITEM.match(line.strip()):
            heading_owner = None  # an `If no:` or other line after an ask group belongs to no one
        line_owner = re.search(r"\bOwner:\s*([^.|]+)", line)
        prefix = re.match(r"^\s*(?:[-*]\s+)?\**([A-Z][\w ,']{2,40}?)\**:\s", line)
        owner = (line_owner.group(1) if line_owner else
                 prefix.group(1) if prefix and matches(prefix.group(1), owners) else heading_owner)
        for clause, found in clauses(line):
            for cond in conds:
                if not mentions(clause, cond):
                    continue
                if cond["date"] and found and cond["date"] not in found:
                    flags.append("%s: %s is due %s on the decision slide but %s here: %s" % (
                        where, cond["name"], show(cond["date"]), "/".join(show(d) for d in found),
                        clause[:70]))
                if cond["owner"] and owner and matches(owner, owners) and not (
                        matches(owner, [cond["owner"]]) or matches(cond["owner"], [owner])):
                    flags.append("%s: %s is owned by %s on the decision slide but %s here: %s" % (
                        where, cond["name"], cond["owner"][:30], owner.strip()[:30], clause[:60]))


def counts(where, text, n, flags):
    for m in re.finditer(r"\b(one|two|three|four|five|six|seven|\d)\s+(?:[a-z-]+\s+)?(gates|conditions)\b",
                         text, re.I):
        said = int(m.group(1)) if m.group(1).isdigit() else NUMWORDS[m.group(1).lower()]
        if said != n:
            flags.append("%s: says %s %s; the decision slide lists %d" % (where, m.group(1), m.group(2), n))


def amounts(text):
    out = []
    for m in MONEY.finditer(text):
        raw = re.sub(r"[^\d.kKmM]", "", m.group(0)).rstrip(".")
        mult = 1000 if raw[-1:] in "kK" else 1e6 if raw[-1:] in "mM" else 1
        try:
            out.append(round(float(raw.rstrip("kKmM")) * mult))
        except ValueError:
            pass
    return out


def figures(text):
    """Formatted figures (%, money, dates, decimals, 5m10s, 63,400) for comparing rendered with source."""
    text = text.replace("−", "-").replace("\u2009", " ")
    found = set(re.findall(r"\d+(?:\.\d+)?%|\d+m\d+s|\b\d+\.\d+\b|\b\d{1,3}(?:,\d{3})+\b", text))
    found |= {"£%d" % a for a in amounts(text)}
    found |= {show(d) for d in dates(text)}
    return found


SEPARATORS = re.compile(r"[,;:—]|(?<!\d)\s[–-]\s")
APPOSITIVE = re.compile(r",\s+(?:one|two|three|four|each|both|all|most|some)\s+(?:a|an|the|of|is|are|for)\b", re.I)
HEAD_FIGURE = re.compile(r"\d+(?:\.\d+)?\s?(?:%|h\b|hrs?\b|min\b|days?\b|weeks?\b)|[£$€¥]\s?\d")


def headline_problems(title):
    """A headline is one claim: one sentence, at most one clause break, at most two figures."""
    found = []
    if re.search(r"[.!?]\s+[A-Z]", title):
        found.append("is two sentences")
    if len(SEPARATORS.findall(title)) >= 2:
        found.append("strings %d clauses together" % (len(SEPARATORS.findall(title)) + 1))
    if APPOSITIVE.search(title):
        found.append("hangs a fragment off a comma (`%s`)" % APPOSITIVE.search(title).group(0).strip(", "))
    if len(HEAD_FIGURE.findall(title)) > 2:
        found.append("packs %d figures" % len(HEAD_FIGURE.findall(title)))
    return found


def stems(text):
    return {w[:5] for w in words(text)}


def frontmatter_list(front, key):
    """Values of `key:` given inline or as an indented YAML list."""
    match = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), front, re.M)
    if not match:
        return None
    inline = match.group(1).strip()
    if inline:
        return [inline.strip(" \"'")]
    items = []
    for line in front[match.end():].splitlines()[1:]:
        item = re.match(r"^\s+-\s+(.+)$", line)
        if not item:
            break
        items.append(item.group(1).strip(" \"'"))
    return items


VERDICT_YES = re.compile(r"\b(yes|go|extend|expand|approve|proceed)\b", re.I)
VERDICT_NO = re.compile(r"\b(no|not yet|not today|not now|stop|later|wait)\b", re.I)
ANSWER = re.compile(r"^\s*(?:[-*]\s+)?\**Answer\**\s*[:·]\s*(.+)$", re.I | re.M)
TIME_ANCHOR = re.compile(r"\b(?:When|Date|By):|\b\d+\s+(?:days?|weeks?|months?)\b|\b(?:before|after|from|until)\s+"
                         r"(?:the|each|week|day|go-live|launch|approval)|\btoday\b|\bnext meeting\b", re.I)
ARITHMETIC = re.compile(r"[×÷=]|\d\s+x\s+\d|\bbreak[- ]?even\b|\bnet\b|\brun-?rate\b|\bpays? back\b", re.I)
CASH = re.compile(r"\bcash\b|\bcapacity\b|\breleased\b|\bfreed\b|\bfree up\b|\bbudget saving\b", re.I)
YEARLY = re.compile(r"\ba year\b|\bper year\b|/\s?y(?:ea)?r\b|\bannual|\byearly\b", re.I)
RANGE = re.compile(r"([£$€¥]?\d+(?:\.\d+)?%?)\s*(?:[–-]|to)\s*([£$€¥]?\d+(?:\.\d+)?%?)(?![\d.]*\s?[kKmM]\b)")
COUNT = re.compile(r"(?<![£$€¥\d.,])\d{1,3}(?:,\d{3})+(?![\d%])|(?<![£$€¥\d.,])\d{3,}(?![\d%.,])")


def norm(fig):
    return fig.replace(" ", "").rstrip(".")


def room_checks(front, slides, visible_all, shapes, appendix_at, scope, flags):
    """The answer to what was asked, labels on arithmetic, the money base, thresholds, goals."""
    presented = visible_all[:appendix_at - 1] if appendix_at else visible_all
    # 1. Answer the question the room asked, in so many words.
    asked = re.search(r"^asked:\s*[\"']?(.+?)[\"']?\s*$", front, re.M) or \
        re.search(r"^decision:\s*[\"']?(.+?)[\"']?\s*$", front, re.M)
    answers = [m.group(1) for v in visible_all[:2] for m in ANSWER.finditer(v)]
    if not answers:
        flags.append("slides 1-2: no `Answer:` line saying yes, no, or `yes to A, not yet to B` for what was asked "
                     "(%s)" % (asked.group(1)[:60] if asked else "add `asked:` to the frontmatter"))
    elif not VERDICT_YES.search(" ".join(answers)) and not VERDICT_NO.search(" ".join(answers)):
        flags.append("slides 1-2: the `Answer:` line gives no verdict (yes, no, not yet): %s" % answers[0][:60])
    elif asked and scope:
        beyond = stems(asked.group(1)) - stems(scope.group(1))
        said = " ".join(answers)
        if beyond and (not VERDICT_NO.search(said) or not beyond & stems(said)):
            flags.append("slides 1-2: the room asked about `%s` but the `Answer:` line only covers `%s`; say what "
                         "happens to the rest (`not yet to …, because …; back on <date>`)" % (
                             asked.group(1)[:50], scope.group(1)[:40]))
    # 2. Arithmetic is Derived, not Assumption.
    for number, visible in enumerate(visible_all, 1):
        for line in visible.splitlines():
            cells = [c.strip(" *") for c in line.strip().strip("|").split("|")]
            assumed = re.match(r"^\s*(?:[-*+]|\d+\.)\s+\*\*Assumption\*\*", line) or "Assumption" in cells
            if assumed and ARITHMETIC.search(line) and not re.search(r"\bsensitivity\b", line, re.I):
                flags.append("slide %d: a calculated figure is labelled Assumption; label it Derived and name its "
                             "inputs (an invented input stays Assumption): %s" % (number, line.strip()[:60]))
    # 3. Money: base, scope, yearly figure, cash or capacity, named sensitivities.
    money = [i for i, v in enumerate(presented) if len(MONEY.findall(v)) >= 2]
    if not money:
        return
    main = max(money, key=lambda i: (bool(PAYBACK.search(presented[i])), len(MONEY.findall(presented[i]))))
    where = "slide %d" % (main + 1)
    slide = presented[main]
    heading = re.search(r"^#{1,2}\s+(.+)$", slide, re.M)
    prices = {a for ln in slide.splitlines() if re.search(r"\bprice\b", ln, re.I) for a in amounts(ln)}
    if heading and prices & set(amounts(heading.group(1))) and PAYBACK.search(heading.group(1) + " more than"):
        flags.append("%s: the headline restates the price as the break-even; lead with what the scope returns "
                     "(net a year, cash or capacity): %s" % (where, heading.group(1)[:60]))
    pilot = {norm(c) for t in visible_all for ln in t.splitlines() if re.search(r"\bpilot\b", ln, re.I)
             and re.search(r"\bvolume\b|a month|per month|a week", ln, re.I) for c in COUNT.findall(ln)}
    scope_terms = words(scope.group(1)) if scope else set()
    nets = [ln for ln in slide.splitlines() if re.search(r"\bnet\b", ln, re.I) and MONEY.search(ln)]
    for ln in nets:
        bases = {norm(c) for c in COUNT.findall(MONEY.sub(" ", ln))}
        names_scope = scope_terms and len(scope_terms & words(ln)) >= max(1, round(len(scope_terms) * 0.6))
        if not bases:
            flags.append("%s: the net row shows no volume base; put it on the row (`at 3,400 a month, the two pilot "
                         "sites`) and label the row for the volume it uses: %s" % (where, ln.strip()[:60]))
        elif names_scope and bases & pilot and not re.search(r"\bpilot\b", ln, re.I):
            flags.append("%s: the net row is labelled for `%s` but uses the pilot volume %s" % (
                where, scope.group(1)[:40], "/".join(sorted(bases & pilot))))
        if names_scope:
            for t in visible_all:
                for calc in t.splitlines():
                    if re.search(r"\bNet\b", calc) and re.search(r"[×=]", calc) and \
                            {norm(c) for c in COUNT.findall(MONEY.sub(" ", calc))} & pilot:
                        flags.append("%s: the net row is labelled for `%s`, but its arithmetic uses the pilot "
                                     "volume: %s" % (where, scope.group(1)[:40], calc.strip()[:60]))
        if not YEARLY.search(ln) and not any(YEARLY.search(o) and re.search(r"\bnet\b", o, re.I)
                                             for o in slide.splitlines()):
            flags.append("%s: give the net a year for the approved scope, not only a month: %s" % (where, ln.strip()[:60]))
        quoted = " ".join(re.findall(r"[“\"]([^”\"]+)[”\"]", ln))
        known = set()
        for i, t in enumerate(presented):
            if i != main:
                known |= {norm(f) for f in figures(t)} | {norm(x) for m in RANGE.finditer(t) for x in m.groups()}
        known |= {norm(f) for f in figures(quoted)}
        for o in slide.splitlines():
            if o not in nets:
                known |= {norm(f) for f in figures(o)}
        for m in RANGE.finditer(ln):
            low, high = m.group(1), m.group(2)
            if high.endswith("%") and not low.endswith("%"):
                low += "%"
            if high[0] in "£$€¥" and low[0] not in "£$€¥":
                low = high[0] + low
            for corner in (low, high):
                fig = norm(corner)
                key = "£%d" % round(float(re.sub(r"[^\d.]", "", fig))) if fig[0] in "£$€¥" else fig
                if fig not in known and key not in known and not re.search(r"\bsensitivity\b", ln, re.I):
                    flags.append("%s: range corner %s appears nowhere in the evidence; show it as a named "
                                 "sensitivity with its input (`Sensitivity: …`): %s" % (where, corner, ln.strip()[:50]))
    if not CASH.search(slide):
        flags.append("%s: say whether the saving is cash or released capacity (and what turns capacity into "
                     "cash, e.g. posts changing)" % where)


def segment_checks(visible_all, shapes, appendix_at, flags):
    """A gate drawn against a segment applies in the rollback too; a weak segment gets its own remedy."""
    end = appendix_at - 1 if appendix_at else len(visible_all)
    plan = " ".join(v for v, s in zip(visible_all[:end], shapes[:end]) if s == "plan")
    remedies = " ".join(ln for v, s in zip(visible_all[:end], shapes[:end]) for ln in v.splitlines()
                        if re.search(r"\bProposal\b", ln) or s in ("plan", "decision"))
    monitored = [c for c in re.split(r"[·;]|\.\s", plan) if re.search(r"monitor\w*\s+only", c, re.I)]
    for clause in monitored:
        remedies = remedies.replace(clause.strip(), " ")
    for number, (visible, shape) in enumerate(zip(visible_all[:end], shapes[:end]), 1):
        gate = re.search(r"^\s*\*?Gate:\s*([\d.]+)%", visible, re.M | re.I)
        if shape != "chart" or not gate:
            continue
        for row in visible.splitlines():
            cells = [c.strip(" *") for c in row.strip().strip("|").split("|")]
            value = re.match(r"^([\d.]+)%$", cells[-1]) if len(cells) >= 2 else None
            if not value or float(value.group(1)) >= float(gate.group(1)):
                continue
            seg = stems(cells[0])
            if not seg:
                continue
            for clause in monitored:
                if seg & stems(clause):
                    flags.append("slide %d: `%s` is drawn against the %s%% gate, but the rollback says it is "
                                 "monitored only; give it that trigger, or drop the gate from the chart" % (
                                     number, cells[0], gate.group(1)))
            if not seg & stems(remedies):
                flags.append("slide %d: `%s` falls below the gate but no Proposal, condition or phase names a "
                             "remedy for it (a route or channel for that group, an owner, a review trigger)" % (
                                 number, cells[0]))


def goal_checks(front, visible_all, appendix_at, flags):
    """Every stated goal (`goals:`) gets a direct response: the holder named, a path, and when."""
    goals = frontmatter_list(front, "goals")
    if goals is None:
        flags.append("deck: frontmatter needs `goals:` (each person's stated aim from the brief, `Who: aim`, "
                     "in the room or not)")
        return
    presented = visible_all[:appendix_at - 1] if appendix_at else visible_all
    for goal in goals:
        holder, _, aim = goal.partition(":")
        aim_stems = stems(aim or holder)
        hit = False
        for visible in presented:
            heading = None
            for line in visible.splitlines():
                head = re.match(r"^\s*###\s+(.+)$", line)
                if head:
                    heading = head.group(1)
                    continue
                if re.match(r"^\s*Decided separately", line, re.I):
                    continue
                named = matches(holder, [line]) or (heading and matches(holder, [heading]))
                if named and aim_stems & stems(line) and TIME_ANCHOR.search(line):
                    hit = True
        if not hit:
            flags.append("deck: `%s` gets no direct response; name them with a path, its condition and when "
                         "(`decided separately` alone is not an answer)" % goal[:70])


def check(path, rendered=None):
    front, slides = split_slides(open(path, encoding="utf-8").read())
    flags, notes = [], []
    for key in ("title", "audience", "decision"):
        if not re.search(r"^%s:\s*\S" % key, front, re.M):
            flags.append("deck: frontmatter needs `%s:`" % key)
    people = decision_makers(front)
    if not people:
        flags.append("deck: frontmatter needs `decision-makers:` (a list of who decides)")
    scope = re.search(r"^scope:\s*[\"']?(.+?)[\"']?\s*$", front, re.M)
    if not 1 <= len(slides) <= 30:
        flags.append("deck: %d slides; keep 1-30 and split into separate decks beyond that" % len(slides))
    shapes, ask_names, visible_all, appendix_at, conds = [], [], [], None, []
    metrics, plan_text = [], []
    for number, slide in enumerate(slides, 1):
        where = "slide %d" % number
        if appendix_at is None and re.search(r"<!--\s*appendix\s*-->", slide):
            appendix_at = number
        heading = re.search(r"^#{1,2}\s+(.+)$", slide, re.M)
        shape = re.search(r"<!--\s*shape:\s*([\w-]+)\s*-->", slide)
        shape = shape.group(1).lower() if shape else ("title" if number == 1 else None)
        shapes.append(shape)
        visible = COMMENT.sub("", slide)
        visible_all.append(visible)
        lines = visible.splitlines()
        for line in lines:
            if PLACEHOLDER.search(line):
                flags.append("%s: placeholder on a customer slide (make it an owned ask, a `Gap ·` "
                             "line, or move it to the notes): %s" % (where, line.strip()[:70]))
            if DECIDED.search(re.sub(r"[#*_`|]", " ", line)):
                flags.append("%s: reads as if the decision is already made; say `For decision today` "
                             "or `Proposed`: %s" % (where, line.strip()[:70]))
        if not heading:
            flags.append("%s: no takeaway headline (`#` or `##`)" % where)
        else:
            title = heading.group(1).strip()
            if len(title) > 95:
                flags.append("%s: headline is %d chars; keep it under 95" % (where, len(title)))
            elif number == 1 and len(title) > 60:
                notes.append("%s: opening headline is %d chars; aim under 60" % (where, len(title)))
            for problem in headline_problems(title):
                flags.append("%s: headline %s; rewrite it as one clean claim: %s" % (where, problem, title[:70]))
        note = NOTES.search(slide)
        if note and not appendix_at and len(note.group(1).split()) > 75:
            flags.append("%s: notes run %d words; write cues the presenter talks from (Say: what the slide "
                         "can't hold. Point: the figure. Bridge: only if not obvious), under 60 words" % (
                             where, len(note.group(1).split())))
        if shape not in SHAPES:
            flags.append("%s: add `<!-- shape: ... -->` (one of %s)" % (where, ", ".join(sorted(SHAPES))))
            continue
        words_n = visible_words(slide)
        if words_n > (65 if shape == "title" else 135):
            flags.append("%s: %d visible words over the %d heuristic; tighten or split" % (
                where, words_n, 65 if shape == "title" else 135))
        if shape == "divider":
            body = [ln for ln in lines if ln.strip() and not re.match(r"^\s*#", ln)]
            if visible_words("\n".join(body)) < 15:
                flags.append("%s: near-empty divider; cut it (mark the first backup slide `<!-- appendix -->`) "
                             "or make it an index of what each backup slide answers" % where)
        slide_source = any(re.match(r"^\s*\*?Source:", line) for line in lines)
        items = [line for line in lines if ITEM.match(line)]
        table = [line for line in lines if line.lstrip().startswith("|")
                 and not re.match(r"^\s*\|?\s*:?-{3,}", line)]
        rows = table[1:]
        if sum(1 for r in rows if "**" in r) > 1:
            flags.append("%s: %d table rows carry bold; emphasise at most one row (the one the headline "
                         "is about)" % (where, sum(1 for r in rows if "**" in r)))
        count = {"comparison": len(re.findall(r"^###\s+\S", slide, re.M)),
                 "results": len(rows) or len(items), "chart": len(rows) or len(items),
                 "table": len(rows) or len(items)}.get(shape, len(items))
        if shape in LIMITS:
            if count == 0:
                flags.append("%s: %s slide has no content" % (where, shape))
            elif count > LIMITS[shape]:
                (notes if appendix_at else flags).append("%s: %d %s items; the limit is %d, split the slide" % (
                    where, count, shape, LIMITS[shape]))
            elif shape in TARGETS and count > TARGETS[shape]:
                notes.append("%s: %d %s items; %d or fewer reads better" % (
                    where, count, shape, TARGETS[shape]))
        for line in items:
            label = LABEL.match(line)
            if shape == "findings" and not label:
                flags.append("%s: finding without a Measured/Reported/Assumption/Proposal/Gap label: %s" % (
                    where, line.strip()[:60]))
            if label and label.group(1).lower() == "evidence":
                flags.append("%s: `Evidence` is ambiguous; use Measured (data) or Reported (a person "
                             "said it): %s" % (where, line.strip()[:60]))
            if label and label.group(1).lower() in ("measured", "reported", "evidence") \
                    and "Source:" not in line and not slide_source:
                flags.append("%s: %s claim without a source: %s" % (where, label.group(1), line.strip()[:60]))
        if shape == "results":
            header = [c.strip(" *").lower() for c in table[0].strip().strip("|").split("|")] if table else []
            col = header.index("metric") if "metric" in header else 1
            for line in rows or items:
                if "Source:" not in line and not slide_source:
                    flags.append("%s: metric without provenance (source, sample, window): %s" % (
                        where, line.strip()[:60]))
                if not ANY_LABEL.search(line):
                    flags.append("%s: metric without a label (Measured, Reported...): %s" % (
                        where, line.strip()[:60]))
                cells = [c.strip(" *") for c in line.strip().strip("|").split("|")]
                if cells and re.match(r"^(not measured|n/?a|unknown|none)$", cells[0], re.I):
                    flags.append("%s: a gap set as a metric value; make it a `Gap ·` line: %s" % (
                        where, line.strip()[:60]))
                if not appendix_at and not MONEY.search(visible) and len(cells) > col:
                    name = re.split(r"[;,(]", cells[col])[0]
                    metrics.append((name.strip(), [w for w in re.findall(r"[a-z]{4,}", name.lower())
                                                   if w not in STOP][:3]))
        if shape == "chart" and not re.search(r"^\s*\*?(Gate|Baseline|Target):", visible, re.M | re.I):
            notes.append("%s: chart without a `Gate:`, `Baseline:` or `Target:` line to compare against" % where)
        if shape == "decision":
            conds = conditions(slide)
            for line in items:
                if not re.search(r"\bOwner:", line) or not re.search(r"\b(By|Date|When):", line):
                    flags.append("%s: condition needs `Owner:` and `By:`: %s" % (where, line.strip()[:60]))
            if not IF_NO.search(visible):
                flags.append("%s: say what a no answer means (an `If no:` line)" % where)
        if shape == "plan":
            plan_text.append(visible)
            for line in items:
                if not re.search(r"\b(When|Date|By):", line):
                    flags.append("%s: phase needs `When:` (a duration or anchored date): %s" % (
                        where, line.strip()[:60]))
                if SITES.search(line.split("Gate:")[0]) and not SEQUENCED.search(line):
                    flags.append("%s: phase starts several sites at once; say the order (one first, the "
                                 "gate to add the next) or why in parallel: %s" % (where, line.strip()[:60]))
        if shape == "ask":
            persons = re.findall(r"^###\s+(.+)$", visible, re.M)
            ask_names += persons
            if not persons:
                flags.append("%s: group the ask by decision-maker with `### Person` headings" % where)
            for line in items:
                if not re.search(r"\b(Date|By|When):", line):
                    flags.append("%s: ask needs `Date:`: %s" % (where, line.strip()[:60]))
            if not IF_NO.search(visible):
                flags.append("%s: say what a no answer means (an `If no:` line)" % where)
        if shape == "next-steps":
            for line in items:
                owner = re.search(r"\bOwner:\s*([^.]+)", line)
                if owner:
                    ask_names.append(owner.group(1))
                if not owner or "Date:" not in line:
                    flags.append("%s: action needs `Owner:` and `Date:`: %s" % (where, line.strip()[:60]))
    presented = shapes[:appendix_at - 1] if appendix_at else shapes
    if presented and presented[-1] not in ("ask", "next-steps"):
        flags.append("deck: the last presented slide must be the ask (`ask` or `next-steps`)")
    if "decision" not in presented[:2]:
        flags.append("deck: put a `decision` slide (the answer, conditions, owners) at slide 1 or 2")
    for person in people or []:
        if not matches(person, ask_names):
            flags.append("deck: decision-maker `%s` has no specific ask on the closing slide" % person)
    run = 1
    for i in range(1, len(presented)):
        run = run + 1 if presented[i] == presented[i - 1] and presented[i] not in ("divider",) else 1
        if run == 3:
            flags.append("deck: slides %d-%d share the `%s` shape; vary the layout" % (i - 1, i + 1, presented[i]))
    if len(presented) >= 6 and presented.count("findings") > len(presented) / 3:
        flags.append("deck: %d of %d slides are bullet `findings`; turn some into charts, tables or tiles" % (
            presented.count("findings"), len(presented)))
    if len(presented) >= 6:
        common = max(set(presented), key=presented.count)
        if presented.count(common) > len(presented) / 2:
            notes.append("deck: %d of %d slides are `%s`; mix in charts, tables or tiles" % (
                presented.count(common), len(presented), common))

    # Money: a net range for exactly the scope asked for.
    text = "\n".join(visible_all)
    framed = [line for line in text.splitlines() if PAYBACK.search(line)
              and (re.search(r"\d", line) or re.search(r"\bGap\b", line))]
    if MONEY.search(text) and not framed:
        flags.append("deck: money appears but no payback, break-even or ROI frame (or a `Gap ·` naming "
                     "the missing input), with a number or a range")
    money = [i for i, v in enumerate(visible_all) if len(MONEY.findall(v)) >= 2
             and (not appendix_at or i < appendix_at - 1)]
    if money:
        main = max(money, key=lambda i: (bool(PAYBACK.search(visible_all[i])), len(MONEY.findall(visible_all[i]))))
        nets = [ln for ln in visible_all[main].splitlines() if re.search(r"\bnet\b", ln, re.I)
                and len(MONEY.findall(ln)) >= 2]
        gap_net = [ln for ln in visible_all[main].splitlines() if re.search(r"\bnet\b", ln, re.I)
                   and re.search(r"\bGap\b", ln)]
        if not nets and gap_net:
            notes.append("slide %d: net stated as a Gap; give a range under assumed inputs if any are "
                         "defensible" % (main + 1))
        elif not nets:
            flags.append("slide %d: the money slide states no net figure; add `Net (benefit − cost), <scope>: "
                         "£a–£b a month` as a range under the stated assumptions" % (main + 1))
        if not scope:
            flags.append("deck: money appears; add `scope:` to the frontmatter (exactly what today's ask "
                         "approves, e.g. which sites and lines)")
        elif nets:
            need = words(scope.group(1))
            best = max(len(need & words(ln)) for ln in nets)
            gap_volume = any(re.search(r"\bGap\b", ln) and re.search(r"\bvolume\b", ln, re.I)
                             and len(need & words(ln)) >= max(1, round(len(need) * 0.6))
                             for ln in visible_all[main].splitlines())
            if need and best < max(1, round(len(need) * 0.6)) and not gap_volume:
                flags.append("slide %d: no net row for exactly the requested scope (`%s`); show that row first, "
                             "wider scope only as context" % (main + 1, scope.group(1)))

    room_checks(front, slides, visible_all, shapes, appendix_at, scope, flags)
    segment_checks(visible_all, shapes, appendix_at, flags)
    goal_checks(front, visible_all, appendix_at, flags)

    # Conditions: one date, one owner and one count everywhere.
    owners = (people or []) + [c["owner"] for c in conds if c["owner"]]
    if conds:
        skip = {c["line"] for c in conds}
        for number, visible in enumerate(visible_all, 1):
            consistency("slide %d" % number, visible, conds, owners, flags, skip)
            counts("slide %d" % number, visible, len(conds), flags)
            if shapes[number - 1] == "table" and not (appendix_at and number >= appendix_at):
                repeated = sum(1 for ln in visible.splitlines() if ln.lstrip().startswith("|")
                               and any(mentions(ln, c) for c in conds))
                if repeated >= 2:
                    notes.append("slide %d: repeats %d conditions from the decision slide as rows; refer to "
                                 "them in one line and keep the rows for other risks" % (number, repeated))

    # Rollback covers every reported metric.
    if metrics and plan_text:
        rule = " ".join(ln[ROLLBACK.search(ln).start():] for t in plan_text for ln in t.splitlines()
                        if ROLLBACK.search(ln)).lower()
        if not rule:
            flags.append("deck: the plan has no rollback or stop rule (`Rollback:` with a trigger per metric)")
        else:
            for name, keys in metrics:
                if keys and not any(re.search(r"\b%s" % k[:5], rule) for k in keys):
                    flags.append("deck: the rollback rule has no trigger for reported metric `%s`; add one, or "
                                 "say it is monitored only" % name[:50])

    if rendered:
        check_rendered(rendered, slides, visible_all, appendix_at, conds, owners, flags)
    for line in flags:
        print("FLAG  " + line)
    for line in notes:
        print("note  " + line)
    print("%d flags, %d notes, %d slides. Heuristic only: render and inspect every slide to claim fit."
          % (len(flags), len(notes), len(slides)))
    return 1 if flags else 0


def check_rendered(path, slides, visible_all, appendix_at, conds, owners, flags):
    shots = json.load(open(path, encoding="utf-8"))
    if len(shots) != len(slides):
        flags.append("rendered: %d slides but deck.md has %d; render one slide per deck.md slide" % (
            len(shots), len(slides)))
        return
    for number, (shot, source) in enumerate(zip(shots, visible_all), 1):
        where = "rendered slide %d" % number
        text = shot.get("text", "")
        extra = sorted(figures(text) - figures(source))
        if extra:
            flags.append("%s: shows figures not on deck.md slide %d (%s); put them in deck.md or drop them" % (
                where, number, ", ".join(extra[:6])))
        for line in text.splitlines():
            if DECIDED.search(line):
                flags.append("%s: reads as if the decision is already made: %s" % (where, line.strip()[:60]))
        nav = (shot.get("nav") or "").strip()
        if appendix_at and number >= appendix_at and nav and not re.search(r"appendix|backup", nav, re.I):
            flags.append("%s: appendix slide shows `%s` as the current section; add an Appendix section "
                         "or drop the tracker" % (where, nav))
        if conds:
            consistency(where, text, conds, owners, flags)


if __name__ == "__main__":
    args = sys.argv[1:]
    rendered = None
    if "--rendered" in args:
        i = args.index("--rendered")
        rendered = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]
    if len(args) != 1:
        sys.exit(__doc__.strip().splitlines()[2])
    sys.exit(check(args[0], rendered))
