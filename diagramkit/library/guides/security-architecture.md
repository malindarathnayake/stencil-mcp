# Security architecture, segmentation and identity

> Use this guide when the diagram shows trust zones, enforcement points, compliance scope, zero-trust access, identity and federation, PKI or secrets, SaaS data controls, or privilege paths.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. Each has the default you will use if the user says to proceed.

1. Which zones or trust boundaries exist, and who owns each one? (default: only the zones named in the brief, such as Internet, DMZ and Internal, with no owner labels)
2. What is in scope and what is out of scope, and which connected or security-impacting systems (directory, jump hosts, patching, logging, IdP) touch the scoped systems? (default: only the systems named as in scope sit inside the scope boundary; everything else is drawn outside it, not omitted)
3. Which flows between zones are permitted, which side opens the connection, and on which protocol and port? (default: draw only the flows the brief names, one edge per flow from the initiator, labelled with the protocol it gives; no implied "allow all" edges and no return-traffic edges)
4. What is the enforcement point between each pair of zones, is it one device or a pair, and is any control host-attached (security group, microsegmentation, host firewall)? (default: one enforcement point per boundary that the brief names; a boundary with no named control is drawn as a boundary only)
5. Where is TLS terminated, re-encrypted or inspected? (default: not drawn unless named; when named, label the edge after the termination point "HTTP (cleartext)" or "TLS re-encrypt")
6. For zero-trust access: which component decides, which enforces, is a separate policy administrator named, and which inputs does the decision use (identity, authentication strength, device posture)? (default: the identity provider named in the brief sends identity context to security/policy-engine; security/security-gateway sends a decision request to the policy engine, which returns allow/deny; policy engine and administrator are one card; MFA and device posture only if named)
7. For SSO or federation: which components are the client, the authorization server or identity provider, and the resource server (API); which party issues tokens and which validates them? (default: the identity provider issues, the application validates, and the application trusts the identity provider, not the reverse)
8. Is the protocol SAML, OIDC, or something else, and does any application or gateway mint its own session or internal token after validating the identity provider's token? Are service accounts or privileged-access sessions part of the picture? (default: protocol written as a label only if given; one issuer; no service accounts or privileged access shown)
9. For PKI: which CA tiers exist (root, policy or intermediate, issuing per purpose), is the root offline, are CA keys held in an HSM, and where are the CRL distribution point and OCSP responder published? (default: the CA tiers the brief names; if it names one CA, one CA card labelled as the brief labels it; no HSM, CRL or OCSP unless named)
10. For secrets: where do secrets live, how does the workload authenticate to the vault (platform identity, cloud IAM role, AppRole, mTLS), and how do secrets arrive (agent or sidecar injection, environment at deploy, runtime API call)? (default: a `control` edge from the workload to identity/secrets-vault labelled with the auth method, and a `control` edge back labelled "short-lived credential")
11. Which logs and audit trails must appear, and where do they go? (default: no audit or log sink unless the brief names one; if named, decision and enforcement points send to it)
12. For SaaS controls: is the CASB inline (proxy) or API-based, and does DLP inspect in transit, at rest, or both? (default: API-based CASB reading from the SaaS; DLP drawn only where the brief places it)
13. For offboarding or privilege paths: what triggers the leaver flow (HR system, ticket, person), which systems must revoke or delete, are active sessions and refresh tokens revoked, and which accounts sit outside SSO or SCIM (local admins, API keys, shared secrets)? (default: the trigger the brief names; if none, the identity provider deprovisions the listed systems with edges labelled "SCIM deprovision" or "session revoke", and no ticket)

## Push back when

- The brief puts the policy decision and the enforcement in one box while calling the design zero trust. Say that the drawing can merge them only if they really are one component, and ask whether to keep them separate.
- The brief shows an application issuing tokens while also using an identity provider. Ask whether the application or gateway mints its own session or internal token after validating the identity provider's token; if so, draw both issuers with labelled `control` edges. If not, the identity provider issues and the relying party or resource server validates.
- The brief draws federation trust pointing from the identity provider to the application. The relying party is configured to trust the identity provider's signing keys; ask the user to confirm the direction before drawing.
- The brief shows an online root CA issuing end-entity certificates directly while also describing an offline root. An offline root signs subordinate CA certificates and its own CRL; issuing CAs sign end-entity certificates. Ask which arrangement is real.
- The brief places outside PCI scope a system that stores, processes or transmits cardholder data, has any connectivity to the cardholder data environment (CDE), or can affect its security (directory, jump hosts, patching, logging, IdP). Tell the user it is in scope as a CDE or connected-to system, and ask what isolates it.
- The brief claims a segment is out of scope while a permitted flow reaches the CDE. A segment with any permitted flow into the CDE is connected-to and in scope, whatever firewall sits between them; only segments with no permitted path are out of scope. Ask what blocks all traffic, and whether segmentation has been validated by a penetration test (PCI DSS 11.4.5 and 11.4.6).
- The brief shows a secret or private key sent over a plain data edge. Ask whether it is injected, fetched over an authenticated channel, or never leaves the HSM; private keys held in an HSM are used inside it, not exported.
- The brief treats a trust boundary as the control itself. A boundary is a container; ask which device or service enforces it.

## How we draw it here

Flow runs left to right, from the least trusted zone (Internet, external users) to the most trusted (data stores, CDE, root of trust). Each trust zone is a `group` with `style: "boundary"` and a title that names the zone and, when known, its owner. Draw compliance scope as its own boundary group, separate from the trust zones, because scope can cut across zones; title it with the words "In scope" or "Out of scope" (for example "PCI scope: CDE + connected-to") so the meaning survives monochrome and colour-blind viewing. Use `style: "panel"` to split a long story into views, such as "Access" and "Certificate lifecycle".

