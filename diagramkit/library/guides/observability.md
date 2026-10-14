# Observability, monitoring and service health

> Use this guide when the diagram shows how telemetry is collected, stored and acted on, how alerts reach the on-call engineer, how services depend on each other and on their SLOs, what was healthy or failing during an outage, or how network devices and traffic are monitored.

## Questions to ask first

Ask only the questions the brief leaves open, in one numbered round, so the user can answer "yes to all" or correct one. Always settle questions 1 and 12, then ask only the questions tagged for the chosen view.

1. [all] Which view is this: telemetry pipeline, alert routing and on-call, dependency or SLO map, status overlay, or network monitoring? (default: the view the brief names; ask when two could fit)
2. [pipeline] Which signals and sources are in scope: metrics, logs, traces, events, profiles; browser real-user telemetry; synthetic probes run from outside locations? (default: metrics, logs and traces from the named services, as three separate paths; no browser telemetry, no external probes)
3. [pipeline] How is telemetry collected: in-process SDK, a node agent on every host, a sidecar per workload, a central collector tier, or the backend scraping targets; and does a queue buffer it before the stores? (default: services push to one collector tier; nothing scrapes; no buffer)
4. [pipeline] Which store holds each signal, is any shared, is there an archive or retention tier, and is sampling applied to traces? (default: one store per signal; no archive; sampling not drawn)
5. [alert routing] Where are alert rules evaluated, what fires them (thresholds, SLO burn rate, log patterns, probes), and is there a routing layer that groups, deduplicates, silences or routes by severity or team before paging? (default: metric rules in one alerting component; no routing layer drawn)
6. [alert routing] Where do alerts go and who is paged (paging service, chat, email, ticket queue; which rotation), is there escalation, after what timeout, and what stops it, such as acknowledgement by the primary? (default: paging service to the primary on-call; no escalation)
7. [pipeline, alert routing] Does anything detect the monitoring itself failing (a heartbeat or watchdog alert, an external probe, alerting on absent data), and does alerting run outside the failure domain it watches? (default: not drawn)
8. [dependency or SLO map] Which services and dependencies, and what are the SLO targets and windows? (default: only the services and dependencies the user named; no SLO numbers)
9. [status overlay] What state is each component in, at what time, and according to which source? (default: no status markers until the user states them)
10. [network monitoring] How is device health collected: SNMP polling (the poller pulls), SNMP traps or syslog (the device pushes), or streaming telemetry such as gNMI dial-in or dial-out? (default: SNMP polling from one poller; no traps, no syslog)
11. [network monitoring] Is traffic copied or summarised: a TAP, a local SPAN, RSPAN, ERSPAN or cloud traffic mirroring; a packet broker before the tools; flow export from which devices; which tools receive it; should possible SPAN drops be noted? (default: draw no TAP, mirror or flow export until the user names the copy point and the receiving tool)
12. [all] What is out of scope: security monitoring and SIEM hand-off, business analytics, cost reporting, incident timelines or post-incident review? (default: all out of scope)

## Push back when

