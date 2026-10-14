# Visual references and originals

These files preserve the work from the conversation. They are not the runtime asset library.

- **Approved brand:** `branding/stencil-selected-concept.png` (option C from the original board).
- **Approved MRC raster:** `mrc/mrc-approved-reference.png`.
- **Working editable MRC scene:** `../diagramkit/library/templates/mrc-loss-recovery.json`, rendered in `../examples/`.
- **Actual individual vector icons:** `../diagramkit/library/assets/`; stable IDs and metadata are in `../diagramkit/library/catalog.json`.
- **Concept sheets:** `icon-concepts/`. These are PNG illustrations, not SVG sprites. Printed board IDs such as INF-01 and MRC-11 are not runtime lookup IDs.
- **History:** `mrc/history/` includes superseded diagrams, the earlier SVG, and the endpoint-flip issue. Retained for reference, not technical authority.
- **Original delivery:** `original-package/` retains the untouched v0.1.0 ZIP and companion files.

The production SVG library is a generic implementation of the design direction, not a pixel-exact vector extraction of every illustrated concept. Not every proposed tile has a dedicated implementation. `../docs/PACK_COVERAGE.md` records the gaps relevant to the earlier discussion.

`manifest.json` records the source filenames, destination paths, status, and SHA-256 hashes.
