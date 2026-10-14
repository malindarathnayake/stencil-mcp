# Extending the kit

## Add a role variant

Edit `scripts/build_library.py`: add a row under the appropriate `DATA` category.
Rows use `id | display name | glyph family | role badge | search aliases`.
The actual delimiter is `|`; do not include it inside a field.

Reuse a base glyph only when the relationship is meaningful. A different label
or role badge is a variant, not a claim of a completely new drawing. The catalog
records `glyph_family` and `role_badge` so this is inspectable.

Run the asset builder, template builder, gallery builder and tests. Stable IDs
are public API: avoid renaming existing IDs without a migration map.

## Add a new shape

Add an original geometry branch in `art()` in `scripts/build_library.py`.
Use basic SVG geometry only: paths, rectangles, circles, ellipses, lines and text.
Keep the 144 × 112 viewBox, consistent stroke widths and theme palette. Avoid
scripts, stylesheets, raster images, external references, `foreignObject`, or
font files. Add metadata, tags and a usage warning where a symbol could be
technically misleading. Regenerate the checksum rather than editing it by hand.

## Add a new template

Create a valid scene JSON file in `diagramkit/library/templates/` and add a
reproducible definition to `scripts/build_templates.py` when appropriate. Render,
inspect and test. Use explicit waypoints for important routes and label states.
Templates should teach one mechanism or show one level of architecture detail.

## Useful next additions

An obstacle-aware routing engine and accurate text measurement would improve
complex scenes more than simply adding hundreds of extra icon variants. A live
scene editor could make final manual cleanup faster while preserving scene JSON.
An approved custom-asset importer would need SVG sanitization, license/provenance
tracking, checksums, search indexing and a documented trust boundary.

Vendor-specific packs should remain separate from the generic collection, with
source URLs, version, license and usage restrictions recorded per asset. This
release does not include AWS, Azure, GCP, Cisco, VMware, Proxmox, AMD or NVIDIA
logo packs. Vendor terms currently function only as search aliases.

A future remote MCP deployment requires a maintained transport implementation,
authentication, authorization, concurrency/resource limits, isolated export storage
and operator monitoring. Do not expose this stdio adapter through an unauthenticated
shell bridge and call that a hosted service.