- The user wants a dashboard to page someone. Dashboards display data; alert rules evaluate conditions and send notifications. Tell the user the page comes from the alerting component, and ask whether the dashboard should be drawn beside it.
- The user treats every alert as an incident. An alert is a notification; an incident is declared by a person or a rule. Ask whether incidents are opened automatically or by the on-call engineer.
- The user expects NetFlow or IPFIX to show payloads or full conversations. Flow export carries summary records (addresses, ports, protocol, byte and packet counts, timing), often sampled. Content needs a packet capture.
- The user expects SNMP interface counters to show which flows or applications use a link. Counters give utilisation, errors and discards per interface, not per-flow detail. Ask whether flow export or capture is also wanted.
- The user draws a TAP that exports flows, filters or alerts by itself. A TAP only copies traffic to its monitor ports. A packet broker can aggregate, filter, deduplicate or load-balance the copy; analysis happens in a capture tool, IDS or flow probe. Ask what sits after the TAP.
- The user expects a SPAN port to deliver every packet. A mirror port can drop traffic when the mirrored links exceed its capacity, and switches usually do not mirror errored frames. Ask whether a TAP is needed or the diagram should note possible drops.
- The user wants an end-to-end trace through a service that is not instrumented or does not propagate trace context. That hop breaks the trace. Ask whether the gap should be shown.
- The user wants every request traced while also stating sampling is on. With sampling, only some requests produce stored traces. Ask which statement is true.
- The user calls an SLO an SLA, or the reverse. An SLO is an internal reliability target; an SLA is a contractual commitment with consequences. Ask which one the numbers represent.
- The alerting runs in the same cluster or region it monitors. Ask whether it must page during that region's outage, and whether a heartbeat to an external service exists.
- The user wants a status overlay but gives no states, or treats a passing health probe as proof that dependencies are healthy. Do not invent health; a probe only shows its endpoint answered as designed. Ask for each state, and what the probe checks.

## How we draw it here

Direction and grouping:
- Pipelines run left to right: sources, agents or collectors, buffers, stores, dashboards and alerting, then people. Put each stage in its own `panel` group when there are three or more stages.
- Use a `boundary` group only for a real ownership or trust boundary, such as a vendor-hosted backend, a separate monitoring network, or an external probe location.
- On-call routing that crosses teams is a swimlane: one `lane` group per role or team, time left to right, following the process rules of the design system.
- Dependency maps run from user-facing services on the left to shared dependencies on the right.
- Network monitoring keeps the device-health path (polling, traps, syslog, telemetry) separate from the traffic-copy path (TAP, mirror, flow export).

Asset IDs by role:
- Sources: `software/microservice`, `software/backend`, `software/frontend`, `software/rest-api`; `software/browser` for real-user telemetry; `compute/rack-server`, `kubernetes/worker-node` or `kubernetes/pod` when placement matters.
- Signals: `observability/metrics`, `observability/logs`, `observability/traces`, `observability/audit-log`. Events and profiles have no dedicated asset: use `observability/logs` for events and `observability/metrics` or `observability/traces` labelled "Profiles". Do not invent IDs; check with `search_assets`.
- Collection: `observability/collector`, labelled for its job ("OTel collector", "SNMP poller", "syslog receiver"). Node agents: `kubernetes/daemonset`; sidecars: `kubernetes/container` inside the pod's group.
- Probes: `observability/health-probe`; for external synthetic checks, place it in a group per location with `cloud/edge-location` beside it.
- Buffers: `software/message-queue` or `software/message-broker`; stream jobs with `data/stream-processor`.
- Stores, each labelled with its signal: metrics in `data/time-series-db`; logs in `data/search-index` for full-text indexed stores, otherwise the closest data store labelled "log store"; traces in `data/document-db` or `data/time-series-db` labelled "trace store", or `storage/object-store` when spans land in object storage. Archives and retention tiers: `storage/object-store`, `data/data-lake`, and `storage/immutable-backup` for audit logs that must not change.
- Views and response: `observability/dashboard`, `observability/alert`, `observability/incident`, `observability/service-map`.
- Notification and people: `software/external-service` labelled as the paging service, `business/chat`, `business/email`, `business/ticket`, `business/timer` for escalation timeouts, `identity/user` for one engineer, `identity/group` for a rotation.
- Network monitoring: the monitored devices (`network/router`, `network/switch-l3`, `network/switch-l2`, `security/firewall`), `network/network-tap`, `observability/netflow`, `observability/packet-capture`, and `security/ids` when it receives the copy. A packet broker has no dedicated asset: use a separate `network/network-tap` node labelled "Packet broker", with its filtering or deduplication in `detail`, between the TAP or SPAN and the tools.
- Health state: `status/healthy`, `status/warning`, `status/down`, `status/pending`, `status/unknown` as `symbol` nodes next to the component they describe, or a `marker` node with `state` `down`, `pending`, `blocked`, or `missing` for a broken trace hop.
- Security monitoring in scope: `security/siem` as the receiver of a labelled log feed; for the rest, use the security guide listed by `stencil_guide`.

