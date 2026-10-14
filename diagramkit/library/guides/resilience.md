# Disaster recovery, backup and resilience patterns

> Use this guide when the diagram shows recovery sites or regions, replication, backups and retention, a failover or failback sequence with RTO/RPO, or runtime resilience policies such as retry, circuit breaker, timeout, rate limiting, autoscaling and health checks.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. Skip any question the brief already answers.

1. Which sites, regions or zones exist, and what is in each one? (default: draw only the locations the brief names; if it names one site, draw no recovery site)
2. Is the deployment active-active (both sides serve traffic) or active-passive? If active-passive, how ready is the standby: hot (full capacity, receiving data), warm (scaled-down capacity, receiving data), pilot light (data replicated, compute off) or cold (rebuilt and restored from backup)? (default: draw a standby only if the brief names a second site, and caption it "standby readiness not stated" rather than picking one)
3. For each replicated system, what is the replication mode and direction: synchronous, semi-synchronous, asynchronous, or quorum/consensus; one-way or bidirectional; and which side is the source? (default: asynchronous, one-way from primary to recovery, labelled "async")
4. What are the RPO and RTO targets, and do they differ per workload? (default: no numbers; the callout says "RPO/RTO not stated" rather than inventing values)
5. What backup copies exist, how many, on which media, and where? Is any copy immutable or offline (object lock, WORM, tape)? Is the backup copy in a separate account or tenant with separate credentials, and where do its decryption keys live? Is a restore test part of the process, and where does the restored copy land? (default: only the copies the brief mentions; no immutable copy, tape or restore test unless named)
6. What is the backup schedule and retention, are snapshots used as well, and are transaction or log backups or point-in-time recovery used, and how often? The backup RPO is the log interval if they are used, otherwise the backup interval. (default: omit schedule and retention text rather than guess it)
7. Is failover manual (a person decides) or automatic, and what triggers it? If automatic, what acts as the witness or quorum? Should failback, and the data resynchronisation before it, be shown? (default: manual with an explicit human decision step; failover only, failback noted in the footer as out of scope)
8. How is traffic redirected on failover (DNS with what TTL, global load balancing, anycast or BGP, a connection string change), and how is the old primary fenced so it stops accepting writes? (default: show a "Repoint traffic" control step with the mechanism marked "not stated")
9. For runtime policies, which specific call does each retry, timeout, circuit breaker or rate limiter govern, and on which side (caller or callee) is it enforced? (default: draw only the policies the brief names, on the caller side of the call it names; ask before adding any other policy; if a retry is drawn and idempotency is not stated, caption it "idempotency not stated")
10. What drives the autoscaler, which metric and what scales (pods, instances or nodes), and are there minimum and maximum counts? (default: CPU metric scaling service instances; no counts shown)
11. What does the load balancer health check probe, and what happens to a failing target, and to the pool when every target fails? (default: an HTTP readiness endpoint on each target; failing targets are removed from rotation, not restarted)

## Push back when

