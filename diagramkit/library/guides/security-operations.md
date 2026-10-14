# Security operations: detection, response and vulnerability management

> Use this guide when the diagram shows the systems of a security operation as an architecture view: telemetry feeding a SIEM, automated or analyst-driven containment, identity, cloud, data-loss or phishing response, threat hunting and evidence retention, ransomware recovery, the vulnerability management lifecycle, or a honeypot or sandbox flow.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. The user can answer "yes to all" or correct any of them.

1. Which scenario is this: alert pipeline, identity compromise, cloud detection, data loss, phishing report, threat hunt, forensics and evidence, ransomware recovery, vulnerability lifecycle, or deception and detonation? (default: the alert pipeline only; other scenarios become separate diagrams)
2. Which log and telemetry sources feed the pipeline, and how many of each? (default: only the sources the brief names; if none are named, ask rather than drawing a firewall, identity provider and server logs as filler)
3. How does each source reach the SIEM: straight, through a collector or forwarder, or, for cloud and SaaS sources, by an API pull or a cloud event stream? (default: straight to the SIEM unless a collector or forwarder is named; cloud and SaaS sources connect to the SIEM directly with an edge labelled "API pull")
4. Which security tools exist, and in what order does an event pass through them: SOAR, EDR, NDR, UEBA, a threat intelligence feed, a data lake? (default: only the tools the brief names; if SOAR is not named, there is no SOAR box)
5. What issues a response action: a separate SOAR, automation built into the SIEM, or an analyst, and which steps run without a person? (default: an analyst issues containment; if SOAR is named, it enriches and opens a case automatically)
6. Which containment actions exist, and which enforcement point carries out each one: block on a firewall or IPS, isolate a host on EDR, quarantine on NAC, disable an account or revoke sessions at the identity provider, reset MFA? (default: only the actions the brief names, each carried out by the enforcement point the brief names; an IDS is passive, fed from a tap or mirror port)
7. Which actions need human approval, and does a condition such as detection confidence, asset criticality or an approval time-out decide between automatic and approved? (default: every action that disconnects a host, disables an account or blocks traffic needs approval, with no condition)
8. Where do cases go, and how do findings flow back into detection? (default: one ticketing system for SOC cases and IT tickets; a feedback edge from the closed case to the SIEM labelled "Tune rule"; no rules repository)
9. Who owns the SOC, and how many environments are in scope: in-house team, managed detection and response provider, or a split; one site or several sites, tenants or clouds? (default: in-house, one environment, one boundary around the SOC tooling)
10. Where is data kept beyond the SIEM: a data lake or search index for hunting and long retention, an evidence store for forensics, immutable backup for recovery? (default: the SIEM only; no evidence store or backup unless the scenario needs it)
11. For vulnerability management: which scanners run (network, authenticated host, container image, code in CI), where does the asset owner come from, how are findings prioritized, who remediates with which tool, is there a risk-acceptance path, and how is the fix verified? (default: one network scanner; owner from an asset inventory; tickets to the owner; patch management applies the fix; no exception branch; a rescan verifies)
12. For phishing, deception or detonation: how do users report suspicious mail, is the sandbox inline or out of band, is the honeypot an internet-facing research decoy or an internal deception decoy, and is it low or high interaction? (default: users report to a mailbox that opens a case; sandbox out of band, receiving copies from the email or web gateway; honeypot is a low-interaction internal decoy inside the segment it protects, alerting the SIEM)

## Push back when

