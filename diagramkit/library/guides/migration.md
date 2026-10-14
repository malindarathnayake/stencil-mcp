# Migrations, transition architectures and cutover plans

> Use this guide when the diagram shows how a system moves from a current state to a target state: data-centre exit, cloud migration waves, strangler-fig decomposition, database or platform cutover with rollback, WAN migration, or a decommission plan.

## Questions to ask first

1. Which states should the diagram show: current, interim (coexistence) and target, or only two of them? (default: current and target side by side, plus one interim panel only if the brief mentions running old and new together)
2. Is this one move or a series of waves? What moves in each wave? Do dependent components land in different waves, and what latency can that split link tolerate? (default: a single move with dependencies kept together; for a split dependency, ask for the latency and label the cross-environment link with it)
3. Do old and new run side by side, for how long, and how are they connected during that period? (default: no coexistence unless the brief mentions it; if it does, ask how old and new connect before drawing a link)
4. How is traffic switched from old to new: DNS change, load-balancer weights, a routing change, a changed connection string or endpoint, or a facade that routes by path or feature? (default: the method the brief implies, drawn on the entry point the user already has; if the brief implies none, ask, and do not add a load balancer, DNS record or facade to carry a default)
5. Do both sides run the same database engine and version, or is this a heterogeneous move with schema conversion? How is data kept in step before cutover: bulk copy, change data capture (CDC), dual-write, or storage replication? (default: same engine, with a bulk copy from a consistent snapshot and CDC capturing from the snapshot point until cutover; the copy job and CDC pipeline are drawn only if the user accepts this default)
6. Which side is the system of record during coexistence, and when does that change? During a weighted split, where do requests served by the new side write: across the link to the old store, or to a new store? (default: the old system until cutover, with new-side writes crossing the link to the old store, drawn as their own edge)
7. What evidence passes the go/no-go, and who approves each gate? (default: row count and checksum reconciliation as a gate before a go/no-go ahead of the switch, and a separate sign-off before decommission; approvers unconfirmed, noted in the footer)
8. Is there a write freeze or maintenance window at cutover, and how long? (default: a short write freeze, shown as a gate before the switch)
9. What triggers a rollback, and what is the rollback path? (default: a failed health or reconciliation check triggers rollback and traffic switches back; whether new-side writes are reverse-synced or lost is unconfirmed and goes in the footer)
10. Is there a point of no return after which you only roll forward, and what marks it? (default: none drawn; flagged in the footer as unconfirmed)
11. What is retired at the end, and when: immediately, after a soak period, or after a data-retention period? (default: retired after a soak period, shown in the target panel as retired, not deleted)
12. What stays out of scope, and what else reaches the old system outside the main traffic path, such as batch jobs, hard-coded IP addresses, firewall rules, partner allow-lists or service accounts? (default: out-of-scope systems drawn once at the edge as external; no hidden consumers assumed, flagged in the footer)

## Push back when

- **The cutover has no rollback.** Say that every cutover needs a rollback path and a trigger, even if rollback is "restore from backup", and ask what it is before drawing.
- **Dual-write has no reconciliation story.** Writes to two stores are not atomic; if one write fails, the stores diverge silently. Ask how divergence is detected and repaired (a reconciliation job, an outbox, or CDC from one source of truth), and draw that.
- **A stateful system moves big-bang with no freeze window or sync.** Writes that land on the old system during the copy are lost or diverge. Ask whether there is a write freeze, or a CDC or replication catch-up before the switch.
- **CDC is drawn as starting after the bulk copy.** Writes made during the copy are then missed. CDC must record its start position (a log sequence number or a consistent snapshot) before or at the start of the copy. Ask how the start point is fixed.
- **The switch is DNS-only and ignores caching.** Resolvers and clients cache records until the TTL expires, some clients cache longer than the TTL, and open connections stay on the old endpoint regardless of DNS. Ask about the TTL, when it is lowered, and how long the old endpoint keeps serving.
- **Rollback is drawn as "switch traffic back" after the new side accepted writes.** Those writes must be copied back, or they are lost. Ask whether a reverse sync exists or whether data loss is accepted.
- **Both sides run the same jobs or consumers during coexistence.** Scheduled jobs and queue consumers on old and new process the same work twice, for example sending duplicate invoices or emails. Ask which side owns each job, and whether sessions are sticky or shared during a weighted split.
- **A strangler facade is drawn, but some callers still reach the monolith directly.** The facade only routes traffic that passes through it. Ask whether every caller goes through the facade.
- **An extracted service still shares the monolith's database.** Ask which side owns each table after extraction and how the other side reads it (API, events, or CDC), and draw that ownership.
- **Blue and green clusters or versions share one database.** Both versions must work with the same schema during coexistence. Ask whether schema changes are backward compatible (expand, then contract).
- **WAN migration has migrated and unmigrated sites with no path between them.** During coexistence, sites on the old network and sites on the new network still need to reach each other. Ask where the two networks interconnect, which network is preferred for a site reachable both ways, how routes are redistributed at the interconnect (with filtering or tagging to prevent loops), and whether address ranges overlap.
- **A component is decommissioned before its traffic is drained or its data is retained.** Ask what confirms it is idle and where its data goes.

## How we draw it here

**Layout.** Time runs left to right. Choose one of two layouts:

- Side-by-side panels: one `group` with `style: "panel"` per state, titled "Current", "Interim" and "Target" (or "Wave 1", "Wave 2"). Repeat a component in each panel where it exists, with the same label.
- One diagram with palette-coded phases: every component drawn once, its `palette` showing the phase in which it is added or retired, and a legend that names each palette.

