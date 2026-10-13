# Stencil — start here

Open **`START_HERE.html`** for the package dashboard, or **`gallery.html`** for the searchable icon library.

| Need | Location |
| --- | --- |
| Setup and MCP registration | `README.md` |
| GitHub logos, avatar, banner and colors | `branding/BRAND_GUIDE.md` |
| Actual SVG icons | `diagramkit/library/assets/` |
| Canonical asset metadata | `diagramkit/library/catalog.json` |
| Use-case pack map | `asset-packs.json` |
| Editable example scenes | `diagramkit/library/templates/` |
| Example SVGs and PNGs | `examples/` |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `diagramkit/library/guidelines.md` |
| Coverage and requested trunk/routing additions | `docs/PACK_COVERAGE.md` |
| Original designs and previous ZIP | `references/` |

Users install the release wheel and register the `stencil-mcp` command (see `README.md`). Contributors run from the repository folder:

```sh
python3 -m unittest discover -s tests -v
python3 -m diagramkit.cli info
python3 scripts/client_config.py
```

Use `py -3` on Windows when appropriate. The helper creates snippets and prints registration commands without modifying the client's live configuration.

The raster sheets in `references/` preserve the visual workshop. The runtime icons are the individual SVG files in `diagramkit/library/assets/`; they are not crops of those sheets.
