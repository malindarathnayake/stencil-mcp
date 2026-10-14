# Privacy data maps, data residency and cross-border transfer

> Use this guide when the diagram shows where personal data goes for a privacy, legal or audit reader: a data flow map, a residency-by-jurisdiction view with transfer mechanisms, a data subject request flow, consent propagation, or a processor and sub-processor map.

## Questions to ask first

Ask these in one round when the brief leaves the fact open. Each answer changes what is drawn.

1. Which regime is the map for: GDPR, UK GDPR, CCPA/CPRA, LGPD, PIPL, India DPDP, HIPAA or another? The regime sets the role names and the rights you draw. (default: GDPR terms, meaning controller, processor and sub-processor. For CCPA/CPRA I would use business, service provider, contractor and third party. For HIPAA I would use covered entity and business associate.)
2. Which view do you want: personal-data flow map, residency by jurisdiction, data subject request flow, consent capture and propagation, or sub-processor map? (default: one personal-data flow map. Request and consent flows become separate diagrams, not extra arrows on the same one.)
3. Which data categories move, and does any of them need a regime-specific marking? Examples are GDPR Art 9 special-category data, Art 10 criminal-offence data, CPRA sensitive personal information and children's data. Is any of it pseudonymised or tokenised, and who holds the re-identification key or token vault? (default: "contact details" and "account data" only, with no sensitive marking, and no pseudonymised flows unless you name them)
4. Which countries hold the data, including replicas and backups? Does any law, contract or customer commitment require some categories to stay in one country (localisation)? (default: only the regions you name. Replicas and backups are labelled "location not stated" and listed in the footer. If you name no region at all, I ask instead of picking one. No localisation marking unless you state it.)
5. Which processors and sub-processors are in scope? For each one: what does it do, where is the legal entity established, and where does it process? Is any recipient a non-EEA entity even though its servers are in the EEA? (default: only the vendors you name, placed where you say. I will not add typical ones such as an email or analytics provider.)
6. Which flows are transfers, and what mechanism covers each one? Options include adequacy (for a US recipient, the EU-US Data Privacy Framework applies only if that recipient is certified), EU SCCs, the UK IDTA or UK Addendum, BCRs, or an Art 49 derogation. Does a transfer impact assessment exist? Do processors pass data onward to third-country sub-processors? (default: transfer edges and onward-transfer edges labelled "transfer mechanism: not stated". I will not guess a mechanism or a TIA.)
7. Where do support staff, administrators and on-call engineers work, which legal entity employs them, and can they reach the data remotely? (default: "support and admin access location not stated", drawn as an `identity/admin` card with a dashed edge labelled "access location not stated", plus a footer line)
8. What is the retention period for each store, including logs, backups and the analytics copy? (default: no retention shown, and a footer that says retention is not stated)
9. Which rights does the request flow cover? GDPR rights are access, rectification, erasure, restriction, portability, objection and rights about automated decision-making. CPRA rights are know, delete, correct, opt-out of sale or sharing, limit use of sensitive personal information, and Global Privacy Control as an opt-out signal. How is the requester's identity verified, and can authorised agents or people without an account submit requests? (default: access and erasure only, with a `presentation/decision` node labelled "Identity verification method not stated")
10. For erasure, which copies are in scope: primary database, replicas, caches, search index, warehouse, logs, backups and each processor? Which stores are kept despite erasure because of a legal obligation, legal claims or a litigation hold? Which recipients must be told? (default: every store on the flow map, with backups marked "expire by retention" and no retained stores or recipient notices unless you name them)
11. What lawful basis or purpose applies to each flow, and is consent actually the basis for any of them? For special-category data, which Art 9 condition applies? (default: purpose on the edge only where you state it. No consent gate unless consent is the stated basis. On a CCPA/CPRA map the gate is the opt-out, not a lawful basis.)
12. What is the source of these facts, such as records of processing or a vendor register, and its version or date? (default: footer says "Source not stated")

## Push back when

