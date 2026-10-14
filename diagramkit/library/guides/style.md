# Shared design language

> Read this after the brief is confirmed and the topic guide is read, whenever you compose any diagram, split one into panels, or add status, so every output looks like one system.

## Questions to ask first

Ask these in one round, together with the topic guide's questions, and only when the brief leaves the fact open. Decide layout, colours and wording yourself.

1. What is the one thing the reader should understand from this picture? (default: the sentence I write from the brief, shown as the subtitle)
2. What is in scope and what is out of scope? (default: only the components, people and steps the brief names; anything else appears as a single slate "external" card or not at all)
3. Is this a comparison, such as before and after or option A against option B? (default: no; if yes, two side-by-side panels with the same components in the same positions)
4. Should the diagram show current state, and if so which component or step is in which state? (default: no status at all; I never invent a failure, warning or success)
5. Which relationship kinds matter for this story: physical links, data movement, control, feedback, dependency, tunnels or replication? (default: only the kinds the brief describes; no physical cabling on a logical or process diagram)
6. Are there boundaries the reader must see, such as trust zones, sites, accounts, teams or departments, and who owns each? (default: only boundaries the brief names)
7. Will it be printed in black and white or rendered in the monochrome theme? (default: no; light colour theme)

Only when the brief mentions specific hosts, products, versions or teams, also ask whether labels should carry those real names (default: role names, with the real name in the detail line).

## Push back when

- The user wants every component, link and flow in one picture for a page-width figure. Tell them it will not be legible at that size and offer two or more panels that share component positions.
- The user asks for status as decoration. A healthy, warning or down sign is a factual claim about state; ask which state is real, or leave status off.
- The user wants colour alone to carry meaning, such as "red means production". Colour does not survive monochrome output or colour-blind readers; every coloured element also needs a label or icon, and the meaning goes in the legend.
- The user wants a group box to show security, isolation or a namespace. A group in a scene is only drawing; say that the boundary is a label for the reader, and name the real enforcement point as its own card if it matters.
- The user wants nested containers to imply ownership chains (site contains rack contains host, department contains team). Groups are flat in the scene format; nesting is visual only, so the hierarchy must also be written in titles or captions.
- The user asks for more than 200 nodes, 40 groups, 400 edges or 12 legend entries. Those are hard limits; propose separate diagrams.
- The user wants a stretched or resized icon to show "bigger" or "more important". Symbols keep a fixed aspect ratio; show scale with labels, counts or a detail line.

## How we draw it here

**Theme and colour.** Light theme by default: white background, navy text, thin outlines and restrained pastel fills. Use `dark` or `monochrome` only when asked, and one theme throughout. Keep palette meanings consistent across a diagram set:

- `blue`: the primary subject and main flow (also the default for nodes, groups and every edge kind). `teal`: a secondary system, data tier or other in-scope component.
- `purple`: logical or overlay constructs such as tunnels. `orange`: control, policy and hand-offs to external parties.
- `yellow`: caution, pending or attention. `red`: failure, loss, threat or rework.
- `green`: healthy or success only, always paired with a status icon or label. `slate`: external, neutral or out-of-scope parties.

In `monochrome` every palette renders the same grey-blue, including card stripes, edges and legend swatches. Tell edges apart by kind (dash pattern) and labels only, and keep legend entries to ones a dash pattern or label can distinguish.

**Direction.** One primary direction per diagram: left to right for flows, requests, pipelines and processes; top to bottom for hierarchies and tiers (spine above leaf, control plane above workers, manager above team). Return paths and feedback run against the primary direction on a separate route.

**Spacing and text.** Leave 48 to 80 px outer padding, 60 to 100 px between cards and 24 px clear space around labels. Start content below about y = 120 and leave the bottom strip free for the legend and footer.

**Panels and display size.** Decide splitting yourself: assume document width unless the user says otherwise, and split when a panel passes about 28 elements or labels must shrink to fit. For comparisons use two `panel` groups of equal size side by side, keep shared components at the same relative positions, and highlight only what differs with palette and a short caption.

**Card anatomy.** A `component` card is icon, label and an optional `detail` line. The label states the role ("Primary database", "Approve request"); the detail adds one fact ("PostgreSQL 16, 2 replicas"). The icon signals the role only and implies no product, capacity or compatibility. Default card size is 200 x 146.

**Node kinds.**
- `component`: any real system, device, person or process step; the default.
- `symbol`: an icon without a card, for decisions, gateways, timers, start and end points and extra status signs. Default size is 144 x 112; set `w` and `h` when you want it small. Set `caption` for visible text, because `label` on a symbol is accessibility metadata only.
- `packet`: a numbered or labelled unit in transit in protocol explanations.
- `memory`: an ordered strip of receive or buffer slots (up to 32 cells).
- `text`: notes, callout bodies, panel headings and sequence anchors.
- `marker`: a small sign placed where something stops or completes.

