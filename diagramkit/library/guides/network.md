# Network topology (L1/L2/L3, campus, data-centre fabric, WAN)

> Use this guide for physical and logical network drawings: campus, leaf-spine and Clos fabrics, AI and storage back-end fabrics, VLAN, LAG and HA domains, routing sessions, overlays and data-centre interconnect, WAN, SD-WAN, VPN, service-provider and peering edges, the internet edge and DMZ, wireless, management and monitoring, and packet walks.

## Questions to ask first

Ask these in one round when the brief leaves the fact open. Skip any the brief already answers.

1. Which layer does the diagram show: L1 cabling, L2 switching, L3 routing, an overlay, or one packet's walk through the network? (default: one layer per canvas; if two are needed, one panel per layer)
2. How many devices sit in each tier or site, what are they called, and is the fabric 3-stage or 5-stage with a super-spine or several pods? (default: the smallest count the brief implies, such as 2 spines and 4 leaves, 3-stage)
3. How many uplinks does each device have, to which devices, at what speeds, and are any bundled as a LAG, an MLAG pair, a stack or EVPN multihoming? (default: in a fabric, one link from each leaf to each spine; in a campus, one uplink per access switch unless dual-homing is stated; speeds unlabelled)
4. Which links are routed and which are switched, and is ECMP used across the routed uplinks? (default: routed point-to-point uplinks with ECMP in a leaf-spine fabric; switched trunks in a campus access layer)
5. Where is the default gateway for each VLAN: an HSRP or VRRP pair at distribution or core, routed access, or an anycast gateway on every leaf? (default: an FHRP pair on the distribution or core tier in a campus, an anycast gateway on the leaves in an EVPN fabric, shown as labels on the devices)
6. Which control-plane protocols run, between which devices, with which ASNs, areas, route reflectors or confederations? (default: no protocol sessions drawn; physical links only)
7. Is there an overlay or interconnect, and where do its endpoints sit: VTEPs, PE routers, SD-WAN edges, VPN gateways, or a data-centre interconnect between sites? (default: no overlay and no DCI)
8. Which VLANs, VRFs, VNIs or prefixes must appear, on which devices or links, and is the network IPv4, IPv6 or dual-stack? (default: none; devices labelled by role only; addressing family not stated)
9. Which devices are HA pairs (firewalls, load balancers, gateways), which unit is active, and which devices or links are deliberately single? (default: only the redundancy the brief states)
10. For an internet edge, how many ISPs are there, is BGP run to them with the site's own ASN, which controls sit in which order, and where do NAT and TLS termination happen? (default: one ISP with a static default route; internet, firewall, then the application tier, NAT on the firewall, no TLS termination drawn)
11. For WAN and branches, which underlay circuits does each site have, and is the overlay hub-and-spoke or full mesh? For a service provider, which routers are CE, PE and P? (default: one internet circuit per site and hub-and-spoke tunnels)
12. For wireless, how many APs are there, is there an on-premises controller at all or is it cloud-managed, is client traffic tunnelled to a controller or bridged locally at each AP, and which VLAN does each SSID map to? (default: no controller unless named; SSIDs bridged locally to the access VLANs; SSIDs only if named)
13. Are out-of-band management, 802.1X, multicast, QoS policy, monitoring (TAP, SPAN, NetFlow) or a DMZ in scope? (default: not drawn)

## Push back when

- Storage multipathing is attributed to ECMP alone. Host MPIO picks a path per session; in a routed fabric, ECMP places each iSCSI or NVMe/TCP session's flow on a path. FC and L2 dual-fabric SANs use MPIO only. Ask whether the storage network is routed and whether there are separate A and B fabrics.
- ECMP is expected to spread one flow over all paths. Flow-hash ECMP keeps a single flow on one next hop so its packets stay in order, and several flows can hash to the same path. Ask whether they mean per-flow hashing or per-packet spraying.
- Two redundant L2 links between switches are said to both forward without a LAG or MLAG. STP blocks one link per VLAN or MST instance (per-VLAN load balancing lets each link forward different VLANs), unless an L2 multipath fabric such as EVPN multihoming is used. With no STP it is a loop. Ask which applies.
- A LAG runs from one device to two independent switches. The two switches must be an MLAG pair (vPC, MC-LAG), a stack or virtual chassis, or EVPN multihoming peers sharing an ESI. Ask which.
- VXLAN is shown with no IP underlay, or EVPN is called the tunnel. VXLAN encapsulates traffic over a routed underlay; EVPN is the BGP control plane that distributes reachability. Draw them as separate things.
- iBGP peers form a partial mesh with no route reflector or confederation. iBGP does not re-advertise iBGP-learned routes, so it needs a full mesh, a route reflector or a confederation. Ask which.
- A route reflector is placed in the forwarding path. It reflects iBGP routes and does not need to carry the traffic. Ask whether the device really forwards data as well.
- An OSPF non-backbone area has no connection to area 0. Areas attach to the backbone through an area border router or a virtual link. Ask how it attaches.
- Traffic leaves through one firewall of a stateful pair and returns through the other. A stateful firewall drops return traffic it has no session for unless the pair shares state and handles asymmetric flows. Ask how the pair is clustered.
- Two firewalls are active-active with no state synchronisation. Sessions break when traffic moves between them or one fails. Ask whether state is synchronised or the pair is active-passive.
- A VLAN is stretched between sites with no interconnect named. L2 extension needs a DCI such as a dark-fibre trunk, VXLAN EVPN multi-site or VPLS. Ask what carries it.
- The design is called fully redundant but each VLAN has one gateway device. Hosts lose their gateway when it fails unless an FHRP or anycast gateway is used. Ask which.
- MPLS or a private WAN is described as encrypted by itself. An MPLS VPN separates traffic but does not encrypt it; encryption needs IPsec or similar. Ask what protects the traffic.
- RPKI is said to validate the whole AS path. Route origin validation checks only that the origin AS may announce the prefix. Ask which check they mean.
- A TAP or SPAN port is shown blocking traffic, or an IPS is drawn out of band and said to block. A copy of the traffic can only be inspected; blocking needs the device inline. Ask whether it is an inline IPS or an IDS.
- An SSID is treated as a security boundary on its own. Isolation comes from the VLAN, VRF, firewall or NAC policy behind the SSID. Ask what enforces it.
- RIP, IGRP or EIGRP is requested. Draw it as asked and label the protocol literally; do not swap in OSPF. Mention once, if relevant, that IGRP is obsolete or that RIP is limited to 15 hops.

