# Presentation HTML — Core Methodology

Always read this file when generating a presentation HTML report. It contains the design principles, pattern selection rules, visual language, wording guidance, and review checklist — the minimum context needed for every generation task.

For layout details and component specs, read [layout-reference.md](layout-reference.md) when building or tuning the page structure. For large-content chaptering, iteration guidance, and known limitations, read [advanced-guide.md](advanced-guide.md) when the task is complex.

## Source Experience

This pattern was distilled from a Harness roadmap and inventory page that needed to combine deployment status, architecture diagrams, completed work, future work, and milestones for leadership review.

The pattern generalizes to presentation HTML: a shareable, self-contained page that turns structured material into a readable visual artifact. It can be used for leadership reports, technical explainers, product briefs, project inventories, research digests, roadmaps, and long-form chaptered summaries.

The strongest pattern is not visual decoration. It is the combination of:

- a compact hero with the page purpose and status metrics;
- sticky section navigation for long material;
- dense but readable cards;
- architecture diagrams implemented directly in HTML/CSS;
- consistent color semantics across sections;
- section patterns that stay balanced and action-oriented.

## Page Structure

Treat section order as a design decision, not a rigid template. Start from the reader's task and the source material's natural shape, then choose a narrative structure:

- summary-to-detail: best for decision briefs, inventories, and broad status pages;
- chronological: best for roadmaps, incident reviews, migrations, and implementation histories;
- problem-to-solution: best for proposals, transformation plans, and capability upgrades;
- capability map: best for platform, product, and architecture overviews;
- comparison: best for options, vendors, designs, teams, or before/after states;
- layered architecture: best for systems where physical, logical, and operational views differ.

This order works well for many project inventory, roadmap, or status reports, but adapt it freely:

1. Hero: title, short subtitle, metadata pills, and 4-6 numeric status metrics.
2. Navigation: sticky horizontal anchor list.
3. Overall status: 4-5 summary cards with similar text volume.
4. Architecture: one or two diagrams, split physical and logical views when needed.
5. Completed work: grouped by platform, apps, support services, operations, or governance.
6. In-progress work: focus on capabilities and constraints, not team ownership.
7. Gaps or focus areas: short problem statements with priority tags.
8. Medium/long-term plan: describe capability evolution without overclaiming current deployment.
9. Milestones: 4-6 balanced cards with action verbs and concrete outcomes.

## Visual Language

Use a neutral operational palette:

- background: `#f7f8fb`
- panel: `#ffffff`
- text: `#172033`
- muted text: `#647086`
- border: `#dfe5ee`
- blue: deployed apps, runtime, primary status
- green: common support, shared capabilities
- orange: in-progress work, pending capabilities
- purple: external systems or independently hosted services
- yellow: storage or persistence
- pink/red: risk, governance, alerts

Do not use one color family for everything. If two blocks share a color, they should share a semantic category.

## Design Principles

1. **Density serves scanning.** 14px body text, compact cards, and tight spacing maximize information per viewport.
2. **Color is classification, not decoration.** Every color carries a fixed semantic meaning. Using color for visual variety breaks the system.
3. **One card, one idea.** Each card answers a single question. Dense evidence belongs in dedicated blocks.
4. **Hierarchy through structure, not font size.** Visual hierarchy comes from position and container weight, not new font sizes.
5. **Content drives structure, not the reverse.** Start from the source material's natural shape.
6. **Self-contained by default.** Every output works as a single `.html` file — no CDN calls, no external fonts, no remote image references. When a section genuinely needs a real photo or chart image (not a CSS/SVG diagram), download or generate the file, then base64-encode it and inline it as a `data:` URI in the `src` attribute — never leave a filesystem path or remote URL in the final HTML, since the deliverable must still work standalone when emailed or opened on another machine. If a source image fails to download, generate a simple flat-icon illustration (matplotlib patches saved as PNG) and inline that the same way rather than shipping the section with no visual.

## Do's and Don'ts

### Do

- Decide the page mode before writing any HTML.
- Assign semantic colors at the page level before filling content.
- Use business-readable names as primary labels.
- Keep card text under 3 lines.
- Give each chapter a single takeaway.
- Check architecture diagram column widths against each other.

### Don't

- Don't use color to indicate priority (use P0/P1 tags instead).
- Don't place internal system IDs or environment variable names as primary labels.
- Don't mix more than two visual patterns in one chapter.
- Don't use decorative gradients or drop shadows on individual cards.
- Don't flatten large material into a single long list.
- Don't call external CDNs or load remote fonts/images.

## Visual Pattern Selection

| Pattern | When to use |
|---|---|
| **Metric cards** | Status snapshots, KPI overviews, count-based summaries |
| **Architecture diagram** | System structure, platform composition, service relationships |
| **Comparison matrix** | Comparing alternatives, teams, systems, or before/after states |
| **Timeline / Roadmap** | Sequential events, version plans, migration phases |
| **Milestone cards** (P0/P1 tags) | Action-oriented next steps with priority and concrete outcome |
| **Detail table** | Dense facts: feature lists, configuration tables, dependency matrices |
| **Risk register** | Uncertainty tracking with likelihood, impact, and mitigation |

## Review Checklist

Before finishing:

- Section card text volume is balanced.
- Architecture columns align across diagrams.
- Architecture cards are equal height, titles single-line and top-aligned.
- Color categories are consistent across the page.
- Common capabilities appear once, not repeatedly.
- No external dependencies — the file works offline.
