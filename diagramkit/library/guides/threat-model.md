# Threat models, attack paths, attack graphs and attack trees

> Use this guide when the user wants a STRIDE or LINDDUN data-flow diagram, an attack path across stages, an identity or cloud attack graph, an AND/OR attack tree, a supply-chain or AI-agent threat model, or a cardholder or personal-data flow diagram for an audit.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. Each question gives the default you will use if the user says "yes to all". Questions 10 to 12 apply only to the diagram type they name.

1. Which kind of diagram do you need: a data-flow diagram, an attack path across stages, an attack graph (identity or cloud privilege paths that are not stage-ordered), or an attack tree? For a data-flow diagram, should threats follow STRIDE, or LINDDUN for personal-data privacy threats? (default: a STRIDE data-flow diagram, because the brief names a system rather than an attack)
2. Which system is in scope, and where does scope stop? Name the components you want drawn and any you want shown only as external entities. (default: only the components the brief names; everything else is an external entity outside the boundary)
3. Which trust boundaries exist, and who owns each one (internet to edge, application to data tier, tenant to tenant, vendor, build system, model provider)? (default: one boundary between untrusted users and the application, and one around the data stores)
4. What data crosses each flow, and how is it classified (public, internal, confidential, cardholder data, sensitive authentication data such as CVV, PIN or track data, personal data, credentials)? (default: each flow labelled with the data named in the brief; classification marked "unclassified, confirm" where unknown)
5. Which threats or attack steps are confirmed by evidence (incident, test finding, log) and which are hypothesised? (default: everything is hypothesised and drawn as red dashed `control` edges)
6. Who is the threat actor and where do they start: external, malicious insider, compromised supplier, or compromised account? (default: one external actor outside every boundary)
7. Which controls exist on the path, and for each one, did it block, detect only, or miss the step? (default: draw only controls the brief names; mark their outcome "unknown")
8. Should flows and threats be numbered so they can be referenced from a threat register or audit report? (default: flows numbered F1, F2 and threats numbered TH-01, TH-02, keeping T-numbers free for ATT&CK technique IDs)
9. Who may see this file, and should hostnames, IP addresses and unremediated gaps be generalised? (default: internal-confidential; real hostnames kept only for the defending team; the footer carries the classification)
10. Attack path only: which framework and stages (MITRE ATT&CK tactics, Lockheed Martin Cyber Kill Chain, Unified Kill Chain or your own), which ATT&CK domain (Enterprise, ICS, Mobile) and version, and must technique IDs appear for traceability? (default: the current Enterprise version, stages limited to what the evidence supports, in tactic order, from Initial Access, Execution, Credential Access, Discovery, Lateral Movement, Command and Control, then Exfiltration or Impact; technique IDs in card labels)
11. Attack tree only: what is the root goal, how many levels deep should it go, and should mitigations appear on the leaves? (default: one root goal, two levels of sub-goals, mitigations shown on leaves the brief mentions)
12. Compliance only: which systems store, process or transmit the regulated data, which are connected to them or can affect their security (identity provider, logging, patching, jump hosts, the segmentation devices), and which are separated by a tested segmentation control? (default: systems the brief names as connected are drawn in the in-scope connected boundary and marked "scope: confirm")

## Push back when

