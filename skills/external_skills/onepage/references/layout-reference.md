# Presentation HTML — Layout & Component Reference

Read this file when building or tuning the page layout, working with architecture diagrams, or applying component-level rules.

## Layout Patterns

Use `max-width: 1360px` for wide presentation reports. Keep body font at `14px/1.65`.

Recommended top layout:

- `.hero`: two-column grid, main narrative on the left and metrics on the right.
- `.hero-side`: two-column metric grid.
- `.nav`: sticky, horizontally scrollable anchors.
- `.section`: white panel with 8px radius and a subtle shadow.
- `.summary-grid`: 4-5 equal cards.

Architecture diagrams:

- Use `.architecture-set` to stack multiple diagrams.
- Use the same `.architecture-flow` grid across related diagrams:
  `grid-template-columns: minmax(220px, 0.85fr) minmax(0, 2fr) minmax(240px, 0.95fr);`
- Use `align-items: stretch` on `.architecture-flow` so the three outer cards stay equal height.
- Use `.diagram-card.wide` for center columns or full-width layers.

Mobile rules:

- Collapse hero and architecture grids to one column below 900px.
- Collapse summary, matrix, and milestone grids to one or two columns.
- Avoid fixed heights except for compact status labels or visual chips.

## Architecture Diagram Guidance

- Split infrastructure from application organization if physical deployment and logical app composition are mixed.
- Put direct external service entry points in their own layer.
- Put common capabilities outside apps and connect them conceptually through copy or layout.

## Component Guardrails

### Hero
- Must contain: eyebrow label, h1 title, subtitle, metadata pills, and 2-6 metric cards.
- Must NOT contain: architecture diagrams, long-form text (>2 sentences in subtitle), or interactive elements.

### Navigation (.nav)
- Required when the page has 4 or more top-level sections.
- Labels: 2-6 words in English. Parallel construction. Must be sticky and horizontally scrollable.

### Section (.section)
- Every section must have: a section-title (h2 + optional section-note), and at least one content block.
- Vertical spacing between sections must be consistent (20px margin-top).

### Summary Cards (.summary-card / .summary-grid)
- Use 4-5 cards per grid.
- Each card: one strong title + one short paragraph.
- Card text volume should be visually balanced.

### Architecture Diagram (.architecture-flow)
- Always use the three-column grid: left context → center detail → right context.
- Column widths must use the same `grid-template-columns` across all architecture diagrams.
- Every `.diagram-card` must use the same internal layout:

  ```css
  .architecture-flow { align-items: stretch; }
  .diagram-card { display: grid; grid-template-rows: auto 1fr; gap: 10px; }
  .diagram-card h3 { margin: 0; line-height: 1.5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .diagram-card > :not(h3) { align-self: start; }
  ```

### Milestone Cards (.next-step)
- Always include a priority tag: P0 (critical, near-term) or P1 (important, medium-term).
- Each card should start with an action verb.
- 4-6 cards per grid.

### Tags (.tag)
- P0 tags: red styling. P1 tags: orange styling.
- Tags are for milestone cards only.