## How we draw it here

- Layout: tiers run top to bottom, with the WAN or internet at the top, then core or spine, then distribution or leaf, then access and hosts. In leaf-spine, put border leaves in the leaf row, at one end or as a separate panel, and connect edge routers, firewalls, the WAN and DCI to the border leaves; connect them to spines only when the brief says so. An internet-edge chain or a packet walk may run left to right instead. Keep one direction per canvas.
- Grouping: racks, sites, pods, branches and tiers are `panel` groups. VRFs, AS numbers, OSPF or IS-IS areas, VLAN domains, DMZs, trust zones, MLAG pairs and HA pairs are `boundary` groups. When one diagram shows two layers, such as underlay and overlay, give each its own `lane` group or panel.
- Devices are `component` cards with explicit labels:
  - Switching: `network/leaf-switch`, `network/spine-switch`, `network/switch-l2`, `network/switch-l3`, `network/chassis-switch`.
  - Routing and WAN: `network/router`, `network/border-router`, `network/route-reflector`, `network/sdwan-edge`, `network/vpn-gateway`, `network/modem`, `network/wan-provider`, `network/internet`. CE, PE and P roles are `network/router` cards labelled with the role.
  - Internet edge: `security/ddos-protection`, `security/firewall`, `security/waf`, `security/ips`, `security/ids`, `network/load-balancer`, `network/reverse-proxy`, `routing/nat`.
  - Access control: `security/nac`, `security/acl`, `security/microsegmentation`; 802.1X uses `security/nac` with `identity/identity-provider` as the RADIUS or directory back end.
  - Wireless: `network/wireless-ap`, plus `network/wireless-controller` only when one exists.
  - Hosts: `compute/rack-server`, `compute/workstation`, `compute/laptop`, `compute/mobile`, `compute/edge-server`, `compute/compute-cluster`.
  - AI and RoCE back-end fabrics: `hardware/rdma-nic`, `hardware/smartnic`, `hardware/dpu`, `hardware/gpu`, with `protocol/ecn`, `protocol/pfc-pause` and `protocol/congestion` for lossless behaviour.
  - L1 detail: `hardware/nic`, `hardware/optical-transceiver`, `network/patch-panel`.
  - Sites, circuits and peering: `cloud/datacenter`, `cloud/branch-office`, `cloud/dedicated-circuit`, `cloud/edge-location` for CDN or anycast points of presence, `routing/peering` for an IXP or transit session.
  - Management: `compute/management-controller` for BMC or console ports, `compute/bastion-host` for the jump host into an out-of-band network.
  - Monitoring: `network/network-tap`, `observability/netflow`, `observability/packet-capture`, `observability/collector`.
  - HA: `resilience/active-passive`, `resilience/active-active` and `resilience/failover` symbols beside the pair's `boundary` group.
