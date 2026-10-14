# Fleet telematics, IoT and field operations

> Use this guide when the diagram shows vehicles, trailers or field devices sending positions, events, vehicle data or video to a platform; the dispatch, coaching, maintenance, provisioning, firmware or device-health work around them; or an approximate IoT/OT edge or Purdue-level layout.

## Questions to ask first

Ask these in one round, only for facts the brief leaves open. Each answer changes what is drawn.

1. Which view is this, and how many vehicles or sites does it show? Options: device-to-cloud data path, dispatch/coaching/maintenance workflow, device provisioning, firmware (OTA) rollout, fleet device-health monitoring, an upload/ack/retry sequence, or an OT/Purdue view. (default: device-to-cloud data path with one representative vehicle labelled "× N vehicles")
2. Which devices are fitted to each vehicle, and is the cellular modem built into the telematics unit? (default: one telematics unit with a built-in modem and one dashcam that uploads through it)
3. Is there an in-cab tablet or driver app, does dispatch message the driver through it, and how is the driver identified on the vehicle (NFC/RFID fob or app login)? (default: no driver app or display; driver identification not shown)
4. Does the telematics unit read the vehicle bus, and is hours-of-service/ELD compliance in scope? (default: yes, odometer, engine hours and fault codes over J1939/OBD-II; HOS/ELD not shown)
5. Are there other sensors or tracked assets, such as trailers, reefer temperature, door or tyre-pressure sensors, BLE asset tags, or unpowered trackers that report rarely? (default: none shown)
6. What is the uplink, and how do devices connect to the platform: an MQTT broker or IoT hub, a vendor TCP/UDP listener, or HTTPS? (default: cellular LTE through a mobile network and the public internet to an MQTT/IoT broker endpoint; clips upload over HTTPS, often by pre-signed URL straight to the object store; no Wi-Fi offload, satellite or private APN)
7. What is detected on the device, which event types matter, and what is evaluated in the cloud? (default: the telematics unit detects harsh braking and impact from its accelerometer and sends GPS fixes and events; the dashcam detects camera-based events and trims clips; geofence and speeding checks run in the cloud unless the user says on-device)
8. How does video work? Can reviewers request historical footage from the device's local storage, is live view offered, and is a retention or privacy rule part of the point? (default: continuous local recording, automatic event-clip upload, no historical request, no live view, no retention note)
9. Who consumes the outputs, are there outside integrations (ERP, TMS, fuel cards), and for a review workflow who acts and what are the end states? (default: dispatcher, safety and coaching team and maintenance team; no integrations; safety reviewer, then coach, then driver acknowledgement, ending "Coaching closed" or "No action")
10. How are devices authenticated and enrolled, and is traffic isolated? (default: per-device certificate over TLS across the public internet; enrollment and the issuing CA not shown unless this is a provisioning view; no VPN or private APN)
11. For a firmware rollout, which stages exist and who approves? (default: build in an artifact registry, approval, a pilot ring, then the full fleet, with rollback if devices fail to report healthy)
12. For an OT or industrial view, which Purdue levels are in scope and is there a DMZ between plant and enterprise? (default: Levels 0 to 4/5 with a Level 3.5 DMZ; plant data leaves only through the DMZ)

## Push back when

- The brief draws position coming from the cellular network. A GNSS fix is normally computed in the device; the cellular link carries the result and may carry A-GNSS assistance data. If the brief means network location (cell-ID or Wi-Fi) as a fallback, ask, and label the source explicitly, such as "Network location (cell-ID)".
- The brief promises guaranteed real-time delivery from moving vehicles. Coverage has gaps and devices commonly buffer and send later. Ask whether to show buffering, and do not label the path "real-time" unless the user confirms a latency target.
- The brief calls the video design "event-based" but also asks for continuous upload or live streaming from every vehicle. Continuous local recording with event-based upload is normal; continuous upload is a different policy with very different cellular data use. Ask which one they mean.
- The brief has the dispatcher or coach talking directly to the device. Commands to the device go through the platform. Voice or phone contact between dispatcher and driver is a separate person-to-person path; ask whether to show it, and draw it to the driver, not the device.
- The brief draws a geofence as a container that vehicles sit inside. A geofence is a stored boundary that positions are compared against; it is data, not a network or physical zone.
- An OT brief connects Level 0 to 2 devices straight to the internet or a cloud service while also describing a DMZ. That path bypasses the DMZ. Ask whether traffic really goes direct or through Level 3.5.
- An OT brief describes a one-way (unidirectional) gateway and also shows commands flowing back into the plant. A one-way gateway cannot carry return traffic. Ask which is true.
- The brief calls the Purdue drawing a compliance zone design. Purdue is a reference model for levels; zones and conduits for a security standard need their own analysis. Draw it as approximate and say so in the footer.

