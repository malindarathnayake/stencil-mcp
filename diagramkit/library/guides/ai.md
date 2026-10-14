# AI, agent and ML systems

> Use this guide for agents with tools and approvals, multi-agent orchestration, RAG pipelines, model gateways, LLM inference serving, MLOps lifecycles, and block-level model or notebook sketches.

## Questions to ask first

1. Who calls the system, which tools does the agent have, and which only read data and which change something? (default: a user through a frontend, with one read-only tool and one mutating tool, each labelled as such)
2. Are tools run in-process as functions or direct API calls, through MCP, or by the model provider as hosted tools? If MCP is used, are the servers local stdio subprocesses or remote HTTP servers? (default: tools run by the agent runtime with no MCP drawn, unless the brief mentions MCP)
3. Does each tool act with the end user's delegated credential or with a shared service account, and where are its secrets held? (default: a scoped `identity/service-account` per tool server, with secrets in `identity/secrets-vault` on the tool side and never in the prompt)
4. Where do approval and guardrails sit: a human approver, an automated policy check, or both, and does a guardrail check input, output or both? (default: human approval before every mutating tool runs, and no guardrail drawn unless named)
5. Which content entering the context is untrusted (retrieved documents, web pages, emails, tool results, other agents' output), and may any of it lead to a mutating tool call without approval? (default: all of it is untrusted, and no mutating call runs without approval)
6. Which models are involved, does a separate vision, embedding or reranking model appear, and does a gateway route requests across several models or providers? (default: one LLM, an embedding model only if vector retrieval is in scope, and no gateway)
7. What memory exists: none, conversation history only, or a long-term store the agent reads and writes between sessions? (default: no long-term memory; context comes from the prompt and tool results only)
8. For RAG, what are the sources, is ingest batch or continuous, is retrieval vector, keyword or hybrid, is there a reranker, and are results filtered by the caller's permissions? (default: one document source, scheduled batch ingest, vector retrieval, no reranker, no permission filter drawn and the reply states that assumption)
9. For multi-agent designs, how many agents are there, who orchestrates them, do agents talk directly or only through the orchestrator, and does any agent belong to another organisation? (default: one orchestrator and two workers in one organisation, communicating only through the orchestrator)
10. For inference serving, do the same workers run prefill and decode, or are they separated? If separated, how many of each, and should GPUs, NICs and the KV-cache fabric be shown? Is the response streamed? (default: colocated workers, no KV-cache transfer, no hardware drawn, streamed tokens shown as one response edge)
11. For MLOps, which stages are in scope, is the job pretraining, fine-tuning or batch inference, and does drift monitoring retrain automatically or only alert a person? (default: only the stages the brief names, with drift raising an alert; ask separately whether an evaluation gate and model registry exist)
12. Which trust boundaries should be shown? (default: one boundary around the agent runtime, including any local stdio MCP servers; one around remote tool servers; and one around a provider-hosted model when the model is not self-hosted)

## Push back when

- The brief says the model calls the database or API directly. A language model only produces output, including a structured request to call a tool. The agent runtime runs that request as an in-process function, a direct API call or an MCP client call to an MCP server; for hosted tools the model provider's platform runs it. Ask which, draw MCP only when they use it, and draw provider-run tools inside the provider boundary.
- The brief places human approval after the action it is meant to approve. Approval after execution is review or audit. Ask whether the action should wait, or whether they want an audit log instead.
- The brief treats a prompt instruction or an output guardrail as the authorization control. Prompt text does not enforce permissions. Ask where enforcement really happens (tool server, policy engine, scoped credential) and draw that point.
- The brief treats tool results or retrieved content as trusted. That text enters the model's context and can carry injected instructions that steer later tool calls. Tell the user so. Draw it as untrusted input, and draw a guardrail or approval before any mutating tool it could trigger.
- The brief passes API keys or tokens through the prompt. Anything in the context can be echoed into output or logs. Tell the user that credentials belong in the tool server or a vault, and draw them there.
- The brief says the model "learns" from each conversation or from retrieved documents. Inference does not change weights. Persistent memory is an external store, and weight changes come from a separate training or fine-tuning job. Ask which one they mean.
- The RAG brief embeds documents with one embedding model and queries with an unrelated one. Query vectors must come from the same model, or from one built to share its vector space, or similarity search is meaningless. Ask whether that is intended.
- The brief has the reranker search the whole corpus. A reranker scores candidates the retriever already returned. Draw the retriever first, then the reranker.
- The brief puts the whole knowledge base into the prompt. Ask how large it is. If it fits the context window and is loaded on every request (optionally with prompt caching), draw it as a static context source with no retriever. If it does not fit, ask what is retrieved per query.
- The brief shows a KV-cache transfer in a colocated design. A prefill-to-decode transfer exists only in disaggregated serving. Colocated designs may still offload or share KV cache (CPU or SSD tier, shared prefix cache). Ask which movement they mean and draw only that one.
- The brief requires RDMA for the KV-cache transfer. Disaggregated serving can use other transports. Draw RDMA only if the user states it.
- The brief asks for a governed ML pipeline but deploys straight from the training job. Ask whether an evaluation gate and registry exist. Do not invent them, and do not silently drop them.

## How we draw it here

Flow runs left to right: caller, then agent, gateway or router, then models, then tools, data and actions. Use `boundary` groups for trust or ownership zones, such as "Agent runtime", "Remote tool servers", "Provider-hosted model", "Untrusted content" or one per organisation. Use `panel` groups to split one story into stages, such as ingest above query, or training beside serving. Use `lane` groups only for a human approval process.

Roles and asset IDs:

- Callers: `identity/user`, `identity/admin`, `software/browser`, `software/frontend`.
- Agents: `ai/ai-agent` (label orchestrator and workers by role), `ai/tool`, `ai/mcp-client` and `ai/mcp-server` only when MCP is used, and `software/workflow` or `software/scheduler` for a non-agent orchestrator.
- Models: `ai/llm`, `ai/vision-model`, `ai/embedding-model`, `ai/reranker`, `ai/model-server`, `ai/prompt`, `ai/context-window`; `ai/router` labelled "Model gateway" for routing across models; `cloud/saas` or a "Provider-hosted model" boundary for an external model API; `ai/llm` labelled "Judge model" for LLM-as-judge evaluation.
- Controls: `ai/guardrail` (caption "Input check" or "Output check"), `ai/human-approval`, `security/policy-engine`, `identity/service-account`, `identity/access-token`, `identity/secrets-vault`, `observability/audit-log`, `resilience/rate-limiter`, `resilience/timeout`.
- Memory: `data/key-value-db` or `data/vector-db` labelled "Agent memory".
- RAG: `data/dataset` or `storage/object-store` for sources, `data/etl` for chunking, `ai/embedding-model`, `data/vector-db` or `data/search-index`, `ai/rag-retriever`, `ai/reranker`, `ai/prompt` for prompt assembly.
- Serving: `ai/router`, `ai/model-server`, `ai/prefill-worker`, `ai/decode-worker`, `ai/kv-cache`; only when stated, `hardware/gpu`, `hardware/rdma-nic`, `protocol/rdma-operation`, `protocol/memory-buffer`, `resilience/autoscaler`.
- MLOps: `data/dataset` (version in `detail`), `data/data-lake`, `ai/training-job` (detail "Fine-tuning" or "Pretraining"), `software/batch-job` for batch inference, `ai/model-registry`, `presentation/decision` captioned "Eval passed?", `devops/release-approval`, `devops/cd-release`, `devops/rollback`, `observability/metrics`, `observability/alert`, `observability/dashboard`.
- Block-level architecture: `presentation/process` per block, `text` nodes for tensor shapes, `presentation/annotation-bracket` around repeated blocks.

Edge kinds:

- `control` for orchestration, task dispatch, tool invocations, approval requests, approved actions and policy decisions.
- `data` for forward payloads: prompts, context, retrieved chunks, ingest, KV-cache transfer and model artifacts.
- `feedback` for returns on the request path (tool results to the agent, the response or token stream to the caller) and for evaluation or drift results fed back to data or training. Label each one ("Tool result", "Response", "Eval results") so returns and loops stay distinct.
- `dependency` for "loads from" relations, such as a model server and a registry version. `replication` only for stores that really replicate.

Palettes: `blue` for callers, `teal` for agents and models, `purple` for the integration layer (MCP servers, model gateway, KV-cache transfer), `orange` for data stores, memory and logs, `red` for mutating or privileged actions and their approval path, `green` for read-only tools, `slate` for supporting infrastructure. Colour never replaces a label: write "read-only" or "mutating" in each tool's `detail`, and "untrusted" in the `detail` of untrusted sources.

Add a `legend` whenever more than one edge kind appears, with an entry for each kind used and one for the red privileged path. Keep the standard `footer` stating that labels describe roles and generic symbols do not assert product compatibility. Write `description` as one or two sentences naming the tools, approvals and data paths drawn.

## Common mistakes

- Drawing a direct edge from `ai/llm` to a database, API or action tool. Draw the call from the agent runtime, or from the provider boundary for hosted tools, and show what limits its scope.
- Adding MCP servers the user never mentioned, or putting local stdio MCP servers in a remote zone. They run as subprocesses with the host user's privileges, inside the agent runtime boundary.
- Drawing a token edge that passes through the model or the prompt.
- Returning tool results or retrieved chunks to the agent with no untrusted marking, then letting them drive a mutating tool with no guardrail or approval in between.
- Putting read-only and mutating tools on one unlabelled path, so approval seems to cover reads or to be skippable for writes.
- Placing `ai/human-approval` beside the action instead of between the request and the action.
- Using `data` edges for everything, so tool calls look like payload movement. Invocations are `control`; returns are `feedback`.
- Merging RAG ingest and query into one chain. Keep two paths that meet only at the index or vector store.
- Getting the query path wrong for the retrieval type. For vector retrieval, embed the question with the same embedding model. For keyword search there is no query embedding. For hybrid search, draw both queries and a fusion step. Do not skip prompt assembly before generation.
- Adding GPUs, RDMA NICs or a fabric because disaggregated serving often uses them. Draw hardware only when the user states it.
- Drawing the KV-cache edge from decode back to prefill, or through the router. In disaggregated serving it moves from prefill to decode.
- Picking a misleading stand-in for a missing symbol. There is no evaluation harness, notebook, feature store, experiment tracker or drift detector icon. Use labelled cards with the nearest honest role: `devops/integration-tests` "Evaluation suite", `compute/workstation` "Notebook", `data/key-value-db` "Feature store (online)", `data/relational-db` "Experiment tracking", `observability/metrics` "Drift monitor".
- Leaving the MLOps loop open with no `feedback` edge, or drawing automatic retraining the user did not confirm.
- Drawing a neural network as individual neurons. Stencil draws block-level structure only; say so and draw blocks.
- Adding a vector store, cache, gateway, rate limiter or guardrail because typical designs have one. Ask first.

## Start from

- `agent-mcp-tools` for an agent with MCP tools and human approval. Change "Tool call" and "Approved action" to `control`. Add a `feedback` "Tool result" path to the agent. Insert green read-only `ai/tool` nodes (detail "read-only") before the database and log stores. Set the action tool's detail to "mutating", and add a legend. If the tools do not use MCP, replace the MCP server with the agent runtime's own tool calls.
- `disaggregated-inference` for prefill and decode serving with a KV-cache transfer. Change router-to-prefill "Assign" to `control`, add a `feedback` response from decode to the caller, add a legend, and delete the kv-note text unless the user asked about transport.
- Colocated serving (the question 10 default): no template yet; use `layout_diagram` with caller, router, `ai/model-server` workers and a `feedback` response, and no `ai/kv-cache` transfer.
- `threat-model-dfd` when the main question is prompt injection or where untrusted content crosses trust boundaries.
- RAG pipelines, multi-agent orchestration, cross-organisation agents, model gateways, agent memory, LLM-as-judge evaluation, MLOps lifecycles, notebooks, feature stores and block-level architecture: no template yet; use `layout_diagram`.
- `observability-pipeline` and `secure-ci-cd` can supply the monitoring and delivery halves of an MLOps diagram.

Read alongside: `brief` first, then `security-architecture` for approval, credential and policy enforcement points, `data` for stores and pipelines, `network` when the user asks for the GPU or RDMA fabric, and `style` last.
