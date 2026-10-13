# Changelog

## 0.2.0 — 2026-10-10

Hardening and department process diagrams. The design was reviewed through a design
gauntlet (research, design, Codex adversarial review, complexity review, independent
verification) before any change was made.

### Security and robustness

- A request whose id or arguments contain a lone UTF-16 surrogate no longer crashes the
  stdio server; it is rejected with `-32600` and the server keeps serving. Response
  encoding is failure-safe, and stray `print` output from library code goes to stderr.
- Scene text rejects control, invisible (zero-width space, word joiner, BOM, Unicode tag
  block), bidirectional-override and non-XML characters (`illegal_character`). ZWJ, ZWNJ,
  LRM and RLM remain allowed for scripts that need them.
- Identifier patterns use a full match, so an id such as `"a\n"` is no longer accepted.
- An oversized array stops schema traversal at the first error, and validation reports
  return at most 200 issues with a `truncated` count. Validity is still decided on the
  full list. This removes a 50 KB → 40 MB response amplification.
- `export_diagram` rejects Windows reserved device names, takes a per-name lock, stages
  both files before publishing, and rolls back only files it created. Exports are
  written with LF line endings on every OS.
- `layout_diagram` advertises the 200-edge limit it enforces.

### Rendering and validation

- Marker nodes draw `blocked` and `pending` states with the matching status symbol
  (previously both drew as healthy).
- `symbol` nodes accept an optional `caption`, drawn inside the node box.
- The SVG root uses `aria-labelledby` for the title and `aria-describedby` for the
  description. All example SVGs changed by this one attribute.

### Library

- Catalog 0.2.0: 324 assets in 20 categories. New `business` (15) and `fleet` (9)
  categories with 19 new glyph families. The original 300 SVGs are byte-identical and
  pinned by `tests/fixtures/legacy_sha256.json`.
- The library, schema, template and gallery builders write LF bytes and record checksums
  of the bytes on disk. `.gitattributes` keeps LF on checkout.
- Eight department swimlane templates: engineering, security, IT, finance, HR, sales,
  fleet operations and customer support.
- `scripts/build_release.py` regenerates `asset-packs.json`, `VALIDATION_REPORT.json`,
  `docs/TEST_RESULTS.txt` and `MANIFEST.sha256`.

### Packaging and license

- Licensed under Apache-2.0. The LICENSE file ships inside the wheel, and catalog entries
  carry `"license": "Apache-2.0"`.
- Distributed as a wheel attached to each GitHub Release. Install with `uv tool install`
  or `pipx install` and register the `stencil-mcp` command; no clone or absolute paths.
- The `infra-diagram` and `infra-diagram-mcp` console aliases are removed. Use
  `stencil-diagram` and `stencil-mcp`.
- `scripts/client_config.py` prints the `stencil-mcp` command when the package is
  installed, and the interpreter plus `server.py` path from a clone otherwise.
- CI runs the tests on Linux, Windows and macOS, checks that a rebuild leaves generated
  files unchanged, and builds and smoke-tests the wheel. A `v*` tag publishes a release.

### Not changed

- Protocol version stays 2025-06-18. Answering with the one supported version is
  conformant negotiation.
- No new node kinds, edge kinds or lane auto-layout; swimlanes use existing `lane` groups.

Tests: 69 (1 optional CairoSVG test skipped).