## How we draw it here

Flow runs left to right: field (vehicles, trailers or plant), uplink, ingest, processing and storage, then consumers on the right.

- **Vehicle.** A `group` with `style: "panel"` titled with the vehicle type, containing `fleet/telematics-unit` and `fleet/dashcam` cards. Add `fleet/vehicle` as a data-source card whenever vehicle-bus data is in scope, with a `physical` edge labelled "J1939" or "OBD-II". Set each node's `group` so containment is checked.
- **Buffering.** When confirmed, put `protocol/queue-buffer` labelled "Store-and-forward buffer" inside the vehicle panel on the telematics-unit path, optionally `resilience/retry` near the uplink edge, and a footer note "Sent when coverage returns".
- **Driver and extra devices.** `compute/mobile` labelled "Driver app" or "In-cab tablet" inside the panel. An asset or trailer tracker is `fleet/telematics-unit` labelled "Asset tracker"; a sensor is `presentation/process` labelled with its role ("Reefer temperature sensor"), joined by `physical` edges labelled "BLE".
- **Uplink.** `network/modem` labelled "Cellular modem (LTE)" only when separate; otherwise put "LTE" in the telematics unit `detail`. `network/wan-provider` labelled "Mobile network (LTE/5G)" and `network/internet` when traffic crosses it. There is no cell-tower icon.
- **Data artefacts.** `fleet/gps-fix`, `fleet/event-clip` and `fleet/geofence` as cards or symbols that name what is carried, beside the edge or in the store they land in.
- **Edge site.** `compute/edge-server` labelled "Edge gateway" for an on-site gateway, `cloud/branch-office` for a depot or yard, `cloud/edge-location` for a provider edge.
- **Cloud ingest.** A `boundary` group for the platform owner containing `software/message-broker` labelled "IoT broker (MQTT)" (or `compute/rack-server` labelled "Device listener (TCP/UDP)" for a vendor protocol; `network/api-gateway` or `software/rest-api` only when the user says HTTPS), `data/stream-processor`, `data/time-series-db` for position history, `storage/object-store` for clips, `data/relational-db` for events and assets, and `software/background-worker` for scoring or clip processing.
- **Video retrieval.** Historical footage on request is a `control` edge "Video request" to the dashcam and a `data` edge "Requested clip" back. Live view, when confirmed, is a `control` request plus a separate `data` edge "Live view (on request)". Retention goes in the footer; add `security/dlp` only if named.
- **Consumers.** `fleet/dispatcher`, `fleet/coaching-session` and `fleet/maintenance-bay` on the right, `software/frontend` for the web console, and one `software/external-service` or `software/webhook` with its own `data` edge per named integration.
- **Security.** `identity/certificate` for device identity, `security/firewall` at real enforcement points, `security/siem` only if named.
- **Provisioning view.** `identity/certificate-authority` issuing `identity/certificate`, `security/policy-engine` for the per-device access policy, and `control` edges for enrollment steps.
- **Firmware rollout view.** `devops/artifact-registry`, `devops/release-approval`, `devops/cd-release` per ring, `devops/rollback`, and `control` edges labelled "Firmware update" to devices. There is no OTA icon.
- **Device-health view.** `observability/health-probe` or heartbeat `data` edges into `observability/metrics`, then `observability/alert` ("Device silent > 24 h") and `observability/dashboard`; `status/healthy`, `status/warning`, `status/down` or `status/unknown` beside devices.
- **Sequence view.** `presentation/sequence-lifeline` per participant, `data` edges for uploads, `feedback` edges with `protocol/ack`, and `resilience/retry` where a resend happens.
- **Workflow views.** Follow DESIGN_SYSTEM.md process rules: lanes are roles (driver, safety reviewer, coach, dispatcher, maintenance), tasks are verb-object cards, `presentation/decision` for questions such as "Clip shows unsafe driving?", `business/ticket` for work orders, `business/timer` for SLAs, `presentation/start-end` for the trigger and each end state.
- **Purdue view.** Stack `panel` groups top to bottom, using `boundary` where a level is a trust zone: L4/5 enterprise, L3.5 DMZ as a `boundary` holding `security/firewall`, `compute/bastion-host` and an optional replicated `data/time-series-db`, L3 `data/time-series-db` "Site historian", L2 `compute/workstation` "Operator HMI" and `compute/rack-server` "Supervisory server (SCADA)", L1 `compute/edge-server` "Controller (PLC)", L0 `presentation/process` "Field devices (sensors, actuators)". L3.5 is a common convention, not part of the original Purdue model.

