---
name: mermaid-diagrams
description: "Mermaid diagrams: flows, sequences, ER, Gantt, mindmaps."
version: 1.0.0
author: Ask Dealer
license: Unspecified
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [diagram, mermaid, flowchart, sequence, er-diagram, gantt, mindmap, visualization]
    category: creative
    related_skills: [architecture-diagram, concept-diagrams, excalidraw]
---

# Mermaid Diagrams Skill

Turn a description into a clean Mermaid diagram written in a fenced `mermaid` code block. Hermes Desktop draws these blocks live in the chat and follows light/dark mode on its own. It does not produce polished infrastructure graphics, hand-drawn sketches, or image files by itself; for those see `When to Use`.

## When to Use

- The user asks to diagram, draw, map, chart, visualize, or illustrate a process, system, sequence of calls, data model, schedule, state machine, or idea hierarchy.
- The diagram should stay editable as text and live inside the chat or a Markdown document.
- Not for dark, styled cloud/infra pictures: use the `architecture-diagram` skill. Not for hand-drawn editable sketches: use the `excalidraw` skill. Not for teaching illustrations: use `concept-diagrams`.

## Prerequisites

- Nothing for the chat: Desktop renders ` ```mermaid ` blocks.
- Only to export an image for a PDF, slide, or document: Node.js with `npx -y @mermaid-js/mermaid-cli` (it downloads a headless browser on first run).

## How to Run

Write the diagram in a fenced block and reply with it. To turn it into an image, save the source with `write_file` (use a fresh file name) and run with `terminal`:

```bash
npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png -t neutral -b white -s 2
```

Insert the PNG into a PDF with the `image` element of the `pdf` skill's `pdf_create.py`.

## Quick Reference

| Intent | Diagram type |
|---|---|
| Steps, pipelines, decisions | `flowchart` |
| Time-ordered calls between parties | `sequenceDiagram` |
| Classes and data models | `classDiagram` |
| Database tables and relations | `erDiagram` |
| Lifecycle, statuses, transitions | `stateDiagram-v2` |
| Schedule, plan, milestones | `gantt` or `timeline` |
| Idea hierarchy, brainstorm | `mindmap` |
| Share of a whole | `pie` |
| Git branches and merges | `gitGraph` |
| System context boxes | `C4Context` (experimental) or a `flowchart` with subgraphs |

Syntax and a working example of every type: `references/diagram-types.md`.

## Procedure

1. Pick the diagram type from the table; read its entry in `references/diagram-types.md` if unsure of the syntax.
2. List the entities, the relationships, and the direction of flow from the user's description. Ask only if a missing detail changes the diagram.
3. Write the diagram. Do not add a `theme` setting: Desktop themes diagrams itself, and a fixed theme can wash out in dark mode. Set the theme only when exporting an image (`-t` flag above).
4. Apply these rules:
   - One concept per node; break long labels with `<br/>`.
   - `LR` for pipelines, `TD` for hierarchies; reorder nodes to avoid crossing edges.
   - Label every edge that carries meaning; every visible node has a human-readable label, never a raw id.
   - Use `subgraph` once a cluster passes about 6 nodes; keep top-level nodes to about 12, otherwise split into several diagrams.
   - Use colour only for meaning (primary, warning, danger, success), always with explicit `fill`, `stroke` and `color` so it reads in light and dark:

   ```
   classDef primary fill:#4A90D9,stroke:#2C5F8A,color:#fff
   classDef warning fill:#E8A838,stroke:#B07820,color:#000
   classDef danger fill:#D94A4A,stroke:#8A2C2C,color:#fff
   classDef success fill:#4AAD6A,stroke:#2C7A45,color:#fff
   class NodeA,NodeB primary
   ```
5. Reply with the fenced block and one or two sentences saying what it shows. Offer the editable source when the user wants a file.
6. If the user wants Excalidraw, use the `excalidraw` skill, or paste the source into excalidraw.com (menu: "Mermaid to Excalidraw"). Mindmap, timeline and requirement diagrams do not convert; offer a flowchart instead.

## Pitfalls

- **`end` in a label.** The lowercase word `end` inside a flowchart node breaks parsing; write `End` or quote the label.
- **Special characters.** Parentheses, brackets, quotes, and `#` in a label need the label in double quotes: `A["Rate (target $150)"]`.
- **Ids with spaces.** Node ids are single tokens; put the readable text in the label: `svc[Service desk]`.
- **Desktop is strict.** Links, click handlers and raw HTML in labels are disabled in the chat renderer; `<br/>` for line breaks is fine.
- **C4 is experimental.** It renders plainly and varies by version; prefer a flowchart with subgraphs for architecture.
- **Too big to read.** A diagram with dozens of nodes is unreadable at chat width; split it by area.
- **Dates in Gantt.** Always set `dateFormat YYYY-MM-DD` and use that format.

## Verification

- The block opens with the diagram keyword on its first line, with no theme set for chat output.
- Every node has a readable label; labelled edges where meaning matters; no more than about 12 top-level nodes.
- In Desktop the diagram draws. If an error box appears instead, fix the syntax (see Pitfalls) and resend.
- For an exported image, open the PNG with `vision_analyze` and check for clipped or overlapping text before using it in a document.