Network enforcement points (firewall, WAF, VPN gateway, reverse proxy) sit on the boundary they enforce: place the card across the shared edge between two zones, not deep inside one. A straddling card has no `group` field, because validation rejects a grouped node that extends past its group; position it by coordinates. Security groups, microsegmentation, NAC and host firewalls attach to the workload or port they protect: place them beside or on that workload, not on a zone edge.

Every permitted flow is its own edge, drawn from the side that opens the connection and labelled with protocol and port when the brief gives them ("HTTPS 443", "SSH 22 from bastion only"). Do not draw return traffic for stateful flows; it implies an inbound rule that does not exist.

Roles and asset IDs:

- Zones and places: cloud/vpc, cloud/subnet, cloud/datacenter, cloud/saas, network/internet, cloud/branch-office.
- Enforcement points: security/firewall, security/waf, security/security-gateway, security/acl, security/security-group, security/microsegmentation, security/nac, network/vpn-gateway, network/reverse-proxy.
- Zero trust: security/policy-engine for the decision point (and the policy administrator unless the brief separates it), security/security-gateway for the enforcement point, identity/identity-provider as the identity source, identity/mfa attached to the identity provider when named, security/edr or security/nac as a device-posture input when named.
- Identity: identity/user, identity/admin, identity/group, identity/service-account, identity/federation, identity/passkey, identity/access-token, identity/privileged-access, compute/bastion-host.
- PKI and secrets: identity/certificate-authority (label "Root CA (offline)" or "Issuing CA"), identity/certificate, identity/key, hardware/hsm-device, identity/secrets-vault; status/expired, status/warning and status/healthy as symbol nodes beside a certificate to show its lifecycle state.
- SaaS data controls: security/casb, security/dlp, cloud/saas.
- Detection and records: security/siem, security/ids, observability/logs, observability/audit-log.
- Process triggers and retention: business/ticket, business/approval, business/timer for retention periods, storage/backup and storage/immutable-backup for retained copies.

Edge kinds: `data` for user traffic and payloads, `control` for policy decisions, configuration, token issuance, secret delivery and deprovisioning, `dependency` for trust relationships (relying party depends on the identity provider; issuing CA depends on root), `tunnel` for VPN or mTLS overlays, `feedback` only for a distinct application-level message such as a deny page or webhook. Label every `control` edge with what it carries ("allow/deny", "signed assertion", "short-lived DB credential").

Palettes: green for in-scope groups, slate for out-of-scope groups, third parties and shared services, red only for hostile or untrusted zones (an out-of-scope corporate zone is not hostile), orange for enforcement points, purple for identity and keys. Colour never carries scope alone; the group title does. State the scope rationale in a presentation/callout or text node next to the scope boundary ("Out of scope: no CDE connectivity; receives tokens only, cannot detokenise"). Add a `legend` whenever more than one edge kind or scope colour appears, and use `footer` for the assessment date, standard (such as PCI DSS v4.0.1 or ISO 27001) and the assumptions you made.

## Common mistakes

- Adding a firewall, WAF, IDS, MFA, audit log or DDoS service the brief never mentioned because a typical design has one. Ask instead.
- Setting `group` on a card that straddles two zones, which fails validation with `group_containment`.
- Placing a network enforcement point deep inside a zone, away from the boundary it controls. The `segmented-network` template places the WAF fully inside the DMZ group; move it onto the shared edge when you copy it, and recolour its groups to match the palette rules above.
- Drawing a security group or microsegmentation control on a zone edge instead of on the workload it protects.
- Merging security/policy-engine and security/security-gateway into one card, drawing the identity provider as the enforcement point, or drawing MFA as a separate input to the policy engine.
- Drawing one generic "allow" edge between zones, or adding response edges back into an untrusted zone.
- Using colour alone to show scope, or reusing one red group for both "out of scope" and "untrusted".
- Dropping out-of-scope systems from the picture. They belong outside the scope boundary, visible, with the connection or absence of one that justifies their status.
- Inventing icons for roles, policy documents, accounts or control IDs. There are none; use identity/key, security/policy-engine or a component card with a clear label and detail.
- Trying to draw a control matrix or requirement-to-control mapping. The kit has no table layout; say so and offer a diagram plus a separate table in the reply.
- Using identity/certificate for a CA, or adding a root and issuing tier the brief never described.
- Drawing secrets moving on an unlabelled `data` edge, a single vault-to-workload edge for a runtime pull, or a private key leaving hardware/hsm-device.
- Using status/locked or status/blocked to mean "secure"; those are state markers, not controls.
- Showing step order (login, redirect, token exchange) in an architecture view. Step order belongs in a sequence diagram.

## Start from

- Segmentation, DMZ, PCI CDE scope, compliance boundaries: `segmented-network` (move the WAF onto the boundary and adjust group palettes).
- Zero-trust and identity-aware access: `zero-trust-access`.
- Data flows across trust boundaries for threat modelling: `threat-model-dfd`.
- PKI hierarchy, secrets delivery, CASB/DLP, privilege-escalation graphs, retention flows: no template yet; use `layout_diagram`, then place straddling enforcement cards by coordinates.
- Offboarding as a process: copy the lane pattern from `it-onboarding-access`.

Read alongside: `brief` first, then `sequence` for SSO, OIDC or SAML step order, `network` for the underlying topology, `kubernetes` when secrets are injected into pods, and `style` last.
