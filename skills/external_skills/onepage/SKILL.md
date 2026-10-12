---
name: onepage
description: "HTML presentation pages: reports, roadmaps, dashboards."
version: 0.2.1
author: wjhuang88
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [html, report, presentation, dashboard, roadmap, infographic, visual-report]
    category: productivity
---

# Presentation HTML Report

## Decision Priorities

Decisions are not equally weighted. Making them out of order produces inconsistent pages. Follow this priority:

1. **Page mode** (most important) — determines the narrative structure and all subsequent visual choices. Decide this before writing any HTML.
2. **Chapter flow** — group source material into sections with a clear narrative arc. Each chapter gets one job.
3. **Visual pattern per chapter** — assign each chapter a dominant visual pattern (metric cards, architecture diagram, comparison matrix, timeline, risk register, detail table).
4. **Color mapping** — assign semantic colors at the page level, once. The same color must mean the same thing everywhere.
5. **Content fill** — write and place content only after the above decisions are locked.

Reversing this order (writing content first, then choosing visuals) is the most common cause of inconsistent output.

## Workflow

Steps follow the Decision Priorities above. Each step is tagged with its priority band.

1. **[Page mode]** Identify the audience, viewing context, source-material type, and desired action from the source material.
2. **[Page mode]** Choose the page mode before writing any HTML: executive report, technical explainer, roadmap, product brief, research digest, project inventory, operating plan, or chaptered long-form showcase.
3. **[Chapter flow]** Design the chapter flow around the material instead of forcing a fixed report structure. Choose, merge, split, or reorder sections so the page has a clear narrative arc for the intended reader.
4. **[Chapter flow]** Convert raw notes into balanced sections that match the chosen flow. Common building blocks include overview, architecture or operating model, current state, evidence, completed work, in-progress work, gaps, plan, risks, milestones, and appendix-style details.
5. **[Visual pattern]** For very large inputs, build a chapter plan before drafting HTML. Keep the detailed planning workflow in `references/advanced-guide.md`.
6. **[Color mapping]** Before writing content, lock the semantic color assignments for the whole page so the same color means the same thing everywhere. Detailed palette and semantics live in `references/design-system.md`.
7. **[Template & layout]** Use `assets/report-template.html` as the base when creating a new page — copy it, replace all `{{PLACEHOLDER}}` values with real content, and save the result as the output file. Read references progressively:
   - `references/design-system.md` — always (principles, pattern selection, visual language, wording, checklist).
   - `references/layout-reference.md` — when building or tuning layout, diagrams, or component details.
   - `references/advanced-guide.md` — when the source is very large, iterating on an existing page, or hitting edge cases.
8. **[Content fill]** Write content into the locked structure. Apply the Content Rules below as you go. Keep the output self-contained (no external CDN, no remote images) so it works as a single shareable .html file.
9. **[Verify]** Verify the page by inspecting the generated HTML for overlapping text, inconsistent grid widths, cramped cards, weak chapter flow, and mismatched color semantics.

## Content Rules

- Lead with the clearest outcome, current state, or reader decision, not background narrative.
- Use business-readable names in visible labels.
- Avoid repeating the same capability in multiple cards. Use one canonical location.
- Separate physical deployment architecture from logical application architecture when one diagram becomes too dense.
- Use color consistently: the same color must mean the same kind of thing across the page.
- Keep milestone content balanced.
- For large materials, build a visible chapter structure with section anchors, compact summaries, and progressive detail.
- Let chapters follow the natural logic of the source material.
- Keep each card scoped to one idea.

## Diagram Rules

- Prefer HTML/CSS diagrams for presentation pages when the diagram needs to live in the report itself.
- Use aligned three-column architecture grids for comparable diagrams.
- Keep three-column architecture cards equal height while keeping card titles single-line, top-aligned, and visually aligned across columns.
- Avoid standalone legends when the card labels and color semantics are obvious.

## Images

"No remote images" means the file must stay viewable offline — it does not mean skip illustrations. For topic/explainer pages (not pure data dashboards):

- Embed every image as a `data:image/...;base64,...` URI inline in the `src` attribute. A plain `src="photo.jpg"` link breaks the moment the HTML is moved or emailed on its own.
- Source order: try a real photo (Wikimedia Commons, Unsplash) downloaded via `requests` first, then base64-encode it. If the fetch fails (403/429, SVG with no raster render) or no suitable photo exists, generate a simple concept graphic with matplotlib (e.g. an icon-style illustration: shapes, a node graph, a shield) sized ~5:3, save as PNG, and base64-embed that instead. Never ship a report with a broken `src` or a placeholder.
- Verify embedded images actually render by opening the file in the browser tool and taking a screenshot before declaring the report done — a base64 string that didn't get substituted correctly looks fine in the HTML source but shows a broken image box on screen.

## Output

The final output is a single self-contained `.html` file. Save it to disk and show a file card. The user can open it in a browser, share it by email, or print it. No internet connection required to view it.

## Output Checklist

- The page works as a single `.html` file with no external dependencies.
- Desktop layout is dense but readable; mobile layout collapses to one column.
- Section headings, notes, and cards align cleanly.
- No text overlaps later content.
- Architecture diagrams use consistent widths, equal-height outer cards, top-aligned single-line card titles.
- The final page can be printed or shared as a static artifact.
