# Endpoint and device management (MDM/UEM, patching, conditional access, VDI)

> Use this guide when the diagram shows how end-user laptops, desktops, phones or virtual desktops are enrolled, kept compliant, patched, given apps, granted access, or wiped, revoked and retired.

## Questions to ask first

Ask these in one round, only for the facts the brief leaves open.

1. Which device types and platforms are in scope (Windows, macOS, Linux, iOS, Android), and should each be one card per type or one per device? (default: one card each for corporate laptops and mobile phones, drawn as types, not an inventory)
2. Who owns the devices: corporate-owned and fully managed, BYOD with an enrolled work container (Android work profile, Apple User Enrollment), BYOD with app protection only and no enrollment, or a mix? (default: corporate laptops fully managed; BYOD phones with app protection only)
3. Where does the management plane run: a cloud MDM/UEM service, an on-premises server, or both in co-management, and does a third-party MDM feed the identity provider through a partner compliance integration? (default: one cloud MDM/UEM service that reports compliance to the identity provider)
4. How do devices enroll and how are they bought: automated enrollment registered by the reseller, existing devices registered by IT, user-initiated enrollment, or bulk enrollment? (default: automated enrollment through the reseller for corporate laptops; no enrollment for BYOD)
5. Which compliance signals count, and who reports them? (default: the MDM agent reports OS version, encryption and screen lock; the EDR service reports device risk to the MDM through its connector; the MDM publishes compliant or non-compliant to the identity provider or policy engine)
6. How does the device prove its identity at access time: a device certificate, identity-provider device registration, or a client certificate at the access proxy? (default: identity-provider device registration, with a device certificate on corporate devices)
7. Which applications sit behind conditional access, where is access enforced, and what happens to a non-compliant device: block, limited access, or remediation? (default: the identity provider sign-in enforces and the policy engine decides; non-compliant devices are blocked and told how to remediate)
8. How are patch rings structured, how are they promoted, and is there an expedited path for critical or zero-day updates that bypasses ring deferrals? (default: Ring 0 IT pilot 1% with 0-day deferral, Ring 1 early adopters 10% at +3-7 days, Ring 2 broad 89% at +7-14 days, an install deadline per ring; promotion by deferral time with a pause or rollback check, or a manual approval only if the user says so; no expedited path drawn)
9. What is patched and where do updates come from: OS only, or also third-party apps, drivers and firmware; directly from the vendor service, an internal distribution point, or peer caching? (default: OS and browser updates, downloaded directly from the vendor service)
10. How are applications delivered: required pushes, a self-service catalogue, or both; and for virtual desktops, persistent or non-persistent, on-premises or DaaS, where profiles and files live, and whether apps are baked into the image or attached as layers? (default: MDM pushes required apps and offers optional ones in a catalogue; physical devices only, no VDI drawn)
11. What happens when a device is lost, stolen, or its user leaves, and which relying parties trust the device certificate (Wi-Fi/802.1X, VPN, proxy) and check revocation? (default: full wipe for corporate devices, selective wipe of work container or managed-app data for BYOD, session revocation in the identity provider, disabling the device object in the directory, and revocation of the device certificate at the issuing CA, checked by relying parties through CRL or OCSP)
12. Which extras are in scope: recovery key or local admin password escrow, vulnerability-driven patching and compliance reporting, device retirement, shared or kiosk devices, an enterprise browser, EDR detection workflows? (default: none drawn; EDR appears only as a risk signal source)

## Push back when

