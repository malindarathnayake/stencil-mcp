# Flowcharts, decision trees, state machines and hierarchies

> Use this guide for generic flowcharts, runbooks and troubleshooting trees, decision-analysis trees, simple state machines and lifecycles, product user flows, approximate value stream maps, and hand-laid hierarchies such as org charts, OKR trees, legal-entity charts and mind maps.

## Questions to ask first

Ask questions 1-5 for any flow. Then ask only the questions for the diagram type in the brief: decision tree 6, state machine 7, org chart 8, entity chart 9, OKR tree 10, user flow 11, value stream map 12. Ask them together in one round.

1. What starts the flow, and is there one entry point or several? (default: one entry, drawn as `presentation/start-end` with the trigger as its caption, such as "Alert fired")
2. What are the decisions, and what are all the outcomes of each one? (default: only the decisions the brief names, each with exactly the outcomes it states; nothing is invented to make the tree look complete)
3. What are the exit criteria, and how many distinct end states are there? For runbooks, who is the escalation target and after how long? (default: one end state for each outcome the brief names. If a path has no stated end, ask; do not add an escalation end state, retry count or contact the brief did not give)
4. Do any steps repeat, and what stops the loop? (default: no loops; if the brief implies a retry, one loop-back edge labelled with its exit condition as stated)
5. Do any steps run in parallel, and where do the branches rejoin? (default: none; strictly sequential)
6. Is this a troubleshooting tree or a decision-analysis tree with probabilities and payoffs? (default: troubleshooting tree with labelled yes/no or stated outcomes)
7. For state machines: what is the initial state, which states are terminal, what event and guard trigger each transition, and does any state react to an event without changing state? (default: the first state named is initial, no terminal state unless the brief names one, each transition labelled with its event only, no self-transitions)
8. For org charts and team topologies: how many levels deep, which people or teams appear, and are there dotted-line reports? (default: the levels and names the brief gives, primary reporting lines only, no dotted-line reports)
9. For legal-entity charts: what is the percentage on each link, is it voting or economic interest, which share class does it refer to, and is it a direct holding? (default: label each edge with the figure and basis exactly as stated; a missing figure is "% not stated" and a missing basis adds "basis not stated", never guessed)
10. For OKR trees: how many objectives, how many key results under each, and are initiatives in scope? (default: objectives and key results only, no initiatives)
11. For product user flows: which screens are in scope, and which error or abandonment paths should appear? (default: the happy path, plus only the error or abandonment paths the brief names)
12. For value stream maps: which process steps, and which wait times or cycle times are known? (default: steps with any stated cycle time in the card detail; waits drawn only where a duration is given)

## Push back when

- A decision has only one outgoing branch. Tell the user a decision needs at least two labelled outcomes; otherwise it is a step and will be drawn as one.
- A path never reaches an end state. Ask where it ends, because a runbook that stops mid-path leaves the reader with no next action.
- A loop has no exit condition. Ask for the condition, such as an attempt limit or timeout, because an unbounded retry is a defect in a runbook, not something the diagram should hide.
- Two transitions leave the same state on the same event with no guards to tell them apart. Tell the user the machine is ambiguous and ask for the guard that decides between them.
- Guards on one event, or branch labels on one decision, overlap or leave a gap, such as `[amount > 100]` and `[amount > 50]`, or "<50%", "50-90%" and "90%". Tell the user which values fall into two branches or into none, and ask for the boundaries.
- The brief asks for composite (nested) states, history states or orthogonal regions. Say this kit draws flat state machines only, and offer to split the sub-machine into a second panel linked by name.
- The brief asks for a decision-analysis tree. Say probabilities and payoffs go in edge labels and end-state captions exactly as given, and that Stencil does not compute or roll back expected values. Ask the user for any values they want shown.
- An org chart puts one person under two managers with solid lines. Ask which line is the primary report; the other becomes a dotted-line report.
- Stated holdings in one entity add up to more than 100 percent of the same share class on the same basis. Tell the user the figures conflict and ask which is correct before drawing.
- The brief asks for a funnel chart, an emotion or experience curve, progress bars, wireframe or screenshot thumbnails, or quantitative charts. Say Stencil has no shapes for these, and offer a step flow with numbers in labels or a separate charting tool.
- The user asks for a full value stream map with standard lean icons (push arrows, kanban, kaizen bursts). Say Stencil can only approximate one with step cards, timers and data stores, and confirm that is acceptable.

## How we draw it here

Direction:
- Flowcharts, runbooks, decision trees and state machines run top to bottom. This differs from the left-to-right default for architecture.
- The main path runs down one column, and branches go to the side.
- Loop-backs return up the side through explicit `points` waypoints, with `source_port` and `target_port` set so they never run over the main column.
- If the brief is mainly about who does what, use cross-functional swimlanes as described in DESIGN_SYSTEM.md, and copy from a department template.

