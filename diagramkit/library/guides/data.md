# Data platforms, pipelines and database topology

> Use this guide for lakehouse and warehouse pipelines, streaming and ETL, curated data lineage, database primary/replica/cache/search topology, and data architecture overviews with governance.

## Questions to ask first

Ask only the questions whose facts the brief leaves open, usually about five to seven in one round. Questions tagged (pipeline) apply to data pipelines and platforms, questions tagged (database) apply to database topology, and the last one applies to every brief.

1. (pipeline) Which source systems feed the platform, and how many of each kind? (default: only the sources the brief names, each as its own card; no extra "other sources" card)
2. (pipeline) How does each source arrive: scheduled batch extract, event stream, or change data capture, and if CDC, is it log-, trigger- or query-based? (default: batch for files and SaaS exports, stream for application events, and no CDC unless the brief says CDC)
3. (pipeline) Which stages sit between ingest and consumption, and where does each land: object-store lake, warehouse, or a lakehouse table format on one store? (default: raw, cleaned and curated stages; a data lake feeding a warehouse, drawn as two stores; bronze, silver and gold names only if the user uses them)
4. (pipeline) Who consumes the output: BI dashboards, reports, ML training, reverse ETL into applications, or downstream APIs? (default: one BI dashboard consumer and nothing else)
5. (pipeline) What is the refresh cadence or freshness target for each path, and for streams, what delivery guarantee and ordering does the sink rely on? (default: daily batch written on the ingest edge; no "real-time" or "exactly-once" claim; ordering not drawn)
6. (pipeline) Who owns each stage or domain? (default: one platform team owns everything, so no ownership lanes)
7. (pipeline) Which datasets carry personal or regulated data, where is it masked, tokenised or dropped, and where do the token vault and keys live, and who can detokenise? (default: none marked; ask rather than assume a dataset is clean)
8. (database) How many secondaries are there, is replication synchronous or asynchronous, is each secondary a readable replica or a non-readable HA standby, and is failover automatic, with which node promoted? (default: one asynchronous readable replica in the same site, manual failover, failover not drawn)
9. (database) Is the data sharded or partitioned, are any replicas chained from another replica or placed in another region, and is there a proxy or pooler that splits reads and writes? (default: one unsharded primary, replicas fed directly by the primary, no proxy)
10. (database) For a cache: is it cache-aside, read-through or write-through, and who invalidates entries? (default: cache-aside, where the application reads the cache, reads the primary itself on a miss, populates the cache, writes to the primary and invalidates the entry)
11. (database) Is the search index fed by the application, by CDC, or by a batch job? (default: the application updates the index asynchronously after the primary commit, labelled "Async index update"; no CDC node)
12. (any) Is this one diagram or several, and what is out of scope (orchestration, quality checks, backup, governance tooling)? (default: one data-flow diagram; orchestration and backup out of scope)

## Push back when

- The user wants read replicas drawn as scaling writes. Replicas serve reads; all writes still go to the primary in a single-primary design. Ask whether they mean read scaling or a multi-primary database.
- Application reads are routed to an asynchronous replica with no comment. Reads there can be stale right after a write, so a user may save and then read old data. Ask whether reads that must see their own writes go to the primary, and label the replica read edge "Reads (may lag)".
- An HA standby is drawn serving reads. Many standbys, such as some managed multi-zone setups, cannot serve reads at all. Ask which kind each secondary is before drawing read traffic to it.
- An asynchronous replica is described as a backup or as having zero data loss. Asynchronous replicas can lag and lose recent commits on failover, and deletes and corruption replicate too. Say so and offer to add a separate backup or snapshot path.
- Synchronous replication is drawn between distant regions without comment. Every commit then waits for the remote acknowledgement, so write latency includes the round trip. Ask whether that is intended or whether the remote copy is asynchronous.
- A nightly batch job is called CDC or "real-time". Log-based CDC streams committed changes from the transaction log, and query- or trigger-based CDC also exists. A nightly extract is batch whatever it is called. Ask which mechanism is used (log, trigger, query polling or full extract) and label the edge with that mechanism and its cadence.
- Exactly-once delivery is claimed end to end. Across system boundaries delivery is usually at-least-once, made safe by idempotent or deduplicating sinks; exactly-once normally holds only inside one system. Ordering is usually guaranteed only per partition or key. Ask what the sink does with duplicates and label the edge with the actual guarantee ("at-least-once, dedup on order_id").
- The search index or cache is shown as the system of record. Both are derived, eventually consistent copies; the primary database stays the source of truth. Ask before drawing writes that go only to the cache or index.
- PII is said to be "masked in the dashboard" while raw copies land unmasked in the lake. Masking at the consumer does not protect earlier copies. Ask where masking actually happens and draw PII on every edge until that point.
- Tokenised or pseudonymised data is called anonymous. While a token vault or key can reverse it, it is still personal data. Ask whether tokens can be reversed in that environment before showing PII as stopped.
- The user asks for column-level lineage, an entity-relationship diagram or a star schema with keys. Stencil has no column, key or cardinality notation. Offer table-level lineage instead, or say an ERD tool is the better fit.

## How we draw it here

