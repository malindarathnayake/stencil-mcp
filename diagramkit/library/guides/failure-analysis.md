# Incident post-mortems, blast radius and single-point-of-failure reviews

> Use this guide when the diagram explains how a failure spread, what an outage takes down, or where an architecture has single points of failure, including before/after views of a remediation.

## Questions to ask first

Ask in one round, only for facts the brief leaves open. Each question has the default you would otherwise use. Always ask questions 1-7 when they are open. Ask questions 8-11 only for the story type they name.

1. What was the trigger, and what kind of event was it: a deploy, a config change, an expired certificate, a capacity limit, a dependency outage or a hardware fault? (default: one trigger card labelled exactly as the brief words it, with no invented cause)
2. What was the user-visible impact: error rate, affected users or tenants, any data loss, any SLO breach? (default: impact only as the brief states it, written in the boundary title or the footer, with no invented percentages)
3. Which components failed outright, which were degraded but still serving, and which were unaffected? (default: only components the brief names as failed are marked down; everything else is drawn without a state)
4. Which contributing factors made the failure possible or worse, for example a missing timeout, a shared dependency or an alert that did not fire? (default: only the factors the brief lists, each as its own unnumbered note card)
5. Where and how was the incident detected, and how long did detection take? (default: one detection card attached to the component whose signal fired, outside the request path, with any duration the brief gives in its label)
6. What was the mitigation, and what was the later permanent fix? (default: mitigation and fix as separate numbered steps; the fix is not shown as applied unless the brief says so)
7. Should the diagram show the state during the incident, after the fix, or both, and is it for an internal blameless review or a customer-facing report? (default: incident state only, internal blameless review)
8. Blast-radius map only: what is the failing element, is impact measured in services, tenants or regions, and which dependents depend hard on it versus having a fallback, cache or degraded mode? (default: services only; every hop the brief names; dependents with no stated fallback are asked about, not assumed hard)
9. SPOF review only: what counts as a single point of failure here (instance, zone, provider, team), and which dependencies are shared across zones or regions, such as identity, DNS or a config store? (default: mark a SPOF only where the brief says there is one instance or one shared dependency; if failover is unstated, ask)
10. Dependency impact graph only: should it show upstream callers, downstream dependencies or both? (default: both directions, every hop the brief names)
11. Retry storm or cascading timeout only: which layers retry, how many times, and with what timeout at each layer? (default: only the layers and values the brief gives, written on the edge labels)

If the user says to proceed without answering, list unanswered facts in `description`, for example "failover unknown" for components you left unmarked.

## Push back when

- The brief names one root cause but lists several contributing factors. Say the factors are part of the causal story and a single "root cause" card would hide them; offer the trigger plus each factor as its own card.
- The brief names an individual or labels the trigger "human error". Post-mortems are normally blameless. Suggest labelling by role or system ("on-call engineer", "config change via CD") and drawing the missing safeguard, such as no validation or no staged rollout, as a contributing factor.
- The brief draws detection (metrics, logs, an alert) inline between the client and the service. Monitoring observes the path; it does not sit in it. Say you will attach detection beside the path, unless the monitoring component really is an inline proxy.
- Replicas are called redundant but share one database, zone, load balancer or config source; or one surviving replica cannot carry peak load; or every replica receives the same release, config or certificate at the same moment with no staged rollout. Say the redundancy is unproven and offer a SPOF or "correlated failure" marker.
- Retries are drawn as the fix for an overload. Retries add load to a component that is already overloaded, and retries at several layers multiply. Ask whether there is backoff, a retry budget, a rate limiter or a circuit breaker, and draw only what exists.
- A circuit breaker is drawn as making the downstream healthy again. An open breaker sits on the caller side and fails the caller's own outbound calls fast; the downstream is still failed. Ask what the caller does while the breaker is open.
- A caller's timeout is shorter than the time its callee may spend on its own retries. The caller gives up while the callee keeps working, which wastes capacity during an incident. Point this out and ask whether the values are correct.
- The user wants a timeline with real time spacing. Stencil has no time axis, and x position is not time. Offer numbered steps with durations in the labels.
- The user wants overlapping blast radii (for example a zone failure and a tenant failure) in one picture. A node can belong to only one group, so `validate_diagram` checks containment against one box only. Nested or overlapping boundary boxes can be drawn by hand, but membership in the inner one is not checked. Prefer separate diagrams, or set `group` to the innermost box and check the outer one visually.

## How we draw it here

Choose one story per diagram: a causal chain, a blast-radius map, a SPOF review, a dependency impact graph, or a before/after pair. Mixing them makes every arrow ambiguous.

**Layout.** Causal chains run left to right in numbered order: trigger, cascade, detection, mitigation. Contributing factors are not in the numbered sequence, because most are latent conditions that existed before the trigger. Place each factor as an unnumbered `presentation/note` card above or below the step it worsened, linked with a labelled `dependency` edge in `orange` ("allowed", "amplified"). Dependency impact graphs put the failed or changed component in the middle, upstream callers on the left and downstream dependencies on the right; `layout_diagram` gives a first placement. Before/after uses two `panel` groups side by side titled "Before" and "After", with the same components in the same positions.

