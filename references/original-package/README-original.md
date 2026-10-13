# Infra Diagram Kit

A local MCP server and editable SVG library for Codex, Claude Code and other MCP
clients. Designed for infrastructure, security, networking, routing, software,
Kubernetes, data, AI and packet-level explanations.

**300 SVG assets · 18 categories · 109 base glyph families · 16 diagram templates · 12 MCP tools**

The 300 entries include meaningful role variants that reuse a base shape with
labels or badges. They are not 300 unrelated drawings. No official vendor logos,
font files, stock icon downloads or raster screenshots are embedded in the assets.

## Start here

Open `gallery.html` after extracting the complete repository. It works offline
and provides category filters, text search, asset IDs, and template previews.

`previews/catalog-overview.png` shows 54 representative components. Every category
also has an SVG contact sheet and PNG preview under `previews/`.

The MRC example is in `examples/mrc-loss-recovery.svg`. Its source scene is in
`diagramkit/library/templates/mrc-loss-recovery.json`. The original packet 4
terminates at a loss marker; a separate panel retransmits only packet 4.

## Requirements

Python 3.10 or later. The MCP server, catalog search, SVG renderer and basic test
suite use only the standard library. No install step, API key, cloud service or
account is required for local operation.

Optional PNG rendering uses CairoSVG. Its installation may require native Cairo
libraries on some operating systems. SVG output does not depend on it.

```sh
# Run from the extracted repository directory.
python3 -m unittest discover -s tests -v
python3 -m diagramkit.cli info
python3 scripts/client_config.py
```

On Windows, use `py -3` in place of `python3` when Python is installed through
the Windows launcher. The config helper writes snippets with the actual absolute
interpreter and repository paths for the machine where it runs. It does not edit
live Codex or Claude configuration.

## Connect Codex and Claude Code

Use the commands printed by `scripts/client_config.py`, or substitute your own
absolute paths here. Do not copy `/ABSOLUTE/PATH` literally.

```sh
codex mcp add infra-diagrams -- python3 /ABSOLUTE/PATH/infra-diagram-kit/server.py

claude mcp add --transport stdio --scope user infra-diagrams -- python3 /ABSOLUTE/PATH/infra-diagram-kit/server.py
```

The host launches the server as a child process. You do not need to start a daemon
first. Inspect the MCP status in each client after registration. A terminal that
seems to sit silently after manually running `server.py` is waiting for protocol
messages; it is not an interactive drawing application.

The local snippets generated under `config/` include Codex TOML, Claude Code JSON
and Claude Desktop JSON. Merge the relevant entry into existing settings; do not
replace an existing settings file wholesale. The generated Desktop snippet uses
the conventional `mcpServers` configuration shape but has not been live-tested in
Claude Desktop.

Exports default to `~/infra-diagram-exports`. Set `INFRA_DIAGRAM_OUTPUT_DIR` in the
server's environment to use another operator-chosen directory. The export tool
accepts a filename stem only and will not overwrite files unless explicitly asked.

## Ask an agent to create a diagram

> Use the infra-diagrams MCP. Make an overview of an Internet-facing application
> with a WAF, gateway, Kubernetes services, a database, and a separate logging path.
> Search the library for matching roles, start from the Kubernetes template, and
> keep physical links separate from request/control arrows. Label trust boundaries.
> Validate, render, inspect, then export both SVG and scene JSON. Split into panels
> rather than shrinking the labels.

Another example:

> Use the MRC loss-recovery template. Preserve packets 1–5: arrival order 1, 3, 5, 2;
> original packet 4 is lost; SACK says “Have 1, 2, 3, 5 — missing 4”; retransmit only
> 4. Do not draw the dropped original reaching the receiver. Keep the diagram editable.

The MCP returns metadata first. The model does not need to consume all SVG bodies:
it searches asset IDs, prepares a scene, and the compositor loads only the symbols
that the scene actually uses.

## Render without MCP

```sh
python3 -m diagramkit.cli render diagramkit/library/templates/software-overview.json --output exports/software-overview.svg

python3 -m diagramkit.cli validate diagramkit/library/templates/mrc-loss-recovery.json

python3 -m diagramkit.cli search rdma
```

SVG output has editable geometry, text, groups and stable IDs. Open it in a vector
editor or browser. The adjacent scene JSON is the repeatable source for future edits.

## Included categories

