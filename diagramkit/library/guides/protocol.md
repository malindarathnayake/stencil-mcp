# Packet and protocol explanations

> Use this guide when the diagram teaches how packets move, get lost, reorder, queue or get recovered, how a connection is set up, or how protocol headers wrap one another, rather than how a system is deployed.

## Questions to ask first

Ask these in one round, and only about facts the brief leaves open. Each question gives the default you will use if the user says "yes to all".

1. Which scenario is this: loss and reorder recovery, congestion signalling, connection setup or teardown (TCP three-way handshake, TLS or QUIC handshake, 0-RTT), encapsulation and MTU, or address translation? (default: loss and reorder recovery)
2. Which protocol and mode is it about, for example TCP with or without SACK, QUIC, plain UDP, RoCEv2 reliable connection, or a multipath transport? For RDMA, does the traffic run on a PFC lossless priority with ECN/DCQCN? (default: TCP with SACK; for RoCEv2, a PFC lossless priority with ECN/DCQCN)
3. How many paths and which devices sit between sender and receiver, does the network spread traffic per flow (ECMP hashing) or per packet, and which header layers matter? (default: sender NIC, one switch, receiver NIC on a single path; if the brief says "multipath", two ECMP paths with per-flow hashing; only the layers the brief names, and no overlay unless VXLAN or a tunnel is mentioned)
4. Which packets does the example follow, which are lost or only delayed, where does each loss happen, and in what order do the rest arrive? (default: packets 1 to 5 as illustrative segment indexes; packet 4 is tail-dropped at a full switch egress queue, packet 2 is delayed, and the arrival order is 1, 3, 5, 2; for RoCEv2 on a lossless priority there is no congestion drop unless the brief says the fabric is lossy)
5. What feedback does the receiver send, and how does the sender detect the loss: three duplicate ACKs or the SACK threshold, time-based detection (RACK for TCP, the time threshold for QUIC), or a retransmission timeout? (default: TCP sends a cumulative ACK of the next expected segment plus SACK blocks, and because only packet 5 follows the hole, the loss is detected by a timeout or a tail loss probe; QUIC sends ACK frames with ACK ranges; RoCEv2 RC sends a sequence-error NAK; plain UDP sends nothing)
6. How is the loss recovered: selective retransmission, go-back-N from the missing packet, NewReno resending one hole per partial ACK, QUIC resending the lost frames in a new packet, an application-level resend, a spurious retransmission of a delayed packet, or no recovery? Should the congestion window reaction be shown? (default: TCP resends only packet 4; QUIC sends the data of packet 4 in packet 6; RoCEv2 RC goes back to 4 and resends 4 and 5; the congestion window is not shown)
7. Are congestion signals or receive buffers in scope? (default: no congestion signals unless the brief mentions congestion; if it does, TCP shows a drop at a full queue, and RoCEv2 shows an ECN mark, a congestion notification packet (CNP) back to the sender and a PFC pause one hop upstream; one receiver memory strip with one slot per example packet)
8. In one sentence, what should the reader conclude? (default: one packet was lost, the receiver reported the gap, and only the missing data was resent; confirm this when the brief does not state the takeaway, because the conclusion decides which packets and panels appear)

## Push back when

Say what looks wrong and ask which the user means. Do not silently draw the request as written, and do not silently correct it.