Flow runs left to right: sources, ingest, storage stages, serving, consumers. Put each stage in its own `panel` group as a column, titled with the stage name and captioned with its purpose ("Raw, append-only"). Use `lane` groups only when rows mean owners or domains, stacked full width, with each node's `group` set to its lane. For medallion layouts, use three panels titled Bronze, Silver and Gold, each captioned with what that layer guarantees here.

Assets by role:

- Sources: `data/relational-db`, `data/document-db`, `software/backend`, `software/external-service`, `cloud/saas`, `observability/logs`, `business/form`.
- Batch ingest and transform: `data/etl`, `software/batch-job`, `software/scheduler` or `software/workflow` for orchestration.
- Streaming and CDC: `software/message-broker` or `software/topic` for the log, `data/stream-processor` for processing. There is no CDC-specific symbol; use `data/stream-processor` labelled "CDC capture", only when the user names CDC, with the mechanism and source table in `detail`.
- Storage: `data/data-lake` or `storage/object-store` for the lake, `data/data-warehouse` for the warehouse, `data/dataset` for a named table or dataset.
- Consumers: `observability/dashboard` labelled "BI dashboard", `business/report`, `ai/training-job`, `software/rest-api`.
- Database topology: `software/backend` for the application, `data/relational-db` for the primary, `data/database-replica` for each replica, `data/cache`, `data/search-index`. Draw an HA standby with `data/database-replica` and "Standby, not readable" in `detail`. Draw a read/write proxy or pooler with `network/reverse-proxy` labelled "Read/write router". Draw each shard as its own `data/relational-db` labelled with its key range.
- Governance: `security/policy-engine` for access policy, `security/dlp` for classification or masking, `observability/audit-log` for access records, `observability/alert` for failed quality checks, `identity/secrets-vault` for a token vault or key store.
- Markers: `status/locked` as a `symbol` beside a sensitive dataset or the token vault with a caption such as "PII"; `status/warning` or `status/approved` for quality gate outcomes; `status/pending` for late data.

Edge kinds: `data` for movement of records, with the mechanism and cadence in the label ("Log CDC, seconds", "Batch, daily 02:00"). `replication` from the upstream node (the primary or a relay replica) to each replica, labelled "sync" or "async". `dependency` for lineage, pointing downstream from input dataset to transform to output dataset. `control` for orchestration triggers, cache invalidation and failover promotion when the user asks for failover. `feedback` for quality-check results sent back to an owner.

Cache paths: draw each path as its own edge on its own port. For cache-aside, the application owns every step: application to cache "Read (hit/miss)", application to primary "On miss, read primary", application to cache "Populate (TTL)", application to primary "Write", then a `control` edge from application to cache labelled "Invalidate". Draw a cache-to-primary edge only when the answer is read-through or write-through, and say so in the edge label.

Sensitive data: give every edge that carries PII the `red` palette and a label that says so ("Orders + PII"), and mark each store holding it with `status/locked`. Label a tokenised edge "Tokenised (pseudonymised)" and keep it `red`. Show the PII marking as stopping only where fields are dropped or aggregated, unless the user confirms the tokens cannot be reversed there. Use `legend` entries for each edge meaning and for the PII colour. Put cadence assumptions and "Illustrative; labels describe roles" in `footer`.

For lineage graphs and any DAG beyond about 12 nodes, call `layout_diagram` for initial positions (it accepts up to 80 nodes), then add groups. Split larger graphs by domain or stage into separate diagrams.

## Common mistakes

- Drawing a generic "Kafka" or queue between every stage when the brief describes batch files. Only draw a broker if one exists.
- Adding a CDC capture node because a search index or warehouse needs feeding. Use CDC only when the user names it.
- Using `data/relational-db` for every store, so the lake, warehouse and replicas look identical. Pick the role-specific asset.
- Drawing a replica with a plain `data` edge, which hides that it is replication and whether it is synchronous.
- Drawing every replica fed by the primary when the user described cascading or cross-region relay replicas.
- Drawing an HA standby with a read edge as if it were a read replica.
- Drawing a cache-aside miss as a cache-to-primary edge, which shows read-through instead.
- Merging the cache read and write paths into one bidirectional line, which hides the consistency behaviour.
- Pointing lineage arrows upstream on some edges and downstream on others. All lineage edges point downstream.
- Inventing icons for gaps: there is no feature-store, data-catalog, BI-tool, column or ERD symbol. Do not substitute `data/key-value-db` for a feature store or `data/search-index` for a catalog without asking; label a `data/dataset` or use a text note.
- Marking only the first PII store and letting PII disappear from later edges with no masking step shown, or treating the first tokenised edge as clean.
- Labelling every path "real-time" or "exactly-once" when the stated cadence is hourly or daily and the guarantee is unknown.
- Adding orchestration, quality checks or backup that the user never mentioned because a typical platform has them.

## Start from

- `event-driven` for streaming and CDC pipelines with producers, a topic and consumers.
- `observability-pipeline` for a left-to-right sources, collection, storage and consumer layout.
- `backup-dr` when replicas sit next to backups and the difference matters.
- Otherwise no template yet; use `layout_diagram`, especially for lineage graphs.
- Read alongside: `brief` first, `style` for layout, and `business-process` when the diagram is a data operations workflow with owners and approvals.
