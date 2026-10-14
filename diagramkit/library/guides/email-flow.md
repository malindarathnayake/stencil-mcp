# Email flow and email security

> Use this guide when the diagram shows how mail enters, leaves or moves inside an organisation, which controls inspect it, where sender authentication (SPF, DKIM, DMARC) is checked, or how a reported phishing message is remediated.

## Questions to ask first

1. Which flows should the diagram show: inbound, outbound, internal mailbox-to-mailbox, or a combination? (default: inbound only; outbound is added only if the brief mentions sending, DLP or DKIM signing; internal mail is not shown, and if it is shown it stays inside the mailbox platform)
2. Where do mailboxes live (a SaaS mail platform, an on-premises mail server, or both), and in a hybrid setup which side receives internet mail first? (default: a single SaaS mailbox platform; for hybrid, MX points to the cloud side, which routes on-premises mailboxes over a TLS connector)
3. How is inbound mail filtered: the mailbox platform's native filtering, an inline secure email gateway that the MX record points to, or an API-connected product, and if API-connected, does it run before or after delivery? If there is an inline gateway, does the mailbox platform accept internet mail only from the gateway's IPs? (default: an inline gateway via MX, with the platform locked to accept inbound mail only from the gateway)
4. Is attachment and link sandboxing part of the gateway path, or a separate step that runs after delivery or at click time? (default: the gateway hands suspicious attachments to a sandbox before releasing the message)
5. Which DNS records should be shown (SPF, DKIM key, DMARC policy, and optionally MTA-STS, TLS-RPT or BIMI), and what DMARC policy is published (p=none, p=quarantine or p=reject)? (default: SPF, DKIM key and DMARC only, DMARC at p=quarantine)
6. Which hop evaluates inbound SPF, DKIM and DMARC: the gateway, or the mailbox platform behind it? If the platform, is ARC trust or a connector feature that looks past the gateway (such as enhanced filtering) configured? Should forwarding or mailing lists, which break SPF and often DKIM, be shown? (default: the gateway evaluates; forwarding and ARC are not shown)
7. Who signs outbound mail with DKIM, and do third-party services (marketing, ticketing, billing) send on the organisation's behalf? (default: the outbound gateway signs after the last message change; no third-party senders)
8. Is outbound DLP applied in the mail path, in the mailbox platform, or by an API-based CASB, what happens on a match, and is message-level encryption (S/MIME or an encryption portal) used? (default: inline DLP before the outbound gateway, matches quarantined; transport TLS only, stated as an assumption)
9. Is there journaling or archiving, and if so, which component sends the journal copy and where does it go? (default: no archive unless the brief mentions retention, legal hold or compliance)
10. Do on-premises applications, scanners or devices send mail through an SMTP relay? (default: none)
11. Should quarantine handling (user digests, release requests, non-delivery reports) or the phishing report and purge loop be included? (default: neither; if quarantine is shown, release is an admin-only control edge; if the phishing loop is shown, a SOAR playbook searches and purges matching messages)
12. Is the diagram meant to explain the protocol checks step by step, or to show the deployed architecture? (default: architecture; copy the sequence-request template only when the brief asks how the checks work)

## Push back when

- The brief draws DMARC "p=reject" as an enforcement point inside the sending organisation. The domain owner only publishes the policy in DNS; the receiving server evaluates it and decides whether to reject, quarantine or deliver. Tell the user the enforcement point belongs on the receiver's side.
- The brief treats SPF alone as anti-spoofing. SPF checks the envelope sender (the Return-Path domain) against the connecting IP, not the From address the user sees, and it usually fails when mail is forwarded. Tell the user that protecting the visible From domain needs DMARC, which requires SPF or DKIM to pass and to align with that domain.
- The brief shows the mailbox platform doing sender authentication behind an inline gateway, especially one that adds banners or rewrites links. After the gateway relays the message, the platform sees the gateway's IP as the connecting host, and body changes break the original DKIM signature. Tell the user the check either happens at the gateway or needs ARC trust or a connector feature that looks past the gateway, and ask which one applies.
- The brief places a sandbox inline in the delivery path while also saying the product connects through the mailbox platform's API. API-connected tools usually scan after delivery, though some offer a pre-delivery mode. Ask which mode the product runs in and draw only that path.
- The brief shows DNS as a hop the message passes through. The sending server looks up the recipient domain's MX (and MTA-STS or TLSA records if TLS is enforced); the receiving server looks up the sender domain's SPF, DKIM public key and DMARC records. The message itself goes directly from server to server. Draw each lookup as a `dependency` edge from the server that makes it.
- The brief has a gateway modify outbound messages (disclaimer, banner, link rewriting) after DKIM signing. Changes to signed headers or body break the signature. Tell the user that signing must happen after the last change.
- The brief says SMTP between organisations is always encrypted. Server-to-server STARTTLS is opportunistic by default; enforcement needs MTA-STS, DANE or a forced-TLS connector. Ask which applies before labelling a link as encrypted. Transport TLS also differs from message encryption such as S/MIME, which protects the message at rest.
- The brief claims a gateway cannot be bypassed. A second MX record pointing at the mailbox platform is one bypass; the more common one is sending directly to the SaaS platform's default inbound host, which accepts mail whatever the MX says unless an inbound connector restricts it to the gateway's IPs. Ask whether that lock-down exists; if not, draw or footnote the bypass path.
- The brief says SPF, DKIM and DMARC stop all phishing. They do not stop mail sent from a compromised internal or partner account, because that mail authenticates correctly. Tell the user this business email compromise case needs identity controls such as MFA and the identity provider's sign-in policy.

