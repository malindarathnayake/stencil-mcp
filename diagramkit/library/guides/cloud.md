# Cloud, hybrid and landing-zone architecture

> Use this guide for regions, availability zones, VPC/VNet and subnet layouts, peering and transit hubs, NAT and gateways, hybrid connectivity, landing-zone hierarchies, disaster recovery, serverless or SaaS integration, CDN and edge delivery, and C4 deployment views on a cloud.

## Questions to ask first

Ask only the questions the brief leaves open, in one round and numbered, so the user can answer "yes to all" or correct one.

1. Which cloud provider or providers does this describe, or should it stay provider-neutral? (default: provider-neutral labels such as "VPC" and "Dedicated circuit", generic icons)
2. How many regions are in scope, and what is each one for? For disaster recovery, what are the RPO and RTO, and is the standby pilot-light, warm or active-active? (default: one region, no disaster recovery drawn)
3. How many availability zones does the workload use in each region? (default: two)
4. How many VPCs or VNets are there, and which environment, account or subscription owns each one? (default: one VPC for the environment the brief names)
5. What are the CIDR ranges for each VPC or VNet, its subnets and the on-premises networks? (default: no CIDRs drawn; never invent ranges)
6. Which subnet tiers exist: public, private application, data, or others? (default: public and private application only; a data tier only if the brief names a database)
7. How does traffic enter from and leave to the internet: a load balancer, a NAT gateway, public addresses, or none? (default: only the paths the brief names; private subnets have no internet egress drawn)
8. How do VPCs reach each other: not at all, direct peering, or a transit hub? (default: no VPC-to-VPC connectivity)
9. How does on-premises reach the cloud: site-to-site VPN, dedicated circuits, or both? How many, from which sites, on which carriers, and where does each circuit meet the provider (colocation or connection location)? (default: two dedicated circuits from one datacenter, each drawn as its own physical line; redundancy stated as unknown, not called redundant)
10. How does name resolution work between on-premises and the cloud: private DNS zones, inbound or outbound resolver endpoints, conditional forwarders? (default: not drawn)
11. Where is traffic filtered: security groups, network ACLs, NSGs, VPC firewall rules, a central firewall in a hub, or a combination? (default: no filtering controls drawn unless the brief names them)
12. For a landing zone, what is the hierarchy and which shared accounts exist? (default: draw only the units the brief names. On AWS, propose the Control Tower layout: a Security OU with Log Archive and Audit, Infrastructure with Network and Shared Services, Workloads with Prod and Non-prod, and Sandbox. On Azure, propose the CAF management groups (Platform, Landing zones, Sandbox, Decommissioned). On GCP, propose a folder hierarchy. When provider-neutral, use "OU / management group / folder" and "account / subscription / project" wording)

Ask only the questions for the view chosen:

- a. Serverless and managed services: what triggers each function (HTTP, queue, event bus, schedule), is it synchronous or asynchronous, is the function attached to the VPC, where do secrets come from, and are managed services reached through private endpoints? (default: trigger as named, asynchronous only if a queue or bus is named, not VPC-attached, public endpoints not drawn as a separate path)
- b. SaaS integration: which way do calls go (we call the SaaS, the SaaS calls our webhook, or both), how is each side authenticated (OAuth, API key, mTLS), and is there an egress IP allowlist? (default: one outbound call, authentication labelled "unspecified")
- c. CDN: what is cached and what is passed through, where does TLS terminate, does the origin accept traffic only from the CDN, and is the WAF at the edge or regional? (default: CDN in front of one origin, no WAF unless named)
- d. C4 deployment: which environment is shown, and which containers run on which deployment node? (default: production, one node per container the brief names)

## Push back when