- **UDP retransmitting, acknowledging or handshaking.** UDP has no ACKs, retransmission, ordering or handshake. Ask which protocol above UDP does that work (QUIC, DTLS, RoCEv2, the application) and draw that protocol.
- **A reorder drawn as a loss.** A gap in the receive buffer does not prove a packet is lost, because it may still be in flight on a slower path. Ask whether the packet is delayed or dropped.
- **Fast retransmit with fewer than three packets after the hole.** TCP fast retransmit needs three duplicate ACKs, and SACK loss detection needs three SACKed segments above the hole. With fewer, the recovery is a timeout or a tail loss probe. Ask for more packets after the hole, or draw the timeout.
- **TCP recovery drawn without saying which kind.** With SACK and fast recovery, the sender resends only segments it judges lost, never SACKed ones. Without SACK, fast retransmit resends the first missing segment, and NewReno resends one hole per partial ACK. After a retransmission timeout, TCP may resend from the first unacknowledged byte, which can include segments that already arrived. Ask whether the brief means fast recovery or a timeout.
- **ACK N read as "received up to and including N".** A TCP ACK names the next byte expected, and SACK blocks list ranges that arrived, not ranges that are missing.
- **QUIC retransmission drawn with the same packet number.** QUIC never resends a packet. It puts the lost frames into a new packet with a new packet number.
- **RoCEv2 RC with selective retransmission by default.** Classic RoCEv2 reliable connection recovers with go-back-N after a sequence-error NAK. Some NICs support selective repeat, so ask which one the user means.
- **ECN described as dropping or slowing traffic.** A switch sets the CE mark on an ECN-capable packet instead of dropping it. The receiver echoes the signal (ECE in TCP, a CNP in RoCEv2) and the sender reduces its rate. The mark itself slows nothing.
- **PFC drawn end to end or per flow.** A PFC pause goes hop by hop to the directly attached upstream device and pauses one priority class on that link, not one flow. It can spread congestion upstream and cause head-of-line blocking.
- **"Lossless" meaning no drops at all.** PFC prevents congestion drops in the paused priority. It does not prevent drops from corruption, misconfiguration or traffic in other priorities.
- **One TCP connection spread across ECMP paths.** Per-flow ECMP keeps every packet of a flow on one path. One connection uses several paths only with MPTCP (separate subflows, each hashed on its own 5-tuple), per-packet spraying, flowlet switching, or a transport that varies the hash entropy, such as the UDP source port. This kit's `mrc-loss-recovery` template is an illustrative example of that last kind.
- **Receive window and congestion window confused.** The receiver advertises the receive window. The sender keeps the congestion window and never advertises it. The sender is limited by the smaller of the two.
- **VXLAN drawn without its MTU impact.** VXLAN adds about 50 bytes of outer headers over IPv4. The underlay MTU must allow for that, or the inner MTU must shrink.
- **QoS adding bandwidth.** Queueing and scheduling decide which traffic waits or drops when a link is full. They do not make the link faster. Policing drops or remarks excess traffic, and shaping buffers and delays it.
- **A bit-accurate header diagram.** This kit draws layers as nested panels, not RFC bit layouts. Point the user to the specification for field widths and offsets.

## How we draw it here

- **Direction.** Put the sender on the left, the receiver on the right and the paths in between. Put feedback below or above the forward traffic so the return edges do not share segments with it.
- **No time axis.** The renderer does not draw proportional time. Show order with numbered panels (`group` with `style: "panel"` and titles such as "1  Arrivals" and "2  Recovery") or numbered `presentation/step` symbols. Write the arrival order in the memory strip and labels, and do not imply it by distance.
- **Packets.** Use one `packet` node per packet, labelled "Packet N". N is an illustrative segment index, not a TCP byte sequence number. Put the distinguishing field in `detail` (UDP source port, PSN, DSCP value). Keep each packet's `palette` the same in every panel. For QUIC, label the resend "Packet 6 (carries data from 4)" and keep the palette of packet 4's data.
- **Drops.** Give a lost original packet `state: "dropped"` and end its edge at a `marker` node with `state: "dropped"`, placed where the drop happens. A queue drop ends at a marker on the switch. A link error ends at a marker on the receiving port of that link. A receiver discard (checksum or ICRC failure, buffer overrun) ends at a marker on the receiver NIC. A dropped packet never appears in the memory strip.
- **Receive buffers.** Use the `memory` node kind with one cell per slot, up to 32 cells. Put received packets in sequence position with their packet palette, and mark a gap with cell `state: "missing"` and a dash as the value. Show the buffer again, complete, after recovery.
- **Feedback.** Draw ACK, SACK, NAK, CNP and ACK frames as `feedback` edges from the receiver to the sender. Label them in plain words that match the protocol. For TCP, use "ACK 4 (next expected) + SACK 5". For QUIC, use "ACK ranges 1–3, 5". For RoCEv2, use "NAK: expected PSN 4". Use a `protocol/ack`, `protocol/sack` or `protocol/nack` symbol only when the feedback needs its own node.
- **Other edges.** Use `data` for packets moving forward, `physical` for links between devices, `control` for a PFC pause sent to the upstream hop, and `tunnel` for an overlay such as VXLAN between VTEPs. Draw a handshake with `sequence-request` lifelines.
- **Encapsulation.** Draw each layer as a group nested inside the layer that carries it: an Ethernet panel holds an IP panel, which holds a TCP panel, which holds the payload. Use `protocol/ethernet-frame`, `protocol/ip-packet`, `protocol/tcp-segment` or `protocol/udp-datagram` as the layer symbol. For VXLAN, the outer Ethernet, IP and UDP panels wrap a VXLAN panel (`routing/vxlan`), and that panel wraps the inner Ethernet frame. Name the key field in the caption (VNI, destination port, added bytes), not every field.
- **Asset roles.**
  - Endpoints: `hardware/nic`, `hardware/rdma-nic` or `hardware/smartnic`, plus `compute/rack-server` when the host matters.
  - Forwarding: `network/switch-l3`, `network/leaf-switch`, `network/spine-switch`, `network/router`.
  - Path selection: `routing/ecmp`, `routing/flow-hash`. Address translation: `routing/nat`.
  - Queueing and QoS: `protocol/queue-buffer`, `routing/qos`. Overlays: `routing/vtep`, `routing/vxlan`.
  - Packet events: `protocol/dropped-packet`, `protocol/out-of-order`, `protocol/retransmission`, `protocol/congestion`, `protocol/ecn`, `protocol/pfc-pause`.
  - Transport state: `protocol/receive-window`, `protocol/sequence-number`, `protocol/rtt`, `protocol/memory-buffer`. RDMA: `protocol/rdma-operation`, `protocol/queue-pair`.