Flowcharts and runbooks:
- Use `presentation/start-end` as a `symbol` node for each entry and each named end state, with a caption.
- Use `presentation/decision` as a `symbol` node with a question as its caption ("Disk above 90%?"), and label every outgoing edge ("Yes", "No").
- Draw ordinary steps as `component` cards using `presentation/process` with a verb-object label. Reserve `presentation/step` (a numbered step) for strictly linear walkthroughs with no branches.
- Draw a call to a sub-procedure documented elsewhere as a `presentation/process` card labelled "Run: <procedure>", with the document name in `detail`.
- Draw a parallel split and its join with `business/gateway-parallel` symbols (or `presentation/fan-out` and `presentation/fan-in`). Draw a merge of alternative branches into a shared step with `presentation/connector-junction`.
- Use `observability/alert` or `observability/incident` for a runbook trigger card, `business/ticket` for "open a ticket", `business/timer` for waits with the duration in the caption, `resilience/retry` and `resilience/timeout` for bounded loops, and `identity/admin` or `identity/group` for escalation targets the brief names.
- Show outcomes with `status/healthy`, `status/down`, `status/blocked` or `status/pending` symbols beside the end state.
- For decision-analysis trees, put each probability on its branch label and each payoff in the end-state caption, as given.

State machines:
- Draw every state, including the initial and terminal ones, as a `component` card with `presentation/process`.
- Add a small `presentation/start-end` symbol captioned "Start" with an unlabelled edge into the initial state, and an "End" symbol after each terminal state the brief names.
- Draw transitions as labelled `data` edges with the label "event [guard]".
- A self-transition needs `points` that take it out and back around one side, with different ports for the outgoing and return ends.

Hierarchies:
- Draw a top-down tree. You may call `layout_diagram` with `direction: "TB"` for starting positions, then adjust by hand.
- `layout_diagram` accepts at most 80 nodes and returns only `component` cards; change symbol nodes afterwards.
- Any cycle, including a single self-transition, makes `layout_diagram` fall back to a grid. Remove back edges and self-transitions before calling it, then add them back with `points`.
- A scene holds at most 200 nodes. Split larger org charts by division into separate diagrams.
- Org charts use `identity/user` for people, `identity/admin` for leadership roles where that reads naturally, and `identity/group` for teams.
- Primary reporting lines are solid `data` edges from manager to report. Dotted-line reports are `dependency` edges.
- Entity charts use `presentation/external-entity` for every entity, with the jurisdiction in `detail`. Mark external or minority holders by palette or group, not by a different icon. Put the percentage and basis on the edge label from owner to owned.
- OKR trees use `presentation/process` cards, with the metric and target in `detail`.

Mind maps:
- Place nodes by hand in a radial arrangement around a central topic card, joined by `dependency` edges with `route: "straight"` and no waypoints.

Product user flows:
- Use `presentation/process` cards named after each screen, `presentation/decision` for user choices, and `software/browser` or `compute/mobile` for the entry device. Do not show screen images.

Value stream maps:
- Use `presentation/process` cards with the cycle time in `detail`, `business/timer` between steps for waits, `presentation/data-store` for queues of work, and `feedback` edges for rework.

Edges, legend and footer:
- Edge meanings follow DESIGN_SYSTEM.md: `data` (solid) for the main flow and transitions, `control` for a hand-off to or from an external party, and `feedback` for rework or exceptions.
- Edge kind does not set colour, and `control` and `feedback` use the same dash. Set `palette: "orange"` on `control` edges and `palette: "red"` on `feedback` edges.
- Add a `legend` (up to 12 entries) whenever more than one edge meaning appears. Each entry needs `label` and `palette`, plus `dashed: true` for dashed or dotted kinds. In org charts, add one entry for primary reports and one for dotted-line reports.
- Use `footer` for the source, as-of date and owner of the runbook or chart, and `description` for a short narrative of the flow.

## Common mistakes

- Drawing a decision as a `component` card, or leaving its branches unlabelled.
- Inventing an extra end state, error path, retry count or escalation contact that the brief did not give.
- Drawing parallel steps as a sequence, or as an unlabelled decision.
- Drawing the initial state itself as a `presentation/start-end` terminator, so loop-backs to it look like the flow restarting.
- Loop-back edges that run straight up through the main column. Add waypoints and check with `preview_diagram`, because validation does not catch shared segments.
- Self-transitions with no `points` fail validation (`self_edge`). Add waypoints that take the edge out and back around one side.
- Feeding a cyclic state machine to `layout_diagram` and accepting the grid as if it were an order.
- Leaving `feedback` and `control` edges at the default blue, which makes them identical.
- Reaching for stand-ins when guessing: `ai/router` or `network/router` for a decision, `presentation/swimlane` cards instead of `lane` groups, `status/approved` in place of a named end state, `software/workflow` as a generic step, or `business/contract` as a legal entity.
- Using `physical` edges in hierarchies. They mean cables.
- Stacking more than about 12 cards in one column. Split the runbook into linked panels instead.
- Putting ownership percentages inside entity cards instead of on the edges, which loses which owner holds which share.

## Start from

No template yet; use `layout_diagram`.

For process diagrams organised by role, copy from the department templates: `it-change-approval`, `support-escalation`, `sec-incident-response`, `eng-platform-delivery`, `it-onboarding-access`, `fin-procurement-approval`, `hr-employee-onboarding` or `sales-lead-to-cash`. For request and response ordering between participants, use `sequence-request`.

Read alongside this guide: `brief` (confirming open facts) and `style` (visual rules).
