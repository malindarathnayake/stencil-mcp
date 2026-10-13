# Scene JSON v1

A scene describes content, placement and relationships. The renderer embeds registered
vector symbols and escapes all labels. No caller-supplied SVG, HTML, CSS, remote URL,
JavaScript or arbitrary file path is accepted.

## Minimal example

```json
{
  "version": "1.0",
  "title": "Application request path",
  "subtitle": "The client reaches an API through an edge gateway.",
  "width": 1100,
  "height": 430,
  "nodes": [
    {"id":"client","kind":"component","asset":"software/browser","x":45,"y":180,"label":"Client"},
    {"id":"gateway","kind":"component","asset":"network/api-gateway","x":445,"y":180,"label":"API gateway"},
    {"id":"api","kind":"component","asset":"software/rest-api","x":845,"y":180,"label":"Application API"}
  ],
  "edges": [
    {"id":"request","source":"client","target":"gateway","kind":"data","label":"HTTPS"},
    {"id":"upstream","source":"gateway","target":"api","kind":"data","label":"Forward"}
  ]
}
```

Every asset ID is a catalog key, not a filesystem path. Search before selecting IDs.
`diagramkit/library/scene.schema.json` is the full specification for this renderer.

## Node kinds

| Kind | What it draws | Important fields |
| --- | --- | --- |
| `component` | A symbol inside a labelled card | `asset`, `label`, optional `detail` |
| `symbol` | The vector symbol without a card | `asset`, `w`, `h`; optional `caption` (≤ 120 chars, up to two lines) draws a visible label inside the node box |
| `packet` | A numbered or labelled packet tile | `label`, `detail`, `palette`, `state` |
| `memory` | Ordered destination slots | `cells`, optional `label` |
| `text` | Wrapped text at a chosen position | `label`, `font_size`, `weight`, `align`, `w`, `h` |
| `marker` | A loss/failure or success marker | `state`, `w`, `h` |

All nodes require `id`, `kind`, `x`, `y`. Node and group IDs must be unique and
start with a letter. Dimensions default by kind; explicitly setting `w` and `h`
is preferable for reusable templates. The `label` on a `symbol` is accessible
metadata; set `caption` when the symbol needs a visible label (decisions, events). Empty text nodes can serve as sequence anchors.

A memory cell contains `value`, optionally `palette` and `state`. Example:

```json
{"id":"memory","kind":"memory","x":50,"y":230,"w":410,"h":86,
 "label":"Receiver memory",
 "cells":[
  {"value":"1","palette":"orange"},
  {"value":"2","palette":"blue"},
  {"value":"3","palette":"green"},
  {"value":"—","palette":"purple","state":"missing"},
  {"value":"5","palette":"yellow"}
 ]}
```

## Connectors

`source` and `target` name nodes. `source_port` and `target_port` choose cardinal
anchors (`n`, `e`, `s`, `w`). Without explicit ports, the renderer chooses facing
sides based on relative positions. Anchors refer to the enclosing card/symbol
bounds, not the visible connector socket drawn inside an icon.

`route` may be `orthogonal` (default) or `straight`. `points` is an ordered list
of extra `{x,y}` waypoints between the two endpoint anchors. Supplying waypoints
can produce diagonal segments; they are used exactly as provided.

`kind` controls the default line pattern and arrow. `arrow` can override the
arrowheads with `forward`, `both` or `none`. `palette` selects a named color pair;
`width` is the line width. `label_x` is the label center x coordinate and `label_y`
is its text-baseline reference (the label rectangle starts 14 units above it).

For parallel flows, avoid identical routes that hide one another. Give them
separate waypoints or split a detailed traffic overlay into another panel.

## Groups and boundaries

A group has `id`, `x`, `y`, `w`, `h`, `title`, optional `caption`, `palette`, and
`style` (`panel`, `boundary`, `lane`). Groups are rendered behind connectors.
A node's optional `group` field enables strict containment checking. Group boxes
are not automatically resized around children. Group membership is not a security
control and does not automatically imply a deployment or namespace.

## Theme and rendering

Set `theme` to `light`, `dark` or `monochrome`. Palettes are `blue`, `teal`, `purple`,
`orange`, `red`, `slate`, `green`, `yellow`. Colored roles do not replace labels.

An SVG includes `<title>`, `<desc>`, stable node/edge group IDs and editable text.
Assets are embedded as vector geometry, not linked PNGs or base64 screenshots.
No fonts are embedded. Appearance depends slightly on locally available fonts.

The renderer draws groups, connectors, nodes, then connector labels. It does not
add automatic crossing bridges or compute complex cable routing. Validation
warns about edge/card collisions and estimated label collisions. Render and inspect
at the actual display size before publication.

## Bounds

Canvas: 480–6000 × 240–6000 units. Maximum 200 scene nodes, 400 edges, 40 groups,
32 memory slots per strip and 32 intermediate waypoints per edge. MCP messages
are limited to 1 MiB. The initial graph-layout helper accepts up to 80 nodes.
Large graphs should be split; these are resource limits, not layout quality targets.