Never put more than three states on one canvas. Validation warns when a panel holds more than 28 elements; a wave plan with more states is split into separate diagrams, one per wave or pair of waves.

**Palettes.** Pick one palette per phase and keep it for the whole diagram. Unchanged components keep the default palette. Retired components use `palette: "slate"` and the detail "Retired" (or "Retired after soak"), the same convention as the explainer guide. Do not use `state: "down"` or `status/down` for a retired component; that draws a failure badge and reads as an outage. Use `status/pending` for a step not yet done and `status/approved` for a passed gate, as `symbol` nodes with a caption.

**Asset roles.**

- Locations: `cloud/datacenter` for the source site, `cloud/public-cloud`, `cloud/cloud-region`, `cloud/vpc` or `cloud/private-cloud` for the target; `cloud/dedicated-circuit` or `network/vpn-gateway` for the link between them during coexistence.
- Workloads: `compute/rack-server`, `compute/virtual-machine` and `compute/hypervisor` for lift-and-shift; `software/monolith` and `software/microservice` for strangler-fig; `kubernetes/cluster` for blue and green clusters.
- Traffic switch: `network/load-balancer` for weighted switching, `network/api-gateway` or `network/reverse-proxy` for a strangler facade, `network/router` for a routing change.
- DNS cutover: the catalog has no DNS asset. Draw a `component` card with no asset, labelled with the record and TTL (for example "DNS app.example.com, TTL 60s"), with a `data` edge to each endpoint labelled "before" and "after". Do not use `network/router` for DNS.
- Data: `data/relational-db` and `data/database-replica` for source and target stores, `data/etl` for a bulk copy job, `data/stream-processor` for a CDC pipeline, `software/background-worker` labelled "Reconciliation job" for dual-write checks.
- WAN: `routing/mpls` or `network/wan-provider` for the old network, `network/sdwan-edge` for new edges, `cloud/branch-office` for sites.
- Gates: `devops/release-approval` for go/no-go and decommission sign-off, `devops/cd-release` for the switch, `devops/rollback` for the rollback step, `presentation/decision` with a question caption ("Checks pass?") where the plan branches.

**Edges.**

- `data` for live traffic, labelled with what decides the route: "90% old / 10% new", "/orders", "/billing", "Feature: search". New-side writes to the old store during a split are their own `data` edge.
- `replication` for the sync path, labelled with the method: "CDC", "Dual-write", "Bulk copy", "Storage replication". Show direction; a reverse sync for rollback is its own edge.
- `feedback` with `palette: "red"` for the rollback path, labelled with the trigger and action ("Rollback: error rate > 2%, switch traffic back"). Draw it explicitly; never leave rollback to the description.
- `control` for gates and approvals acting on the switch; `dependency` for a depends-on relation that crosses waves, labelled with its latency when known.
- `physical` for circuits and WAN links in a network migration.

**Legend and footer.** Add a legend whenever more than one phase palette or more than one edge kind appears; a migration diagram almost always needs one. Each legend item names a phase ("Added in wave 2", "Retired") or a line meaning ("Sync: CDC", "Rollback"). Put the assumptions in the `footer`: the switch method, the freeze window, the point of no return, whether rollback loses new-side writes, unconfirmed approvers and hidden consumers, and anything else the user did not confirm. Write the `description` as the sequence: what moves, how data syncs, how traffic switches, what triggers rollback, what is retired.

**Runbooks.** A step-by-step cutover runbook with owners is a process diagram, not an architecture diagram. Draw it as swimlanes per the process guide, with go/no-go as `presentation/decision`.

## Common mistakes

- Showing only the target state when the brief asks how to get there; the interim coexistence state is usually the point.
- Drawing old and new side by side with no sync edge, so the reader cannot tell how data gets across.
- Leaving the rollback path out, or drawing it as an unlabelled arrow.
- Drawing a reverse sync for rollback that the user never mentioned.
- Showing decommission with no sign-off gate; decommission cannot be undone.
- Marking retired components with `state: "down"`, a red palette or `status/down`, which reads as a failure.
- Deleting retired components from the target panel, which hides what was decommissioned.
- Drawing the strangler facade as `software/rest-api` or `software/backend`; the facade is a routing point, so use `network/api-gateway` or `network/reverse-proxy`, and label each route.
- Using `network/router` or `cloud/edge-location` as a stand-in for DNS.
- Using `resilience/failover` or `resilience/active-passive` for a planned cutover; those mean automatic recovery, not a one-time move.
- Using `resilience/replication` as a node when the sync is an edge between two stores; draw the method on the edge.
- Using `cloud/hybrid-cloud` as a stand-in for "both sites" instead of drawing the two locations and the link between them.
- Putting four or more states on one canvas, or every wave's components in one panel.
- Adding a load balancer, CDC pipeline, interconnect or gate the user neither mentioned nor accepted as a default.

## Start from

- Data-centre to cloud and WAN coexistence: `hybrid-cloud`.
- Strangler-fig and application replatforming: `software-overview`.
- Database cutover with sync and recovery: `backup-dr`.
- Blue and green Kubernetes clusters behind one entry point: `kubernetes-ingress`.
- Cutover runbook with approvals: `it-change-approval`.
- Wave plans and current-to-target explainers: no template yet; use `layout_diagram` with panel groups.

Read alongside: `brief` first, then `network` for WAN and data-centre moves, `business-process` for runbooks, `explainer` for panel conventions, and `style` last.
