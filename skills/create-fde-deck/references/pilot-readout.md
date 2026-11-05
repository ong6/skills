# Pilot readout

## Contents

- [Use it for](#use-it-for)
- [Arc](#arc)
- [Workflow](#workflow)
- [Rules](#rules)
- [Money](#money)
- [Skeleton](#skeleton)

Report what changed, what is still unknown, and the decision the evidence permits, with its
conditions, in the first two slides.

## Use it for

Proof-of-concept readouts, pilot scorecards, go/no-go and expansion decisions. 20 minutes holds
8–11 presented slides plus an appendix. Build only from customer-visible pilot records.

## Arc

| # | Shape | Job |
|---|---|---|
| 1 | `title` | The answer as the headline ("Conditional go to all six regions, gated on two security items"), the deciding result, and an `Answer:` line for the scope the room asked about (`yes to A; not yet to B, because …; back <when>`); slide 3 holds the full results, not a copy |
| 2 | `decision` | Each condition with owner and by when; what is decided separately (headcount, pricing), each with its path and when; what a no means |
| 3 | `results` | The pre-agreed gates against the results, each labelled |
| 4 | `chart` | The segment that differs (a site, a document type) against the gate it is held to, and the specific remedy for it |
| 5 | `findings` or `comparison` | Against the old way: measured versus reported, and whether they are comparable |
| 6 | `table` | Incidents and risks that are not gates: why each matters, mitigation, owner; gates referred to by name in one line, not re-listed |
| 7 | `results` | Money: run-rate cost, the net a year as a range on a stated volume base, cash or released capacity, break-even, what the price excludes |
| 8 | `plan` | Phases, the gate that opens each, durations or anchored dates, site order, a rollback trigger per reported metric |
| 9 | `ask` | Each decision-maker's actions and dates; a response to every stated aim (`goals:`), including holders outside the room; `If no:` |
| — | appendix (first slide marked `<!-- appendix -->`) | Method, arithmetic, definitions; no empty divider |

Merge or drop rows for a shorter meeting; never drop slides 1, 2, the money or the ask.

## Workflow

1. Gather the hypothesis, the pre-agreed success and stop gates (mark any set after the fact),
   baseline, cohort, sample, window, exclusions, method, cost and incidents.
2. Build the **measurement ledger**: metric, numerator and denominator, unit, baseline (and whether
   it was measured or reported), observed value, window, source, caveat. Absent data is a Gap with
   an owner, never zero.
3. Check comparability: cohort shifts, different units (per field versus per document), windows,
   manual assistance. No causal or population-wide claim from an uncontrolled pilot. Show any
   computed figure's formula in the notes or a footnote.
4. Give unfavourable evidence equal visibility when it changes the decision: a weak segment, an
   outage you caused, an unmet gate.
5. Recommend a **bounded** outcome (stop, extend, or expand to a named cohort) with security and
   quality gates, owners, a rollback rule and a review point. An unmet hard safety gate stays a
   visible blocker.
6. Verify every number against the ledger; list unresolved gaps, each with its owner, for the
   pre-read.

## Rules

| Bad | Required |
|---|---|
| "Success rate up 15%" (60% → 75%) | "Up 15 percentage points (25% relative)", and whether the cohorts match |
| "Manual error rate ~5%" tagged Assumption | **Reported** · "about 5%", team lead, never measured; and say whether the units match |
| A computed share ("about 40% of company volume") tagged Measured, or a break-even tagged Assumption | **Derived** with its formula in a footnote; only its invented inputs are Assumptions |
| "Net, all of region X" computed from the two pilot sites' volume | "Net at pilot sites' volume (3,400 a month)", plus `Gap · region X volume: operations team` |
| Range corners "70–85% matched, $2–$5 an invoice" with 70% and $2 invented | The evidenced row (85%, Finance's $5), then `Sensitivity: $2 an invoice (under half Finance's figure)` |
| "Region X pays back if a manual match costs more than $0.40" (the price restated) | "The two pilot sites alone free $90k–$170k of AP time a year" |
| A per-site pause line drawn on a customer segment's bar, and that segment "monitored only" in the rollback | The gate on the unit it governs; the segment gets its own trigger and remedy ("paper invoices go to the scan-fix route; under 80% for 2 weeks triggers review") |
| A director's stated aim (redeploy 4 staff) answered only with "decided separately" | Their path, condition and date: "log handling time 8 weeks, agree with HR, decide at week 8" |
| "2x faster" with no matched baseline | "Speed-up not sizeable: the old process has no timestamps" |
| "Errors concentrate in two fields" when the source lists only those fields | Say what was measured; anything more is an Assumption or cut |
| "3 conditions" on slide 2 and "four things stand in the way" on slide 8 | One count everywhere; things that are not gates are labelled "decided separately" |
| `Owner: TBD — confirm`, `Date: TBD` | `IT lead: commit a scoping date today`, or a role with authority and an anchored date |
| "Run a two-week manual baseline at every site" with no cost | Its cost in people-days and its effect on the date, or a cheaper historical sample |
| `Not measured` as a big number on a card | A `Gap ·` line under the metric it qualifies |
| Disclosure or outage moved to notes | On the risks slide and in the recommendation |
| A positive pilot presented as production readiness | Readiness only with its gates met and cited |
| A gate due 3 March on slide 2 and "by end of March" on slides 1 and 8 | One date per condition everywhere; a summary line gives each condition's own date |
| A phase tagged `Decided today` or `Approved` before the meeting | `For decision today` or `Proposed` |
| Rollback on resolution and incidents only, while satisfaction is also reported | A trigger per reported metric ("satisfaction under 3.9 for 2 weeks"), or "monitored only" |
| "Sites B and C go live" in one phase | "Site B first; site C 4 weeks later if B holds its gates", or why both at once |

Result tiles hold two to four metrics: value under 18 characters, label under 70, source with
sample and window under 120.

## Money

Finance needs to judge the price against something. Show, on one slide:

- **Run-rate cost** from the price and the customer's volume (label the volume Reported when it is
  their estimate), monthly and annual, and what the price excludes (integration, support, the
  review effort that remains).
- **What it replaces or returns**, in the customer's own unit: hours, roles, cycle time, errors.
- **Net** (benefit minus cost) a year, as a range under the stated inputs, on a row for exactly
  the `scope:` being approved, with its volume base on the row ("Net, invoice line at two new
  sites, 14,000 invoices a month: $480k–$1.1M a year at $3–$6 an invoice"). Label it **Derived**.
  When the scope's volume is unknown, give the net at the volume you have, labelled for that volume
  ("pilot sites"), and a `Gap ·` for the scope's volume with its owner; never stretch a pilot
  base to the wider label. A wider-scope run-rate may follow as context, labelled as such.
- **Cash or capacity.** Say which: staff time freed is capacity, worth cash only if posts or
  overtime change; name what would turn it into cash. Tie it to any redeployment aim.
- **Sensitivities by name.** A corner not in the evidence (a lower rate elsewhere, half a reported
  cost) goes in a `Sensitivity:` row naming the input, so the evidenced figure stays the headline.
- **Payback or break-even** as a range from stated inputs. When a key input is missing (a loaded
  salary, a volume), give the break-even in that input ("pays back if it frees at least one
  staff-year at a loaded cost of $48k or more") or a short sensitivity across plausible values
  labelled Assumption, and add a Gap with the person who supplies the real number. Never present a
  saving that depends on an undecided headcount change as committed; show it as a scenario.

## Skeleton

Replace every `{{…}}`; `check_deck.py` flags any left. Delete a slide rather than fill it with
invented content.

```markdown
---
title: "{{Customer}}: {{pilot}} readout"
audience: "{{who is in the room}}; {{minutes}} minutes"
decision: "{{the go/no-go question}}"
asked: "{{the scope the room asked to decide, in its words}}"
goals:
  - "{{Who}}: {{their stated aim}}"
decision-makers:
  - {{role or name 1}}
  - {{role or name 2}}
deck-type: pilot-readout
scope: "{{exactly what today's ask approves: sites, lines, cohort}}"
---

<!-- shape: title -->
PILOT READOUT · {{SCOPE}}

# {{The answer: go, extend or stop, and its scope}}

{{The two or three results behind it.}}

Answer: {{yes to A; not yet to B, because …; back <when>}}.

*Source: {{pilot logs and audit, window}}*

---

<!-- shape: decision -->
THE DECISION

## {{Conditional go: two conditions before any new site goes live}}

- **{{Short name}}**: {{condition}}. Owner: {{role}}. By: {{date or anchor}}
- **{{Short name}}**: {{condition}}. Owner: {{role}}. By: {{date or anchor}}

Decided separately: {{headcount, pricing, anything not gating}}.
If no: {{what happens to the pilot sites and the next decision point}}.

<!-- notes: Say: {{why these and only these are gates}}. Point: {{the condition with the nearest date}}. Bridge: {{the result that earns the go}}. -->

---

<!-- shape: results -->
01 / RESULTS

## {{The pre-agreed gate was met: n% against a n% target}}

| Value | Metric | Label | Source |
|---|---|---|---|
| {{n%}} | {{metric, unit, against its gate}} | Measured | Source: {{system, sample, window}} |
| {{n}} | {{metric}} | Measured | Source: {{system, sample, window}} |

Labels: Measured, from pilot data · Reported, stated by your team · Assumption, ours · Proposal, our plan.

---

<!-- shape: next-steps -->
02 / DECISION TODAY

## {{Approve the conditional go today}}

- {{Action}}. Owner: {{decision-maker}}. Date: today
- {{Action}}. Owner: {{decision-maker}}. Date: {{anchored date}}
```

The closing slide in the full arc is an `ask` grouped by person:

```markdown
<!-- shape: ask -->
## {{Three decisions today unlock the first new site}}

### {{VP Operations}}
- {{Approve the gated rollout}}. Date: today

### {{CFO}}
- {{Agree the price in principle; share loaded cost so payback can be stated}}. Date: {{date}}

If no: {{what happens next and when the room meets again}}.
```
