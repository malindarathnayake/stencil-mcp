# Changelog

## 0.2.2 — 2026-10-13

- `preview_diagram` gives an actionable error when PNG previews are unavailable. A
  missing `preview` extra now points to `uv tool install "stencil-mcp[preview]"`
  instead of a `pip install` that targets the wrong environment. A missing native
  Cairo library, previously reported as cairocffi's raw `OSError`, now names the
  package to install per platform.
- The gallery and brand build scripts, and the optional preview test, treat a missing
  native Cairo library like a missing package instead of crashing.
- README documents the optional PNG preview setup.

Tests: 72 (1 optional CairoSVG test skipped).

## 0.2.1 — 2026-10-13

First published release. Version 0.2.0 was never released; its changes are included here.

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
  IT change approval and customer support.
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

### Supply chain and CI/CD security

- The wheel is built from a hash-locked toolchain (`requirements-build.txt`, installed
  with `--require-hashes`) without build isolation, and is byte-reproducible; CI builds
  it twice and fails on any difference.
- Every GitHub Action is pinned to a full commit SHA. Dependabot updates actions and the
  build toolchain after a cooldown. Tokens are read-only by default, checkout does not
  persist credentials, and event data reaches shell only through `env`.
- `security.yml` runs CodeQL (Python and workflows), gitleaks, zizmor and a Syft + Grype
  SBOM scan that fails on high or critical findings. Scanners are checksum-verified
  binaries at fixed versions, not third-party actions.
- Releases repeat every gate on the tagged commit, then publish from a separate job in
  the `release` environment with a signed SLSA build-provenance attestation, CycloneDX
  and SPDX SBOMs and `SHA256SUMS`.
- The renderer's active-content check now compares attribute local names, so a
  namespaced `xlink:href` in a catalog asset is rejected. A regression test covers
  scripts, event handlers, `href`, `style`, `url()` and unsupported elements.
- Releases also publish to PyPI with Trusted Publishing (OIDC, no stored token) from a
  separate `pypi` environment, after the GitHub Release succeeds.
- Added `SECURITY.md` and `docs/SECURITY_POSTURE.md`.
- `build_schema.py` and `build_brand.py` write LF bytes; the schema had been written
  with CRLF on Windows.
- The forbidden-character pattern in `scene.py` is written with ASCII escapes only. It
  had contained literal bidi-override and zero-width characters, the Trojan Source
  pattern, and CodeQL flagged its control-character range. It matches the same 2,224
  code points. A test now fails if any source file contains hidden characters.
- Text-width estimates use `math.fsum`. Python 3.12 changed float `sum()` to
  compensated summation, so one label rendered 0.01 px differently on 3.10 and 3.11.
  Renders are now byte-identical on 3.10 through 3.13.

### Not changed

- Protocol version stays 2025-06-18. Answering with the one supported version is
  conformant negotiation.
- No new node kinds, edge kinds or lane auto-layout; swimlanes use existing `lane` groups.

Tests: 71 (1 optional CairoSVG test skipped).
