# Discovery narrative

## Contents

- [Use it for](#use-it-for)
- [Workflow](#workflow)
- [Rules](#rules)
- [Skeleton](#skeleton)

Turn discovery into a decision, not a transcript summary.

## Use it for

Customer discovery synthesis, opportunity framing, an executive recap of interviews and workflow
observations, or deciding whether an opportunity is worth a validation step. Usually 5–7 slides,
with the decision (run the test or not, and on what terms) on slide 1 or 2.

## Workflow

1. Establish the audience, the decision, the workflow in scope and the time horizon. Ask for
   permissioned notes with dates, participant roles, the observed workflow and any contradictory
   observations.
2. Build the **evidence ledger** before any slide: claim, source locator, observed or inferred,
   confidence limits, counterexample. Repeated hearsay is one source, not several. Keep customer
   and participant identifiers out unless authorised.
3. Arc: current workflow → friction → impact → bounded opportunity → validation plan → decision.
4. Recommend the **smallest experiment that could disprove the opportunity**: baseline collection,
   success and stop criteria, what it costs the customer in people-days, an accountable owner and
   a target date. A commitment only the room can make is the ask itself ("Ops lead: name two
   operators for a week of timings"); never assign real people without authority, and never show
   `TBD` on a slide.
5. Keep nuance and counterevidence in notes, but decision-changing caveats stay on the slide.
6. List unresolved evidence gaps outside the deck.

## Rules

| Bad | Required |
|---|---|
| "Search wastes 40% of operator time" with no timings collected | "Impact not yet measured" and a baseline step in the plan |
| A quote assembled from two interviews | Quotes only verbatim from a cited note, or no quote |
| Two operators who disagree merged into one finding | Both observations kept, the disagreement shown |
| "Customers want X" from one interview | Scope stated: "1 of 2 operators, 2026-08-02" |
| An operator's estimate ("takes about an hour") shown as a finding | **Reported** · with who said it; a timing study measures it |
| A stakeholder asks for a stronger story than the notes support | Keep the uncertainty; offer the experiment that would earn the stronger claim |

Never invent quotes, sample sizes, savings, benchmarks or customer names.

## Skeleton

Replace every `{{…}}` (`check_deck.py` flags any left); delete a slide rather than fill it with
invented content.

```markdown
---
title: "Discovery: {{workflow}} worth a bounded test"
audience: "{{decision owner and workflow team}}"
decision: "Whether to run {{the smallest test}}"
decision-makers:
  - {{decision owner}}
  - {{workflow lead}}
deck-type: discovery-narrative
---

<!-- shape: title -->
DISCOVERY · {{WORKFLOW}}

# {{Run a two-week test of X to size the friction operators report}}

{{What the notes show, and what we ask today.}}

*Source: {{which notes, dates and participant roles}}*

---

<!-- shape: decision -->
THE DECISION

## {{Approve a two-week baseline before any build}}

- {{Name the operators who will log timings}}. Owner: {{workflow lead}}. By: {{date}}
- {{Agree the success and stop criteria}}. Owner: {{decision owner}}. By: {{date}}

If no: {{what stays as is, and what would reopen the question}}.

---

<!-- shape: findings -->
01 / WHAT WE KNOW

## {{Both operators named search and disagree on its cost}}

- **Reported** · {{an observed step, in the participant's terms}}. *Source: {{note, role, date}}*
- **Reported** · {{a counterexample or disagreement}}. *Source: {{note, role, date}}*
- **Assumption** · {{the inference drawn, stated as unvalidated}}
- **Gap** · {{what no one has measured; who could}}

Labels: Measured, from data · Reported, stated by a participant · Assumption, ours · Proposal, our plan.

---

<!-- shape: comparison -->
02 / THE OPPORTUNITY

## {{A reversible test beats building now}}

### Current workflow
{{Known steps, constraints and friction; impact unquantified without a baseline.}}

### Smallest test (recommended)
{{A reversible change, its cost in people-days, non-goals, what would invalidate it.}}

---

<!-- shape: ask -->
03 / THE ASK

## {{Two commitments today start the test on a date}}

### {{Decision owner}}
- {{Approve the test and its stop criteria}}. Date: today

### {{Workflow lead}}
- {{Name two operators for a week of timings}}. Date: {{date}}

If no: {{what happens instead}}.
```