- A flow connects two data stores, or an external entity directly to a data store. In a DFD, data only moves through a process. Tell the user a process must sit between them (a replication job, an import service, a database engine) and ask which one it is.
- The user wants the trust boundary drawn as if it were a control. A boundary marks where trust changes; it does not block anything. Ask which component enforces the crossing (a gateway, firewall, policy engine or authorization check) and draw that as its own node.
- The user asks to mark a whole path "blocked" because one control stopped one step. An attacker with another route is not stopped. Ask whether alternative paths exist and draw them, or state in the description that only this path is shown.
- In an attack tree the user marks a root goal as mitigated because one leaf under an OR node is mitigated. Under OR, any single child achieves the parent, so every child must be addressed. Under AND, removing one child is enough. Explain this and ask which they intend.
- The user wants ATT&CK tactics drawn as a strict one-way sequence and calls it the actual order of events. Real intrusions repeat and skip tactics. Draw the stages in the observed order and say so, or label the drawing as a simplified model.
- A detection-only control (SIEM, IDS, EDR in alert mode) is drawn as preventing a step. Detection does not stop the step. Ask whether a response action followed, and show that separately.
- A compliance scope drawing leaves out systems that connect to the regulated environment or can affect its security. Under PCI DSS, connected-to and security-impacting systems are in scope even if they never handle cardholder data, and a system is out of scope only if segmentation isolates it and that segmentation has been tested. Ask about each such system and the control between them.
- Encryption on a flow is used as a reason to drop its classification. Encrypted cardholder or personal data is still that data class; label both the class and the protection, for example "PAN, TLS 1.3". Truncation, tokenization, or encryption where this entity holds no keys can change scope; ask who holds the keys or the detokenisation service, and draw that system in scope.
- A flow carries sensitive authentication data (CVV, PIN block, full track) into any data store after authorization. Storing it is not permitted, even encrypted. Flag it as a finding rather than drawing it as a normal flow.
- A code signature or provenance record is drawn as proof that the source was clean. A signature shows who signed and that the artifact is unchanged since signing; it says nothing about the source or the build that produced it.
- A system prompt or model instruction is drawn as the control that stops prompt injection. Instructions are input to the model, not an enforcement point. Ask what limits the tool call (permission scope, an allow list, human approval) and draw that.
- The user asks for working exploit steps, payloads or credentials in labels. Use technique names and IDs only; the diagram describes the path, not how to execute it.

## How we draw it here

**Data-flow diagram (STRIDE or LINDDUN).** Left to right, from untrusted to trusted. Each trust boundary is a `group` with `style: "boundary"`, titled by owner ("Internet", "Application tier", "Payment provider"). Use `presentation/external-entity` for people and systems outside your control, `presentation/process` for processes, and `presentation/data-store` for stores. Use a more specific asset only when the role matters to a threat: `identity/user` or `identity/admin` for human actors, `identity/identity-provider`, `security/policy-engine`, `security/waf`, `software/rest-api`, `data/relational-db`, `identity/secrets-vault`. Every flow is a `data` edge with its direction set; a request and a response that carry different data are two edges. Every edge that crosses a boundary has a label naming the data and its classification, prefixed by the flow number: "F3: card number (cardholder data)". Attach threats as `presentation/callout` symbol nodes with a `caption` such as "TH-04 Tampering: replayed token", placed next to the element they apply to. Use `control` edges for policy or configuration paths and `dependency` edges for depends-on relations, not data.

**Supply chain.** Same DFD rules. Source, build, store and deploy are processes in separate boundaries per owner (developer, build service, registry, runtime): `devops/git-repository`, `devops/ci-build`, `devops/artifact-registry`, `devops/cd-release`, with `devops/container-image` and `devops/sbom` as the data on the flows. Third-party dependencies enter from an external entity outside every boundary.

**AI and agent systems.** Same DFD rules. Draw `ai/llm`, `ai/ai-agent`, `ai/mcp-client`, `ai/mcp-server` and `ai/tool` as processes, and the retriever (`ai/rag-retriever`) with its store. Retrieved documents, web content and tool output are untrusted input: draw them as flows that cross a boundary into the model, labelled as such. Put `ai/guardrail` and `ai/human-approval` on the crossing they enforce, never as the boundary itself.

**Attack path.** Left to right by stage. One `group` with `style: "panel"` per tactic or stage, titled with the stage name. Assets the attacker touches are `component` cards inside the panel for the stage where they are touched, labelled with the asset and the technique, for example "Mail gateway, T1566 phishing". The actor is `security/threat-actor` with `palette: "red"`, labelled with its starting privilege. An external actor sits outside every boundary on the left; an insider, compromised account or compromised supplier starts inside the boundary where it holds trust. Observed steps are `data` edges with `palette: "red"`. Hypothesised steps are `control` edges with `palette: "red"`; this is a scoped exception to the control meaning, declared in the legend as `{label: "Hypothesised step", palette: "red", dashed: true}`. Do not use `dependency` for attack steps. A control that blocked a step gets a `status/blocked` symbol or a `marker` with `state: "blocked"`. A control that detected but did not stop it gets `status/warning`. A control that was absent, disabled or bypassed gets `status/down` or a marker with `state: "down"`. Defender response (containment, `security/quarantine`, `observability/incident`) uses `feedback` edges in teal or green.

**Attack graph.** For identity and cloud privilege paths that have no stage order. Left to right from the foothold to the target, no stage panels; boundaries only where an account, tenant or subscription changes. Nodes are the principals and resources: `identity/user`, `identity/group`, `identity/service-account`, `identity/access-token`, `identity/privileged-access`, `identity/admin`, and the target asset (for example `cloud/vpc` or `identity/secrets-vault`). Each edge is a step the attacker can take, labelled with the relationship ("member of", "can assume role", "session on host"), using the same observed and hypothesised convention as an attack path.