- The brief has the SIEM blocking traffic or isolating hosts by itself. A SIEM does not enforce; the firewall, EDR, identity provider or NAC does. Ask what issues the action: a separate SOAR, automation built into the SIEM, or an analyst.
- The brief has an IDS on a tap or mirror port stopping an attack. A passive sensor sees a copy of traffic and cannot drop packets; at most it resets sessions or asks a firewall to block. Ask whether the sensor is inline (IPS) or passive.
- The vulnerability scanner is drawn applying patches. The scanner role finds and reports; patch or configuration management remediates, and a later scan confirms. If the platform has a patch module, draw it as a node separate from the scanner role.
- Legitimate users or services would route to a decoy, or a high-interaction honeypot has unrestricted outbound access. A decoy works because no legitimate traffic reaches it, and a high-interaction honeypot needs egress containment so an attacker cannot use it as a pivot. Ask where it sits and what it may reach.
- An out-of-band sandbox is drawn as protecting delivery. If the gateway does not hold the file until the verdict arrives, the sandbox detects after delivery and cannot stop it. Ask whether the gateway waits.
- The brief says the same action is both automatic and approved by an analyst. Ask what condition decides between them (confidence, asset criticality, time-out); do not reject the brief.
- Ransomware recovery is drawn from backups the attacker could reach. Recovery depends on copies that cannot be altered or deleted from the compromised environment. Ask whether the backup is immutable or isolated.
- The brief wants the process with named roles, hand-offs and SLAs. That is a business process and belongs in a swimlane drawn with the `business-process` guide; this guide is the system view. Offer both as separate diagrams if needed.

## How we draw it here

Write the one-sentence meaning first, for example "Telemetry reaches the SIEM, SOAR proposes containment, and an analyst approves it before the firewall blocks the host."

Layout runs left to right in stages, each a `panel` group: sources, collection and detection, triage and response, enforcement points. Use `boundary` groups only for real ownership or trust boundaries (corporate network, cloud tenant, managed provider), and give each a title. A boundary is a label, not a control.

A system that both emits telemetry and enforces (firewall, EDR, identity provider, NAC) is drawn once. Put it in the enforcement panel with an outgoing data edge to the SIEM or collector and an incoming control edge. Draw two nodes only when the user confirms two separate instances.

Asset roles:

- Sources: `security/firewall`, `security/waf`, `security/edr`, `security/dlp`, `security/casb`, `identity/identity-provider`, `observability/logs`, `observability/audit-log`, `observability/netflow`, `cloud/saas`, `cloud/vpc` for cloud control-plane logs, or a server card such as `compute/rack-server` labelled with what it is.
- Network detection: `security/ids` fed by `network/network-tap` with a data edge; label it "NDR" when that is what the user has. Packet forensics: `observability/packet-capture`.
- Collection and detection: `observability/collector`, `security/siem`. UEBA: `software/microservice` labelled "UEBA" beside the SIEM. Detection rules as code: `devops/git-repository` labelled "Detection rules".
- Threat intelligence: `software/external-service` labelled with the feed, joined by a `dependency` edge labelled "Enrichment" into the SIEM or SOAR.
- Hunting and retention: `data/data-lake` or `data/search-index`; evidence in `storage/object-store` labelled "Evidence store"; log integrity records in `observability/audit-log`.
- Alerting and cases: `observability/alert`, `observability/incident`, `business/ticket`, `observability/dashboard` for SOC views, `business/report` for periodic reporting.
- Automation: `security/soar`, with `software/workflow` for a specific playbook. When automation is built into the SIEM, nest `security/soar` inside a SIEM boundary or issue the control edge from `security/siem`. Show `identity/secrets-vault` or `identity/service-account` as a dependency if credentials matter.
- People and decisions: `identity/user` labelled "SOC analyst"; `ai/human-approval` or `business/approval` for an approval step; `presentation/decision` as a `symbol` with a question caption ("Contain host?") and labelled branches. A conditional playbook uses a decision with an "Automatic" branch straight to the control edge and an "Approval" branch through the approval node.
- Enforcement and containment: `security/firewall`, `security/ips`, `security/waf`, `security/ddos-protection`, `security/edr`, `security/nac`, `security/dlp`, `security/casb`, `identity/identity-provider` (disable account), `identity/access-token` (revoke), `identity/mfa` (reset), `security/quarantine` for the isolated segment or state.
- Phishing: `identity/user` reports `business/email`; `security/security-gateway` as the email gateway, `security/sandbox` for detonation, then a control edge "Purge" or "Block sender".
- Recovery: `storage/immutable-backup` with a control edge labelled "Restore" to the rebuilt system.
- Vulnerability management: `security/vulnerability-scanner`, `devops/sast`, `devops/sca`, `devops/dast`, `devops/sbom`; `data/relational-db` labelled "Asset inventory" for owners; `business/ticket`; `compute/rack-server` labelled "Patch management" for host fixes; `devops/infrastructure-as-code` only for cloud configuration and image fixes; `devops/pull-request` and `devops/ci-build` for code fixes; a rescan edge back to the scanner. A risk-acceptance path is a decision with "Remediate" and "Accept risk" branches, the second ending at `business/approval`.
- Deception and detonation: `security/honeypot`, `security/sandbox`, `security/threat-actor`, and `security/firewall` labelled "Egress control" for a high-interaction honeypot.
- State: `status/healthy`, `status/warning`, `status/blocked`, `status/approved`, `status/pending` as small `symbol` nodes next to the thing they describe.

