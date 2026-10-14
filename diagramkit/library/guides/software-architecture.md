# Software architecture (C4-style, services, integration)
> Use this guide for system context, container, component, deployment and dynamic views, microservice overviews, monolith migrations, bounded-context maps, API management, event-driven or serverless integration, SaaS integration maps and executive business context diagrams.

## Questions to ask first
Ask only the questions the brief leaves open, all in one round, and skip any that the brief already answers. Questions 1 to 6 apply to most views. Questions 7 to 11 apply only when the diagram covers data, messaging, an API gateway or a migration.

1. Which view do you want: system context (C4 level 1), containers (level 2), components inside one container (level 3), deployment (where containers run: cloud, region, cluster), dynamic (numbered steps of one scenario), a before/after migration, a bounded-context map, or an executive business context picture? (default: containers for "architecture", context for "overview for leadership")
2. Which single system is in focus, and what is outside its boundary and owned by someone else? (default: the one system the brief names is in scope; every other system is drawn as external)
3. Who uses the system, and are there distinct roles such as customers, staff, administrators or partner systems? (default: only the roles the brief names; one generic "User" if none are named)
4. Which external systems does it talk to, and which side starts each interaction? (default: only the external systems named, with synchronous calls drawn from caller to callee)
5. What are the deployable units and what technology does each use? Is there a backend-for-frontend, a GraphQL layer or a CDN in front of the clients? (default: one card per named service or app, the technology line left empty rather than guessed, and no BFF or CDN unless stated)
6. For each link, is it a synchronous request/response or asynchronous through a queue, topic or stream, and what protocol does it use? Does any business transaction span several services, through a saga, an orchestrator or compensation steps? (default: synchronous request; protocol label only where stated; no saga unless stated)
7. Does each service own its own data store, or do several services share one database? Does a service write to its database and publish an event in one step, and if so, is there a transactional outbox or change data capture? (default: a store only for services that the brief says keep data; shared only if stated; no outbox or CDC drawn unless stated)
8. For messaging, how many consumer groups or subscriptions are there, and how many instances are in each? (default: the word the brief uses. A queue means one consumer gets each message, and a topic means every subscriber gets a copy. Draw only the consumers named. If the wording is unclear, use a broker with an open note.)
9. Are retries, a dead-letter queue, timeouts or circuit breakers part of the design, and where? Does the broker move failed messages to the dead-letter queue after a maximum delivery count, or does the consumer publish them? Is there a replay path back to the source? (default: none drawn unless stated)
10. Which policies does the API gateway apply, and in what order? Does it validate JWTs locally against cached signing keys (JWKS), or does it introspect opaque tokens? Is authorization by scopes or roles enforced at the gateway or in the service? (default: the gateway card alone; an identity provider only if the brief mentions login or tokens)
11. For a migration, how many stages should be shown, and which routes have already moved? Which data stores do the moved routes use, and is data synchronised back through CDC, dual writes or events? (default: two panels, "Before" and "Target", with no sync path unless stated)
12. Who is the audience? (default: engineers, with protocols and technology shown; for executives, business roles only and no protocols)

## Push back when
- The brief asks for one diagram that shows people, every container and the classes inside them. C4 levels answer different questions, and mixing them makes the picture unreadable. Offer a context diagram, one container diagram, and a component diagram for the container that matters.
- The brief says a queue "sends each message to all consumers". Each subscription or consumer group gets its own copy, but the instances inside one group compete for messages, so each message reaches only one of them. Ask how many groups there are and how many instances are in each.
- The brief draws a synchronous reply coming back through a queue as if it were a direct call. Request/reply over messaging needs a reply queue or topic and a correlation identifier. Ask whether those exist or whether the call is really synchronous.
- The brief claims exactly-once delivery from end to end. Delivery is at-least-once or at-most-once, depending on when the consumer acknowledges. Exactly-once effects need idempotent consumers, deduplication keys, or broker transactions that only cover that one broker. A database write plus a publish is not atomic unless there is an outbox or CDC. Ask what provides the guarantee before writing it on the diagram.
- The brief expects global ordering. At best, ordering holds per partition, per FIFO message group or per session key. Standard queues may not order messages at all, and competing consumers and retries reorder them. Ask what key the order is per and whether retries must keep that order.
- A browser calls a gRPC service directly. Browsers cannot speak native gRPC. They need gRPC-Web through a proxy, or a REST/JSON endpoint. Ask which one is used.
- The brief calls a step "strangler" but replaces the whole monolith at once. The strangler pattern routes traffic through a façade and moves routes to new services one at a time. A single cut-over is a big-bang migration. Ask which one they mean.
- The brief says the services are independent, but they share one database. Draw the database as shared and say that it couples their schemas and releases. Do not draw separate stores that do not exist.

