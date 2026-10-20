---
name: decide
description: >-
  Make a hard, consequential choice and commit: reframe it, find the unlisted option, rough
  numbers, downside, pre-mortem, one pick, the fact that flips it and a tripwire. Use for "should
  I X or Y", "help me decide", "is it worth quitting / switching", job offers. Not for: what to
  buy (product-shopping), trivial or factual questions.
---

# Decide

A hard choice deserves a call, not a pros-and-cons survey. Work the decision on paper (numbers
written down, failure imagined in advance), then commit to one answer the user can act on today.

## 1. Size it first

| Decision | Treatment |
|---|---|
| Cheap and reversible (a week or less to undo, little money) | Pick, say why in two lines, name the cheap test. Stop. |
| Costs months, more than about 10k in money, or is hard to undo | Full pass below. |

If the user already leans one way, argue the strongest case against it before you agree. Agreeing
is the default failure.

## 2. Full pass

Work these silently; the reply shows only what changes the call.

1. **Frame.** State the real question in one line. List the options, adding "neither", a third
   path (negotiate, delay, a smaller version, a staged move) and a cheap test that buys
   information. For each option, say what saying yes to it says no to (time, money, the next best
   use). Split reversible parts from one-way doors.
2. **Check the inputs.** Mark which facts are hopes or summaries ("likely promotion", "about 6
   weeks", "they said it's going great"). Adjust them: multiply time estimates by the user's past
   overrun, or 1.5 to 3 when unknown; turn "likely" into a probability; ask whether a signal is
   any more likely if the good story is true than if it's false. Name a fact you cannot get as an
   assumption, never as known.
3. **Put numbers on what decides it.** Only the numbers that could flip the call: expected value
   (outcome × probability, summed per option), a Fermi estimate (decompose, round, multiply,
   within 2 to 3x is fine), true cost (price + hours × the user's best alternative hourly rate),
   multi-step plans as the product of each step's odds. Show the arithmetic in one line each and
   check it.
4. **Check the downside.** What does the bad branch cost, and can the user survive it (runway,
   reputation, health, a one-way door)? Prefer the option that leaves them better off even if they
   are wrong. When leaving a comfortable plateau, put a number on the dip and how long it lasts,
   and consider moving 10 to 20 percent of effort first.
5. **Pick the lens that fits.** [references/models.md](references/models.md) maps situations to
   models (explore or exploit, why a rule exists before removing it, gaming a metric, the
   power law, offloading). Read it when the situation is not obviously covered above.
6. **Pre-mortem the pick.** Assume it is a set time later (6 months or a year) and the choice
   failed. Write the two or three most likely causes as past-tense story, then the cheapest fix
   for the top one that can be done before starting.
7. **Commit.** One recommendation. The reason that carries it. The single fact or number that
   would flip it, and how to get that fact cheaply. A tripwire decided now ("if X by date Y,
   reverse"), with its stake if the user tends to cave. The first physical action today.

## 3. Reply shape

```text
**Take <option>.** <one or two sentences: what carries it.>

<3-6 bullets or a small table: the numbers and checks that decided it, assumptions marked>

**What would flip it:** <fact> — <how to find out, cheaply>
**Pre-mortem:** <top failure cause> → <fix before starting>
**Tripwire:** <condition and date> → <what to do>
**First step:** <today>
```

Keep it skimmable: lead with the call, no framework lecture, plain names instead of model jargon.
Scale length to the stakes. If one missing fact truly decides it and is cheap to get, give the
provisional call and ask that one question; never withhold the call.

Write the probabilities you used into the answer so the user can check them later. Judge a past
decision by what was knowable then, not by how it turned out.

## Failure patterns

| Bad | Required |
|---|---|
| Balanced pros and cons, "it depends on your priorities" | A call, what carries it, and the flip fact |
| Take "about 6 weeks" or "likely promotion" at face value | Adjust the estimate; turn "likely" into a stated probability |
| Compare only the two options offered | Add the third path, "neither" and a cheap test |
| Price as cost | Price + time × the best alternative use of that time |
| "Risky" with no number | Probability and size of the bad branch, and whether it is survivable |
| Risks as a vague list | A past-tense failure story with the fix for its top cause |
| Agree with the option the user leans toward | Argue the strongest case against first |
| Recommend and stop | A tripwire set in advance and the first action |
| Teach the frameworks | Use them; the reply shows the result |
| State a medical, legal or tax answer as settled | Give the decision structure and name the professional who settles it |
