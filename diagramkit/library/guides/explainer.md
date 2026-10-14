# Explainers, comparisons and decision panels

> Use this guide when the diagram teaches one idea across panels, compares option A with option B for a decision record, shows a current and target state, tiles a coarse capability map, or lays out migration phases side by side.

## Questions to ask first

Ask these in one round, and only for facts the brief leaves open. Each answer changes what is drawn.

1. What is the single takeaway a reader should leave with? (default: the sentence in the brief that states a change or a choice, used as the subtitle)
2. How many panels, and what does each one show? (default: two panels for a comparison or before/after; three for an annotated walkthrough; one panel per phase for a migration plan)
3. What exactly differs between the panels: added, removed, moved or changed components, or a different flow? (default: only the elements the brief names as changing; everything else is drawn identically)
4. For a decision comparison, has a choice been made, and which option was chosen? (default: no choice recorded; both options are drawn neutrally with `status/pending`)
5. Which criteria decide between the options, and should they appear on the canvas? (default: up to three criteria per option, as short `detail` text, with no scores)
6. For before/after, what happens to components that disappear: retired, merged into something else, or still running in parallel? (default: retired; the element stays at its original position in the after panel with palette `slate` and `detail` "Retired", never silently dropped and never marked with state `down` or `status/down`, which mean failure)
7. Is there an intermediate or transition state between current and target? (default: no; two panels only)
8. For a migration plan, how many phases, in what order, and what is the exit condition of each phase? (default: the phases named in the brief, in that order, with no exit conditions invented)
9. For a capability map, how many top-level domains and roughly how many capabilities in each? (default: the domains named in the brief, one panel each, no capabilities added that the brief does not list; use the counts to check the limits under "Push back when")
10. Should capabilities carry a status, such as present, missing or blocked? (default: no status; plain cards)
11. Which reading order should the numbered steps follow in an annotated walkthrough? (default: the order of the flow, left to right, starting at the request or trigger)
12. Where will this be shown: slides, docs, print, or monochrome output, and for which audience? (default: light theme for engineers, technical labels kept, product names omitted unless the brief uses them; every difference is also marked in text so the diagram survives monochrome)

## Push back when

- The user wants a heat map of maturity, cost or risk across capabilities. Palettes are categorical (blue, teal, purple, orange, red, slate, green, yellow) with no defined order, so readers cannot rank them. Tell the user you will write the level as text in `detail` or use status markers, and use palette only for categories such as domain.
- The user wants a dated timeline or Gantt-style axis for migration phases. The scene format has no time axis or scaled duration. Tell the user phases will be ordered, numbered panels, with target dates written in each panel caption if they supply them.
- The user wants an option marked as chosen when the brief says the decision is still open. Marking it `status/approved` records a decision that has not been made. Ask whether it is decided; if not, use `status/pending` on both.
- The user wants a separate legend for each panel. A scene has one `legend` list of at most 12 entries, drawn as one row along the bottom of the canvas. Tell the user you will use one shared legend and, if meanings genuinely differ per panel, a short `text` note inside that panel.
- The capability map is larger than the format holds. A scene allows at most 40 groups (which do not nest), 200 nodes and a 6000 x 6000 px canvas, and validation warns when one panel holds more than 28 elements. A default card is 200 x 146 px. Tell the user that a map of more than about 200 cards, or more than about 28 cards in one domain, will be split by domain into several diagrams or summarized to fewer cards.
- The user asks for one panel that shows option A and option B running together when they are alternatives. Two alternatives in one panel read as a combined architecture. Tell the user each option gets its own panel.
- The before and after panels would differ in components the user never mentioned. Do not add or remove elements to make the target look cleaner; ask instead.

## How we draw it here

