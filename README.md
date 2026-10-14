<div align="center">

<img src="https://raw.githubusercontent.com/malindarathnayake/stencil-mcp/main/branding/banners/stencil-readme-banner.png" alt="Stencil" width="800" />

# Stencil

<p align="center">
  <a href="https://github.com/malindarathnayake/stencil-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.10-brightgreen.svg" alt="Python >= 3.10" /></a>
  <img src="https://img.shields.io/badge/MCP-2025--06--18%20stdio-6b4fbb.svg" alt="MCP 2025-06-18 stdio" />
  <img src="https://img.shields.io/badge/dependencies-none-success.svg" alt="No runtime dependencies" />
</p>

</div>

Stencil is a local MCP server and SVG symbol library for Claude Code, Codex and other MCP clients. The model searches a catalog of 324 generic symbols, writes a diagram as scene JSON, validates it, and renders a deterministic, editable SVG. The scene JSON is the source of truth: change the scene and render again rather than hand-editing the SVG.

It covers infrastructure, networking, security, Kubernetes, data, AI/agent systems and packet-level explanations, plus business-process swimlanes for engineering, security, IT, finance, HR, sales, IT change management and support.

**324 SVG assets · 20 categories · 24 diagram templates · 12 MCP tools · Python standard library only**

<p align="center">
  <img src="https://raw.githubusercontent.com/malindarathnayake/stencil-mcp/main/examples/it-change-approval.png" alt="IT: change approval" width="49%" />
  <img src="https://raw.githubusercontent.com/malindarathnayake/stencil-mcp/main/examples/mrc-loss-recovery.png" alt="How MRC uses multiple paths" width="49%" />
</p>

## Install