- **Palettes.** Keep red for loss, drops and congestion, and slate for links and feedback. Give each packet its own palette when there are six or fewer (blue, teal, purple, orange, green, yellow). With more than six, reuse palettes and rely on the "Packet N" label. A dropped packet or a missing cell renders red whatever its palette, so its palette only matters for matching the resent copy.
- **Legend and footer.** Add a `legend` whenever more than one edge meaning appears, and set `dashed: true` on the feedback entry. Always set a `footer` saying that packet numbers, ports and feedback text are illustrative, not wire-format encodings. Put the reader's conclusion in `subtitle` and the full story in `description`.

## Common mistakes

- Drawing the lost packet at a drop marker and also in the receiver memory.
- Resending packets that arrived without saying it was a timeout or go-back-N recovery.
- Drawing a resend of a packet that was only delayed, unless the point is spurious retransmission. In that case, show the duplicate arriving and a D-SACK reporting it.
- Drawing SACK-triggered fast retransmit when too few packets follow the hole.
- Labelling feedback "missing 4" as if SACK listed holes, or treating ACK numbers as packet counts.
- Drawing `protocol/packet` symbols in a row instead of `packet` nodes, which loses the number and the state.
- Drawing the receive buffer as a `component` card that lists numbers, instead of a `memory` strip.
- Drawing feedback as a `data` edge, or sending a PFC pause straight to the original sender across several hops.
- Showing RoCEv2 congestion as drops and go-back-N when the fabric is lossless and the real story is an ECN mark and a pause.
- Hiding an unused ECMP path. Keep every physical path visible, even when no packet uses it.
- Implying that port numbers map to fixed paths A, B, C and D. Hash results are not a universal mapping.
- Spacing packets to suggest timing. The reader will read distance as time.
- Inventing header fields or field sizes in labels to look precise.
- Adding a load balancer, firewall or extra switch tier that the brief did not mention.

## Start from

- `mrc-loss-recovery` for multipath loss, receive memory, gap feedback and selective recovery. Its feedback label uses the kit's illustrative notation, so relabel it when the protocol is TCP or QUIC.
- `ecmp-flow-hashing` for how flows hash onto paths and why one flow stays on one path.
- `sequence-request` for an ordered exchange between two parties, such as a TCP, TLS or QUIC handshake. Lifelines show order only, not time.
- For congestion signalling, QoS queueing, encapsulation, MTU or NAT, there is no template yet. Use `layout_diagram` and build the panels by hand.
- Read alongside: `brief` first, then `network` when the physical topology matters, then `style`.