- **Synchronous replication over a long distance.** Each write waits for the remote acknowledgement, so write latency grows with round-trip time. Tell the user synchronous replication is normally limited to short distances unless the database uses quorum commit and they accept the write latency, and ask whether they mean asynchronous replication to the distant site.
- **Synchronous replication claimed as RPO 0 with no failure behaviour stated.** Ask what happens when the replica is unreachable: does the primary stop accepting writes, or fall back to asynchronous? Many products fall back by default, and RPO 0 no longer holds while they do.
- **Asynchronous replication with "zero data loss" or "RPO 0".** Asynchronous replication can lose writes that had not shipped when the primary failed. Ask whether the link is really synchronous, or whether the RPO should be stated as non-zero.
- **RTO shorter than the recovery mechanism allows.** Restoring a large dataset from backup or tape, or provisioning a cold or pilot-light site, takes hours. Ask how long a restore or scale-up took in a test, and whether capacity in the recovery region is reserved.
- **Replication drawn as the backup.** Deletions, corruption and ransomware encryption replicate to the copy. Tell the user replication protects against site loss, not bad writes, and ask whether separate backups exist.
- **Snapshots on the same array called a backup.** A snapshot on the same storage system fails with that system. Ask whether snapshots are copied elsewhere.
- **"Immutable" or "offsite" backups reachable with production credentials.** Ask whether the copy is in a separate account or tenant, whether object lock is in compliance mode or governance mode (privileged users can bypass governance mode), and whether the decryption keys survive loss of the primary site or account.
- **"3-2-1" claimed with copies that do not meet it.** 3-2-1 means three copies of the data, on two different kinds of media, with one copy offsite. Point out which part is missing rather than labelling the design 3-2-1.
- **Active-active writes to one database with only one-way replication.** Two sites cannot both accept writes for the same data unless the database supports multi-writer operation or conflict handling. Ask which site owns writes, or how conflicts are resolved.
- **Automatic failover between two sites with no witness or fencing.** Without a third vote, a network split can leave both sides believing they are primary (split brain). Ask what provides quorum, and how the old primary is fenced so clients that still reach it cannot keep writing; otherwise draw the failover as manual.
- **Retries on non-idempotent calls, or retries at every layer.** Retrying a payment or order creation can duplicate it, and retries stacked at several layers multiply load during an outage. Ask whether the call is idempotent, which single layer retries, and for backoff with jitter and a retry budget or cap.
- **Autoscaling expected to fix a bottleneck in a shared dependency.** Adding instances adds load to a saturated database or downstream service. Say so and ask whether the dependency scales too.
- **A health check that fails all targets together.** If every target's probe calls the same shared dependency, one outage marks every target unhealthy at once. Depending on the load balancer, that empties the pool (Kubernetes readiness) or triggers fail-open routing to all targets (for example AWS ELB, Envoy panic mode). Ask what the probe checks and what the load balancer does when all targets fail.
- **Kubernetes liveness used for traffic removal, or checking dependencies.** A failing liveness probe restarts the container; a failing readiness probe removes the pod from service endpoints. A liveness probe that checks a database or downstream service restarts every pod repeatedly during a dependency outage. Liveness should check only the process; dependency checks belong in readiness, if anywhere. Slow-starting containers need a startup probe.

## How we draw it here

