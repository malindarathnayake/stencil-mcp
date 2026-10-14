# Service blueprints and customer/user journeys

> Use this guide when the diagram follows a customer, user or employee through a service, either as a journey map (the person's view only) or as a service blueprint (frontstage, backstage and support work as well).

## Questions to ask first

1. Is this a customer journey map (the person's view only: stages, actions, touchpoints, optional rating row) or a service blueprint (adds frontstage, backstage and support lanes)? (default: journey map when the brief says "journey map" or "user journey"; blueprint when it names backstage teams or systems)
2. Who is the persona, and what are they trying to get done? (default: one generic customer with the single goal named in the brief; no second persona)
3. Where does the scenario start and end, and is it one episode or the whole relationship? (default: one episode, from the first contact named in the brief to the moment the customer has the outcome)
4. Which channels does the person use: web, mobile app, email, chat, phone, a physical store or a human agent? (default: only the channels the brief names)
5. Which stages should appear, and in what order? (default: stages taken from the steps in the brief; if it gives none, Discover, Start, Use, Finish, capped at eight; a "Get help" stage only when the brief mentions support, failure or escalation)
6. Is this the current state or the target state? (default: current state, said in the subtitle; a target state goes in a separate diagram)
7. Which backstage roles and support systems take part, and who owns each backstage step? (default: only the roles and systems the brief names; a stage with none named keeps its backstage and support cells empty)
8. Should the diagram show only the happy path, or also failure and exception branches, drop-outs and channel switches? (default: happy path plus only the exits and hand-offs the brief names)
9. Are there known waits or service-level times for any step? (default: none drawn; a timer only where the brief gives a duration)
10. Where are the known pain points and moments of truth, and what evidence supports each? (default: none marked; the model does not guess where customers struggle)
11. For sign-up, checkout or password reset, which checks are required: identity checks, MFA, payment, email confirmation? (default: only the checks named)
12. Should a physical-evidence row (receipt, confirmation email, screen, parcel) or a per-stage rating row appear? (default: neither, unless the brief names items or asks for ratings)

## Push back when

- The brief wants servers, networks and protocols in the same picture as the journey. Tell the user that a blueprint shows which system supports a step, not how that system is built. Offer a separate architecture diagram and keep the support lane to named systems.
- The brief asks for an emotion curve or sentiment line. Stencil cannot draw a curve across stages. Offer a text row with a short rating per stage, such as "Frustrated: has to re-enter the card", and say the rating is a summary, not measured data, unless the user supplies the data.
- The brief has more than about eight stages. Tell the user the columns will become too narrow to read, and offer two panels or two diagrams, such as "Before purchase" and "After purchase".
- The brief puts a system or team in the customer lane, or a customer action in backstage. The customer lane holds only what the person does. Frontstage holds what the person sees or talks to. Backstage holds work the person cannot see.
- The brief asks for a journey map but describes internal teams and systems in detail. Ask whether the user wants a service blueprint instead, because a journey map has no backstage.
- The brief mixes current and target state in one row. Ask which one it is and draw one state per diagram.
- The brief marks a pain point with no source. Ask whether it comes from research, support tickets or an assumption, and label assumptions as such.
- The brief describes an internal hand-off process with no customer in it. That is a cross-functional swimlane, not a blueprint; use the business-process guide.

## How we draw it here

- Time runs left to right. A stage is a span made of one or more step columns. Each step gets its own column: a card is 200 px wide, with a 60-100 px gap between columns. Several actions in one stage, such as Browse, Compare and Add to cart, sit in separate columns at regular x positions, never stacked. Cards in different lanes that answer each other share the same step column. Add a slightly wider gap, or a thin text separator, between stages.
- Each stage label is a bold `text` node above the lanes, with `w` set to the stage's full span and `align: "center"`.
- Lanes are `group` entries with `style: "lane"`, stacked full width in this fixed order, top to bottom: optional physical evidence (text nodes only), customer actions, frontstage, backstage, support processes and systems. A journey map uses only the customer lane and, when it helps, a touchpoint or channel lane. An optional rating row goes as text nodes under the stage labels, above the customer lane.
- The renderer draws each lane title at the lane's top-left corner. Leave a left gutter of about 160-200 px in every lane for the title, and start the first step column to the right of it.
- The lines of interaction, visibility and internal interaction are the gaps between lanes. Lanes are separate rounded rectangles, so leave a 24-32 px gap between them. Name each line in the lower lane's `caption`, which is drawn under the title (for example "Below the line of visibility"), or with a small right-aligned `text` node at the right end of the gap. Never put the name at the left edge, where it covers the next lane's title. Never draw an edge to stand in for a line.
- Customer actions are `component` cards with verb-object labels ("Enters card details"). Use `identity/user` for the customer, or the channel asset when the channel is the point of the step.
- Channels: `compute/mobile` for the mobile app only, `software/browser` for the website, `business/email`, `business/chat`, `business/ticket` for a support case, `business/payment` for payment, and `compute/laptop` or `compute/workstation` for an agent's desk. The library has no phone or store symbol today. Draw a phone call as `identity/user` (the agent) captioned "Phone". Draw a store or counter as `identity/user` captioned with the location, or as a plain component card with no asset. The caption must name the channel.
- A human agent is `identity/user`; use `identity/admin` only for a privileged operator. Backstage work uses `business` assets where they fit (`form`, `approval`, `invoice`, `report`, `calendar`), and `identity/group` for a team.
- Support systems use `software/backend`, `software/rest-api`, `software/external-service` for a third-party provider, `software/message-queue` or `software/workflow` for automation, and `data/relational-db` or `data/document-db` for records. Draw `identity/identity-provider`, `identity/mfa` or `identity/passkey` only when the brief names them.
- Start and end use `presentation/start-end` with a caption naming the trigger and the outcome. A choice uses `presentation/decision` with labelled branches. A wait uses `business/timer` with the duration as its caption.
- Edge colour comes only from `palette`, never from `kind`, and the default is blue. `data` is solid with the default blue palette, for journey flow and steps within a lane. `control` is dashed; set `palette: "orange"` for a crossing of the line of interaction or visibility. `feedback` is dashed too; set `palette: "red"` for a retry, rework or channel switch. Control and feedback use the same dash, so every feedback edge needs a `label` ("Retry", "Switches to phone"). Without labels the two cannot be told apart in `theme: "monochrome"`. `dependency` is dotted; set `palette: "slate"` for a step relying on a support system.
- Keep journey flow horizontal. Draw vertical links straight only between adjacent lanes. A link that skips a lane, such as frontstage to support, must not pass through the card in between. Chain it through that card when the card really takes part. Otherwise set `source_port`/`target_port` and add `points` waypoints that run beside the card in the column gap. Clear every `edge_node_crossing` warning before preview.
- Pain points: a `status/warning` symbol (or `status/blocked` for a dead end) sized small, for example `w: 36, h: 28`. A symbol defaults to 144x112, so always set the size. Place it inside the same lane in the column gap, touching no card, plus a short `presentation/callout` or `text` node that says what goes wrong. A symbol caption allows at most 120 characters on two lines. A `marker` node with state `blocked` or `down` is a compact alternative for a dead end.
- Moments of truth: a `presentation/callout` or `presentation/note` whose text starts "Moment of truth:", placed off the card's top-left corner. Keep `status/approved` for a real approval or a confirmed success.
- Lane palettes stay quiet: customer orange, frontstage blue, backstage purple, support slate. Evidence and ratings are plain text. Colour marks the lane, not quality.
- The `legend` explains connector meanings only, and draws a line swatch for each entry. Its `dashed: true` style is the same for dashed and dotted lines, so the label must say which is which ("Dotted slate: relies on system"). Explain pain-point and moment-of-truth symbols with a small key near the footer, made of a symbol node plus a text node.
- Set `subtitle` to the persona and scenario. Set `footer` to say current or target state, and that steps are illustrative unless the user supplied them. Write `description` as a short narrative of the journey.

## Common mistakes

- For a blueprint, drawing a single row of screens with no backstage. For a journey map, adding backstage and support lanes the user never asked for.
- Swapping lane order, or putting the line of visibility under backstage.
- Drawing lines of visibility as edges between text nodes, or placing line labels on top of lane titles.
- Giving each stage one x position, so steps in the same stage overlap or stack. Also letting steps drift, so a frontstage step no longer sits under the action it answers.
- Expecting `control` to come out orange or `feedback` red without setting `palette`. Every connector then comes out blue.
- Vertical links that run through a middle lane's card.
- Full-size status symbols that overlap the next column, or a check mark used for a moment of truth.
- Stand-ins picked by guessing: `network/router` or `network/internet` for "the website" (use `software/browser`), `compute/mobile` for a phone call, `cloud/branch-office` for a shop, `software/frontend` for the customer, `fleet/dispatcher` for a support agent, `business/email` for chat, `data/relational-db` as a generic "backend". Use `search_assets` when unsure.
- Inventing MFA, CAPTCHA, fraud checks, loyalty steps, a "Get help" stage or a CRM that the brief did not name.
- Marking pain points by turning a card red, or faking an emotion curve with diagonal edges.
- Squeezing ten or more stages onto one canvas, or mixing target-state steps into a current-state journey.
- Forgetting the exits the brief names, such as an abandoned checkout or an escalation to a human agent.

## Start from

- `support-escalation` for a support journey from self-service to a human agent.
- `sales-lead-to-cash` for ordering and checkout backstage.
- `hr-employee-onboarding` and `it-onboarding-access` for employee experience journeys.

These templates are internal swimlanes, not blueprints. Copy their step, decision, timer and edge palette patterns (`control` with orange, `feedback` with red). Then rename the lanes into the order above, add the title gutter, and add stage labels as text nodes. For a journey with no close match, use `layout_diagram` and set positions by step column. Run `validate_diagram`, clear overlap and crossing warnings, then use `preview_diagram` to check that columns line up and that lane titles and labels do not overlap.

Read alongside: `brief` first, then `business-process` for swimlane mechanics, then `style`.
