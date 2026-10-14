# Storage networking and storage architecture

> Use this guide when a diagram shows how hosts reach storage (iSCSI, Fibre Channel, NVMe-oF, NFS/SMB, object), how multipathing works, how an HCI, distributed or cloud storage system is built, or how storage replicates between arrays or sites.

## Questions to ask first

Ask only the questions the brief leaves open, in one round, and use the default if the user says to proceed.

1. Which protocol and storage type do hosts use: iSCSI, Fibre Channel, FCoE, NVMe-oF (TCP, RoCE or FC), NFSv3, NFSv4.1, SMB, or object (S3-style over HTTPS), and which workloads use which type? (default: iSCSI block for hypervisor hosts, NFSv3 for file; other workloads only if named)
2. For block storage, how many fabrics are there, and for iSCSI do the array ports use one subnet or two (one per switch)? (default: two independent fabrics, A and B, two subnets, no link between the switches; if the answer is single subnet, draw the ISL the vendor requires)
3. How many storage ports does each host have, and are they dedicated to storage or converged with VM and front-end traffic on the same NICs? (default: two dedicated ports per host, one per fabric; for HCI, ask, because many HCI designs converge on two shared ports)
4. How many arrays and controllers are there, does every controller reach both fabrics, and is the array active/active symmetric or ALUA (ANA for NVMe-oF)? (default: one array with two controllers, one port per controller on each fabric, paths drawn without optimised or non-optimised marking)
5. Where does the storage sit: a dedicated storage rack, the compute racks, another site, or a cloud VPC? (default: a dedicated storage rack or zone; ask rather than placing arrays in compute racks)
6. Is the storage network separate from the front-end network, or a VLAN on shared switches, and is it routed? (default: block storage on separate switches, not routed, no default gateway; file and object storage reached over the routed network)
7. What link speeds and MTU are used, and for NVMe over RoCE is the fabric lossless with PFC and ECN? (default: speeds omitted unless given; jumbo MTU 9000 end to end for iSCSI, NFS and NVMe/TCP, written in the footer; for RoCE, ask)
8. For Fibre Channel, how is zoning done, and should zoning or LUN masking appear in the diagram? (default: single-initiator zoning, not drawn)
9. For HCI: is it classic HCI with node-local disks, or disaggregated (vSAN Max, HCI Mesh compute-only, dHCI with an external array, compute-only nodes)? How many nodes and disks per node? If it is 2-node or stretched, where does the witness run? (default: classic HCI with the nodes named in the brief; a witness is mandatory for 2-node and stretched clusters, so ask where it runs, usually a third site or the cloud)
10. For distributed storage: how many nodes, is there a separate back-end (cluster or replication) network, how is data protected (replicas or erasure coding), and how many monitor or quorum nodes? (default: back-end network drawn only if named; protection in the footer; monitors an odd count, shown only if named)
11. Is there replication between arrays or sites: synchronous or asynchronous, which direction, over which link (IP WAN, dark fibre, FCIP)? For active-active metro replication, where does the mediator run? (default: no replication; if mentioned without a mode, ask; a metro active-active design needs a mediator in a third site, so ask where)
12. Are RAID layout, storage tiers, snapshots, backups or DR in scope? (default: connectivity only; RAID and tiers as card detail; backups out of scope unless named)

## Push back when

