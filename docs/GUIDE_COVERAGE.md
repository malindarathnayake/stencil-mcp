# Guide coverage and gaps

`stencil_guide` serves one topic guide per diagram family. The guides were produced by a
multi-agent sweep of the catalog, industry practice and each department's needs, then
each was checked by a technical reviewer and a repository-grounding reviewer before
revision. A test fails if a guide cites an asset, template or guide that does not exist.

## Topics

| Topic | Title |
| --- | --- |
| `ai` | AI, agent and ML systems |
| `brief` | Confirm the brief before drawing |
| `business-process` | Business process swimlanes (BPMN-lite) |
| `cloud` | Cloud, hybrid and landing-zone architecture |
| `compute` | Compute, virtualization and hardware |
| `data` | Data platforms, pipelines and database topology |
| `devops` | Delivery pipelines, supply chain and GitOps |
| `email-flow` | Email flow and email security |
| `endpoint-management` | Endpoint and device management (MDM/UEM, patching, conditional access, VDI) |
| `explainer` | Explainers, comparisons and decision panels |
| `failure-analysis` | Incident post-mortems, blast radius and single-point-of-failure reviews |
| `fleet-iot` | Fleet telematics, IoT and field operations |
| `flowchart` | Flowcharts, decision trees, state machines and hierarchies |
| `kubernetes` | Kubernetes and container platforms |
| `migration` | Migrations, transition architectures and cutover plans |
| `multi-tenancy` | Multi-tenant SaaS and tenancy isolation |
| `network` | Network topology (L1/L2/L3, campus, data-centre fabric, WAN) |
| `observability` | Observability, monitoring and service health |
| `payments` | Payment and financial transaction flows |
| `privacy-data-map` | Privacy data maps, data residency and cross-border transfer |
| `protocol` | Packet and protocol explanations |
| `release-strategies` | Progressive delivery: canary, blue-green, feature flags and rollouts |
| `resilience` | Disaster recovery, backup and resilience patterns |
| `security-architecture` | Security architecture, segmentation and identity |
| `security-operations` | Security operations: detection, response and vulnerability management |
| `sequence` | Sequence and interaction diagrams |
| `service-blueprint` | Service blueprints and customer/user journeys |
| `software-architecture` | Software architecture (C4-style, services, integration) |
| `storage` | Storage networking and storage architecture |
| `style` | Shared design language |
| `threat-model` | Threat models, attack paths, attack graphs and attack trees |

## Coverage gaps

Scenarios people ask for that the catalog draws poorly today, and what is missing.
The guides tell the model to say so up front and offer the nearest alternative.

| Scenario | Missing |
| --- | --- |
| Core network services (DNS, DHCP, NTP, syslog, IPAM) | dns, dhcp, ntp, syslog, ipam assets |
| Cellular / 5G / satellite / telecom core | cell-tower, 5G core NF, RAN, satellite, backhaul assets |
| Rack elevation / physical layout | RU grid layout, variable-height device shapes (symbols fixed aspect), front/rear views, per-port interface labels at both link ends, cable-type styling (fiber/copper/DAC) |
| Physical facility / power and cooling | UPS, PDU, generator, cooling, power-feed A/B assets |
| Wi-Fi floor plan / heatmap | floor-plan background, coverage/heatmap rendering, SSID asset |
| Unified communications / VoIP / contact center | PBX, SIP trunk, IP phone, headset, IVR, knowledge-base assets |
| Office / end-user IT | printer, conference-room/TV, camera assets |
| IoT / OT / SCADA / industrial control | sensor, IoT gateway, PLC, HMI, SCADA, historian assets |
| Supply chain / logistics and warehouse | warehouse, factory, store, truck-freight, ship, pallet, forklift, scanner assets |
| Field service | technician, work-order, tool assets; fleet template |
| Formal BPMN / UML class / UML state | BPMN event subtypes, pools, message flows, BPMN XML export; compartmented class boxes, inheritance/composition arrowheads, composite states, self-transition helper |
| ER diagram / star schema | table node kind with field rows, PK/FK markers, crow's-foot cardinality arrowheads |
| RACI, risk heat map, ATT&CK matrix, DoA matrix, IP/VLAN plan, control-to-component mapping | 2D table/grid node kind (memory cells are one row, max 32) |
| Charts: SLO/error budget, KPI, financial waterfall, sales funnel | chart primitives (bar/line/pie/funnel/gauge); out of scope for symbol renderer |
| Gantt / roadmap / incident timeline / TCP timing ladder | time axis with ticks, proportional spacing, duration bars, milestone diamonds |
| Sequence diagrams (full UML) | activation bars, alt/loop/opt combined fragments, automatic message ordering, self-call helper |
| Git branching graph | commit-dot rail / merge-curve notation |
| Territory / geofence maps | geographic map background |
| Wireframes, customer journey emotion curve | UI-control primitives, screen thumbnails, curve rendering |
| Vendor-branded cloud diagrams | official AWS/Azure/GCP icons (excluded by design) |
| Service mesh | sidecar / mesh asset |
| GPU/HPC fabric | InfiniBand, NVLink, rail/pod-specific assets |
| FC/iSCSI SAN | HBA and FC-switch assets |
| Static routes / legacy IGP, VLAN trunks | static-route/IGRP icons, parameterized trunk/tag widget, LAG bundle glyph on edges, per-VLAN link colouring |
| ML / data platforms | notebook, feature-store, experiment-tracking, drift, eval-harness, schema-registry, DLQ, BI assets |
| C4 component / IAM graphs / landing zones | generic module/interface, role, policy-document, account/OU/subscription icons; nested group semantics (groups flat, 40-group cap) |
| Trees, org charts, mind maps, attack trees, capability maps | tree/radial auto-layout guarantees, AND/OR gate notation, Team Topologies shapes, auto grid tiling, heatmap palette scale |
| Encapsulation / header layouts | bit/byte-level RFC header field layout widget |

## Open consistency items

Found by the completeness critic; not yet resolved in the guides.

- Edge kinds for return paths and state transitions differ between some guides (`ai`, `flowchart`, `observability`). `style` should be the single source of truth.
- The renderer draws `control` and `feedback` with the same dash, and a dashed legend entry always uses one pattern, so several guides describe workarounds. Distinct dash patterns would remove them.
- Some templates have defects that guides describe instead of fixing: `sequence-request` skips the gateway on the return path, `observability-pipeline` merges collector and stores, and `backup-dr` includes components a brief may not ask for.
- PCI scope is defined in both `security-architecture` and `threat-model`; keep one canonical definition.
- A "retired or decommissioned" convention (slate card, "Retired" detail) should live in `style` so other guides do not reuse the `down` state, which draws a failure badge.
- Stand-in assets for things the catalog lacks (packet broker, transparency log, threat intelligence, DNS) are chosen differently in different guides; a shared stand-in table in `style` would make them consistent.
- Groups are flat (no nesting semantics) and capped at 40, which some guides work around in different ways.
- `fleet-iot` overlaps the IoT/OT/SCADA gap: there are no PLC, HMI or sensor assets.