**Failure state.** Set `state: "down"` on a `component` that failed; the renderer draws the `status/down` badge in its top-right corner. Use `state: "blocked"` only for a component that sheds its own inbound load: rate limited, load-shedding or quarantined. For an open circuit breaker, mark the failed downstream `down` and place a `resilience/circuit-breaker` symbol near the caller's end of the edge, captioned "Open: failing fast". There is no degraded state, so mark degraded components with a `status/warning` symbol beside the card and write "Degraded" in the `detail`. Use `state: "pending"` for "recovering" and a `status/healthy` symbol for "restored" in an after panel. Never show failure by red colour alone.

**Causal order.** Draw steps as `component` cards with `presentation/step` or `presentation/process` and a numbered label ("1. Config pushed", "2. Cache misses spike"), or number the edge labels. Show every duration the brief gives in `detail` or edge labels ("Mitigated after 42 min").

**Edge meanings.** Causal "led to" links are `data` edges with the `orange` palette and a short label. Request flow, when it must appear, is `data` in `blue`. Depends-on relations in impact graphs and SPOF reviews are `dependency` (dotted). Detection is `control` from the observed component to `observability/alert` or `observability/health-probe`. Retries and error returns are `feedback` with the count in the label ("retry ×3"). Always add a legend that states the convention, for example "Orange arrow: caused or led to (not request flow)", because readers assume arrows are requests.

**Blast radius.** Draw the impacted area as one `boundary` group in `red` or `orange`, titled with the cause ("Impacted if the primary database fails"). Put the failed element and its hard dependents inside it. Draw soft dependents (those with a fallback, cache or degraded mode) outside it with a `status/warning` symbol and "Degraded" in the detail. Leave unaffected components outside. Groups are not resized around their children, so size the box by hand and check containment with `validate_diagram`.

**SPOF markers.** Place a `status/warning` `symbol` node about 24×24 with no caption just outside the card, above or beside its top-right corner, plus either a legend entry or a small `text` node beside it reading "SPOF". A symbol caption renders inside the node box, so if you want a caption, size the symbol about 96×64 and keep the caption to one or two words. Do not place the marker on the card: it collides with the state badge and raises `node_overlap`.

**Resilience controls.** Draw `resilience/circuit-breaker`, `resilience/retry`, `resilience/timeout` and `resilience/rate-limiter` as `symbol` nodes about 96×72 beside the edge they govern, near the caller's end, not as cards in the path. Keep captions to one short line ("Timeout 2 s", "Retry ×3").

**Asset roles.**
- Triggers: `devops/cd-release`, `devops/infrastructure-as-code`, `identity/certificate` (expiry), `software/external-service` or `cloud/saas` (provider outage), `protocol/congestion` (capacity).
- Affected systems: the real role, such as `software/microservice`, `data/relational-db`, `data/cache`, `network/load-balancer`, `cloud/availability-zone`, `cloud/cloud-region`.
- Tenants or customer groups: `identity/group` or `kubernetes/namespace`, labelled with the tenant.
- Detection: `observability/alert`, `observability/metrics`, `observability/logs`, `observability/health-probe`, `observability/dashboard`; a customer report is `business/ticket`.
- Response and mitigation: `observability/incident`, `devops/rollback`, `resilience/failover`, `resilience/autoscaler`, `resilience/rate-limiter`.
- Many callers converging (thundering herd): `presentation/fan-in`.

**Text.** Put the incident identifier, data source and "times are as reported" in `footer`. Write `description` as a short narrative of the chain and list every assumption there.

## Common mistakes

- Showing a failure with a red card or red palette only, with no state badge, status symbol or label.
- Using `down` for a degraded component, or leaving partial impact unmarked. Degraded and failed are different facts.
- Putting `blocked` on the downstream behind an open circuit breaker. The downstream is `down`; the breaker belongs at the caller's end.
- Numbering contributing factors after the trigger, so the chain reads as "the trigger caused the factors".
- Drawing the causal chain with unlabelled `data` arrows and no legend, so it reads as request flow.
- Inventing a root cause, a missing alert or a contributing factor the brief did not state.
- Marking components as SPOFs because failover was not mentioned. Ask instead.
- Putting every dependent inside the blast radius, including ones that only degraded.
- Naming an individual or drawing "human error" as the cause.
- Putting monitoring, alerting or the on-call engineer inline in the request path.
- Captioning a 24×24 marker, which leaves no room for the icon and raises `text_height`.
- Drawing a circuit breaker, retry or timeout as a card between caller and callee, which reads as an extra hop.
- Spacing steps to suggest elapsed time. Position means order, not duration.
- Showing the post-fix component in the incident view, or omitting what changed in the after view.
- Filling an unknown dependency with a typical one, such as a cache or message queue the brief never mentioned.

## Start from

- `software-overview` for the component layout of a SPOF review, a blast-radius map or a dependency impact graph; add states, markers and the boundary group.
- `observability-pipeline` when the story is about detection: which signal fired, which did not, and how late.
- `backup-dr` for failover, replication and recovery in a before/after remediation view.
- `sequence-request` for a retry storm or cascading timeout where call order matters.
- For a pure causal chain there is no template yet; use `layout_diagram` and then number the steps.

Read alongside: `brief` for the ask-first rule; `business-process` for decision cards in a response runbook; `style` for spacing and legends.