- The brief load-balances iSCSI over ECMP routes, or relies on one routed path for redundancy. Block storage redundancy comes from host multipathing (MPIO or native NVMe multipath) over two separate paths. Routed iSCSI and NVMe/TCP are supported, but redundancy still comes from multipathing, not ECMP. Ask whether they mean multipathing over two fabrics.
- The brief links fabric A and fabric B. For Fibre Channel, an ISL merges the two fabrics into one failure domain. For dual-subnet iSCSI, the link is not needed and couples the fabrics. Some arrays need single-subnet iSCSI with the switches joined by an ISL, stack or MLAG. Ask which scheme the array uses before calling the ISL a mistake.
- The brief shows iSCSI multipathing as LACP or a port-channel. For iSCSI, hypervisor and storage vendors generally recommend MPIO over independent links instead of link aggregation. This applies to iSCSI only. NFS and SMB redundancy normally does use LAG, MLAG or multiple IPs.
- The brief applies MPIO to NFS, SMB or object storage. Those protocols use other methods (see "Redundancy by protocol" below). Ask what the design really uses.
- The brief puts native Fibre Channel through an IP router or firewall. FC runs on FC switches. The exception is FCIP or SAN extension between sites (FC switch, FCIP gateway, IP WAN, FCIP gateway, FC switch). Ask whether they mean FCIP, FCoE or iSCSI.
- The brief uses an object store as a VM datastore or mounted LUN. Applications reach object storage over HTTP. It is not attached as a block device. Ask which storage the hosts mount.
- The brief builds a classic vSAN or HCI pool from an external array's LUNs. Classic HCI pools node-local disks, and an external LUN is a separate datastore. Disaggregated designs (vSAN Max, HCI Mesh, dHCI, compute-only nodes) are valid. Ask which one is meant.
- The brief describes a 2-node HCI cluster, a stretched cluster or active-active metro replication with no witness or mediator. Without one, the design cannot fail over safely. Ask where it runs instead of leaving it out.
- The brief asks for synchronous replication between distant sites. Every write waits for the remote acknowledgement, so latency limits synchronous replication to metro distances. Ask whether the link is short or the mode is asynchronous.
- The brief treats RAID, replication or same-array snapshots as a backup. RAID protects against disk failure, and replication also copies deletions and corruption. Ask whether a separate backup is in scope.
- The brief has a single storage switch or a single-controller array but calls the design fully redundant. Point out the single point of failure and ask whether it is accepted.

## How we draw it here

- Redundancy by protocol. Block (iSCSI, FC, NVMe-oF): MPIO or native NVMe multipath (ANA) over two paths. NFSv3: LAG or MLAG, or multiple export IPs. NFSv4.1: session trunking. SMB 3: SMB Multichannel. Object: load-balanced HTTPS endpoints. Draw the mechanism the brief uses, and state it in a note or the footer.
- Layout: hosts on the left or top, storage fabrics in the middle, arrays on the right or bottom. Replication between sites runs left to right between site groups.
- Grouping: put fabric A and fabric B in separate `boundary` or `lane` groups titled "Fabric A" and "Fabric B". For a rack view, use a storage-rack `panel` whose caption states the scheme, such as "two independent L2 fabrics, not routed". Put each site in its own `boundary` group titled "Site 1" and "Site 2". Groups have no asset field. Add a `cloud/datacenter` component inside a group only if the site needs its own card. For a stretched cluster or metro pair, use three site groups and put the witness or mediator in the third.
- Hosts: `compute/rack-server`, `compute/hypervisor`, `compute/hci-node` for HCI nodes, and `compute/compute-cluster` when a cluster is summarised as one card. Write "2x iSCSI NIC" or "2x FC HBA" in the card `detail`. Draw compute-only nodes in a disaggregated design without local capacity disks.
- Host adapters as their own nodes: `hardware/nic` labelled "FC HBA" or "iSCSI NIC", and `hardware/rdma-nic` for NVMe over RoCE. There is no HBA icon. Do not use `hardware/pcie` or `hardware/smartnic` as one.
- Switches: `network/switch-l2` labelled "Storage SW-A" and "Storage SW-B", or "FC switch A" and "FC switch B". There is no FC-switch icon. For FCIP, draw each gateway as a separate `network/router` card labelled "FCIP gateway", `network/wan-provider` for the WAN, and a `tunnel` edge labelled "FCIP".
- Arrays and targets: `storage/storage-array` for a block array (detail "Controller A + B"), `storage/san`, `storage/nas` for a filer, `storage/file-share`, `storage/block-volume` for a LUN or volume, `storage/object-store`, and `storage/distributed-storage` for a scale-out cluster. Draw separate "Controller A" and "Controller B" cards only when per-controller paths are the point.
- Witness, mediator and monitors: `compute/virtual-machine` labelled "Witness" or "Mediator", inside the third site group or a `cloud/public-cloud` card. Show distributed-storage monitors as `compute/rack-server` cards labelled "Monitor", only if named.
- Cloud storage: a `boundary` group titled "VPC" (optionally a `cloud/vpc` card), with `storage/block-volume` linked to `compute/virtual-machine`, and `storage/object-store` reached by a `data` edge. Put `network/load-balancer` in front of object storage when the brief names a load-balanced endpoint.
- Lossless fabric: use `protocol/pfc-pause` and `protocol/ecn` symbols only when the diagram explains RoCE flow control.
- Local media: `storage/disk`, `hardware/nvme-device`, `storage/disk-raid` for a RAID set, and `storage/tape-library` only for a named archive tier.
- Edges: `physical` with `route: "straight"` for every cable, one edge per link. Use teal for fabric A and purple for fabric B, and keep those colours the same across related diagrams. Use slate for front-end links. Use `data` edges only for I/O direction ("NFS mount", "S3 PUT"). Use orange `replication` edges for replication, labelled with mode and direction, such as "Async replication, Site 1 to Site 2". Use `arrow: "both"` only if the user said replication runs both ways. Label an ISL "ISL (single-subnet iSCSI, vendor requirement)".
- ALUA: when optimised paths matter, keep the fabric palette, give non-optimised paths `width: 1` and the label "non-optimised (ALUA)", and add a text note: "MPIO spreads I/O across active-optimised paths; paths to the non-owning controller are standby (ALUA)."
- Zoning and masking: write them as a fabric group caption or a `text` note, such as "Single-initiator zoning", and never as extra edges.
- Legend: include one whenever more than one link meaning appears. Name entries after the brief's protocol, such as "FC fabric A" (teal), "NVMe/TCP fabric B" (purple) and "Front-end network" (slate). Replication uses orange with `dashed: true`.
- Footer: say what is illustrative and what is left out, then list the defaults used. For example: "Illustrative topology. Generic symbols. One link per connection. MTU 9000 end to end. Management network not shown."