**Edges.** Match the kind to the relationship: `data` (solid arrow) for requests, payloads and hand-offs; `control` (dashed) for policy, configuration and signalling; `feedback` for ACKs, responses and status; `dependency` (dotted) for depends-on; `tunnel` (long dash) for encapsulated or logical links; `replication` for copied data; `physical` (line, no arrow) for cables and circuits. `control` and `feedback` render with the identical dash, and `tunnel` and `replication` look almost the same, so whenever two non-solid kinds appear together give each kind its own explicit edge `palette`. Feedback reads as a return only because you draw it from the responder back to the requester; it still has a forward arrowhead. Use ports `n`, `e`, `s`, `w` to keep edges apart, `route: "orthogonal"` for flows and `route: "straight"` for fan-out between rows of a mesh. Add `points` waypoints for loop-backs and to steer around cards. Never route two edges along the same segment or through a card.

**Edge labels.** At most one short label per edge ("HTTPS", "nightly copy"). Move a crowded label with `label_x` and `label_y`. Longer explanation goes in a `text` note or a `presentation/callout` symbol.

**Groups.** `panel` is a solid-outlined section; `boundary` is a dashed outline for trust, ownership, site or account; `lane` is a full-width row for a role or team in a process. A node has at most one `group`, and groups have no parent. For visual nesting, list the larger group first and place the smaller rectangle fully inside it with room for both titles. Group boxes do not resize around children; size them yourself.

**Status.** For `down`, `blocked` or `pending`, set `state` on the `component` itself; the renderer draws the badge at the card's top-right with no extra node. For warning, expired, unknown, locked, unlocked, approved or healthy, add a `symbol` node using `status/warning`, `status/expired`, `status/unknown`, `status/locked`, `status/unlocked`, `status/approved` or `status/healthy` with `w` and `h` of about 24 to 28, placed just outside the card corner. A symbol placed on the card raises a `node_overlap` warning. Always set `state` on a `marker`: with no state it draws the down sign. `dropped`, `down` and `missing` draw the down sign, `blocked` and `pending` their own signs, and only `normal` or `received` the healthy sign.

**Title, legend and footer.** Every diagram has a one-line `title`, a one-sentence `subtitle`, a `description` narrative (it becomes the SVG description) and a one-line `footer` with scope and "as of"; put longer assumptions in `description` or a `text` note, because a wrapped footer is clipped at the canvas edge and a wrapped title runs into the subtitle. Add `legend` whenever more than one edge kind or a meaningful palette difference appears. Entries take `label`, `palette` and optional `dashed`, and every dashed entry draws the same dash, so legend palettes must match the edge palettes. The legend is one row that does not wrap; keep it narrower than the canvas (roughly label width plus 70 px per entry).

**Workflow.** Pass `layout_diagram` (direction `LR` or `TB`, up to 80 nodes, 200 edges) only forward edges: it accepts `id`, `asset`, `label`, `detail` and `palette`, makes every node a 200 x 146 `component`, and any cycle (for example a feedback or ACK edge) switches it to an unordered grid. Afterwards add return edges, symbols, text, packets, markers and groups, and replace its placeholder subtitle. Run `validate_diagram` and read every warning; it does not check title, legend or footer overflow. Render with `render_diagram` and check with `preview_diagram` (widths 400 to 1800, needs the optional CairoSVG); if preview is unavailable, open the SVG in a browser at publication width. Export with `export_diagram` as both `.svg` and `.scene.json`.

## Common mistakes

- Mixing directions, so half the flow reads left to right and half top to bottom.
- Several dashed edge kinds left on the default blue, so control, feedback, tunnel and replication cannot be told apart.
- A legend whose palettes do not match the edges, or a legend in monochrome that is a row of identical swatches.
- Long sentences as edge labels, or two labels on one edge; use a note instead.
- Putting a visible name in a symbol's `label` and getting an unlabelled icon; use `caption`.
- A `marker` with no `state`, which draws a failure the brief never mentioned.
- A full-size 144 x 112 status symbol on top of a card instead of `state` on the component or a small symbol beside it.
- Feeding feedback edges to `layout_diagram` and getting a grid instead of a flow.
- Child cards overlapping the group title because the group was not sized for them.
- Parallel edges drawn on the same route, which reads as one link.
- A wrapped title or multi-line footer that overlaps the subtitle or falls off the canvas.
- Using red or green for ordinary components, so colour no longer signals failure or health.
- Shrinking a crowded diagram instead of splitting it, then never checking it at publication size.
- Treating a clean `validate_diagram` result as proof the picture matches the brief.

## Start from

Call `list_templates` and start from the closest template with `get_template`; fall back to `layout_diagram` only when none fits. Read `brief` first and this guide alongside the topic guide for the diagram type.