| Collection | Assets |
| --- | ---: |
| Compute & virtualization | 15 |
| Hardware & accelerators | 14 |
| Network devices | 20 |
| Routing & overlays | 19 |
| Security controls | 24 |
| Identity & cryptography | 14 |
| Storage & continuity | 13 |
| Cloud & locations | 14 |
| Kubernetes & containers | 21 |
| Software & integration | 19 |
| Data systems | 14 |
| Development & delivery | 20 |
| Observability & operations | 12 |
| AI & agent systems | 20 |
| Resilience & traffic policy | 10 |
| Packets & transport | 21 |
| Diagram notation | 20 |
| State markers | 10 |

The catalog includes generic roles for hypervisors and virtual machines, GPU and
RDMA adapters, leaf/spine networks, BGP/VRF/VXLAN/ECMP, IAM and security controls,
Kubernetes, databases, delivery pipelines, observability, agent/MCP components,
packets, memory slots, ACK/SACK, dropped-packet markers, boundaries and state.

Aliases such as Proxmox, Rancher, Oracle, Infisical, Graylog, NVIDIA and Alveo help
find generic components. These aliases are not product capability claims.

## Included templates

MRC loss recovery; ECMP flow hashing; leaf–spine; hybrid cloud; segmented networks;
identity-aware access; Kubernetes ingress; secure CI/CD; software overview;
event-driven processing; agent/MCP tools; prefill/decode inference; backup/DR;
observability; threat-model data flows; and a request/work/response sequence view.

Each is supplied as scene JSON, SVG and PNG. They are examples to adapt and review,
not verified descriptions of an existing deployment.

## Repository layout

```text
infra-diagram-kit/
  server.py                     Local MCP launcher
  gallery.html                  Offline searchable asset/template gallery
  diagramkit/
    library.py                  Registered catalog and lexical search
    scene.py                    Schema checks and initial graph layout
    renderer.py                 Self-contained editable SVG composition
    service.py                  MCP-independent tool implementations
    server.py                   Bounded stdio JSON-RPC adapter
    cli.py                      Local CLI
    library/
      assets/<category>/*.svg   300 individual vector assets
      catalog.json              Metadata, tags, bounds, anchors, checksums
      palettes.json             Theme colors
      scene.schema.json         Scene schema
      guidelines.md             Composition rules exposed through MCP
      templates/*.json          16 editable scenes
  examples/                     Rendered SVG + PNG examples
  previews/                     Overview and category contact sheets
  scripts/                      Rebuild and local config helpers
  config/                       Client configuration examples
  docs/                         Design, scene format, MCP, extension notes
  tests/                        Catalog/rendering/security-boundary/RPC tests
  AGENTS.md / CLAUDE.md          Repository instructions for coding agents
```

## Checks and limits

The delivered build passed **53 automated tests** in the creation environment.
All 300 SVGs parsed and matched their recorded checksums. All 16 template scenes
passed the kit's validation with no warnings. The test suite includes a real stdio
subprocess exchange for initialization, tool discovery, asset search, SVG rendering
and resource reads. Representative renders and the template contact sheet were
visually inspected; every possible asset composition has not been reviewed.

This has not been connected to your installed Codex or Claude clients. Local
protocol tests are not a formal MCP certification, security audit, or cross-platform
GUI/editor test. Run the supplied tests and verify client status on your machine.

The renderer supports explicit placements, simple DAG/grid initialization, cardinal
anchors, waypoints, groups, wrapped text and three themes. It does not include a
full obstacle-avoiding layout engine, automatic crossing bridges, precise browser
font measurement, or semantic validation of protocols. SVG lint cannot establish
that an architecture is secure or that a product supports a feature.

The server implements a deliberately small MCP 2025-06-18 stdio subset. It is
single-user and local-only. A shared HTTP service needs a maintained transport
adapter plus authentication, authorization and isolated output storage. See
`docs/MCP.md` and `docs/EXTENDING.md` before changing its trust boundary.

## Rebuild

```sh
python3 scripts/build_library.py
python3 scripts/build_schema.py
python3 scripts/build_templates.py
# Optional previews require CairoSVG:
python3 -m pip install cairosvg
python3 scripts/build_gallery.py
python3 -m unittest discover -s tests -v
```

`build_library.py` is the source of the symbol geometry. Rebuilding deliberately
overwrites generated assets and their catalog. Treat stable IDs as public API.
See `docs/EXTENDING.md` for adding roles, shapes and separately licensed vendor packs.

MIT license. Primary protocol/client references are recorded in `docs/REFERENCES.md`.
