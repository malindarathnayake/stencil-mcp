# MCP interface

## Local transport

The included server is a small, dependency-free stdio implementation of the
MCP 2025-06-18 tools/resources/prompts subset. It negotiates that protocol version
at initialization, including when a client offers a newer version. A client must
support the negotiated version to continue.

The host starts `server.py` as a child process. Requests are UTF-8 newline-delimited
JSON-RPC. Only protocol messages are written to stdout; diagnostics use stderr.

Supported: initialize, initialized notification, ping, tools/list, tools/call,
resources/list, resources/templates/list, resources/read, prompts/list, prompts/get.
The tool and resource lists are small and returned in one page.

Not implemented: HTTP/SSE transport, remote authentication, sampling, subscriptions,
MCP tasks, dynamic catalog-change notifications, streaming progress, or cancellation
of a call already executing. Calls run serially and are bounded. This is a local
single-user starter, not a multi-tenant hosted service.

## Tools

| Tool | Purpose | Writes |
| --- | --- | --- |
| `library_info` | Counts, categories, themes and workflow | No |
| `search_assets` | Compact lexical search with role aliases and pagination | No |
| `get_asset` | Metadata, bounds, anchors; optional SVG body | No |
| `list_templates` | Find reusable scene templates | No |
| `get_template` | Copy a template's scene JSON | No |
| `stencil_guide` | Start here: confirm-the-brief rule, guide index, and topic guides (questions to ask, how to draw, common mistakes) | No |
| `get_guidelines` | Composition and technical-review checklist | No |
| `get_scene_schema` | Full scene JSON Schema | No |
| `layout_diagram` | Initial DAG layering or cycle/grid fallback | No |
| `validate_diagram` | Structural and visual-layout lint checks | No |
| `render_diagram` | Self-contained SVG text and validation report | No |
| `preview_diagram` | PNG image content; optional CairoSVG dependency | No |
| `export_diagram` | SVG and scene JSON in the configured output directory | Yes |

Tool discovery uses compact scene argument schemas to avoid repeatedly injecting
the full scene specification into the client's context. Actual scene validation
runs in the service layer. Use `get_scene_schema` when more detail is needed.

Search is lexical, not semantic/vector search. Several common terms expand into
role aliases. A match for a vendor name returns generic relevant components; it
is not a compatibility statement.

## Resources and prompt

Static resources: library overview, diagram guidelines and scene schema.
Template resources: `infra-diagram://asset/{category}/{name}` and
`infra-diagram://template/{name}`. IDs are catalog keys, not file paths.

The `diagram_brief` prompt takes a brief string and returns a planning instruction.
All essential features are also available through tools, so clients do not need
to use resource or prompt UI features.

## Export policy

`INFRA_DIAGRAM_OUTPUT_DIR` is an operator-set environment variable. Default:
`~/infra-diagram-exports`. The tool accepts a simple stem such as `network-v1`,
not a path or extension. It writes `network-v1.svg` and `network-v1.scene.json`.

No overwrite happens by default. An explicit `overwrite=true` is required to
replace regular files. Symlink targets and Windows reserved device names (`CON`,
`NUL`, `COM1` and similar) are refused. Each export takes a per-name lock file
(`.<name>.lock`, cleared after five minutes if a writer crashed), stages both
files completely, then publishes them with atomic renames. A failed new export
removes only the files that call created. Files are written with LF line endings.
A machine compromised by another local process is outside this adapter's
isolation model.

`STENCIL_GUIDE_DIR` is an optional, operator-set folder of `.md` topic guides that add
to or override the bundled ones with house conventions. Only regular `*.md` files
directly in that folder, with a lower-case hyphenated name and at most 64 KiB, are
read; symlinks and subfolders are ignored. The model chooses a topic name, never a
path.

There are no shell tools, arbitrary file reads, external image requests, network
listeners, credentials, telemetry or third-party icon fetches. The catalog is
trusted bundled data, not a remotely writable registry. Rendering verifies each
asset's recorded checksum and rejects active SVG elements.

## Testing status

The test suite covers catalog integrity, XML parsing, scene schema checks,
example scenes, rendering, path restrictions, optional PNG preview, and a real
stdio subprocess initialization/search/render/resource-read exchange.

This is not a formal MCP conformance certification or a security audit. It has
not been tested inside the recipient's Codex CLI, Claude Code, Claude Desktop,
Windows installation or macOS installation. Verify connection with each client's
MCP status view after registering it.

For a shared service, keep this service layer and asset registry but use the
official MCP SDK for a maintained HTTP transport, authentication, authorization,
per-user output storage, concurrency and deployment operations.