## How we draw it here
Flow runs left to right: callers on the left, the system in the middle, and external dependencies on the right. Put the focus system or set of containers inside a `boundary` group titled with the system name. Use `panel` groups for side-by-side stages and for messaging or gateway areas.

Arrow direction: synchronous edges point from caller to callee. Asynchronous edges point the way messages flow (producer to topic to consumer), whether delivery is push or pull. Use `feedback` edges for responses or acknowledgements only when they matter to the point of the diagram.

Roles and asset IDs:
- People: `identity/user`, `identity/admin`, `identity/group` for a team or customer segment, and `identity/service-account` for a machine caller.
- The system as one box at level 1: `presentation/process` labelled with the system name, with "Software system" as the detail. External systems: `software/external-service`, or `cloud/saas` for a hosted product.
- Containers: `software/frontend`, `software/browser`, `compute/mobile` for a mobile app, `software/backend`, `software/rest-api`, `software/grpc-api`, `software/websocket`, `software/microservice`, `software/background-worker`, `software/monolith`, `software/function` or `cloud/cloud-function`, `software/scheduler`, `software/batch-job`, and `software/workflow` for a saga orchestrator.
- Data: `data/relational-db`, `data/document-db`, `data/key-value-db`, `data/cache`, `data/search-index`, `data/data-warehouse`, `data/database-replica`, `data/etl`, `data/stream-processor`, and `storage/object-store` for files and blobs.
- Messaging: `software/message-queue`, `software/topic`, `software/message-broker`, `software/event-bus` and `software/webhook`. For fan-out and fan-in, use `presentation/fan-out` and `presentation/fan-in` as `symbol` nodes with a caption.
- Gateway, edge and policies: `network/api-gateway`, `network/reverse-proxy`, `network/load-balancer`, `cloud/edge-location` for a CDN, `identity/identity-provider`, `identity/access-token`, `identity/secrets-vault`, `resilience/rate-limiter`, `resilience/timeout`, `resilience/circuit-breaker`, `resilience/retry` and `security/waf`. Draw the CDN and the vault only when the brief states them.
- Business context: `business/vendor`, `business/payment`, `business/invoice`, `business/report`, `business/email` and `cloud/saas`.