- Protocols and concepts go in `symbol` nodes with a `caption`: `routing/bgp`, `routing/ospf`, `routing/isis`, `routing/bfd`, `routing/rpki`, `routing/vrf`, `routing/vlan`, `routing/vxlan`, `routing/evpn`, `routing/vtep`, `routing/mpls`, `routing/srv6`, `routing/lag`, `routing/qos`, `routing/ecmp`, `routing/flow-hash`, `routing/route-table`. Congestion and loss on a path use `protocol/congestion` and `protocol/dropped-packet`.
- No icon exists for STP, FHRP (HSRP, VRRP, GLBP), multicast (PIM, rendezvous point) or IPv6; write them as device labels or `detail`, for example "VRRP active, VIP .1" or "STP: blocked for VLAN 20".
- Services with no dedicated icon (DNS, DHCP, NTP, IPAM) are `compute/rack-server` or `compute/virtual-machine` cards labelled with the service name. Static routes are a `routing/route-table` card listing the routes in `detail`. SSIDs, cable types and link speeds are labels, not icons.
- Edge kinds:
  - `physical` with `route: "straight"` for each cable or circuit, with no arrows.
  - LAG to one peer: the renderer draws every edge between the same two anchors on the same line, so member links would stack into one. Draw one `physical` edge labelled with the bundle and member count, such as "Po10: 2x100G LACP", and place a `routing/lag` symbol beside it. Draw separate edges only when the members end on different devices, as with MLAG or ESI legs, or use different `source_port` and `target_port` anchors.
  - `control` for protocol sessions (BGP, OSPF, IS-IS, BFD, route-reflector clients), drawn separately from the physical links. EVPN overlay sessions run loopback to loopback, so draw them as their own `control` edges apart from the underlay point-to-point sessions.
  - `tunnel` for VXLAN, MPLS LSPs, SRv6 paths, IPsec, SD-WAN tunnels and DCI, drawn between the tunnel endpoints with the underlay still visible.
  - `data` only when the point is traffic direction, such as one flow's path or a packet walk.
  - `dependency` for "relies on" relations, such as a switch that uses a RADIUS or DHCP server.
- Palettes: give each fabric, plane or uplink set its own palette (for example blue for links to spine A, green for spine B, teal and purple for storage fabrics A and B), red for security controls and slate for upstream providers, and explain every link palette in the legend.
- Labels: put prefixes, ASNs, VLAN IDs, VNIs, bundle names and speeds on edge labels. An edge has one label, so write interface names in the device `detail` or a `presentation/callout` (for example "Eth1/49 to SPINE-1"). Use `label_x` and `label_y` to move labels off busy crossings.
- Legend: required whenever more than one edge kind or link palette appears. Set `dashed: true` on control and tunnel entries.
- Footer: say what is illustrative and what is not shown, for example "One line per cable; bundles shown as one labelled line. Management network not shown. Single firewall as stated."
- Description: a plain narrative of the devices, counts and links that matches the picture.

## Common mistakes

- Several uplinks merged onto one shared horizontal line. That reads as a bus or one L2 segment. Draw each link as its own straight line fanning out between rows.
- Stacked parallel edges: two or more members of a LAG drawn as separate edges between the same anchors, which render as one line and hide links. Use one labelled bundle edge.
- ECMP drawn for switched traffic, or storage multipathing credited to ECMP alone in an FC or L2 dual-fabric SAN where only MPIO applies.
- Dual-homed campus access switches drawn with both trunk uplinks forwarding and no MLAG, stack or STP label.
- MLAG drawn with no peer-link or keepalive when it is not EVPN-based.
- WAN, internet or firewalls wired to the spines when the fabric has border leaves.
- Devices placed in a rack, site or tier the brief did not give them. Ask where they live.
- L1 cabling, L2 VLANs, L3 sessions and overlay tunnels mixed on one canvas with no panels, so a tunnel looks like a cable.
- BGP or OSPF sessions drawn as `physical` edges, or physical links drawn as `control`.
- An unused ECMP path hidden or faded because one flow did not take it. Keep every path visible and show hash collisions with labels.
- Internet edge in the wrong order, such as the WAF in front of DDoS protection, or NAT after the load balancer when the brief put it on the firewall.
- Invented extras: a management network, out-of-band switches, a wireless controller, a second firewall, an HA pair or a DMZ the brief did not mention.
- Stand-ins picked by guessing: `network/router` for a layer-3 switch or a DNS server, `network/switch-l2` for a leaf, `network/wan-provider` for the public internet, `security/firewall` for a router ACL, `security/ids` for an inline IPS, or `network/load-balancer` for a reverse proxy. Use the asset that matches the role, or ask.
- Branch tunnels drawn as `physical` links straight to the hub, with no underlay circuit shown.
- Wi-Fi drawn as a floor plan or coverage heatmap. Show APs, any controller, the SSID-to-VLAN mapping and guest isolation instead.
- Many links leaving one card from the same anchor. Anchors are only `n`, `e`, `s` and `w`; spread the devices wider, use a different anchor per plane, or split the drawing into panels.

## Start from

- Leaf-spine, Clos, AI and RoCE back-end fabrics: `leaf-spine`.
- ECMP and flow-hash explanations: `ecmp-flow-hashing`.
- Segmentation, DMZ and internet edge: `segmented-network`.
- WAN to cloud, dedicated circuits and site-to-site VPN: `hybrid-cloud`.
- Packet walks and troubleshooting views: `sequence-request`.
- HA pairs and site failover: `backup-dr` for the replication and failover notation.
- Campus, wireless, SD-WAN branches, DCI, service-provider cores, peering and L1 cabling: no template yet; use `layout_diagram`.
- Read alongside: `brief` and `style` first, then `storage` for storage fabrics, `security-architecture` for zones and controls, `cloud` for VPCs, regions and cloud interconnects, and `kubernetes` for CNI and cluster networking.