Edges and palettes:
- `data` edges for telemetry, drawn in the direction the data moves. When the backend scrapes or a poller polls, still point from target to store or poller and label it "scrape" or "SNMP poll". Label device pushes "trap", "syslog" or "gNMI".
- Keep one path per signal, or label every shared edge with the signals it carries ("metrics, logs").
- Pipeline or architecture view: `control` edges for alert to incident to notification. On-call swimlane: follow the process rules, with `data` for the flow, `control` for the hand-off to the external paging service, and `feedback` for re-page and escalation loops.
- Acknowledgement is a `feedback` edge from the on-call engineer back to the paging service; label the escalation timer "if not acked in N min".
- `dependency` edges point from the dependent service to what it depends on. Do not mix them with `data` edges in one map unless the legend explains both.
- TAP or local SPAN: draw the monitored link through the TAP (device A to TAP to device B, `physical`), then `physical` edges from the monitor port or ports to the tool; a passive full-duplex TAP has one monitor port per direction. RSPAN, ERSPAN and cloud mirroring are not cables: use a `tunnel` edge labelled "RSPAN VLAN", "ERSPAN (GRE)" or "VXLAN mirror". Flow records to a collector are `data`.
- Palettes: orange for the telemetry pipeline, red for alerting and incidents, blue for application services, slate for people and external services. Status: green healthy, yellow warning, red down, slate unknown.

Text, legend and footer:
- Put SLO targets and windows, retention periods and sampling rates in `detail` text ("99.9% / 30 days"), never as a chart.
- Add a `legend` whenever more than one edge kind or status colour appears.
- Use `footer` for the time and source of a status overlay ("State as reported at 14:05 UTC by the incident channel") and stated assumptions.
- An incident timeline or post-incident review is a left-to-right process: one step per event, time in `detail`, lanes only when several teams act.

## Common mistakes

- Drawing gauges, line charts or bar charts. There are no chart primitives; a dashboard is an `observability/dashboard` icon with a label.
- Merging metrics, logs and traces into one unlabelled arrow or one "collector / stores" node, which hides that they use different stores.
- Adding a queue, a second collector tier, an archive, a TAP or a packet broker because a typical stack has one. Ask instead.
- Marking components healthy or failed when the user stated no state, or colouring a whole map green by default.
- Using `data` edges for dependencies, which implies traffic flows along the arrow.
- Drawing the dashboard as the thing that pages people, or skipping the alert component between rules and the paging service.
- Drawing escalation without an acknowledgement path, which suggests everyone is always paged in turn, or inventing timers the user did not give.
- Using `observability/service-map` as the dependency map itself; it is one icon. Draw the services and dependency edges.
- Picking `security/siem` as the operations log store, or `network/load-balancer` as a stand-in for a collector or packet broker.
- Drawing an ERSPAN or cloud mirror as a `physical` cable, or connecting a TAP straight to a dashboard with no capture or analysis tool.
- Pointing SNMP poll arrows from the poller to the device, which reads as configuration rather than telemetry.

## Start from

- `observability-pipeline` for signals through collection to dashboards and alerts. The template merges the collector and the stores into one node with unlabelled edges: split it into an `observability/collector` and one store per signal, add an alert-rule evaluator before `observability/alert`, and label edges by signal.
- `sec-incident-response` and `support-escalation` as swimlane examples for on-call routing, escalation and incident timelines.
- `sequence-request` for one request traced across services; mark a broken hop with a `missing` marker.
- Dependency or SLO maps and network monitoring: no template yet; use `layout_diagram`.
- Read alongside: `brief` first, then `style`; `network` for device, TAP, mirror and flow placement. Call `stencil_guide` with no topic to list other guides, such as security monitoring or process swimlanes.