- **Full wipe of a BYOD device.** Work-container enrollment and app protection give the organisation control of corporate data only, and a full wipe would erase the owner's personal data. Tell the user that BYOD offboarding is a selective wipe of the work container or managed-app data, and ask whether those devices are really corporate-owned.
- **MDM compliance treated as proof a device is clean.** Compliance is a set of posture attributes reported by software on the device, and a compromised device can still report them. Tell the user that compliance is one input to the access decision, and that compromise detection comes from EDR and security operations.
- **Compliance drawn as part of the user's request.** The MDM evaluates the device on its own schedule and publishes a state. The request carries device identity (a device certificate or registered-device token), and the policy engine looks up that device's compliance state. Draw the compliance signal as a separate edge and label the request with the device credential.
- **The MDM drawn as the gate on application traffic.** The MDM console and service do not carry user traffic. If the UEM vendor's per-app tunnel or email gateway is in use, draw it as a separate enforcement component, not as the MDM box.
- **"Wipe instantly logs the user out everywhere".** Identity-provider revocation stops new tokens and refresh. Access tokens and app sessions already issued last until they expire, commonly up to about an hour, unless the app supports continuous access evaluation. A wipe stays pending while the device is offline, and a lost device may never check in. The device object must also be disabled in the identity provider.
- **Removing the certificate treated as revocation.** A stolen device keeps its certificate until a wipe runs. Revocation happens at the CA and only helps where relying parties check CRL or OCSP.
- **Automated enrollment for devices bought anywhere.** Automated enrollment (Autopilot, Apple Automated Device Enrollment, Android zero-touch or Knox) needs the device registered with the platform programme. The reseller usually does this, but IT can register existing devices (Autopilot hardware hash, Apple Configurator, with a provisional period). The device needs network access at first setup. Ask how devices are bought.
- **VDI with no profile or storage tier.** Non-persistent desktops reset from the image, so settings and files are lost at logoff unless a profile store and file share exist.
- **Patching non-persistent virtual desktops one by one.** Changes are discarded at refresh. Patch the golden image and roll it out.
- **A single ring called "staged rollout".** Ask whether the user wants a pilot ring; if not, draw one ring labelled "All devices".

## How we draw it here

Lay out plane diagrams left to right: devices on the left, management and identity in the middle, protected applications or virtual desktops on the right. Follow the security-architecture guide: `security/policy-engine` is the decision point and is never drawn as the enforcement point.

| Role | Asset ID |
| --- | --- |
| Corporate laptop or desktop, phone or tablet | `compute/laptop`, `compute/workstation`, `compute/mobile` |
| End user, IT administrator | `identity/user`, `identity/admin` |
| Cloud MDM/UEM service | `cloud/saas`, labelled "MDM / UEM" |
| On-premises MDM or update server | `compute/rack-server`, labelled with its role |
| App protection policy | `identity/key` or `software/backend`, labelled "App protection policy" |
| Identity provider, MFA, passkey | `identity/identity-provider`, `identity/mfa`, `identity/passkey` |
| Policy decision point | `security/policy-engine` |
| Enforcement point | `identity/identity-provider` (blocks at sign-in), `security/security-gateway` (access proxy, UEM email gateway), `network/vpn-gateway` (VPN or UEM per-app tunnel), labelled with the role |
| Device certificate, issuing CA, certificate connector | `identity/certificate` on the device card, `identity/certificate-authority`, `software/backend` labelled "Certificate connector" |
| Certificate-based Wi-Fi | `network/wireless-ap` |
| Token being revoked | `identity/access-token` |
| EDR risk signal | `security/edr`, placed with the services, not on the device |
| Recovery key or local admin password escrow | `identity/secrets-vault` |
| Vulnerability input to patch priority | `security/vulnerability-scanner` |
| Enterprise browser | `software/browser`, labelled |
| Quarantine or remediation | `security/quarantine` |
| Patch source, distribution point | `devops/artifact-registry`; `storage/file-share` or `compute/rack-server`, labelled |
| Manual ring approval, pause or rollback | `devops/release-approval`, `devops/rollback` |
| Protected application | `software/backend`, `cloud/saas` |
| VDI hosts, desktops, broker, gateway | `compute/hypervisor`, `compute/virtual-machine`, `software/backend` labelled "Connection broker", `security/security-gateway` labelled |
| Golden image, profile store, DaaS | `storage/snapshot` labelled "Golden image", `storage/file-share`, `cloud/saas` labelled |
| Audit trail | `observability/audit-log` |
| Device state | `status/healthy`, `status/warning`, `status/blocked`, `status/locked`, `status/pending` (wipe queued), `status/expired`, as `symbol` nodes with a `caption` |