- Panels run left to right in reading order: current then target, option A then option B, phase 1 then phase 2. Use `style: "panel"` groups of equal size, aligned on the same top edge, with a gap of at least 60 px. Stack panels in rows only when more than three would make labels shrink; read rows left to right, top to bottom. Keep each panel at 28 elements or fewer.
- Number panel titles in reading order, as the `mrc-loss-recovery` template does ("1  Current state", "2  Target state"). Use the panel `caption` for the one-line point of that panel, or for a phase exit condition or date. Keep titles short enough to fit the panel width (validation warns with `group_title_width`).
- The panel title is drawn about 31 px and the caption about 54 px below the panel top. Start panel contents at least 80 px below the panel top, more if the caption wraps to two lines. Validation does not check nodes against the panel header, so check the preview.
- Keep every unchanged element at the same position relative to its panel in every panel. Build the first panel, then copy its nodes with a fixed x offset per panel, new unique ids (a duplicate id is an error) and `group` set to the new panel. Only the elements that differ may move, appear or disappear; that is what the reader's eye compares.
- Mark chosen and rejected options with `symbol` nodes using `status/approved` and `status/blocked` near the panel title, each with a `caption` such as "Chosen" or "Rejected: higher latency". Use `status/pending` for an undecided option and `status/warning` for a known risk. These markers explain themselves through their caption.
- The `presentation/step` glyph always shows a fixed "1" in its badge. Use it only when there is a single step. For numbered reading order, place bold `text` nodes (`weight` 700, `font_size` 18 to 22) such as "2" or "Step 2: lookup" next to the element or edge they describe. Number in the same order as the flow; one number per idea.
- Use `presentation/callout` or `presentation/note` symbols for one short explanation each, with the text in `caption`, at most two lines. Symbol art keeps its aspect ratio and is centred in its box, so `presentation/annotation-bracket` does not stretch to span several elements; place it beside one element or a tight cluster at about 144 x 112 px. To cover several elements under one remark ("Removed in target", "Shared by both options"), draw a titled `boundary` group around them. A node has only one `group`, so leave those nodes' `group` on the panel and let the boundary overlap geometrically.
- Use `presentation/decision` only for a real branch inside a walkthrough, with every outgoing edge labelled.
- For a capability map, each domain is one `panel` group in a tiled grid of equal cells; capabilities are `component` cards inside, with `group` set to the domain. Use the subject's own assets for the card icons (for example `data/data-warehouse`, `identity/identity-provider`, `business/invoice`) and `presentation/process` when no subject asset fits. Compute the grid from the card counts against the 6000 px canvas before placing anything. Do not draw edges between capabilities unless the brief states a dependency, and then use `dependency`.
- Edge kinds keep their normal meaning inside panels: `data` for flow, `control` for configuration or policy, `feedback` for responses, `dependency` for depends-on, `replication` for copied data. Do not draw edges between panels to mean "becomes"; the panel order already says that. If one transition cue is needed, use a text node between panels rather than an edge.
- Palette means category, and the same category keeps the same palette in every panel. On a component card the palette shows only as a thin left stripe, symbol nodes ignore it, and the monochrome theme collapses every palette to one colour. Use it as a secondary cue only: slate for unchanged, green for added or chosen, red for removed or rejected, orange for changed. Every added, removed or changed element must also say so in text, with `detail` "Added", "Removed", "Changed" or "Retired", or a callout. For panel-level category, set the panel group's palette, which fills its background.
- Use one `legend` for the whole canvas when more than one palette meaning or a solid versus dashed distinction appears. Legend entries are a coloured line plus a label, and `dashed` draws one fixed dash pattern, so a legend cannot show status icons or tell the different dashed edge kinds apart. Keep labels short: each entry takes about its label width at 12 px plus 70 px in a single row starting 36 px from the left, and overflow is not validated, so cut entries if the row would pass the canvas width.
- Put the caveat in `footer`, for example "Illustrative comparison; labels describe roles, not specific products." Put the takeaway in `subtitle` and a short narrative of what changes between panels in `description`.

## Common mistakes

- Redrawing the after panel from scratch, so unchanged elements move and the reader cannot see what changed.
- Changing many things between panels when the brief named one change, or adding "best practice" components to the target that nobody asked for.
- Relying on palette alone for added, removed, chosen or rejected. The card stripe is thin and monochrome output loses it entirely; always pair it with a `detail` word or with `status/approved` and `status/blocked`.
- Drawing a retired component with state `down` or `status/down`, which reads as a failure, or trying to show it "faded", which the format cannot draw.
- Marking a winner in an open decision, or drawing the preferred option with more detail so it looks better by presentation alone. Draw both options at the same level of detail.
- Several `presentation/step` symbols with captions "2", "3" beside a glyph that reads "1"; numbered steps that skip, repeat or run against the flow; or numbers placed far from what they describe.
- Nodes placed at the panel top, hidden under the panel title or caption.
- Using `presentation/swimlane` lanes or a left-to-right time line for migration phases; phases are ordered panels.
- A legend per panel built from text nodes, a legend listing status markers or meanings that do not appear, or a legend row that runs off the canvas.
- Capability maps drawn as one group per capability, which exhausts the 40-group limit, more than 28 cards crammed into one domain, or invented capabilities to fill empty cells.
- Stand-ins a model picks when guessing: `presentation/boundary` drawn as a symbol instead of a `panel` or `boundary` group; `status/healthy` for "chosen" instead of `status/approved`; a stretched `presentation/annotation-bracket` expected to cover several elements; `business/approval` for an architecture decision when `status/approved` is the marker for this diagram type.
- Panels of different sizes, so the same element sits at different scales and comparison breaks.

## Start from

- `mrc-loss-recovery` for numbered panels, step-by-step teaching layout and a caveat footer.
- `software-overview` as source content for an application before/after or option comparison. It is 1600 x 780 with one `boundary` group (the database node sits outside it) and no node `group` values, so it cannot be copied as is. Replace its boundary with one `panel` group per option, shift its x coordinates into each panel, give copied nodes new ids and `group` set to their panel, and set the canvas width to about two template widths plus the gap (at most 6000), or shrink the spacing so each panel stays readable.
- For capability maps and migration phase plans: no template yet; use `layout_diagram` for the first panel's contents, then place panels and copied coordinates by hand.
- Read alongside: `brief` and `style`, plus the topic guide for the subject shown inside the panels (check the `stencil_guide` index), because the panels must still follow that subject's rules.
