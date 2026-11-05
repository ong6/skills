# Technical architecture

## Contents

- [Use it for](#use-it-for)
- [Workflow](#workflow)
- [Rules](#rules)
- [Skeleton](#skeleton)

Explain a system's responsibilities and boundaries before naming products.

## Use it for

Solution architecture decks, integration proposals, data-flow explanations, security-boundary
reviews and technical trade-off presentations. Usually 5–8 slides: the decision and its conditions
(slide 1 or 2), constraints, architecture, boundary and failure findings, alternatives, validation
steps, an ask per decision-maker.

## Workflow

1. Identify the audience, the decision, existing systems, constraints, the identity model, the
   deployment boundary and non-goals. Ask for the missing constraints that would change the
   design; mark the rest as assumptions.
2. Build the **fact inventory**: each supplied fact with a source locator and date, and each
   component marked existing, proposed or unknown.
3. Trace **one representative request end to end**: caller, identity, authorisation, data
   retrieval, processing, response, audit. Cover sensitive data movement, retention, deletion,
   tenant separation and external egress, and name the component that enforces each boundary.
4. Draw the flow as a linear `architecture` slide of at most five stages (three or four reads
   best): `1. **Stage** — responsibility and trust boundary`. Branches, async paths and failure
   routes (queues, dead letters, retries) get their own slide; adjacency on a slide must never
   imply an integration nobody verified.
5. Compare viable alternatives, including the current approach, on the same criteria: security,
   operational ownership, failure handling, reversibility, effort, cost assumptions. Say why the
   recommendation is conditional.
6. State timeout, retry, idempotency, fallback or abstention, observability and rollback behaviour
   where relevant. Missing access enforcement is a **blocking design gap** on a slide, not prose.
7. Close with validation actions and one specific approval request per decision-maker (security,
   platform, budget holder), each with a date. Integration effort the customer carries is costed in
   people-weeks or stated as a Gap with who will size it.

## Rules

| Bad | Required |
|---|---|
| "Sub-100 ms p95" with no workload data | "Latency target: proposal; workload volumes unknown" |
| "SOC 2 compliant" inferred from a vendor logo | Certifications only from a cited document, else unknown |
| Retrieval before the authorisation check in the flow | Authorise tenant and role before any data is read |
| A fork drawn as a straight line to fit the shape | Main path on one slide, the branch and failure path on the next |
| "Integration tested" with no test run | "Integration not yet tested" plus a validation action |
| A vendor's stated limit ("handles 500 rps") as fact | **Reported** · with the document and date; **Measured** only from a test run |

Stage names under about 35 characters and details under about 180; with five stages, details under
120 or split. Two options compare best (55 words each at most); three options, 35 words each.

## Skeleton

Replace every `{{…}}` (`check_deck.py` flags any left).

```markdown
---
title: "Architecture: {{system}} for review"
audience: "{{platform, security and delivery owners}}"
decision: "Approve {{a testable design}} for {{the next step}}"
decision-makers:
  - {{security lead}}
  - {{platform lead}}
deck-type: technical-architecture
---

<!-- shape: title -->
ARCHITECTURE · {{SCOPE}}

# {{Approve a read-only design: access is checked before any data is read}}

{{The workload, the trust model and the non-goals in one sentence.}}

*Source: {{supplied constraints, with dates}}*

---

<!-- shape: decision -->
THE DECISION

## {{Approve the design for a test, with two conditions}}

- {{Tenant boundary test passes}}. Owner: {{security lead}}. By: {{date}}
- {{Workload volumes supplied}}. Owner: {{platform lead}}. By: {{date}}

If no: {{what we change and when we return}}.

---

<!-- shape: architecture -->
01 / REQUEST FLOW

## {{Every boundary has one enforcing component}}

1. **Caller** — authenticate identity; define caller trust
2. **Access boundary** — authorise tenant and role before data retrieval
3. **Processing** — scope data; timeout and fallback
4. **Response and audit** — provenance; minimal retained data

*Source: Proposal, to validate against the system contracts*

<!-- notes: retention and deletion, retry and idempotency, monitoring, rollback. Branches go on the next slide. -->

---

<!-- shape: table -->
02 / RISKS

## {{Two unknowns could change the design, each with an owner}}

| Item | Why it matters | Next step | Owner |
|---|---|---|---|
| {{Runbook ACLs narrower than tickets}} | {{could leak runbook text}} | {{filter at retrieval}} | {{security lead}} |
| {{Volumes unknown}} | {{sizing and cost}} | {{share last month's peak}} | {{platform lead}} |

---

<!-- shape: ask -->
03 / THE ASK

## {{Two approvals start the test}}

### {{Security lead}}
- {{Review the tenant-boundary test plan}}. Date: {{date}}

### {{Platform lead}}
- {{Share peak volumes and approve the test environment}}. Date: {{date}}

If no: {{what we change and when we return}}.
```