Connector meanings in plane diagrams:

- `data` (solid): enrollment, the user's request (labelled with the device credential), update and app downloads, the desktop session, compliance state to the identity provider or policy engine, EDR risk to the MDM, and an expedited update path drawn as its own labelled edge.
- `control` (dashed): policy pushed to devices, the decision request, wipe and lock commands, token revocation, and "CRL/OCSP" from the CA to each relying party.
- `feedback` (dashed return): check-in status and install results back to the MDM.
- `tunnel` (long-dashed): VPN, per-app tunnel or remote display when the encapsulation is the point.
- `dependency` (dotted): desktops on the golden image; ring device cards on the approval node.

Palettes follow the zero-trust-access template: `blue` users and devices, `purple` identity and policy, `red` enforcement and wipe, block or revoke, `teal` protected applications and desktops, `orange` audit and approvals, `slate` ownership boundaries, `green` compliant, `yellow` warning or pending.

Group with `boundary` style for ownership (Corporate-owned, BYOD) and `panel` style for planes. Draw patch rings as side-by-side `panel` groups. Each ring panel holds at least one device card, such as `compute/laptop` labelled "Ring 1 devices" with detail "~10%, +3-7 days", and `group` set to the ring. Edges run between nodes such as that card and `devops/release-approval`, never to a group. Keep ring titles short ("Ring 1 – Early (10%)") or widen the panel, or validation warns with `group_title_width`.

Draw provisioning, lost-device and retirement lifecycles as swimlanes (Employee, IT, MDM, Identity provider) using the DESIGN_SYSTEM process conventions: `data` for process flow, `control` orange for an external hand-off, `feedback` red for rework. Wipe, revocation and device-disable are task cards ("Send wipe command", "Revoke sessions", "Disable device object"), not control edges. Add `status/pending` for a wipe waiting on check-in.

Add a `legend` whenever more than one connector meaning appears. The `footer` states that the diagram is illustrative, that generic symbols do not assert product compatibility, and, when used, that compliance is posture reporting rather than proof of integrity.

## Common mistakes

- Drawing the compliance signal from the user's request or from the device straight into the application, or drawing a request with no device credential.
- Making `security/policy-engine` the box application traffic passes through, or drawing the MDM box as the traffic gate.
- Using `security/edr` or `security/nac` as a stand-in for the MDM. Use `cloud/saas` or `compute/rack-server` with a clear label.
- Adding a VPN gateway, NAC, tunnel or on-premises update server the user never mentioned.
- Drawing rings with no deferral or share, with empty ring panels, or with edges pointing at the group.
- Showing a full wipe for BYOD, a wipe without token revocation and device disable, or certificate "removal" instead of CA revocation.
- Drawing VDI as desktops only, with no broker, gateway, image or profile store.
- Inventing device icons. Printers, cameras, IP phones, thin clients and kiosks have no asset. Use `presentation/external-entity` with an explicit label, `compute/workstation` or `compute/edge-server` only when the role fits, or a `text` node. Tell the user the symbol is a known gap.
- Using control edges for wipe steps inside a swimlane, which clashes with the process meaning of `control`.

## Start from

- Conditional access and device compliance: `zero-trust-access`.
- Automated provisioning for a new hire: `it-onboarding-access`, with `hr-employee-onboarding` when HR triggers the request.
- Lost-device wipe and revoke, and device retirement: `it-onboarding-access` or `sec-incident-response`, with lanes renamed to Employee, IT, MDM, Identity provider.
- Patch rings, app delivery and VDI: no template yet. Use `layout_diagram` for initial positions. It creates component nodes only and no groups, so add `panel` and `boundary` groups and set each node's `group` by hand.
- Read alongside: `brief`, `style`, `security-architecture` for the decision versus enforcement split, `security-operations` for EDR detection and response, and `fleet-iot` for vehicles and in-cab devices.