- **The user calls tokenised, hashed or encrypted data "anonymised".** It is pseudonymised. It remains personal data for the organisation that holds the key or token vault, and for any recipient who can reasonably re-identify it. Whether it is personal data for a recipient without the key is a legal call. Tell the user you will label it "pseudonymised" and show the key holder, not "anonymised".
- **Erasure scope leaves out backups, logs, replicas, caches, search indexes or the warehouse.** Deleting the primary row does not remove copies elsewhere. Backups usually cannot be edited in place. Common practice is to restrict them, let them expire on schedule and reapply erasure if a backup is restored. Draw that as stated, not as an instant delete.
- **Erasure is drawn for every store, but some data must be kept.** Invoices, tax records and records under a litigation hold are often kept under an exemption. Ask which stores are kept, and draw them with a label such as "Retained: legal obligation (as stated)" instead of an erase edge.
- **A residency map shows data "staying in the EU" but leaves out remote access.** Remote access from a third country by another legal entity (a group company, vendor or sub-processor) is a transfer even when storage stays in the EU. Access by the controller's own employees abroad is not a Chapter V transfer, but it still belongs on the map as a risk. Ask which entity employs the support staff.
- **A cross-border edge has no mechanism, or the user asks you to fill one in.** The label must come from their records. Draw "not stated" rather than inventing SCCs, DPF certification or an adequacy decision.
- **A flow leaves a store that the user says must stay in-country.** Localisation can forbid the export or require approval first, so the edge is not just a labelling question. Ask whether the flow really exists and under what approval.
- **A vendor is drawn as a processor but uses the data for its own purposes**, such as training its own models or building its own advertising profiles. Under GDPR that vendor is a controller for that use. Ask which it is and label the role to match.
- **Consent is drawn as the gate on every flow.** Consent is one of several lawful bases. Payroll and order fulfilment usually rely on contract or legal obligation. Draw the gate only on flows that depend on consent.
- **Consent withdrawal or an opt-out stops at the first system.** A withdrawal must reach every downstream system and processor that received the data on that basis. If it does not, show that in the drawing instead of implying it does.
- **The request flow returns data with no identity check.** Sending personal data to an unverified requester is itself a disclosure. Ask how identity is verified.

## How we draw it here

**Direction.** Flow maps run left to right: data subjects and collection points on the left, the organisation's systems in the middle, processors and sub-processors on the right. In a residency view, stack the jurisdictions vertically so transfer edges are short vertical lines that are easy to label. Rights and consent flows are swimlanes and follow the process rules in DESIGN_SYSTEM.md.

**Grouping.** Groups do not nest, so pick one meaning per diagram:
- Residency view: one `boundary` group per jurisdiction, titled by legal location rather than cloud region name ("EEA: Germany", "UK", "US"). A `cloud/cloud-region` symbol inside may name the hosting region. Put each card's owning entity and its country in `detail`.
- Processor map: one `boundary` group per organisation ("Our systems", "Processor: payments vendor"). Put the entity's country and processing location in each card's `detail`.
- Rights or consent flow: `lane` groups for data subject, privacy team, application owners and each processor.

**Asset roles.**
- Data subjects: `identity/user`. Staff with access: `identity/admin`. Groups of subjects: `identity/group`.
- Collection points: `software/frontend`, `software/browser`, `business/form`, `compute/mobile`, `business/chat`.
- Systems: `software/backend`, `software/microservice`, `software/rest-api`, `cloud/saas`.
- Stores: `data/relational-db`, `data/document-db`, `data/data-warehouse`, `data/data-lake`, `data/cache`, `data/search-index`, `data/database-replica`, `storage/backup`, `storage/immutable-backup`, `storage/snapshot`, `observability/logs`, `observability/audit-log`.
- Processors and sub-processors: `business/vendor` cards with the service, entity country and processing location in `detail`. Outside parties in a DFD-style view: `presentation/external-entity`.
- Pseudonymisation: `identity/secrets-vault` or `identity/key` for the token vault or key, labelled with who holds it. Use `security/dlp` only if the brief names a DLP control.
- Rights flow: `business/ticket` for the request, `presentation/decision` for the identity check, `business/report` for the access export, `business/email` for the response, `business/timer` for a stated deadline, `presentation/start-end` for trigger and outcome, `status/expired` for data removed by retention.
- Consent: `business/form` for capture, `software/event-bus` or `software/webhook` for propagation, and `security/policy-engine` only if a separate enforcement service exists.

