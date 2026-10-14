# What is implemented and what is a visual reference

The runtime catalog contains **324 individual SVG files in 20 categories**. Many are role-specific variants of 128 base glyph families. Catalog 0.2.0 added the `business` (15) and `fleet` (9) categories; the original 300 assets are byte-identical and pinned by `tests/fixtures/legacy_sha256.json`. `asset-packs.json` groups the catalog by use case; `diagramkit/library/catalog.json` is the canonical metadata and lookup map.

The nine later concept boards and eight initial sheets are included in `references/icon-concepts/`. Their printed IDs are not runtime IDs, and their shaded illustrations are not exact matches for the simplified SVG library. The PNG sheets cannot be supplied as individually editable SVGs without further drawing work.

## Earlier discussion mapped to actual components

| Requested subject | Implemented building blocks |
| --- | --- |
| MRC endpoint | `hardware/rdma-nic`, `protocol/rdma-operation`, `protocol/queue-pair` |
| Packet, UDP port and order | `protocol/packet`, `protocol/udp-datagram`, `protocol/sequence-number`; scene packet nodes and labels |
| Loss and selective recovery | `protocol/dropped-packet`, `protocol/sack`, `protocol/retransmission`; MRC template |
| Destination memory | `protocol/memory-buffer`; scene memory-strip nodes |
| ECMP and path selection | `routing/ecmp`, `routing/flow-hash`, `network/switch-l3` |
| BGP and OSPF | `routing/bgp`, `routing/ospf`, `routing/peering` |
| VLAN and link aggregation | `routing/vlan`, `routing/lag`, `network/switch-l2`, `network/switch-l3` |
| Routes and next-hop explanations | `routing/route-table`, `network/router`; explicit labels and arrows |
| Panels, zones and notes | `presentation/panel`, `presentation/boundary`, `presentation/callout`, scene groups and text |

There is **no dedicated IGRP or static-route icon**, or parameterized 802.1Q trunk/tag widget, in the preserved 300-entry runtime catalog. Those requests appear in the concept references. They can currently be depicted with generic router/switch icons, explicit text, and scene connectors. Specialized assets and machine-checked VLAN/route semantics would be a subsequent library extension.

## Proposed notation to continue the workshop

These are drawing conventions to develop, not an implemented protocol simulator or a validated network configuration:

- Show one physical trunk as one link. Put a readable annotation beside it, such as `TRUNK | tagged: 10, 20, 30 | untagged/native: explicitly specified`. Do not draw VLAN-colored lines as additional physical cables unless the legend identifies them as logical overlays.
- Display allowed VLANs separately from examples of frames actually crossing the link. Do not silently choose a native VLAN or an allowed list.
- Show BGP/OSPF control relationships separately from data forwarding arrows; label AS/area information only when provided. Use a legend.
- Label IGRP literally when requested; do not silently substitute EIGRP. A generic router can carry that label until a dedicated role variant is added.
- Show a static route using a destination prefix and next-hop/interface annotation, rather than suggesting a dynamic neighbor session.

The original diagrams and boards are retained so these additions can be developed without losing the chosen look. Existing geometry, asset IDs and template meanings are not changed by this packaging release.