**Attack tree.** Top down. The root goal is a `component` with `asset: "presentation/process"` and `palette: "red"`. Sub-goals use `presentation/process`; a leaf uses the targeted asset when it touches a specific system, otherwise `presentation/process`. Edges run from child to parent as `dependency` edges with `source_port: "n"` and `target_port: "s"`. Mark AND and OR with a `presentation/fan-in` `symbol` node captioned "AND" or "OR" where children join, or in the parent's `detail` ("AND: all children required"). Mitigations are `component` cards using control assets (for example `identity/mfa`, `security/waf`, `security/edr`) beside the leaf they address, linked with a `control` edge, with `status/approved` or `status/pending` showing whether the mitigation is in place.

**Compliance data flow.** Same rules as the DFD, with three categories. The regulated environment (for PCI DSS, the CDE) is a `boundary` group in orange. Connected-to and security-impacting systems sit in their own `boundary` group in yellow, titled "In scope: connected / security-impacting". Out-of-scope systems are slate, and appear only behind a named segmentation control drawn on the crossing and labelled with its test status.

**Palettes.** Red for the actor and attacker movement, orange for regulated environments and sensitive stores, yellow for in-scope connected systems, blue for the system being defended, green or teal for controls and defender response, slate for external or out-of-scope context. Colour never replaces a label.

**Legend and footer.** Add a `legend` whenever more than one edge meaning or status appears. The legend draws every non-solid line with the same dash, and `control` and `feedback` edges render with the same dash pattern, so label each entry explicitly ("Red dashed: hypothesised step", "Green dashed: defender response"). Write `description` as a short narrative naming the scope, the actor and the outcome. The `footer` states that the diagram is a model for analysis, carries the handling classification, and where technique IDs appear reads "Technique IDs from MITRE ATT&CK Enterprise vNN. ATT&CK is a registered trademark of The MITRE Corporation." with the version used.

## Common mistakes

- Drawing a firewall or WAF in place of the trust boundary, or drawing the boundary and treating it as the control.
- Unlabelled flows across a boundary, or labels that name the protocol ("HTTPS") but not the data and its classification.
- Bidirectional arrows on DFD flows. Draw request and response as separate directed edges when they carry different data.
- Placing an external actor inside a boundary, or giving any actor the defended palette.
- Drawing every attack step solid, so the reader cannot tell what was observed from what was assumed, or mixing `control` and `dependency` for hypothesised steps in one drawing.
- Showing a control with no outcome. Every control on an attack path should carry blocked, warning or down status, or be labelled "outcome unknown".
- Building an ATT&CK matrix grid or using technique chips. Put technique IDs in card labels and keep the drawing to the path.
- Forcing an identity or cloud attack graph into stage panels when its steps have no stage order.
- In attack trees, omitting AND/OR, so the reader cannot tell whether one leaf is enough, or leaving goal cards without an `asset`, which fails validation.
- Putting connected or security-impacting systems in the slate out-of-scope group, or drawing an out-of-scope system with no segmentation control between it and the regulated environment.
- Treating retrieved content or tool output in an AI system as trusted because it comes from an internal store.
- Stand-ins when guessing: `security/firewall` for every control, `compute/rack-server` for every process, `data/relational-db` for every store, `identity/user` for every external entity, and an added SIEM or IDS the user never mentioned. Ask instead.
- Threat IDs such as T1, T2 that collide with ATT&CK technique IDs, or numbers in the diagram that do not match the threat register. Use TH-01 and confirm the scheme with the user.

## Start from

- `threat-model-dfd` for STRIDE, LINDDUN and compliance data-flow diagrams.
- `segmented-network` when the threat model or compliance scope is driven by network zones and the controls between them.
- `secure-ci-cd` for supply-chain threat models; `agent-mcp-tools` for AI and agent threat models; `zero-trust-access` for identity-aware enforcement points.
- `sec-incident-response` for the response process after detection.
- Attack paths, attack graphs and attack trees: no template yet; use `layout_diagram` to get initial positions, then group stages into panels by hand.
- Read alongside: the `brief` guide first, and call `stencil_guide` with no topic to list the network and security architecture guides when the path crosses network segments.