Per view:
- Context (level 1): the system card in the centre, people on the left, and external systems on the right and below. Each edge is a `data` edge labelled with a verb phrase ("Places orders", "Sends invoices"). Show no protocols, no databases and no internal services.
- Container (level 2): put the deployable units inside the system boundary, and give each its technology in `detail` ("TypeScript, React", "Go service"). The system's own data stores, queues and topics are containers too. Draw them inside the boundary, on its right-hand side. Only stores owned by another team or system go outside the boundary, drawn as external. Label every edge with what and how ("Reads/writes, SQL", "Publishes OrderPlaced, AMQP", "HTTPS/JSON"). People and external systems stay outside the boundary.
- Component (level 3): one `boundary` group titled with the container name, with the components inside it. Components are not separately deployable, so use `presentation/process` cards with a clear label and the responsibility in `detail`. Do not use `software/microservice` here. If the brief really means separately deployed units, it is asking for a container view. Use `dependency` edges for "uses" relationships, and keep neighbouring containers outside the boundary.
- Deployment: draw containers placed on the infrastructure the brief names (cloud, region, cluster), and start from the Kubernetes template when it applies.
- Dynamic: one scenario with numbered edge labels ("1. Submits order"), in the order the calls happen.
- Event-driven: producers on the left, the broker, queue or topic in a messaging panel, and consumers on the right. Edges go from producer to topic ("Publish") and from topic to each consumer group ("Consumer group X"), never straight from producer to consumer. Draw retry and the dead-letter queue only when the brief states them: a `resilience/retry` symbol on the consumer path, and a `software/message-queue` card labelled "Dead-letter queue". The red `data` edge carries the condition as stated ("After 5 attempts"), and the count is never invented. For broker redrive, the edge starts at the source queue or subscription. Only an application-level DLQ starts at the consumer. Draw a replay edge from the DLQ back to the source only if stated.
- API management: put the gateway and each stated policy, in the order applied, in a panel on the request path, followed by `data` edges to the REST, gRPC and WebSocket backends. Draw client to identity provider as a `data` edge labelled "Obtains token". The gateway-to-identity-provider `control` edge is labelled "Fetches signing keys (JWKS)" for JWTs, or "Introspects token" only when the brief states introspection. A WebSocket edge uses `arrow: "both"`.
- Serverless and webhooks: the external sender calls a `software/webhook` endpoint, which triggers a function. Draw the trigger as a `data` edge labelled with the event name.
- Migration: two or three `panel` groups side by side ("Before", "Stage 1", "Target"). Keep unchanged parts in the same positions so the reader sees what moved. The façade is `network/reverse-proxy` or `network/api-gateway`, labelled "Routing façade". Draw data sync between old and new stores as a `replication` edge or a labelled `data` edge, only when stated.
- Bounded contexts: one `boundary` group per context, titled with the context name. Label edges between contexts with the relationship ("Upstream: publishes OrderPlaced", "Anti-corruption layer").
- Executive context: at most about eight cards, with business role labels, verb edges, and no technology or protocols.

Edge meanings: `data` (solid) for requests and message flow, `dependency` (dotted) for depends-on or uses, `control` (dashed) for configuration, policy and key or token checks, `feedback` (dashed return) for responses and acknowledgements that matter, and `replication` to a `data/database-replica` or for migration sync. Palettes: blue for people and the request path, teal for messaging, purple for consumers and workers, orange for data stores, slate for external systems, and red for dead-letter and failure paths. Add a `legend` whenever more than one edge kind appears. Keep the standard footer: "Illustrative architecture. Labels describe roles; generic symbols do not assert product compatibility."

## Common mistakes
- Mixing levels, such as a database inside a context diagram, or classes or microservice icons inside a component diagram.
- Drawing the system's own database outside its boundary, which implies that someone else owns it.
- Drawing a direct arrow from producer to consumer and calling it event-driven.
- Using `software/topic` when the brief says queue, or `software/message-queue` for several independent subscribers. A topic read by one scaled-out consumer group is still a topic.
- Starting the dead-letter edge at the consumer when the broker does the redrive.
- Drawing a per-request call to the identity provider for JWT validation.
- Inventing gateway policies, a cache, a CDN, a dead-letter queue or a load balancer because typical designs have them.
- Looking for a schema registry, DLQ, interface or class icon. None of these exists. Use `data/dataset` labelled "Schema registry", a queue card labelled "Dead-letter queue", and labelled component cards.
- Leaving edges unlabelled on a container diagram, or labelling every edge "API call".
- Picking `software/monolith` for any large service, or `cloud/saas` for an internal system.
- Drawing "Before" and "After" in one panel, or hiding the shared database in a migration.
- Treating UML class diagrams as in scope. There is no class notation, so say so and offer a component view instead.

## Start from
- `software-overview` for container views and microservice overviews.
- `event-driven` for pub/sub, streaming, retry and dead-letter flows.
- `kubernetes-ingress` for deployment views when the containers run on Kubernetes and ingress matters.
- `sequence-request` for dynamic views where the order of calls in one request is the point.
- `agent-mcp-tools` when an AI agent calls tools in the architecture.
- Context, component, migration, bounded-context and executive views have no template yet; use layout_diagram.
- Read the brief guide first and the style guide after. Read the process guide for business workflows behind the integration.