- The user asks for official AWS, Azure or Google Cloud icons. Tell them Stencil ships only generic symbols. Provider and service names go in the labels (for example "Transit gateway (AWS)"), and the footer states that the symbols are generic.
- The user expects traffic to pass through a peered network to reach a third network. Peering itself is not transitive. In AWS, traffic cannot transit a peered VPC at all. In Azure and GCP it transits only when something forwards it: a hub firewall or appliance with user-defined routes, gateway transit, or exported custom routes. Ask whether they mean a transit hub, a hub appliance that does the routing, or a mesh of direct peerings.
- Two networks that must be peered share overlapping CIDR ranges. Peering does not accept overlapping ranges, and NAT does not change that. Ask for the real ranges, or whether the networks connect through a transit hub with a private NAT, or through a private-link or endpoint service instead of peering.
- The user expects a NAT gateway to accept inbound connections from the internet. A NAT gateway carries connections started from inside outward; inbound access needs a load balancer, a reverse proxy or a public address.
- The brief calls one dedicated circuit, or two circuits on the same device or at the same location, redundant. Say that this is a single point of failure. Also ask whether the circuits use different carriers or paths and different cloud connection locations. A VPN backup through the same edge router shares that router's failure.
- The user assumes a dedicated circuit is encrypted. A private circuit is not encrypted by default. Ask whether IPsec or link-layer encryption runs over it, and label it only if it does.
- The brief treats multiple availability zones as disaster recovery for a regional outage. Zones in one region protect against a zone failure, not a region failure. Ask whether a second region is in scope.
- The brief places one subnet across several zones without naming the provider. AWS confines a subnet to one zone; Azure and GCP subnets are regional. Ask which provider applies before drawing.
- The brief says a guardrail policy grants access to an account. Organisation-level guardrails such as deny policies restrict what accounts may do; access is granted by identity policies. Ask which of the two the user means.
- A VPC-attached function is drawn reaching the internet with no NAT. On AWS, a function attached to a VPC has no internet egress without a NAT path. Ask whether NAT exists or whether the function needs to be in the VPC.

## How we draw it here

Write the one-sentence purpose first, then choose the view. Most cloud requests fit one of these: a network view (regions, zones, VPCs, subnets, gateways), a hybrid view (sites, circuits, cloud edge), an organisation view (OUs, accounts, guardrails), or a request-flow view (edge, application, data, serverless, SaaS). Do not merge them into one dense picture; split into panels or separate diagrams.

Layout runs left to right: users or on-premises on the left, the cloud edge in the middle, workloads and data on the right. In an organisation view, the root and OUs run top to bottom.

Groups are flat. A node belongs to at most one group, and groups render in list order with an opaque fill, so a later group paints over an earlier one. List them as region, VPC, zones, subnets. Use `boundary` style for region, VPC, zone and subnet scope, and `panel` style for provider networks, environments and side-by-side panels. Start zone columns below the VPC title band, and start subnet boxes below the zone titles. Validation does not catch group-title collisions, so check titles after rendering.

The zone layout depends on the provider. Where subnets are zonal (AWS), draw each zone as a tall column across the VPC and each subnet as a box at the zone and tier intersection. Where subnets are regional (Azure, GCP, or provider-neutral by default), draw each subnet as a band across all zone columns and place workloads in their zone column. Set a node's `group` to the innermost box that fully contains it; validation reports a node that extends beyond its group. A gateway that straddles a boundary edge takes the enclosing outer group, or no `group`.

Count the groups before you start: the scene allows 40. Two AWS regions with three zones and three subnet tiers already use 28, so draw one region in detail and summarise the others.

Asset roles, all as exact catalog IDs:

- Locations and scope: `cloud/cloud-region`, `cloud/availability-zone`, `cloud/vpc`, `cloud/subnet`, `cloud/public-cloud`, `cloud/private-cloud`, `cloud/hybrid-cloud`, `cloud/datacenter`, `cloud/branch-office`, `cloud/edge-location`. Use them as small `symbol` nodes inside a group, or as cards in a summary view; the group title still names the scope.
- Gateways and connectivity: `network/internet`, `network/router` labelled "Internet gateway (AWS)", "Internet edge" (provider-neutral) or "Transit gateway", `routing/nat` for NAT, `network/vpn-gateway`, `cloud/dedicated-circuit`, `cloud/cloud-peering`, `network/border-router` for each on-premises edge router, `network/wan-provider` for a carrier, `cloud/datacenter` labelled "Connection location" between the carrier and the cloud gateway, `routing/route-table` and `routing/bgp` when routing is the point.
- Traffic entry: `network/load-balancer`, `network/api-gateway`, `network/reverse-proxy`.
- Security: `security/security-group`, `security/acl`, `security/firewall`, `security/waf`, `security/ddos-protection`, `security/policy-engine`, `devops/policy-as-code`.
- Identity: `identity/identity-provider`, `identity/federation`, `identity/service-account`, `identity/secrets-vault`, `identity/key`.
- Serverless and integration: `cloud/cloud-function`, `software/function`, `software/message-queue`, `software/event-bus`, `software/scheduler`, `software/webhook`, `cloud/saas`, `software/external-service`.
- Storage, data and logging: `storage/object-store`, `storage/block-volume`, `storage/backup`, `data/relational-db`, `data/key-value-db`, `data/cache`, `data/database-replica`, `observability/audit-log`, `observability/logs`, `security/siem`.