**Edges on flow maps and residency views.**
- `data` for personal data moving between systems. Label it with category and purpose ("Contact details: billing").
- `replication` for replicas and backups, including cross-border copies.
- `control` for consent signals, erasure instructions and opt-out propagation.
- `feedback` for confirmations back to the controller.
- `dependency` for "processor relies on sub-processor" where no specific flow is drawn.
- Decide whether an edge is a transfer from the legal location of the exporting and importing entities (EEA or third country), not from cloud region names. Transfer and onward-transfer edges carry the mechanism only as stated ("EU to US: SCCs"), otherwise "mechanism not stated".

**Edges in rights and consent swimlanes.** Follow the DESIGN_SYSTEM.md process meanings. Use `data` for the step sequence, including sending the confirmation. Use `control` for hand-offs to a processor or to the data subject. Use `feedback` only for rejection or rework branches, such as "Identity not verified".

**Sensitive data.** Write the marking that matches the selected regime, in words, on the edge and on the store. Examples: "Health data (GDPR Art 9)", "Criminal records (GDPR Art 10)", "Precise location (CPRA sensitive PI)", "Children's data". GDPR Art 9 covers racial or ethnic origin, political opinions, religious or philosophical beliefs, trade union membership, genetic data, biometric data used for identification, health, and sex life or sexual orientation. Precise location and government ID are not Art 9 categories. Add a legend entry. A red palette can reinforce the text but never replace it, because the diagram may be printed in monochrome. Mark localised stores with a text badge such as "Must remain in-country (as stated)".

**Legend and footer.** Add a legend whenever more than one edge kind appears. The footer states the regime, the source of the facts and its version or date, and every unstated item ("Retention not stated for logs", "Backup location not stated", "Support access location not stated"). Write the `description` as a plain narrative of who collects what, where it goes and under what mechanism.

## Common mistakes

- Drawing a typical stack (analytics, email provider, CRM, CDN) the user never mentioned. Every processor on a privacy map is an assertion an auditor will check.
- Placing a vendor card inside the organisation's own boundary for layout convenience, which tells the reader the organisation controls it.
- Showing only the primary database, so logs, warehouse copies, search indexes and backups drop out of the erasure story.
- Treating cloud region as jurisdiction. A US-incorporated processor in an EU data centre can still be an importer. EU to UK or Switzerland is a transfer even under adequacy. EU to Norway (EEA) is not.
- Defaulting backups or support access to "same region" when the user never said so.
- Labelling location or government ID as GDPR "special category".
- Using `security/firewall` or `security/acl` as a stand-in for a privacy control. A boundary group is not a security control.
- Using `cloud/public-cloud` for every processor. A processor is an organisation, so use `business/vendor` and name its service.
- Drawing a request-flow confirmation as `feedback`, which reads as rework in a swimlane.
- Putting the flow map, the residency view and the erasure process into one crowded drawing.
- Drawing erasure as instant everywhere when backups expire on a schedule and some stores are kept under an exemption.

## Start from

- `threat-model-dfd` for personal-data flow maps and residency views. Replace its zones with jurisdiction or organisation boundaries.
- `software-overview` for a smaller system-level data inventory.
- `support-escalation` or `it-onboarding-access` as swimlane patterns for request, erasure and consent flows.
- For a fresh residency or processor layout with no matching template, use `layout_diagram`.
- Read alongside: `brief`, `data` (PII marking in pipelines), `threat-model` (LINDDUN privacy threats) and `style`.