## Common mistakes

- Drawing host-to-storage links as ECMP uplinks, or labelling multipath paths "ECMP".
- Merging several hosts' links into one shared line, which reads as a bus. Every host needs its own line to each switch.
- Connecting each host to only one storage switch, or each controller to only one fabric, which quietly removes the redundancy the brief describes.
- Placing arrays in compute racks when the brief did not say where they sit.
- Adding an ISL between FC fabrics or dual-subnet iSCSI switches, or leaving out the ISL a single-subnet iSCSI design needs.
- Routing block storage through the core or firewall without the user saying so, or drawing file and object storage as if they must sit on an isolated L2 segment.
- Drawing MPIO for NFS, SMB or object storage, or LACP for iSCSI multipathing.
- Running storage over the front-end switches, or drawing dedicated storage NICs for a converged HCI design, without asking.
- Using `storage/object-store` for a block LUN, `storage/nas` for a SAN array, or `storage/backup` for a replica.
- Using `storage/storage-array` for each HCI node's disks instead of `compute/hci-node` with `storage/disk` or `hardware/nvme-device`.
- Leaving out the witness or mediator in a 2-node, stretched or metro design, or adding one, or fault domains, a backup target or a DR site, where the brief does not need it.
- Drawing a `physical` edge for replication, or a replication edge with no mode, so readers assume synchronous replication.
- Giving a group an `asset` key. Groups accept only id, position, size, title, caption, palette and style, and validation fails otherwise.

## Start from

- `backup-dr` when the diagram centres on array or site replication.
- `hybrid-cloud` when cloud block or object storage connects to an on-premises site.
- Otherwise, no template yet. Use `layout_diagram`, then adjust positions so fabric A and fabric B fan out as separate straight lines.
- Read alongside: `brief` first, `network` for the front-end or routed fabric, `resilience` when backups, snapshots, failover or DR are in scope, and `style` before exporting.
