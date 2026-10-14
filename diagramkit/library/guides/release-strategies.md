# Progressive delivery: canary, blue-green, feature flags and rollouts

> Use this guide when a diagram shows how a new version reaches users, devices or consumers at runtime: a blue-green switch, a weighted canary, a rolling update with an analysis loop, region or ring waves (including device firmware), phased mobile or frontend releases, serverless traffic shifting, feature flags, A/B experiments, shadow traffic or automated rollback. For build pipelines, supply chain and GitOps, read the devops guide instead.

## Questions to ask first

Ask in one round, and only ask what the brief leaves open. Skip questions about scenarios that are clearly out of scope.

1. Which strategy is this: blue-green, canary, rolling update, region or cell waves, device or firmware rings, a mobile phased release, a web frontend served through a CDN, serverless traffic shifting, a progressive config or flag change, an A/B experiment, shadow traffic, or a mix? (default: canary with progressive traffic weights)
2. Is the new version a request-serving service, or a message consumer or batch job? (default: a request-serving service behind a split point)
3. Where is the split made: a load balancer, a Kubernetes ingress or Gateway API route, a service mesh, weighted DNS, a function alias or revision split, a CDN, an app store, an OTA update service, or a flag evaluated in the client or service? (default: one load balancer or ingress in front of both versions)
4. What are the weights or ring sizes, and how many steps are there? (default: canary 1%, 10%, 50%, 100%; rings "internal", "early adopters", "general availability")
5. What promotes the release to the next step: automated metric analysis, an SLO check, a manual approval, or a timer? (default: automated analysis of error rate and latency at each step; no manual gate unless the user names one)
6. What triggers a rollback, and what does rollback actually do? (default: an SLO breach during analysis sets the new version's weight to 0% and scales it down; data and schema changes are not reverted)
7. Do both versions share one data store, or does each have its own? If they are separate, how is data synced, and what happens on rollback to writes made after the switch? Is any schema change backward-compatible? (default: one shared database, with changes following expand/contract so both versions can run at once)
8. What is the unit of the split: requests, connections, users, tenants, devices, or consumer instances or partitions? (default: per request for stateless APIs; per user, by a hash of the user ID or a cookie, for user-facing apps)
9. For blue-green: how is the idle environment tested before the switch, and how long is the old one kept running afterwards? (default: green is checked through a preview endpoint, and blue stays running until a bake period ends; that period is the rollback window)
10. Which of these are in scope: feature flags (and where they are evaluated), shadow traffic (and how its side effects are isolated), and the pipeline that builds the artifact? (default: none of them; the diagram starts at the artifact registry)
11. For device or firmware rings: how many devices are in each ring, how often do devices check in, do they have A/B partitions, and is anti-rollback (version counters) enforced? (default: three rings, devices poll an update service, A/B fallback on each device, and recovery is a roll-forward to a fixed version)

## Push back when

- **Blue-green with a shared database and a breaking migration.** Switching back to blue only works if blue can still read and write the schema that green left behind. Tell the user to use expand/contract: add the new schema in a compatible way, release, migrate the data, and remove the old schema only after the old version is retired. Otherwise, label the rollback path "not possible after migration".
- **Blue-green with separate databases.** Writes made to green after the switch do not exist in blue. Ask how data is replicated or reconciled. Without that, rollback loses those writes or the two copies diverge.
- **Canary with no automated metric gate.** With no promotion signal, the canary is a staged rollout that depends on someone watching. Ask what decides promotion, or label the gate "manual review" so the diagram does not imply automation that does not exist.
- **Session affinity with no stable assignment key.** Cookie or connection stickiness only applies weights to new sessions. Existing sessions stay where they are, including during a rollback, so the real share drifts from the configured weight. Suggest a deterministic cohort assignment, such as a hash of the user ID, and label the edge "by user hash, 10%".
- **"10% canary" with a plain Kubernetes rolling update or Service.** A Service spreads traffic across ready pods, so the share follows pod counts (one new pod out of three gets about a third). Precise weights need an ingress, a Gateway API route or a mesh that supports weighting.
- **Weights on long-lived connections.** kube-proxy, L4 load balancers and many proxies balance connections, not requests. gRPC, HTTP/2 and WebSocket clients hold one connection, so the weights apply to connections, and a weight change or rollback does not move existing connections until they close. Request weights need an L7 proxy or mesh that balances per request, and rollback must drain or reset connections. Label the edge with the real unit.
- **A weighted split in front of a queue consumer or batch job.** An ingress or mesh cannot weight work that consumers pull from a queue. The canary share is the share of consumer instances or partitions, and both versions must accept the same message format in both directions.
- **Fast rollback through DNS weights.** Resolvers and clients cache records, and some ignore the TTL, so a DNS shift takes effect gradually. It cannot be relied on for an immediate rollback.
- **Rolling back a mobile app.** A shipped binary cannot be recalled. A phased release can only be halted, and rollback means a kill switch through remote config or flags, followed by a fixed release.
- **Instant rollback of a web frontend behind a CDN.** Cached bundles and open browser tabs keep running the old code. Both frontend versions must work against the API that is live.
- **An A/B experiment presented as a safety canary.** An experiment assigns users to stable groups and is judged on statistical significance for a business metric. A canary is judged on error and latency SLOs. Ask which one the user means.
- **Instant firmware rollback across a fleet.** Devices only receive a rollback on their next check-in, and offline devices do not receive it at all. An A/B partition only recovers from a failed boot or health check, not from a bad image that boots and runs. If anti-rollback is enforced, an older image cannot be installed, so recovery is a roll-forward.
- **Feature flags as a security boundary.** A flag selects a code path; it is not authorization. Users can read and change client-side flags, and the hidden code is still deployed. Access control belongs in an enforcement point (see the security guides).
- **Shadow traffic that writes.** A mirrored request repeats its side effects (payments, emails, writes) unless the shadow version is isolated or stubbed. Ask how this is prevented, and draw the shadow's responses as discarded.
- **A 1% canary on low traffic.** A handful of requests does not give a meaningful error rate. Suggest a longer bake time or a larger first step rather than drawing a gate that cannot decide.
- **"Automatic rollback undoes everything."** Rolling back code does not revert migrations, messages already sent, or data written by the new version. Say this in the footer.

## How we draw it here

- **Direction.** Left to right: users, devices or producers, then the split point, then the versions, then shared dependencies. Put the controller below the split point and the metrics below the versions, so the analysis loop forms a closed rectangle under the main flow.
- **Versions.** Draw the stable and new versions as separate cards, stable above new, with the version and role in `detail` (for example "v2.3.1 · stable" and "v2.4.0 · canary"). Use `kubernetes/deployment` inside a cluster, `software/microservice` or `software/backend` elsewhere, `cloud/cloud-function` for serverless, and `software/background-worker` for consumers. For a rolling update, show individual `kubernetes/pod` cards with their version.
- **Split point.** Use `network/load-balancer`, `kubernetes/ingress`, `kubernetes/gateway-api`, `network/reverse-proxy` or `network/api-gateway`, whichever the user named. There is no DNS or alias symbol: use `software/external-service` labelled "DNS (weighted records)" or "Function alias (weighted)". Use `cloud/edge-location` labelled "CDN" for frontends, and `software/external-service` labelled "App store phased release" for mobile.
- **Kubernetes weighted routing.** Route weights point at Services, not Deployments. Draw two `kubernetes/service` cards ("stable", "canary") between the split point and each `kubernetes/deployment`, and put the weights on the split point to Service edges.
- **Consumers.** The queue is the split point: `software/message-queue` or `software/topic`, with a `data` edge to each version's workers. Put the instance or partition share in the caption, not as a percentage weight on the edge.
- **Device rings.** There is no load balancer. The split point is an update service, `software/backend` labelled "OTA update service" (or `devops/cd-release`), fed by `devops/artifact-registry`. Draw device to service for the check-in and service to device for the image, as `data` edges labelled with the ring size. Use one representative `fleet/vehicle`, `fleet/telematics-unit` or `compute/edge-server` per ring. A device's self-rollback is a `feedback` edge or a `status/down` symbol with a note "A/B fallback (failed boot only)". With anti-rollback, label recovery "roll forward to vN+1".
- **Clients.** Use `identity/user` or `identity/group` for people and cohorts, `compute/mobile` for app users, and `software/browser` or `software/frontend` when a client evaluates flags.
- **Controller and gates.** Use `kubernetes/operator` for an in-cluster rollout controller (Argo Rollouts or Flagger are examples) and `devops/cd-release` for a delivery system outside the cluster. Use `devops/release-approval` for a manual gate, `presentation/decision` with a caption such as "Ring 1 healthy?" for an automated gate between rings or regions, and `devops/rollback` for the rollback action.
- **Signals.** `observability/metrics` is the analysis source. Add `observability/alert`, `observability/health-probe` or `observability/dashboard` only when they act in the loop, and `resilience/autoscaler` only if scaling is part of the story.
- **Feature flags.** There is no flag symbol. Use `software/microservice` labelled "Flag service" (or `software/external-service` if it is hosted), with `kubernetes/configmap` only when the flags really live in one. Mark a kill switch with a small `status/blocked` symbol next to the flagged path.
- **State.** Small `status/healthy`, `status/warning`, `status/down`, `status/pending` or `status/approved` symbols beside a version or ring show its result. Draw shared data as `data/relational-db` or `data/cache`. When blue and green have separate stores, connect them with a `replication` edge.
- **Edges.** Use `data` (solid, blue) for live traffic, with the weight in the label ("90%", "10%"). Use `data` with `palette: "slate"`, labelled "metrics / SLIs", from each version to `observability/metrics`. Use `feedback` with `palette: "teal"` from metrics to the controller for the analysis result, and `control` with `palette: "orange"` for promotion and weight changes. Shadow traffic is a `data` edge with `palette: "purple"` labelled "Mirrored copy, response discarded". A blue-green pre-switch check is a `data` edge labelled "preview / test" into the idle group.
- **Rollback.** Draw rollback as its own `control` edge with `palette: "red"`, labelled with the trigger and action, such as "SLO breach: weight to 0%". Promotion runs from the controller's `n` port to the split point's `s` port. Rollback must not use those ports: place `devops/rollback` above the split point and draw it into the split point's `n` port, with the controller reaching it from its `w` port. Set `source_port`, `target_port` and `points` explicitly on both edges.
- **Groups.** For blue-green, use two `boundary` groups titled "Blue (live)" and "Green (idle)", or two `panel` groups showing before and after the switch. For rings or region waves, use one `panel` per ring or `cloud/cloud-region` from left to right, with the size in the caption and a gate between them. A process view of approvals uses `lane` groups.
- **Legend and footer.** Add a legend whenever more than one edge meaning appears, with `dashed: true` for the control, feedback and rollback entries and an entry for the metrics edge. The footer states the strategy, the split unit, that the weights are illustrative, the data-compatibility assumption, the rollback window, and that rollback does not revert data.

## Common mistakes

- Drawing one service card with "v1/v2" in the label instead of two version cards, which hides where the split happens.
- Putting weights in the card detail instead of on the traffic edges, or using weights that do not add up to 100% at a given step.
- Leaving `control` and `feedback` on the default palette, so promotion and analysis lines look identical.
- Leaving the versions-to-metrics leg out, or drawing it as blue `data` that looks like user traffic.
- Drawing the analysis loop from metrics straight to the split point, skipping the controller that actually decides.
- Merging rollback into the promotion edge, sending both edges to the same port, or leaving rollback out when the brief mentions it.
- Drawing one Kubernetes Service in front of both deployments while still claiming exact weights.
- Putting a load balancer in front of a queue consumer, or in front of devices that pull firmware.
- Drawing rollback arrows to every device, or a percentage weight on an OTA delivery edge.
- Using `security/policy-engine` or `security/acl` for a feature flag, which suggests a security control.
- Using `resilience/failover` or `resilience/active-passive` for blue-green; those describe availability, not a release switch.
- Using `devops/ci-build` or the whole pipeline when the brief is about runtime traffic shifting.
- Drawing shadow traffic as a normal request whose response returns to the user.
- Showing every device in a firmware ring, rather than one representative device with the count in the caption.
- Adding a mesh, a database, a manual gate or session affinity that the user never mentioned; ask instead.

## Start from

- `kubernetes-ingress` when the split happens at a Kubernetes ingress or route. Replace its single `kubernetes/service` with a stable and canary pair.
- `event-driven` when the new version is a queue or stream consumer.
- `secure-ci-cd` when the diagram must show how the artifact arrives before the rollout.
- `eng-platform-delivery` for an approval or wave process drawn as swimlanes.
- Otherwise: No template yet; use `layout_diagram`.

Read alongside: `brief` and `style` first, then `devops` for pipelines and GitOps. Call `stencil_guide` with no topic to see whether `kubernetes` and `observability` guides are available for the split point and the analysis loop.