## How we draw it here

- Lay out left to right. The internet and external senders sit on the left; the organisation's boundary sits on the right. When both directions are shown, put inbound on the upper row and outbound on the lower row, sharing the internet and DNS cards, or split into two panels if the rows become crowded.
- Draw the organisation as a group with style `boundary` (for example "Organisation mail domain"). Use a `panel` group for an external sending or receiving domain, and a separate `panel` for the on-premises side of a hybrid setup.
- DNS has no asset. Draw it as a `symbol` node using `presentation/external-entity`, labelled "DNS", with a caption listing the records shown.
- Use these assets for these roles:
  - `network/internet` for the public internet; `security/threat-actor` for a phishing sender.
  - `business/email` for the message itself, or for an external sending server when no better asset fits.
  - `security/security-gateway` for the secure email gateway, outbound gateway or SMTP relay; label it with its role, not a product name.
  - `security/sandbox` for attachment and URL detonation; `security/quarantine` for held messages.
  - `security/dlp` for inline outbound DLP; `security/casb` for an API-connected scanner on a SaaS mailbox.
  - `cloud/saas` for a SaaS mailbox platform; `compute/rack-server` labelled "On-prem mail server" for an on-premises server.
  - `identity/user` for senders and recipients; `identity/key` for the DKIM private key; `identity/certificate` for TLS or S/MIME certificates.
  - `compute/workstation` or `software/background-worker` for applications and devices that send through a relay.
  - `storage/object-store` or `presentation/data-store` labelled "Mail archive" for journaling targets.
  - `business/report` for DMARC aggregate and TLS-RPT reports; `security/siem`, `security/soar` and `observability/incident` for the phishing loop; `identity/mfa` and `identity/identity-provider` for account-takeover controls.
- Edge kinds: `data` for message transfer (SMTP or API delivery), `dependency` for DNS lookups from the server that makes them, `control` for quarantine, release, purge or rule updates, `feedback` for verdicts, bounces and DMARC reports, and `replication` for the journal copy.
- Mark each SPF, DKIM or DMARC check on the hop that performs it, using the edge label or a caption on that node, never on a node that only receives the message afterwards.
- Palettes: blue for inbound mail, teal for outbound mail, red for the phishing, bypass or blocked path, slate for DNS lookups. Add a `legend` entry for each palette and dashed style used ("Inbound mail", "Outbound mail", "DNS lookup", "Remediation action").
- Label each mail edge with the protocol or step ("SMTP/TLS", "API scan", "Journal copy"), not with arrows alone.
- Use the `footer` for assumptions the picture cannot show: the DMARC policy value, whether TLS is enforced, whether the platform is locked to the gateway, and that the drawing is illustrative.
- For a step-by-step explanation, copy the sequence-request template: put sending server, DNS, receiving server and mailbox as component columns, and draw each lookup and check as a labelled edge in its own text row. Show the DMARC result as a `presentation/decision` symbol with labelled branches ("Aligned pass", "Fail").

## Common mistakes

- Drawing DNS as a firewall, router or `network/load-balancer` because there is no DNS asset. Use the labelled external-entity card.
- Using `security/firewall` or `security/waf` as a stand-in for the email gateway. Use `security/security-gateway` and label it.
- Using `software/message-queue` or `software/message-broker` for a mail server. Those mean application messaging, not SMTP.
- Placing the DMARC policy or "reject" decision inside the sending organisation instead of at the receiving server.
- Drawing sender authentication at the mailbox platform behind a gateway without ARC or a connector feature to support it.
- Drawing the sandbox both inline and as an API scanner in the same flow.
- Routing internal mailbox-to-mailbox mail out through the inbound gateway when the brief does not say so.
- Drawing a gateway in front of a SaaS mailbox with no note on whether the direct-to-platform path is closed.
- Treating an SPF include as enough for a third-party sender. An include passes SPF only for the service's own Return-Path domain, which does not align with the organisation's From domain. Each sender needs DKIM signing with the organisation's domain (preferred) or a custom Return-Path under it plus an include. Many includes also break SPF's 10-DNS-lookup limit, and a third-party outbound gateway's IPs must be in SPF.
- Showing outbound mail through the inbound path with the same palette, so the reader cannot tell the directions apart.
- Drawing the journal copy as a `data` edge into the mailbox flow, which reads as a second delivery. Use `replication` to the archive.
- Showing a phishing purge or quarantine release as a `data` edge. Both are `control` actions.
- Omitting the legend when inbound, outbound, lookup and remediation edges all appear.

## Start from

- No template matches mail flow directly; use `layout_diagram` for inbound, outbound, relay and hybrid routing diagrams.
- `sequence-request` for a step-by-step SPF, DKIM and DMARC check between sending server, DNS, receiving server and mailbox.
- `threat-model-dfd` when the brief is about trust boundaries and data flows around the mail system.
- `sec-incident-response` for a swimlane version of the phishing report and remediation loop.
- `hybrid-cloud` as a reference for laying out on-premises and cloud sides when mailboxes are split.
- Read alongside: the `security-operations` guide for the phishing loop and the `security-architecture` guide for identity and account-takeover controls. Call `stencil_guide` with no topic to confirm which topics exist.