- **Direction.** Left to right: primary site on the left, recovery site in the middle, backup boundary on the right. For a call chain, caller on the left, dependencies to the right.
- **Grouping.** Each site, region or zone is a `boundary` group titled with its name (use `cloud/datacenter`, `cloud/cloud-region` or `cloud/availability-zone` as a card inside only when the location type matters). Backups get their own `boundary` group. Use `panel` groups for "Normal operation", "Failover" and "After failover" when one picture would overload.
- **Data systems.** `data/relational-db` (or the matching data type) for the primary; `data/database-replica` for replicas. Label the role ("Primary", "Standby replica, read-only").
- **Backups.** `storage/backup` for a backup copy or target, `storage/snapshot` for snapshots, `storage/immutable-backup` only for confirmed object-locked or WORM copies, `storage/tape-library` for tape, `storage/object-store` when object storage matters. Retention and schedule go in `detail`. A restore target is labelled as where data lands ("Restore target, isolated test environment"), not as a backup.
- **Resilience roles.** `resilience/failover`, `resilience/active-active`, `resilience/active-passive` and `resilience/disaster-recovery` as small `symbol` nodes with a `caption` when the pattern is the point. `resilience/replication` only as a marker on the replication path, never as the replica.
- **Runtime policies.** `resilience/retry`, `resilience/timeout`, `resilience/circuit-breaker` and `resilience/rate-limiter` as `symbol` nodes beside the edge they govern, near its midpoint, with no edge crossing the symbol; move the edge label with `label_x`/`label_y` if needed. Caption the setting ("3 tries, exponential backoff with jitter", "2 s timeout"). `resilience/autoscaler` sits next to the group it scales.
- **Traffic and health.** `network/load-balancer` in front of targets; `observability/health-probe` for the check; `observability/metrics` feeding the autoscaler; `observability/alert` and `observability/incident` when an alert triggers failover.
- **Decisions and steps.** `presentation/decision` with a question caption ("Declare disaster?") and labelled "Yes"/"No" branches for manual decisions; `ai/human-approval` or `business/approval` may mark the approver. Number steps with `presentation/step` or edge labels ("1. Fence old primary", "2. Promote replica", "3. Repoint traffic").
- **State.** `status/healthy`, `status/down`, `status/warning` and `status/pending` for before and after states; a `marker` node for the failure point.
- **Edges.** `replication` for replicated data, labelled with mode and direction ("async, primary to DR"). `data` for backup jobs and restores. `control` for failover commands, fencing, promotion and traffic redirection. `feedback` for health results and metrics driving the autoscaler. `dependency` for "requires" relations, such as the replica depending on the witness. `arrow: "both"` only for bidirectional replication the user confirmed.
- **Palettes.** One meaning per palette: for example teal for replication, purple for backup paths, orange for failover control, red for failure and loss, green for restore. Colour never replaces a label.
- **Callouts.** RPO and RTO in a `text` node or `presentation/callout` near the systems they apply to, one per workload when targets differ.
- **Legend and footer.** Add a `legend` whenever more than one edge kind appears, with `dashed` matching. The footer states assumptions ("Illustrative. RPO/RTO not stated in brief; failback not shown.").

## Common mistakes

- Adding a DR site, a second region, a tape library, an immutable copy or a restore test the brief did not mention, often by keeping template nodes unchanged.
- A replication edge with no direction or mode, or the template's bare "Replicate" label left unchanged.
- Implying zero RPO by drawing primary and replica as identical with no lag or mode stated.
- Drawing failover as one arrow labelled "failover" instead of numbered steps for detection, decision, fencing, promotion and traffic redirection.
- Hiding the manual decision; a failover that needs a person must show that decision explicitly.
- Showing backups with no restore path, or drawing the restore target with `storage/backup` so it reads as another backup copy.
- Using `storage/backup` for everything (snapshots, immutable copies, tape) when distinct assets exist, or `storage/immutable-backup` for a copy nobody said was locked.
- Using `data/database-replica` as a backup, or `resilience/replication` as the replica card.
- Floating retry, timeout and circuit-breaker icons in a corner instead of beside the call they govern, or placing them on the edge so it crosses the symbol.
- Adding a timeout, circuit breaker or rate limiter the brief did not name because "resilient calls usually have them".
- Drawing the autoscaler with a `data` edge to the service but no `feedback` edge from metrics, so nothing appears to drive it.
- Health-check edges drawn as `data` traffic instead of `feedback`, which reads as request flow.
- Two replication links between the same pair routed along one segment, which reads as a single link.

## Start from

- `backup-dr` for primary site, recovery site and backup boundary. Relabel replication edge `e1` with mode and direction, and replace the `rpo` text with the user's values or "RPO/RTO not stated". Change the `immutable` node to `storage/backup` (or whatever the brief names) unless the brief confirms object lock or WORM. Delete the `test` node and edge `e3` unless the brief mentions restore testing; when kept, relabel it as the restore target (for example an isolated test environment) with a matching data or compute asset, not as a backup. Delete the Recovery site group if the brief names only one site.
- No template yet for failover sequences, call-chain resilience policies, autoscaling or load balancer health checks; use `layout_diagram`, then split into panels.
- Read alongside: `brief` (confirming open facts), `style` (spacing, legend and footer), `network` (when sites are joined by drawn circuits or routing changes), and `business-process` (when the failover runbook is drawn as a swimlane across teams).