Edge meanings. Every edge renders blue unless `palette` is set; the kind changes only the dash pattern. Set the palette explicitly:

- `data` (default blue, no palette needed): telemetry, logs, alerts, findings and case records. Every source-to-SIEM path is a data edge.
- `control` with `palette: "orange"`: an action issued by SOAR, SIEM automation or an analyst to an enforcement point ("Block IP", "Isolate host", "Disable account").
- `feedback` with `palette: "red"`: case findings or false positives back to detection tuning, and a rescan result back to the vulnerability record.
- `dependency` with `palette: "slate"`: SOAR depends on a vault or service account; threat intelligence enrichment.

Destructive containment passes through a visible approval or decision node before the control edge, unless the user has confirmed the action is automatic; then label the edge "Automatic".

Add a legend whenever more than one edge kind appears, with each item's `palette` matching its edges and `dashed: true` for control, feedback and dependency. Use the `footer` to list assumptions the user did not confirm, and to state that symbols are generic roles, not products.

## Common mistakes

- Adding a collector, SOAR, EDR, NDR, UEBA, a threat intelligence feed or a data lake because a typical SOC has them. Ask instead.
- Routing cloud and SaaS sources through an on-premises collector when the SIEM pulls them by API.
- A control edge that ends at the SIEM, or that skips the enforcement point and goes straight to the affected host or account.
- Drawing the same firewall, EDR or identity provider twice, once as a source and once as an enforcement point.
- Drawing telemetry as control edges, or containment actions as data edges.
- Leaving edge palettes unset, so every edge renders blue and the legend does not match.
- Showing containment with no approval node, or writing "analyst approves" only as an edge label.
- Using `observability/alert` or `security/ids` as a stand-in for the SIEM, or `security/security-gateway` as a generic box for NDR, UEBA or any other tool.
- Using `security/quarantine` as the tool that isolates; it is the isolated zone or state, and the tool is the enforcement point.
- Drawing `devops/infrastructure-as-code` as the fix path for host patches, or leaving out triage between scan and ticket.
- Leaving out the feedback loop, or drawing it as a data edge.
- Routing many sources into the SIEM along one shared segment, which reads as one feed. Give each its own edge or merge them at a named collector.
- Placing `security/threat-actor` inside the trust boundary when the story is an external attack.
- Drawing roles as lanes in this view. Use panels here and the `business-process` guide for the swimlane.

## Start from

- `observability-pipeline` for the telemetry, collection and alert half.
- `sec-incident-response` for the process with roles; it is a swimlane, so use it when the user wants the process view.
- `backup-dr` for ransomware recovery from protected backups.
- `threat-model-dfd` when the user wants trust boundaries and data flows rather than SOC tooling.
- Other scenarios (vulnerability lifecycle, phishing, threat hunt, honeypot and sandbox flows): no template yet; use `layout_diagram`.

Read alongside: `brief`, `style`, and `business-process` when the user also wants the people and hand-offs.
