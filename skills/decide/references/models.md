# Decision lenses

Pick the lens by situation; use one or two, not all. Each gives the move and the trap.

## Contents

- [Situation map](#situation-map)
- [Lenses](#lenses)
- [Asking a model for help](#asking-a-model-for-help)

## Situation map

| Situation | Lens |
|---|---|
| Uncertain payoffs, comparing options | Expected value |
| Doubting a past choice because it turned out badly | Judge the decision, not the result |
| Many options, clients, projects or tasks | Power law |
| A plan with several steps that must all work | Chain law |
| Good but capped: a plateau, thinking of a pivot | Local vs global maximum |
| Sticking with what works vs trying new things | Explore or exploit |
| Removing a rule, process, guard or habit | Why the fence exists |
| Setting a goal, KPI or reward | Gaming the metric |
| How much a signal should move you | Strength of evidence |
| Sizing a market, effort or payoff | Fermi estimate |
| Do it yourself, hire it out, or automate | Offload rule |
| Any deadline or time estimate | Planning-fallacy multiplier |
| Decided, but the user will likely cave later | Commitment device |
| Inputs are dashboards, reports, summaries or advice | Check the ground truth |

## Lenses

**Expected value.** Per option: list outcomes, give each a value and a probability, multiply, sum.
The point is comparing options and leaving a falsifiable prediction, not precision. Positive
expected value only helps if the user can survive the variance; a small pile cannot take many
long-shot bets. Trap: falling back on gut because the inputs are uncertain.

**Judge the decision, not the result.** One outcome is one sample. A good decision that lost
should be repeated; a bad decision that won was luck. Trap: quitting a high-variance strategy (job
applications, outreach) after a few misses that its base rate predicted.

**Power law.** Most results come from a few inputs. Sort by result, keep and double down on the
top fifth, stop feeding the tail. Averages mislead here. Trap: spreading effort evenly, and missing
the concentration risk of one dominant client or income source.

**Chain law.** A plan's odds are the product of its steps' odds: three steps at 90 percent is
73 percent. Fix the weakest link first, then cut or merge steps. Trap: averaging step odds.

**Local vs global maximum.** Signs of a plateau: each improvement returns less, more input gives
no more output, and less skilled people on another path are ahead. Climbing higher means crossing
a dip. Put a number and a duration on the dip, then move 10 to 20 percent of effort to the new
path before moving the rest. Trap: fear of a certain small loss against an unclear larger gain.

**Explore or exploit.** A long horizon or declining returns favour exploring; a short horizon or
a fresh winner favours exploiting. Explore hard early, exploit a winner while it pays, explore
again when it decays. Trap: collecting new options forever, or milking one until it dies with
nothing next.

**Why the fence exists.** Before removing a rule, guard or step, find out why it was built: ask
the builder, read the history (commit log, old threads), or imagine a month without it. If it
still is not clear and removal is reversible, remove it and watch; if irreversible, leave it.
Usually ten minutes. Trap: treating "I don't see the point" as proof there is none.

**Gaming the metric.** A measure that becomes a target stops measuring. Name what the number is a
proxy for and pair it with a counter-metric that worsens when it is gamed (closed vs reopened,
speed vs errors, views vs watch time). Incentives predict behaviour better than intentions.

**Strength of evidence.** Ask how much more likely the evidence is if the claim is true than if
it is false. Work in odds and multiply: a 25 percent prior is 1:3, and evidence 9x likelier if
true gives 3:1, so 75 percent. Polite enthusiasm ("looks great, send details") is weak because it
shows up either way. Update one piece at a time.

**Fermi estimate.** Decompose, estimate each part, round hard, multiply. Within 2 to 3x is a
success; the aim is whether the idea is worth the next step of research.

**Offload rule.** Offload when (own hours × marginal rate) exceeds (price + supervision hours ×
marginal rate) by about 3x, leaving room for revisions. The marginal rate is what the best extra
hour earns, not income divided by hours. Do not offload the core work people pay for; an agent is
worth it only when checking its output is faster than doing the work.

**Planning-fallacy multiplier.** A plan is a best case. Multiply by the user's past ratio of
actual to estimated time on similar work; with no record, use 1.5 for small solo work and 2 to 3
for anything larger or dependent on others. Trap: "the feeling is the fallacy".

**Commitment device.** Decide while clear-headed, then restrict the later self: friction (make the
bad option physically harder), public commitment, or money at stake. The timing matters, not the
mechanism. Pair it with a tiny first action tied to a trigger ("when I sit down, I open the doc").

**Check the ground truth.** Dashboards, pipelines, reports, AI summaries and your own story are
maps. Before an expensive call, look at the underlying thing: the call recording, the raw data,
the customer.

## Asking a model for help

Asking "is this plan good?" invites agreement. Ask instead for the three strongest reasons a
sharp person would not do it, how many of 100 similar attempts succeed (and which reference class
that is), and a postmortem written six months after it failed.
