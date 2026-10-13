# Stencil handoff

This is the existing Infra Diagram Kit v0.1.0 packaged as **Stencil v0.1.1**, with the chosen option-C identity.

**0.2.0 update:** catalog 0.2.0 adds the `business` and `fleet` categories (324 assets), eight department swimlane templates (24 total) and the hardening listed in `CHANGELOG.md`. The original 300 asset SVGs are unchanged. The sections below describe the 0.1.1 handoff.

## Included

300 individual SVG assets, the machine-readable catalog and pack map, 16 editable JSON templates and SVG/PNG renders, 12 local MCP tools, an offline gallery, source/build scripts, client configuration examples, test suite, Stencil logo/avatar/banner exports, brand tokens, and the conversation's visual reference files.

The untouched original ZIP is retained at `references/original-package/infra-diagram-kit-v0.1.0.zip`.

## Compatibility

The public project name and server identity are Stencil / `stencil-mcp`. New registration snippets use the MCP name `stencil`. Python imports remain `diagramkit`; existing asset IDs and `infra-diagram://` resource URIs remain unchanged. The console commands are `stencil-mcp` and `stencil-diagram`; the older `infra-diagram` aliases were removed in 0.2.0.

The legacy `INFRA_DIAGRAM_OUTPUT_DIR` variable and default `~/infra-diagram-exports` directory remain unchanged. The client helper prints and writes machine-local snippets; it does not edit live client settings.

Core asset catalog version remains 0.1.0 because the 300 asset SVG files have not changed. Application/bundle version is 0.1.1. The renderer's existing palette is preserved, not silently replaced by the branding palette.

## Reproducibility

Save scene JSON and pin the renderer, catalog and template versions. In this bundle, repeated renders of an identical scene produce identical SVG text. This does not promise that different models given the same natural-language prompt will invent the same scene. Displayed text can also vary with fonts/renderers; use the outlined wordmark files for fixed branding geometry.

`MANIFEST.sha256` covers the delivered files. The original catalog includes per-asset hashes. `VALIDATION_REPORT.json` and `docs/TEST_RESULTS.txt` record the checks run for this bundle. These are local tests, not proof of compatibility with every client or of protocol correctness. The user's installed Codex/Claude clients have not been live-tested.

## Where to start

Open `START_HERE.html` or `gallery.html`. Use `branding/BRAND_GUIDE.md` for the GitHub identity. Use `AGENTS.md` and the MCP guidelines for diagrams. Use `docs/PACK_COVERAGE.md` before assuming every tile on a concept board has a dedicated runtime SVG.
