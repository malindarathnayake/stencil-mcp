# Compute, virtualization and hardware

> Use this guide when the diagram shows bare metal, hypervisors, VMs, HCI or a private cloud stack, the parts inside a server (CPU, GPU, DPU, NIC, PCIe, NVMe, TPM), a GPU or HPC cluster and its fabrics, bastion and BMC access, edge compute sites, or a coarse view of which servers sit in which rack.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. The user can answer "yes to all" or correct one.

1. How many physical hosts are there, and are they grouped into one cluster or several? (default: one cluster of three hosts, drawn as a `boundary` group for the cluster and one `panel` group per host; a host is a single card only when no VMs or internals are shown)
2. Which hypervisor or virtualization layer runs on the hosts, or does the OS run directly on the server with no hypervisor? (default: a generic `compute/hypervisor` card labelled "Hypervisor", with no product name)
3. How many VMs run on each host, and which named VMs matter to the story? (default: two VMs per host, labelled by role)
4. How do VMs reach the network (virtual switch, SR-IOV, DPU), and how many uplinks does each host have to which switches (single top-of-rack switch, dual ToR or MLAG, bonded NICs)? (default: one vSwitch per host, drawn as `network/switch-l2` labelled "vSwitch" inside the host panel, and one uplink per host)
5. Is storage local to each host, shared from an external array or SAN, or pooled across hosts as HCI, and what else is shared between hosts? (default: shared external storage drawn once outside the host panels; switches and storage shared, everything else per host)
6. For server internals, which devices sit in the server and how many of each, one or two CPU sockets, are devices behind a PCIe switch, and which GPU pairs with which NIC (NUMA or PCIe affinity)? (default: the devices the brief names, PCIe edges only for PCIe devices, and a footer note "PCIe topology not specified")
7. For a GPU or HPC cluster, how many nodes, how many GPUs and RDMA NICs per node, and which fabrics exist (compute, storage, management, front-end)? (default: four nodes and one compute fabric; other fabrics only if the brief names them)
8. What is the compute fabric topology and transport (single switch tier, leaf-spine, rail-optimized; InfiniBand or RoCE)? (default: one leaf tier labelled "RDMA fabric", no transport named, stated in the footer)
9. Should the management plane (BMC per server, bastion host, out-of-band network) appear, and does each BMC have a dedicated port or share a host NIC port? (default: leave it out)
10. For edge sites, how many sites, what runs at each site, and how does each site reach the core (WAN, VPN, internet)? (default: two edge sites, each with one `compute/edge-server`, linked to a central datacenter over a WAN)
11. For rack inventory, which racks exist and which servers go in each? (default: none assumed; ask for the list rather than inventing rack contents)
12. Does the story include a planned live migration, an HA restart after a host failure, or neither? (default: neither shown)

## Push back when

- The user asks for a rack elevation drawn to scale (rack units, exact slot positions, front and rear views). Stencil does not draw to scale. Offer a "what is in which rack" grouping: one panel per rack containing its servers, labelled with the rack name.
- The user wants VMs drawn as connected to their host with arrows. A VM runs inside its host; containment is shown by placing the VM cards inside the host panel. An edge would suggest a network link that does not exist.
- The brief has VMs on one host using another host's local disks directly. Local disks are reachable only by their own host unless something (HCI software, a storage protocol) shares them. Ask whether storage is HCI or external.
- The brief claims live migration with no shared or replicated storage and no migration network. Ask how disks move; some platforms copy storage during migration, but the diagram must say which.
- The brief shows a VM live-migrating off a host that failed. A failed host cannot migrate anything; HA restarts the VM on a surviving host from shared or replicated storage. Ask which event the diagram shows and label the edge "restart" or "live migration" to match.
- The brief connects GPUs in different servers with NVLink as if it were the cluster fabric. NVLink inside a server and a scale-out RDMA fabric between servers are different things unless the user names an NVLink switch system. Ask which they mean.
- The brief puts storage traffic, management traffic and GPU-to-GPU traffic on one unlabelled line. In GPU and HPC clusters these are usually separate fabrics. Ask whether they are really converged before drawing one network.
- The brief treats BMC traffic as production traffic. A BMC manages the server out of band; its traffic is not production traffic. It may share a host NIC port (NC-SI) or have a dedicated port. Ask which, and draw a separate out-of-band link only for a dedicated port.
- The user wants an icon to convey capacity (GPU memory, core counts, link speed). Icons do not imply capacity. Put those facts in the label or detail text, and only when the user stated them.

## How we draw it here

Flow runs left to right: users, management or front-end access on the left; hosts in the middle; shared storage and fabrics on the right or below. A rack inventory reads left to right, one rack per column.

Containment is grouping, not edges. A node has one `group`, so draw the outer box as a group and place the inner boxes geometrically inside it, then assign each card to its innermost group. Use `boundary` for clusters and sites. Use `panel` for one host or one server, and for one rack, titled with the rack name and holding its servers. Use `compute/server-rack` only when a rack appears as a single card in a larger view, such as a site with its racks summarised.

Asset roles:

- Physical servers: `compute/rack-server`, `compute/blade-server`, `compute/tower-server`; `compute/baremetal` only when the OS runs directly on the server.
- Virtualization: `compute/hypervisor` for the layer, `compute/virtual-machine` for each VM, `network/switch-l2` labelled "vSwitch" for the virtual switch, `compute/compute-cluster` for a cluster shown as one card. A private cloud as a whole: `cloud/private-cloud`; a location: `cloud/datacenter`.
- HCI: one `compute/hci-node` panel per host holding its local `hardware/nvme-device` cards. Place one `storage/distributed-storage` card inside the cluster boundary, below the host panels and outside any host, labelled with the datastore or pool name. Draw `dependency` edges from each host's disks to it. Put the replication or fault-tolerance policy in the label only if the user stated it.
- Server internals: `hardware/cpu`, `hardware/gpu`, `hardware/dpu`, `hardware/nic`, `hardware/rdma-nic`, `hardware/smartnic`, `hardware/fpga`, `hardware/memory`, `hardware/pcie`, `hardware/nvme-device`, `hardware/tpm`, `hardware/hsm-device`, `hardware/optical-transceiver`, `hardware/video-accelerator`. When the user names a PCIe switch, use a `hardware/pcie` card labelled "PCIe switch". Draw devices behind it from that card, and draw the GPUDirect `data` edge GPU to PCIe switch to RDMA NIC, not through the CPU.
- Management: `compute/management-controller` for a BMC (label it "BMC" or the vendor term the user uses), `compute/bastion-host` for the jump host, `compute/workstation` or `compute/laptop` for the admin's machine.
- Edge: `compute/edge-server` in a `cloud/edge-location` or `cloud/branch-office` boundary, reaching the core through `network/wan-provider` or `network/vpn-gateway`.
- Fabrics: `network/leaf-switch`, `network/spine-switch`, `network/switch-l2` or `network/switch-l3`, labelled with the fabric name ("Compute fabric, InfiniBand", "Storage network", "OOB management"). For a rail-optimized fabric, draw one leaf per rail labelled "Rail n"; NIC n on every node connects to the Rail n leaf; draw one node in full and summarise the others. Storage targets: `storage/storage-array`, `storage/distributed-storage`, `storage/san`.
- Transport detail, only when the story needs it: `protocol/rdma-operation`, `protocol/queue-pair`, `protocol/pfc-pause`, `protocol/ecn`.

Edge kinds:

- `physical` for cables and fabric links (host NIC to switch), and for PCIe attachment of PCIe devices (GPU, NIC, RDMA NIC, DPU, SmartNIC, FPGA, NVMe, HSM card) to the CPU or to a `hardware/pcie` card. Memory gets an unlabelled `physical` edge to the CPU. A TPM and other onboard parts sit in the server panel with no edge unless the user names the bus. Add "PCIe Gen5 x16" style labels only when the user stated them.
- `data` for traffic you are explaining: a GPU-to-GPU transfer, an RDMA write, a VM's storage reads.
- `control` for management: bastion to BMC, a cluster manager configuring hosts.
- `dependency` for "VM disks live on this datastore" when no packet path is meant.
- `replication` for storage or VM replication between clusters or sites.
- `tunnel` for a site-to-site VPN or overlay between an edge site and the core; draw the WAN or internet underlay as `physical` only when the story needs both.

Palettes: keep one palette per role and repeat it. A workable default is blue for compute (hosts, VMs), purple for accelerators (GPU, DPU, FPGA), teal for network and fabrics, orange for storage, slate for management and out-of-band, red for anything failed. Give each fabric its own panel palette so the reader can tell compute, storage and management networks apart.

Add a `legend` whenever more than one edge kind or more than one fabric appears. Use the `footer` for assumptions and counts the user did not confirm ("Host count assumed: 3", "PCIe topology not specified"), and for "Not to scale" on rack views. Write `description` as one or two sentences that state host counts, fabrics and storage model.

## Common mistakes

- Drawing VMs beside their host and linking them with edges instead of placing them inside a host `panel`.
- Drawing a VM with a `physical` edge to a top-of-rack switch. VMs connect to the in-host vSwitch, SR-IOV function or DPU; only host NICs have physical links.
- Using `compute/baremetal` when the brief says "bare-metal hypervisor" (ESXi, Hyper-V, KVM). That is a type-1 hypervisor; draw the server plus a `compute/hypervisor` card.
- Using `kubernetes/worker-node` or `kubernetes/pod` for a VM, or `compute/compute-cluster` for a single host, because the label sounded close.
- Using `hardware/nic` where the brief says RDMA, InfiniBand or RoCE; use `hardware/rdma-nic` and put the transport in the label.
- Hanging every device off the CPU by PCIe: memory and TPM are not PCIe devices, and devices behind a PCIe switch talk through the switch.
- Using `network/router` for a fabric switch, or `cloud/public-cloud` for an on-premises private cloud.
- Drawing every rail-optimized NIC to one shared leaf, which hides the rail topology.
- Merging the compute, storage and management fabrics into one switch row, or routing several server links along one shared segment so it reads as a bus. Draw each physical link as its own line with `route: "straight"`.
- Duplicating the HCI pool in every host panel, or drawing it outside the cluster as if it were an external array.
- Adding a BMC, bastion, out-of-band network or backup target the user did not mention because a typical server has one.
- Drawing every GPU in a large cluster. Show one node in full and summarise the rest ("Nodes 2 to 16, same as node 1") in a label or caption, after confirming the count.
- Inventing lane counts, PCIe generations, GPU models, memory sizes or link speeds. Leave them out unless stated.
- Attempting a to-scale rack elevation with stacked cards sized by rack units.
- Showing an NVLink connection between servers with no NVLink switch in the brief.

## Start from

- `leaf-spine` for the fabric under a GPU, HPC or virtualization cluster; add host panels and `hardware/rdma-nic` cards. For the single-tier default, delete the spine tier.
- `disaggregated-inference` for GPU clusters serving models with prefill and decode workers.
- For a virtualization stack, HCI, server internals, bastion and BMC access, edge sites or rack inventory: no template yet; use `layout_diagram`, then add groups for containment.
- Read alongside: `brief` first, then `network` for fabrics and switch topology, `storage` for shared storage, HCI and replication, `ai` for inference and training workloads, and `style` before rendering.