Connector meanings: `data` (solid arrow) for telemetry, fixes, clips and events, labelled with the payload; `control` (dashed) for configuration, commands, video requests and firmware; `feedback` (dashed return) for acknowledgements and workflow rework; `physical` (no arrow) for in-vehicle cabling, BLE or a plant link, only when the physical path is the point; `tunnel` for a VPN or private APN the user confirmed.

Keep palettes consistent within one diagram, for example teal for data, orange for control, red for feedback, slate for the vehicle panel and blue for the cloud boundary. Add a `legend` whenever more than one connector kind appears. Use the `footer` for assumptions, such as "Representative vehicle; fleet of N" or "Approximate Purdue levels; not a zone and conduit design". Do not draw a map background; canvas position means role, not geography.

## Common mistakes

- Using `network/wireless-ap` or `network/router` for a cell tower or mobile network. Use `network/wan-provider` labelled with the technology.
- Defaulting device ingest to an HTTP API gateway when the user never said HTTPS.
- Drawing only the dashcam as an event source when the telematics unit's accelerometer also detects harsh braking and impact.
- Using `hardware/fpga`, `hardware/nic` or an unlabelled `compute/edge-server` for a sensor, PLC or HMI. Every generic card needs a role label.
- Drawing the dashcam with its own cellular path when it uploads through the telematics unit, or the reverse.
- Drawing GPS fixes and clips as one edge. They go to different stores at different sizes and rates.
- Adding a SIEM, edge gateway, VPN, firewall, driver app or integration the user never mentioned.
- Making a geofence a `boundary` group around vehicles.
- Drawing Purdue levels or the DMZ as `lane` groups. Lanes are roles or teams; a task such as "Review clip" is never a lane name either.
- Showing one vehicle with fleet-scale numbers in labels and no "× N" note.
- Linking levels that skip the DMZ the user described without asking.
- Using `presentation/swimlane` as a node instead of a `group` with `style: "lane"`.

## Start from

- `event-driven` for the device-to-cloud ingest and processing path.
- `support-escalation` for dispatch, field-service and maintenance ticket workflows in swimlanes.
- `sec-incident-response` as a swimlane pattern for safety-event review and coaching.
- `secure-ci-cd` for a firmware build, approval and staged rollout.
- `observability-pipeline` for device-health monitoring and missing-device alerts.
- `sequence-request` for an upload, ack and retry sequence.
- `segmented-network` for a Purdue or OT DMZ view (rename the zones to levels and stack them top to bottom), or `layout_diagram` with `direction: "TB"` and then adjust the groups by hand.

Read alongside: `brief` and `style` first, then `business-process` for workflow views, `network` for uplink and site connectivity, `security-architecture` for device identity and DMZ placement, and `cloud` for the ingest platform boundary.
