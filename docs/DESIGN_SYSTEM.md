# Diagram composition rules

## Start with meaning

Write one sentence saying what the reader should understand. Identify the real
entities, ownership/trust boundaries, and relationship types before positioning
anything. An icon represents a role; it does not establish compatibility, trust,
redundancy, delivery guarantees, or an operational configuration.

Use generic symbols with explicit labels. Product terms are search aliases, not
vendor endorsements or official logos. A GPU icon can be labelled with a real GPU
model; the icon alone says nothing about memory capacity or supported software.

## Confirm the brief before drawing

A diagram can pass validation and still be wrong, because it answers a different
question. The usual failure is a plausible stand-in: the brief leaves a fact open,
and the drawing fills it with the common pattern instead of the user's design. Do
not do that.

Before placing anything, write two short lists: the facts the brief states, and
the facts it leaves open. Ask the user about every open fact that would change the
topology or the story:

- which components exist, how many, and where they sit (rack, site, zone, lane);
- which links exist, between what, and how many per device;
- what runs over each link and how (routed or switched, ECMP or multipath,
  replication, encryption);
- what is redundant, and what is deliberately a single point of failure;
- who owns each boundary, and what is in or out of scope.

Ask in one round: a few numbered, concrete questions, each with the default you
would otherwise use, so the user can answer "yes to all" or correct one. Do not ask
about layout, colours or wording; decide those yourself.

Push back when the brief conflicts with how a technology works. For example, iSCSI
is not hashed over ECMP routes; it multipaths with MPIO across separate paths. Say
what looks wrong and ask which the user means. Do not silently draw the request as
written, and do not silently "correct" it either.

Do not add components the user did not mention (management nodes, an extra
firewall, a load balancer) because a typical design has them. If you think one is
missing, ask.

If the user says to proceed without answering, proceed, but list every assumption
in your reply and keep the scene `description` consistent with them.

Before exporting, reread the brief and check each stated fact against the rendered
picture. Passing validation does not mean the diagram matches the brief.

## Agent workflow

1. Confirm the brief (section above). Ask before composing; do not guess.
2. Call `library_info` and `get_guidelines` once.
3. Search for roles using `search_assets`; retrieve metadata only for chosen IDs.
4. Start with `get_template`, or use `layout_diagram` for initial graph positions.
5. Keep the editable scene JSON. Change the scene, not arbitrary generated SVG text.
6. Call `validate_diagram`; fix errors and inspect every warning.
7. Render the SVG and visually inspect it at publication size. Use PNG preview
   when available. Check labels, arrows, crossings, groups and the technical story.
8. Reread the brief and check every stated fact against the picture.
9. Export both `.svg` and `.scene.json`. A repeatable source is part of the deliverable.

Do not load all 300 SVGs into model context. Search returns compact metadata;
`get_asset(include_svg=true)` is for individual asset bodies. The scene compositor
loads registered assets directly, so the model normally needs only their IDs.

## Style

White background, navy text, thin outlines, restrained pastel fills. The kit also
supports dark and monochrome output. Use one theme throughout a diagram. Use
legible system sans-serif fonts; font files are not bundled or fetched remotely.

Prefer left-to-right architecture flow. Use 48–80 px outer padding, at least
60–100 px between cards, and 24 px or more of clear space around labels. Keep
headings short. For blog-width output, avoid large topology diagrams squeezed into
small figures. Split into two or more panels instead of shrinking all the text.

Default card size is 200 × 146 px. Component labels are 17 px; detail text is 12 px.
Those are SVG canvas units, not a promise of readability after arbitrary scaling.
Publication previews must be inspected at their intended displayed size.

Do not stretch symbols. Keep the native aspect ratio. Each symbol has a 144 × 112
viewBox and normalized north/east/south/west anchors on its enclosing bounds.
These are diagram connection points, not a hardware interface inventory.

## Connector meanings

| Kind | Default appearance | Use |
| --- | --- | --- |
| `physical` | Solid line, no arrow | Cable, circuit, or physical reachability |
| `data` | Solid arrow | Request, payload, or explicit data movement |
| `control` | Dashed arrow | Policy, configuration, signalling |
| `feedback` | Dashed return arrow | ACK/SACK, response or status feedback |
| `dependency` | Dotted arrow | Depends-on relation, not packet delivery |
| `tunnel` | Long-dashed arrow | Logical/encapsulated connection |
| `replication` | Dash-pattern arrow | Replicated data |

