# Confirm the brief before drawing

> Read this first for every diagram request, in any department, including edits to an existing scene, before you search assets or place a single node.

A diagram can pass validation and still be wrong because it answers a different question. The usual cause is a plausible stand-in: the brief leaves a fact open and the drawing fills it with the common pattern instead of the user's design. This guide exists to stop that.

Before placing anything, do three things in your own reasoning and show the result to the user:

1. Write one sentence saying what the reader must understand from the picture, for example "Each server reaches storage over two independent paths, so losing one switch does not stop I/O."
2. Write two short lists: the facts the brief states, and the facts it leaves open.
3. Pick the diagram type and say which one you picked: topology, flow, sequence, swimlane or explainer. Then call `stencil_guide` with no topic to see the index and read the guide that matches that type, and the `style` guide.

## Questions to ask first

This is a checklist, not a script. Ask only the open items that would change the topology or the story, usually three to six, in one numbered round, each with the default you would otherwise use so the user can reply "yes to all" or correct one item. Put the takeaway sentence and the diagram type into your restatement instead of asking them as separate questions. Skip anything the brief already answers. When the topic guide has its own questions, merge the two lists into one round of at most eight questions: a topic question replaces an overlapping one here, and the questions that change the drawing most come first. Do not ask about layout, colours, fonts or wording. For an edit, also ask what must stay as it is (default: everything the user did not mention, including node IDs, groups and wording).

