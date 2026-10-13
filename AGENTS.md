# Instructions for agents working with Stencil

Read README.md, docs/DESIGN_SYSTEM.md and docs/SCENE_FORMAT.md before composing.
The canonical workflow is scene JSON → validation → SVG → visual inspection.

Search existing asset IDs. Do not invent a name that is not in the catalog.
Do not request the entire catalog's SVG bodies. Metadata and selected templates
are normally enough. Use the diagram compositor to load individual symbols.

Preserve labels and packet states the user has explicitly specified. A loss
illustration must not show the same original packet arriving successfully.
Feedback goes from receiver to sender. A retry of only packet 4 must not show
retransmissions of 1, 2, 3 or 5. Separate panels are preferred over tiny text.

Keep physical cables, logical dependencies, control traffic and payload arrows
distinct. Label trust and ownership boundaries. Do not infer capabilities from
product aliases or turn generic symbols into unofficial vendor logos.

For generated diagrams, retain and deliver both scene JSON and SVG. Inspect all
validation warnings and view the rendered output. Do not claim the layout engine
or lint checks prove protocol correctness.

Development:
- No external requests, shell execution or arbitrary file access in MCP tools.
- Do not permit caller-provided SVG/XML/CSS or image URLs.
- Exports stay within the operator-configured directory; names are stems only.
- Do not print debugging output to stdout in the MCP process.
- Run `python -m unittest discover -s tests -v` after changes.
- Rebuild assets with `python scripts/build_library.py`; rebuild schema,
  templates and gallery with their corresponding scripts, then run
  `python scripts/build_release.py`. CI fails if a rebuild changes committed files.
- Releases: bump the version in pyproject.toml and diagramkit/__init__.py, update
  CHANGELOG.md, then push a matching `v<version>` tag; CI builds and publishes the wheel.
- If an approved SVG is changed, rebuild the catalog/checksum coherently.

Branding and source status:
- Use Stencil, the selected stacked-layer mark, and branding/tokens.json for repo graphics.
- Do not replace the logo with other names from the archived concept board.
- Do not treat reference PNG tiles or their printed IDs as runtime SVG assets.
- Read docs/PACK_COVERAGE.md for canonical asset mappings and unimplemented specialized widgets.
- Preserve catalog IDs and original SVG checksums unless intentionally versioning the asset library.