Python 3.10 or newer. Stencil has no runtime dependencies. Install it from [PyPI](https://pypi.org/project/stencil-mcp/) as a tool, so it gets its own environment and the `stencil-mcp` command lands on your PATH:

```bash
uv tool install stencil-mcp
# or: pipx install stencil-mcp
# or the wheel from a GitHub release:
# uv tool install https://github.com/malindarathnayake/stencil-mcp/releases/download/v0.2.2/stencil_mcp-0.2.2-py3-none-any.whl
```

Register it with Claude Code, then confirm the host sees it:

```bash
claude mcp add --transport stdio --scope user stencil -- stencil-mcp
claude mcp get stencil
```

Then ask for a diagram:

```text
Use the stencil MCP. Start from the sec-incident-response template and adapt it
for a ransomware alert on a file server. Keep the lanes, validate, render, look
at the result, and export it as ransomware-ir.
```

The host starts `stencil-mcp` as a child process; there is no daemon to run. **PNG previews (optional).** `preview_diagram` returns a PNG so the model can look at its own output. It needs the `preview` extra (CairoSVG) and the native Cairo library: `uv tool install "stencil-mcp[preview]"`, plus `apt install libcairo2`, `brew install cairo`, or the GTK3 runtime on Windows. Everything else works without it.

Upgrade with `uv tool upgrade stencil-mcp`. Without installing anything, `uvx stencil-mcp` also works as the server command.

<details>
<summary><b>Codex, Claude Desktop, Windows, and the export folder</b></summary>

Codex:

```bash
codex mcp add stencil -- stencil-mcp
```

or in `~/.codex/config.toml`:

```toml
[mcp_servers.stencil]
command = "stencil-mcp"

[mcp_servers.stencil.env]
INFRA_DIAGRAM_OUTPUT_DIR = "/ABSOLUTE/PATH/diagram-exports"
```

Claude Desktop does not search your shell PATH reliably; use the full path that `which stencil-mcp` (or `where stencil-mcp` on Windows) prints as the `command` in its `mcpServers` entry. The Desktop setup has not been live-tested.

`export_diagram` writes only into `INFRA_DIAGRAM_OUTPUT_DIR` (default `~/infra-diagram-exports`). Set it with `claude mcp add -e INFRA_DIAGRAM_OUTPUT_DIR=/path ...`. Point it at a local folder, not a synced or shared one, if your diagrams describe internal systems.

</details>

<details>
<summary><b>Run from a clone (contributors)</b></summary>

```bash
git clone https://github.com/malindarathnayake/stencil-mcp.git
cd stencil-mcp
python -m unittest discover -s tests      # one optional CairoSVG test skips
python scripts/client_config.py           # prints registration commands for this machine
```

`client_config.py` prints the `stencil-mcp` command when the package is installed, and otherwise this machine's interpreter plus the absolute path to `server.py`. It writes snippets under `config/` and never edits your client settings. `pip install -e .` gives you the `stencil-mcp` command pointing at the clone.

</details>

## How the model uses it

```text
library_info / get_guidelines   learn the categories, connector meanings and composition rules
search_assets                   find symbol ids by role ("firewall", "invoice", "dashcam"); metadata only
get_template / list_templates   start from one of the 24 editable scenes
layout_diagram                  first-pass positions for a small graph (DAG layering, grid fallback)
validate_diagram                schema, ids, bounds, overlaps, text fit, edges crossing nodes
render_diagram                  self-contained SVG text plus the validation report
preview_diagram                 PNG for visual review (needs optional CairoSVG)
export_diagram                  writes <name>.svg and <name>.scene.json to the export folder
```

Search returns compact metadata, so the model never loads all 324 SVG bodies; the renderer pulls in only the symbols a scene uses. Every tool is read-only except `export_diagram`.

<details>
<summary><b>A minimal scene</b></summary>

```json
{
  "version": "1.0",
  "title": "Application request path",
  "width": 1100,
  "height": 430,
  "nodes": [
    {"id": "client",  "kind": "component", "asset": "software/browser",    "x": 45,  "y": 180, "label": "Client"},
    {"id": "gateway", "kind": "component", "asset": "network/api-gateway", "x": 445, "y": 180, "label": "API gateway"},
    {"id": "api",     "kind": "component", "asset": "software/rest-api",   "x": 845, "y": 180, "label": "Application API"}
  ],
  "edges": [
    {"id": "request",  "source": "client",  "target": "gateway", "kind": "data", "label": "HTTPS"},
    {"id": "upstream", "source": "gateway", "target": "api",     "kind": "data", "label": "Forward"}
  ]
}
```

Node kinds: `component` (symbol in a labelled card), `symbol` (bare symbol, optional `caption`), `packet`, `memory`, `text`, `marker`. Edge kinds carry meaning: `data`, `control`, `physical`, `feedback`, `dependency`, `tunnel`, `replication`. Groups draw panels, trust boundaries and swimlanes. Full reference: [docs/SCENE_FORMAT.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/SCENE_FORMAT.md).

</details>

<details>
<summary><b>More prompts</b></summary>

```text
Use the stencil MCP. Draw an Internet-facing app: WAF, API gateway, Kubernetes
services, a database and a separate logging path. Start from kubernetes-ingress,
keep physical links separate from request arrows, label the trust boundaries,
and split into panels rather than shrinking labels.
```

```text
Use the stencil MCP. Draw our purchase approval as swimlanes: Requester,
Manager, Finance, Vendor. Over $10k goes to the CFO. Copy the conventions in
fin-procurement-approval: questions on decisions, labelled Yes/No branches,
dashed orange for anything sent to the vendor.
```

```text
Use the MRC loss-recovery template. Keep packets 1-5: arrival order 1, 3, 5, 2;
packet 4 is lost; SACK says "Have 1, 2, 3, 5 - missing 4"; retransmit only 4.
Do not draw the dropped original reaching the receiver.
```

</details>

## Examples

Every template ships as scene JSON in [`diagramkit/library/templates/`](https://github.com/malindarathnayake/stencil-mcp/tree/main/diagramkit/library/templates/) and as SVG + PNG in [`examples/`](https://github.com/malindarathnayake/stencil-mcp/tree/main/examples/). Open [`gallery.html`](https://github.com/malindarathnayake/stencil-mcp/blob/main/gallery.html) for an offline, searchable view of every symbol and template.

**Department processes** (swimlanes; lanes are roles, time runs left to right)

| Department | Template | Shows |
| --- | --- | --- |
| Engineering | [`eng-platform-delivery`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/eng-platform-delivery.png) | Pull request → review loop → CI → release gate → deploy, with rollback |
| Security | [`sec-incident-response`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/sec-incident-response.png) | Triage, declare, then contain, preserve evidence and notify in parallel |
| IT | [`it-onboarding-access`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/it-onboarding-access.png) | New-hire ticket → account → laptop → privileged approval → MFA |
| Finance | [`fin-procurement-approval`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/fin-procurement-approval.png) | Spend threshold, purchase order, three-way match, dispute, payment |
| HR | [`hr-employee-onboarding`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/hr-employee-onboarding.png) | Contract, parallel preparation by HR, manager and IT, 30-day check-in |
| Sales | [`sales-lead-to-cash`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/sales-lead-to-cash.png) | Qualify, quote, negotiate, order, invoice, revenue |
| IT change management | [`it-change-approval`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/it-change-approval.png) | Risk assessment, standard vs CAB approval, change window, verify or back out |
| Customer support | [`support-escalation`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/support-escalation.png) | L1 → L2 under an 8-hour SLA → engineering fix → customer confirmation |

**Architecture and protocols**

| Template | Shows |
| --- | --- |
| [`mrc-loss-recovery`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/mrc-loss-recovery.png) | Packet spraying across ECMP paths, one loss, SACK, retransmit only the missing packet |
| [`ecmp-flow-hashing`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/ecmp-flow-hashing.png) | Two flows hashing onto the same equal-cost path |
| [`leaf-spine`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/leaf-spine.png), [`segmented-network`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/segmented-network.png), [`hybrid-cloud`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/hybrid-cloud.png) | Network topology and placement |
| [`zero-trust-access`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/zero-trust-access.png), [`threat-model-dfd`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/threat-model-dfd.png), [`secure-ci-cd`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/secure-ci-cd.png) | Security controls and trust boundaries |
| [`kubernetes-ingress`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/kubernetes-ingress.png), [`event-driven`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/event-driven.png), [`software-overview`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/software-overview.png), [`sequence-request`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/sequence-request.png) | Application architecture |
| [`agent-mcp-tools`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/agent-mcp-tools.png), [`disaggregated-inference`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/disaggregated-inference.png) | AI agents and inference |
| [`observability-pipeline`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/observability-pipeline.png), [`backup-dr`](https://github.com/malindarathnayake/stencil-mcp/blob/main/examples/backup-dr.png) | Operations |

<p align="center">
  <img src="https://raw.githubusercontent.com/malindarathnayake/stencil-mcp/main/examples/sec-incident-response.png" alt="Security: incident response" width="49%" />
  <img src="https://raw.githubusercontent.com/malindarathnayake/stencil-mcp/main/examples/fin-procurement-approval.png" alt="Finance: procure to pay" width="49%" />
</p>

<details>
<summary><b>What is in the library</b></summary>

| Collection | Assets | | Collection | Assets |
| --- | ---: | --- | --- | ---: |
| Compute & virtualization | 15 | | Development & delivery | 20 |
| Hardware & accelerators | 14 | | Observability & operations | 12 |
| Network devices | 20 | | AI & agent systems | 20 |
| Routing & overlays | 19 | | Resilience & traffic policy | 10 |
| Security controls | 24 | | Packets & transport | 21 |
| Identity & cryptography | 14 | | Diagram notation | 20 |
| Storage & continuity | 13 | | State markers | 10 |
| Cloud & locations | 14 | | Business process | 15 |
| Kubernetes & containers | 21 | | Fleet telematics | 9 |
| Software & integration | 19 | | Data systems | 14 |

Many entries are role variants of a shared glyph with a badge (128 base shapes). All symbols are original generic drawings: no vendor logos, fonts or raster images. Search aliases such as Proxmox, Rancher or NVIDIA find the matching generic symbol; they are not compatibility claims. Contact sheets for each collection are in [`previews/`](https://github.com/malindarathnayake/stencil-mcp/tree/main/previews/).

</details>

<details>
<summary><b>Render without MCP</b></summary>

```bash
python -m diagramkit.cli search invoice
python -m diagramkit.cli templates
python -m diagramkit.cli validate diagramkit/library/templates/support-escalation.json
python -m diagramkit.cli render diagramkit/library/templates/support-escalation.json --output out/support.svg
```

`render` refuses to overwrite an existing file unless you pass `--overwrite`.

</details>

<details>
<summary><b>Security model and limits</b></summary>

- **Local and single-user.** stdio only, no network listener, no outbound requests, no shell, no telemetry.
- **No caller-supplied markup.** Scenes cannot carry SVG, HTML, CSS, scripts or image URLs. All text is XML-escaped; control, invisible, bidirectional-override and non-XML characters are rejected.
- **Bounded input.** 1 MiB per message, at most 200 nodes and 400 edges per scene, 200 validation issues per report.
- **Confined writes.** `export_diagram` accepts a filename stem only, writes only into the export folder, refuses symlinks and Windows device names, never overwrites unless asked, and stages both files before publishing them.
- **Checked assets.** The renderer verifies each symbol's SHA-256 against the catalog and rejects active SVG content.
- **Verifiable releases.** Each release wheel carries a signed build-provenance attestation and SBOMs. Check it before installing: `gh attestation verify <wheel> --repo malindarathnayake/stencil-mcp`.

The full threat model, which maps these controls to the OWASP LLM and Agentic Top 10, is in [docs/SECURITY_POSTURE.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/SECURITY_POSTURE.md). Report vulnerabilities privately; see [SECURITY.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/SECURITY.md).

Validation checks structure and layout: ids, bounds, overlaps, text fit, edges crossing nodes. It cannot tell you that an architecture is secure, a protocol is drawn correctly, or a product supports a feature. Look at the rendered output. The layout helper is a first pass, not an obstacle-avoiding router; set ports and waypoints for clean edges. A shared HTTP deployment needs the official MCP SDK plus authentication and isolated storage; see [docs/MCP.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/MCP.md).

</details>

<details>
<summary><b>Rebuilding and extending</b></summary>

```bash
python scripts/build_library.py     # symbol geometry and catalog.json
python scripts/build_schema.py      # scene.schema.json
python scripts/build_templates.py   # 24 templates and example SVGs
python scripts/build_gallery.py     # previews/ and gallery.html (PNGs need CairoSVG)
python scripts/build_release.py     # asset-packs.json, VALIDATION_REPORT.json, MANIFEST.sha256
python -m pip install --require-hashes --only-binary=:all: -r requirements-build.txt
python -m build --no-isolation           # the release wheel and sdist, into dist/
```

The release wheel is built from a hash-locked toolchain (`requirements-build.txt`) with `python -m build --no-isolation`, and is byte-reproducible with `SOURCE_DATE_EPOCH` set. CI runs the tests on Linux, Windows and macOS, fails if a rebuild changes any committed generated file, and builds the wheel twice to prove it is reproducible. `security.yml` runs CodeQL, gitleaks, zizmor and a Syft/Grype SBOM scan. Pushing a `vX.Y.Z` tag publishes an attested release. Every action is pinned to a commit SHA and every scanner to a verified checksum; see [docs/SECURITY_POSTURE.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/SECURITY_POSTURE.md).

Builds are deterministic and write LF line endings on every OS, so a rebuild without source changes is byte-identical. Asset ids are public API: the original 300 symbols are pinned byte-for-byte by `tests/fixtures/legacy_sha256.json`, and new symbols are additive. Adding roles, shapes or a separately licensed vendor pack: [docs/EXTENDING.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/EXTENDING.md).

</details>

## Documentation

| Document | Covers |
| --- | --- |
| [docs/DESIGN_SYSTEM.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/DESIGN_SYSTEM.md) | Composition rules, connector meanings, process-diagram notation |
| [docs/SCENE_FORMAT.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/SCENE_FORMAT.md) | Scene JSON reference |
| [docs/MCP.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/MCP.md) | Tools, resources, transport and export policy |
| [docs/EXTENDING.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/EXTENDING.md) | Adding symbols, templates and packs |
| [docs/PACK_COVERAGE.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/PACK_COVERAGE.md) | What each pack covers and what is not implemented |
| [docs/SECURITY_POSTURE.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/docs/SECURITY_POSTURE.md) | Threat model, build integrity, CI/CD hardening, scanning and release verification |
| [SECURITY.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/SECURITY.md) | Reporting a vulnerability |
| [CHANGELOG.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/CHANGELOG.md) | Release notes |
| [branding/BRAND_GUIDE.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/branding/BRAND_GUIDE.md) | Logo and repository graphics |
| [AGENTS.md](https://github.com/malindarathnayake/stencil-mcp/blob/main/AGENTS.md) | Rules for coding agents working in this repo |

## License

Apache License 2.0. See [LICENSE](https://github.com/malindarathnayake/stencil-mcp/blob/main/LICENSE).