Use a legend when mixing meanings. A bidirectional physical link is normally a
line without arrows; arrows are appropriate when you are specifically explaining
traffic direction. A trust boundary is a labelled container, not a security control.

Ports may be explicit (`source_port`, `target_port`: `n/e/s/w`). `points` supplies
ordered waypoints between endpoint anchors. The renderer does not provide a
full obstacle-avoiding routing engine. Add waypoints when an edge crosses a card.
Use `label_x` and `label_y` to move a connector label away from a busy crossing.

For spine-leaf, mesh and dual-homed topologies, draw every physical link as its
own line, and use `route: "straight"` so links fan out between rows. Never route
two different links along the same segment: a shared line reads as one cable, bus
or layer-2 segment, which is a different topology. Validation does not catch this;
check it visually.

## Packet and failure explanations

Keep physical paths distinct from traffic drawn over those paths. Do not make
an unutilized ECMP path disappear. Different hash inputs can still choose the same
next hop; illustrative ports are not a universal mapping to path A/B/C/D.

Out-of-order arrival and loss are different conditions. A delayed packet can
arrive later without a retransmission. A dropped original must terminate at a
visible loss marker; do not simultaneously draw it reaching the receiver.

The MRC teaching template consistently uses packets 1–5:
- Arrival order: 1, 3, 5, 2. The original packet 4 is lost.
- Receive memory: 1, 2, 3, gap, 5.
- Feedback: “Have 1, 2, 3, 5 — missing 4.”
- A separate recovery panel retransmits only 4, then shows complete receive memory.

This is explanatory notation, not a byte-accurate SACK encoding or an implementation
of a retransmission timer. A receive gap alone does not prove a packet is lost.
Memory placement is not by itself an application-completion notification.

## Process and department diagrams

Use cross-functional swimlanes for business processes. A lane is a role or team,
never a task. Draw lanes as `group` entries with `style: "lane"`, stacked full
width in a fixed order, and place each step with `group` set to its lane. Time
runs left to right; keep one step per column so cross-lane edges stay readable.

- Tasks are `component` cards with a verb-object label ("Approve request") and the
  owner or system as `detail`. Use the `business` and `fleet` assets where they fit.
- Decisions use `presentation/decision` as a `symbol` node with a question as its
  `caption` ("Approved?"). Label every outgoing branch ("Yes", "No").
- Parallel work uses `business/gateway-parallel` to split and again to join.
- Start and end points use `presentation/start-end` with a caption that names the
  trigger or outcome ("Offer accepted", "Paid"). Name every distinct end state.
- Waits and SLAs use `business/timer` with the duration in the caption.
- Connector meanings: `data` (solid) for the process flow, `control` (dashed,
  orange) for a hand-off to or from an external party, `feedback` (dashed, red)
  for rework or exceptions. Add a legend whenever more than one meaning appears.
- Give each edge its own port when two edges would otherwise share a segment;
  set `source_port`/`target_port` explicitly and add waypoints for loops.
- Write `description` as a short narrative of the flow; it becomes the SVG `<desc>`.

This is BPMN-lite flowchart notation, not BPMN-conformant modelling, and there is
no BPMN XML export. The eight department templates (`eng-platform-delivery`,
`sec-incident-response`, `it-onboarding-access`, `fin-procurement-approval`,
`hr-employee-onboarding`, `sales-lead-to-cash`, `it-change-approval`,
`support-escalation`) are worked examples to copy from.

## Security and agent diagrams

Name the actual enforcement point. Keep identity provider, policy decision,
policy enforcement, logging and the protected service separate when their
relationship is the point of the drawing.

For an agent and MCP tools, label read-only access separately from mutation.
Show approval before privileged actions. Do not draw the model with unrestricted
database access unless that really is the architecture being described.

## What validation does and does not cover

Validation checks the package's scene schema, IDs, known assets, group membership,
canvas bounds, approximate text fit, node overlaps, edge-to-node crossings and
connector-label overlaps. Density warnings account for split panels.

It does not prove protocol semantics, product support, authorization safety,
physical redundancy, flow reachability, line-to-line crossing clarity, shared
line segments, precise font metrics, or whether the diagram matches the brief. Group-title/caption collisions and title/footer/legend fitting still
need visual review. Passing validation is not publication approval.
