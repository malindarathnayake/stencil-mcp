# Business process swimlanes (BPMN-lite)

> Use this guide when the user wants a cross-functional process drawn as lanes per role, such as approvals, onboarding, escalation, change control, incident runbooks, dispatch or any step-by-step departmental workflow.

## Questions to ask first

Ask only the questions the brief leaves open. If the user says "just draw it", use the defaults and state them in the footer.

1. Which roles or teams take part, and in what order should their lanes appear from top to bottom? (default: the initiator's lane on top even when it is external, such as a customer or candidate; then each internal role in the order it first acts; other external parties such as vendors at the bottom)
2. What event starts the process, and where does this drawing stop; are upstream or downstream processes in scope? (default: a single start named after the obvious trigger, running to the first final outcome, with neighbouring processes shown only as a hand-off)
3. What does each role actually do, step by step? (default: only the steps stated in the brief; no extra reviews, notifications or checks are added)
4. Where are the decisions, and what are all of their outcomes? (default: a two-way Yes/No decision at each point the brief names a choice, and nothing else)
5. Are there approval thresholds or delegation-of-authority limits, and who approves above each one? For each limit: is it inclusive (≥) or exclusive (>), in which currency, before or after tax, and per transaction or cumulative? Who approves when the named approver is unavailable? (default: no threshold; one approver as stated in the brief, with no delegate)
6. Do any steps run in parallel and must all finish before the process continues, or do only some branches run depending on conditions? (default: steps run in sequence)
7. Are there waiting periods, SLAs or time-outs, and what happens when one expires? (default: no timers)
8. What happens when something is rejected, fails or does not match: is it sent back for rework, escalated or ended? (default: a rejection ends the process at a named end state; it is not looped back)
9. Where documents are matched, which ones are compared: a two-way match (purchase order and invoice), a three-way match (adding the goods receipt), or evaluated receipt settlement with no invoice? (default: whatever the brief names; no matching step is added)
10. What are all the possible end states? (default: one success end plus one end for each rejection or failure branch the brief mentions)
11. Which steps does a system perform rather than a person, and should systems get their own lane? (default: systems appear as the `detail` of a task, not as lanes)
12. Is this the documented policy or a description of what happens today? (default: an illustrative process, stated as such in the footer)

## Push back when

- The user asks for BPMN XML, pools, message events or boundary events. Tell them Stencil draws BPMN-lite flowcharts and has no BPMN export. A hand-off to another organisation is drawn as a `control` edge into that party's lane, and a time-out as a decision after the task with an expiry branch.
- The user wants a full approval matrix, RACI chart or delegation-of-authority table inside the diagram. Tell them a matrix is better kept as a table next to the diagram; the diagram shows only the thresholds that change the path, as decision captions.
- A parallel split is requested for an either/or choice. A parallel gateway means every branch happens and the join waits for all of them; an either/or choice is a decision.
- A decision has only one outgoing branch, or a branch that leads nowhere. Ask what happens on the other outcome; every branch must reach a step or a named end.
- The same person submits and approves their own request when the brief also describes a separation-of-duties control. Point out the conflict and ask which is correct.
- A procure-to-pay flow pays the invoice before it is matched, or calls a step a three-way match while it compares only two documents. A three-way match compares the purchase order, the goods receipt and the invoice. A two-way match or evaluated receipt settlement is legitimate when the user says so; then name the step accordingly.
- An incident response runbook restores service before the threat is contained. Common incident handling guidance (for example NIST SP 800-61) puts containment before eradication and recovery; ask whether the order is intentional.
- An offboarding flow removes access only after final pay or long after the leaving date. Point out that the person keeps access in the meantime and ask whether that is the intended policy.
- An emergency change is drawn as skipping approval entirely. ITIL-style processes normally use an emergency change authority (an emergency CAB, or ECAB, in ITIL v3) and a review afterwards; ask which applies.

## How we draw it here

- Lanes are `group` entries with `style: "lane"`, stacked full width in a fixed order, one lane per role or team. A lane is never a task, phase or system. Every external lane uses the `orange` palette and "(external)" in its title, for example "Vendor (external)".
- Time runs left to right. Each step sets `group` to the lane of the actor who performs it; a decision sits in the lane of the role that makes it. When a system performs a step on its own and systems have no lanes, put the step in the lane of the role that owns or configures that system and name the system in `detail` ("Auto-approve", detail "ERP").
- Keep one step per column so cross-lane edges stay readable. Exception: the branches between a parallel split and its join, and the alternative branches of one decision, may share a column. Route their edges through different ports so segments do not overlap.
- Tasks are `component` nodes with a verb-object `label` ("Approve request") and the owner or system as `detail`. Pick the asset by what the step handles:
  - `business/form` for requests and requisitions, `business/approval` for approve steps, `business/rejection` for reject steps, and `business/purchase-order`, `business/invoice`, `business/payment`, `business/contract`, `business/report`, `business/email`, `business/calendar`, `business/chat` and `business/vendor` for those artefacts or parties.
  - `business/ticket` for tickets, change requests and support cases; `observability/incident` and `observability/alert` for incident and on-call steps; `observability/audit-log` for checks, matches and records such as a goods receipt.
  - `identity/user`, `identity/admin`, `identity/group` and `identity/privileged-access` for account and access provisioning; `security/security-review` and `security/quarantine` for review and containment steps.
  - `fleet/dispatcher`, `fleet/vehicle`, `fleet/maintenance-bay` and `fleet/coaching-session` for dispatch and field-service work.
  - `presentation/process` or `presentation/step` when no specific asset fits.
- Decisions are `symbol` nodes using `presentation/decision`, with the question as `caption` ("Approved?", "≥ $5,000?"). Write thresholds with the exact operator. Label every outgoing edge ("Yes", "No", "P1").
- Parallel split and join are both `symbol` nodes using `business/gateway-parallel`. There is no inclusive gateway. Draw a "one or more of these" choice as a separate Yes/No decision for each optional branch, name the condition on each, and rejoin before the next common step.
- Start and end points are `symbol` nodes using `presentation/start-end`. The start caption names the trigger; each end caption names the outcome ("Paid", "Rejected", "Backed out"). Every distinct outcome gets its own end.
- Timers are `symbol` nodes using `business/timer`, with the duration as `caption` (two lines at most). A mandatory delay sits inline in the flow ("After 30 days"). An SLA or time-out races the task, so do not put it inline. Draw a decision after the task ("Done within 48 h?") with a "No: expired" edge to the escalation or end, and place the timer beside the task to show the duration.
- To annotate a step, set the component's `state` to `pending`, `blocked` or `down` for a corner badge, or place a `symbol` node with a status asset (for example `status/approved`, `status/expired`) next to it. A `marker` node ignores `asset` and draws only down, blocked, pending or healthy from its `state`. Status icons never replace end states.
- Edges: `kind` sets only the dash pattern, and colour comes from `palette` (blue when unset). Process flow is `kind: "data"`, blue. A hand-off to or from an external party is `kind: "control", palette: "orange"`. Rework, returns and exceptions are `kind: "feedback", palette: "red"`. Control and feedback share the same dash, so give every one a text label ("Send PO", "Revise") that tells them apart without colour. Set `source_port` and `target_port` so two edges never share a segment, and add `points` for rework loops that run back to the left.
- Add a `legend` whenever more than one edge meaning appears: "Process flow" (blue), "Hand-off with an external party" (orange, dashed), "Rework or exception" (red, dashed).
- Add a `footer` stating that the process is illustrative and that thresholds and timings are examples, unless the user confirms it is their documented policy. Write `description` as a short narrative of the flow.
- Split very long processes by phase into two or more scenes or panels instead of shrinking the text.

## Common mistakes

- Making lanes for tasks, phases or systems instead of roles, or putting a step in the lane of the person who receives it rather than the one who does it.
- Inventing steps the brief did not state, such as an extra manager approval, a legal review or a notification email.
- Leaving a decision branch unlabelled, or letting a "No" branch stop mid-canvas without an end state.
- Using one generic "End" for every outcome, for example one "Closed" for both a successful and a backed-out change.
- Drawing rework as a forward `data` edge instead of a `feedback` edge looping back to the step being redone.
- Setting `kind: "control"` or `"feedback"` without a `palette`, which renders blue and no longer matches the legend.
- Using `presentation/decision` for a parallel split, fanning out to several steps with no gateway, or splitting and never joining.
- Forcing a "one or more" choice into a parallel split (every branch runs) or into one decision (only one branch runs).
- Drawing an SLA as an inline timer, which reads as "wait 48 h, then continue".
- Picking stand-ins when guessing: `presentation/callout` or `presentation/note` as a task, `status/pending` or a `marker` node instead of `business/timer`, a `status` asset as a task component, `presentation/swimlane` as a node instead of a `lane` group, or `identity/user` for every step.
- Staggering parallel branches across columns, which implies an order that does not exist. The opposite mistake is stacking unrelated steps in one column so cross-lane edges overlap.
- Drawing a hand-off to an external party as a plain `data` edge, so the boundary of responsibility is lost.
- Writing thresholds and SLAs as policy facts when the user gave none; mark them as examples in the footer or ask.

## Start from

Each template below has known gaps. When you copy one, fix the gaps listed for it.

- `fin-procurement-approval` for procure-to-pay, expense approval and purchase thresholds. It has no goods-receipt step, so add "Record goods receipt" before the three-way match (or rename the match as two-way). Also add a "CFO approved?" decision with a "Rejected" end.
- `hr-employee-onboarding` for onboarding and hiring pipelines. Its new-hire lane is not marked external and its contract hand-offs are `data`; use "(external)" and `control` until the start date. There is no offboarding template; reuse these lanes and revoke access on or before the leaving date.
- `sales-lead-to-cash` for lead-to-cash and order-to-invoice flows.
- `it-change-approval` for change approval and CAB. Add a "Rejected" end off "Approved?" and a separate "Backed out" end. It has no emergency path; add an "Emergency?" decision, an emergency approval step and a later review when needed.
- `it-onboarding-access` for new-hire access provisioning. Its "HR system" lane is a system, so rename it to the HR role. Add parallel split and join gateways around laptop and group provisioning, add a rejection branch on privileged access, and replace `status/approved` on "Verify first login" with a real task asset. It has no access-removal steps.
- `support-escalation` for tiered support and ticket lifecycle. Its "Respond within 8 h" timer has no incoming edge and acts as a second start. Redraw it as an SLA decision after the L2 hand-off with an escalation branch, and replace `presentation/note` and `identity/user` tasks with `business/ticket` or `presentation/process`.
- `sec-incident-response` for security incident response runbooks. Its parallel split has no join and the update-cadence timer leads nowhere; add a join and route the timer into it. Rename the "Detection" lane to a role, for example "Security monitoring", and replace the `presentation/note` review with `business/report`.
- `eng-platform-delivery` for pull-request-to-production flows owned by several teams.
- Dispatch or field service, warehouse fulfilment and asset lifecycle have no template yet; copy the lane structure of the closest template above. `layout_diagram` makes every node a `component`, creates no lanes, and falls back to a grid when the flow has a rework loop. Use it only for rough first placement, then add lane groups, set `group`, convert decisions, starts, ends, timers and gateways to `symbol` nodes, and re-place nodes by lane and column.

Read alongside: `security-architecture` for incident response and access-control steps, `devops` for delivery flows, `observability` for alerting and on-call, and `security-architecture` for identity, provisioning and access reviews. Call `get_template` for the chosen template, then `validate_diagram` and `preview_diagram` before exporting.