1. Is this the current state, the target state, or one step of a migration? (default: current state)
2. Who reads it, and at what level of detail? (default: system or container level, with no ports, interfaces or IP addresses)
3. Which components exist, and how many of each? (default: exactly the components named, one of each unless a count is stated)
4. Where does each component sit: which site, zone, rack, cluster or lane? (default: a single location, with no racks, zones or sites that the brief did not name)
5. Which links exist, between which components, and how many per device? (default: one link for each pair the brief connects, and no others)
6. What runs over each link, and how: routed or switched, ECMP or multipath, replicated, encrypted, a request or a hand-off? (default: in a topology, a `physical` edge with no arrow between devices; in a flow or sequence, a `data` edge with the arrow from the initiator; the brief's own label whenever it gives one)
7. Who initiates each interaction, and is it synchronous or asynchronous? (default: the first-named component initiates, and the call is synchronous)
8. What is redundant, and what is deliberately a single point of failure? Is redundancy active-active or active-passive? (default: single instances, nothing marked redundant)
9. Which boundaries matter (trust, ownership, network, organisation), who owns each, and what is out of scope? (default: only the boundaries the brief names; each named external system as one card at the edge, with no internals)
10. Which scenario should the picture show: normal operation, a failure, a recovery, or several panels? (default: normal operation only)
11. For a process: what starts it, how does it end, and what happens on rejection, timeout or exception? (default: one start, one successful end, and rejection paths only where the brief names them)
12. May real hostnames, IP addresses, account IDs, vendor names or people's names appear? Exported SVG and scene JSON get shared. (default: generic role labels and no real addresses)

## Push back when

Push back when the brief conflicts with how a technology or process really works. Say what looks wrong in one or two sentences and ask which the user means. Do not silently draw the request as written, and do not silently "correct" it either.

Networks and storage:

- **iSCSI over ECMP alone.** ECMP hashes each iSCSI TCP session onto one path, so it does not give host-level path redundancy. That comes from MPIO, often over two separate fabrics or subnets, which may themselves be routed. Ask whether they mean MPIO, ECMP reachability, or MPIO over an ECMP fabric.
- **ECMP described as per-packet spraying.** Default ECMP hashes each flow onto one path, which stays fixed until the topology changes. Per-packet, flowlet or adaptive spraying exists but is a deliberate feature that needs reordering tolerance. Ask which one they mean.
- **Out-of-order arrival treated as loss.** A delayed packet can still arrive, so a gap alone does not prove loss, but reordering can trigger a spurious fast retransmit after duplicate ACKs. Ask whether to show reordering, real loss, or a spurious retransmit.
- **A layer-2 switch routing between VLANs.** A pure layer-2 switch does not route. Ask what does the inter-VLAN routing: a layer-3 switch, a router or a firewall.
- **One host bonded to two switches as a single LAG.** A LAG that spans two switches needs MLAG, vPC-style pairing or a stack. Ask which they have, or whether the links are active-backup.
- **Shared-fate redundancy.** Two links to the same switch, power feed, conduit or availability zone are not independent. Ask what the two paths actually share.
- **One load balancer, gateway or NAT drawn as the HA answer.** A single instance is itself a single point of failure. Ask whether it is a pair or cluster.
- **DNS round-robin called failover.** It has no health checking, and clients cache answers. Ask whether health-checked DNS or a load balancer does the failover.
- **Cloud network scope.** In some clouds (AWS, for example) a subnet lives in one availability zone; multi-zone is not multi-region DR; VPC or VNet peering is not transitive. Ask for the actual scope and the hub or transit for spoke-to-spoke traffic.
- **RAID, a same-array snapshot, a read replica or replication called a backup.** RAID and snapshots fail with the array, and replication copies deletes, corruption and ransomware encryption. Ask whether an independent, ideally immutable or offline, copy exists, where it lives, and its retention.

Security and identity:

- **A VLAN or subnet drawn as the security control.** Separation is enforced by whatever routes or filters between segments. Ask for the enforcement point; a trust boundary is a labelled container, not a control.
- **An identity provider or policy engine drawn as the enforcement point.** Ask for the actual enforcement point (firewall, gateway, proxy) and keep identity provider, policy decision, enforcement and logging separate.
- **TLS terminated at a load balancer or proxy called end-to-end encryption.** Ask whether traffic is re-encrypted to the backend.
- **A stateful firewall drawn with separate inbound rules for return traffic.** Return traffic is allowed by connection state. Ask whether the device is stateless.
- **An agent or model with unrestricted database or mutation access.** Ask whether reads and mutations are separated and where `ai/human-approval` sits before privileged tool calls.

Applications and platforms:

- **Several Deployment replicas on one node called HA.** Ask how many nodes or zones the replicas spread across.
- **An Ingress drawn without its controller.** The Ingress resource does nothing on its own. Ask what fronts the cluster: a cloud load balancer, an ingress controller or a gateway.
- **A message queue promising global ordering or end-to-end exactly-once delivery.** Ordering usually holds per partition or queue, and end-to-end exactly-once needs idempotent consumers. Ask what guarantee is really needed.
- **A sequence that leaves sync and async implicit.** A synchronous call needs a response; an asynchronous message through a queue or event has no inline reply. Ask which each step is.

Processes:

- **A swimlane named after a task.** A lane is a role or team. Ask who performs the step.
- **An approval drawn after the action it gates.** Ask whether it is a pre-approval or an after-the-fact review.
- **Segregation of duties broken.** The same role requests and approves, or payment happens without a purchase order, receipt and invoice match. Ask whether that is intended.
- **Incident response with eradication or recovery before containment.** Containment normally comes first. Ask whether the order is deliberate.
- **One end state where rejection or timeout paths exist.** Ask for every end state.

If you are not sure a claim is wrong, ask a question instead of asserting it.

## How we draw it here

- **Direction.** Architecture flows left to right. Swimlane processes stack lanes full width with time running left to right, one step per column. Sequences run top to bottom along lifelines.
- **Grouping.** Use `group` entries: `boundary` for trust or ownership boundaries, `panel` for a site, zone, cluster or a split explanation panel, and `lane` for a role in a process. Only create groups for boundaries and locations the brief or the user's answers name.
- **Assets.** Choose assets by role with `search_assets`, then confirm only the chosen IDs with `get_asset`. Never pick an asset because it looks close; if no asset fits a role, use a labelled `component` card and say so. For flow and annotation roles use `presentation/decision`, `presentation/start-end`, `presentation/process`, `presentation/external-entity`, `presentation/data-store`, `presentation/callout` and `presentation/note`; for sequences use `presentation/sequence-lifeline`. Do not place `presentation/legend` as a node to explain edges; use the scene `legend` array instead.
- **State.** Use `status/*` assets (`status/healthy`, `status/warning`, `status/down` and others) as `symbol` or `component` nodes only when the brief is about state. For loss or failure on a path, use a `marker` node with a `state` (dropped, missing, down, blocked, pending, received, normal).
- **Edges.** Use the connector meanings from the design rules: `physical` for cables and circuits, `data` for requests and payloads, `control` for policy, configuration and signalling, `feedback` for responses, ACKs and rework, `dependency` for depends-on, `tunnel` for encapsulated or logical connections, `replication` for replicated data. A physical link between devices is a line without arrows unless the picture is explaining direction.
- **Palettes.** Keep palette use consistent within a diagram: one palette per role family, and red reserved for failure, threat or rework. Never carry meaning by colour alone: pair red with a `status/*` asset, a marker `state` or a text label so the picture still reads in the `monochrome` theme.
- **Legend, description and footer.** Add a `legend` (items with `label`, `palette` and optional `dashed`, at most 12) whenever more than one edge or marker meaning appears. Write the scene `description` as a short narrative of what the picture shows; it becomes the SVG `<desc>`, and it must agree with any assumptions you listed. Use `footer` for source, scope or "illustrative" notes the user should not miss.

## Common mistakes

- **Plausible stand-ins.** Filling an open fact with the textbook pattern: two spines and four leaves when no count was given, dual-homed servers when the brief said one link, an HA pair when the brief said one firewall.
- **Unrequested components.** Adding management nodes, an extra firewall, a load balancer, a bastion host or a monitoring stack because a typical design has them. Ask by name instead, and mention it in the reply if the user proceeds.
- **Asking the wrong questions.** Asking about colours, layout or wording, reading the whole checklist out, or asking open-ended questions with no defaults.
- **Silent correction.** Redrawing iSCSI as MPIO without saying so is as wrong as drawing iSCSI over ECMP without comment.
- **Wrong diagram type.** Drawing a request sequence as a topology, or a business process as a component diagram. Pick the type first and say it.
- **Merged links.** Drawing dual-homed or leaf-spine links as one shared line. Draw each link as its own edge with `route: "straight"` so the per-device count stays visible.
- **Known gaps hidden.** Stencil does not draw data tables, charts, scaled time axes, true entity-relationship notation or floor plans. Say so up front and offer the nearest alternative: for an ERD, `component` cards per entity linked by `dependency` edges whose labels carry cardinality text ("1..*"), stated as not true ERD notation; for a timeline, a swimlane or step explainer with dated captions, stated as not to scale; `panel` groups per room or rack for a floor plan; and a separate charting tool for numbers.
- **Unlisted assumptions.** If the user says "just draw it", proceed, but list every assumption in the reply, matching the defaults above, and keep the `description` consistent with that list.
- **Editing by regeneration.** For an existing scene, rebuilding from scratch changes IDs, positions and wording the user did not ask to change. Load the scene JSON and change only what was requested.
- **Treating validation as approval.** `validate_diagram` checks schema, IDs, overlaps and text fit. It does not check protocol semantics, redundancy or whether the picture matches the brief.

### Before export

1. Run `validate_diagram`, fix errors and read every warning.
2. Render with `render_diagram`, and use `preview_diagram` when PNG previews are available, to inspect the picture at its intended size.
3. Reread the brief. Find every named component, count, link, boundary and stated redundancy in the picture, then check that nothing appears that the brief and the answers did not ask for.
4. Export with `export_diagram`, producing both `.svg` and `.scene.json`.

## Start from

No template is specific to this guide. Prefer a template whenever one fits the diagram type: call `list_templates`, choose the closest match, tell the user which template you are starting from and what you will add, remove or relabel, and then load it with `get_template`. If none fits, use `layout_diagram` for initial positions.

Read alongside: the guide for the chosen diagram type (find it in the `stencil_guide` index) and `style`.