Gateway placement also depends on the provider. On AWS, put a NAT gateway inside the public subnet of each zone that uses it, because it is zonal. On Azure, put NAT beside the subnet it is attached to. On GCP, put a regional Cloud NAT beside the VPC edge. Place VPN or circuit gateways on the VPC or hub edge facing on-premises, and a transit hub between the VPCs it connects.

Filtering controls are enforcement points, not decoration. Draw them only where the brief names them, put the traffic through them or next to the tier they guard, and say what they allow in `detail`. AWS has security groups (stateful, per instance) and network ACLs (stateless, per subnet); a NACL `detail` says "stateless" and notes the return ports. Azure NSGs are stateful and attach to a subnet or a NIC. GCP firewall rules apply VPC-wide to tags or service accounts, so draw them at the VPC edge, not per subnet.

For a landing zone, draw each OU, management group or folder as a `boundary` group, and each account, subscription or project as a component card with a clear label and a role icon (`observability/audit-log` for log archive, `security/siem` for security tooling, `network/router` for the network hub). Draw guardrails as `security/policy-engine` or `devops/policy-as-code`, with `control` edges to the units they apply to.

There is no DNS, anycast or private-endpoint icon. Draw DNS as `software/external-service` labelled "DNS resolver" or "Private DNS zone", anycast as a label on `cloud/edge-location`, and a private endpoint as `hardware/nic` labelled "Private endpoint" inside its subnet.

For CDN delivery, draw users, then `cloud/edge-location` cards for points of presence, then `data/cache` labelled "Origin shield" if there is one, then the origin; label where TLS terminates. For a C4 deployment view, draw deployment nodes as `boundary` groups and containers as `software/*` or `data/*` cards, with the technology in `detail`.

Connectors: `physical` for circuits, cross-connects and provider links, one line per circuit; `data` for requests and payloads, labelled with the protocol or purpose; `tunnel` for IPsec VPNs and other encapsulated paths; `control` for guardrails, route advertisement and configuration; `replication` for cross-zone or cross-region replication, labelled with the RPO if known; `dependency` for relations such as a function depending on a secret.

Use one palette per meaning, for example blue for private paths, slate for internet paths and orange for control. Add a legend whenever more than one connector meaning or palette appears. Keep the template footer, "Illustrative architecture. Labels describe roles; generic symbols do not assert product compatibility.", and add the provider name when labels name provider services.

## Common mistakes

- Adding a NAT gateway, WAF, CDN, bastion host, security groups or an extra firewall because reference designs have one. Draw only what the brief names; ask about the rest.
- Inventing CIDR ranges, or accounts and OUs the brief did not name.
- Drawing Azure or GCP subnets inside one zone column, or an AWS-style internet gateway and public subnet for Azure or GCP.
- Drawing a subnet box outside its VPC or zone box, or giving a node an outer group so that validation passes while the picture is wrong.
- Listing zone or subnet groups in an order that paints over the VPC or zone titles.
- Exceeding the 40-group limit by drawing every region, zone and subnet for every environment.
- Drawing transitive routing through a peering connection, or NAT on a peering link.
- Routing two circuits or two tunnels along one shared line, or ending both on one router, so that they read as one redundant link. Give each its own router, ports or waypoints.
- Drawing a circuit straight from the datacenter into the VPC with no carrier or connection location.
- Using `cloud/public-cloud` as a stand-in for a region, VPC or account, `security/firewall` for a security group or ACL, or an unlabelled `network/router` for a gateway.
- Showing a dedicated circuit as encrypted when the brief did not say so.
- Leaving out the internet, on-premises or SaaS side, so gateways appear to connect to nothing.

## Start from

- `hybrid-cloud` for on-premises to cloud with an internet edge. It collapses the circuits into one `cloud/dedicated-circuit` card and ends them on one border router. Split that into one node or edge per circuit, and one edge router per circuit when the brief names them.
- `segmented-network` for tiered trust zones (public, application, data) inside one environment.
- `event-driven` for serverless and queue-based integration, and `backup-dr` for replication and recovery.
- No template yet for a multi-region VPC layout, a hub-and-spoke network, a landing-zone hierarchy or CDN delivery; use `layout_diagram` for the initial positions, then add groups by hand.

Read alongside: `brief` first, `network` for routing and physical links, `security-architecture` for enforcement points and trust boundaries, and `style` last.
