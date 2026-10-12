# Presentation HTML — Advanced Guide

Read this file when the source material is very large (>5000 words), when iterating on an existing report, or when encountering edge cases not covered by the core methodology.

## Large Content Chaptering

When the input is too large to fit naturally into the template, plan the page before writing final copy.

1. Inventory the source material into themes, decisions, systems, timelines, risks, and evidence.
2. Select a chapter count that fits the reader's task. Five to nine top-level anchors is a useful default.
3. Choose the ordering logic deliberately: urgency, chronology, dependency, business domain, user journey, system layer, maturity level, or decision sequence.
4. Write one takeaway per chapter.
5. Choose one dominant visual pattern per chapter.
6. Keep the top of the page as a compression layer: hero metrics, summary cards, and navigation help the reader choose a path.
7. Use progressive disclosure: summary first, then grouped evidence, then implementation or appendix detail.
8. Balance chapter density.

For very large source sets, generate in passes:

1. Outline and chapter map.
2. Section-by-section content extraction.
3. HTML composition with anchors and reusable card patterns.
4. Visual QA for overflow, repeated content, color consistency, and chapter flow.

## Known Limitations

- **Three-column architecture grids may look sparse when content is asymmetric.** Keep the three outer cards equal height; accept whitespace.
- **Print mode breaks long tables across pages.** Keep tables under ~15 rows.
- **14px body text is uncomfortable for extended reading.** This is intentional — presentation reports are scanning artifacts, not reading documents.
- **No dark mode.** The system is optimized for light-background presentation.

## Iteration Guide

1. Change one chapter at a time.
2. When adding a new chapter, decide its visual pattern first.
3. When changing colors, re-verify the entire page.
4. When adjusting a chapter's content, check card balance afterwards.
5. Default to 14px/1.65 for all body text.
6. When the source material changes significantly, start from the Decision Priorities in SKILL.md.
7. Run the Review Checklist after every iteration.
