# Diagram and chart snippets

Copy these into the page and change the labels and numbers. They are plain HTML, CSS and inline SVG: no JavaScript, no CDN, no
Mermaid, no Chart.js. Report previews are sandboxed (scripts are stripped), so anything that needs a script will show up blank.

Rules for every visual:
- Put the CSS block once in the page's `<style>`; reuse the palette variables from `assets/report-template.html`
  (`--blue`, `--green`, `--orange`, `--purple`, `--red`, `--yellow`, `--ink`, `--muted`, `--line`).
- Colour means one thing across the page (see `design-system.md`). Text in a diagram is at least 12px.
- Wrap each visual in a `<figure>` with a one-line `<figcaption>` saying what to take from it. Give SVGs `role="img"` and an
  `aria-label`.
- Draw the numbers from the data. Compute bar heights, slice lengths and positions; do not eyeball them.
- Aim for at least two different visuals in a report (for example one process or architecture diagram plus one chart or
  timeline), placed next to the section they explain.

## CSS (add once)

```css
figure.viz { margin: 16px 0 0; padding: 18px; border: 1px solid var(--line); border-radius: 8px; background: #fbfcff; }
figure.viz figcaption { margin-top: 10px; color: var(--muted); font-size: 13px; }
.flow { display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px; }
.flow .step { box-sizing: border-box; flex: 1 1 0; min-width: 110px; padding: 12px; border: 1px solid #b8d2ff; border-radius: 8px; background: var(--blue-soft); }
.flow .step strong { display: block; font-size: 14px; color: #263752; }
.flow .step small { display: block; margin-top: 4px; font-size: 12px; color: var(--muted); }
.flow .step.green { border-color: #b8e4cb; background: var(--green-soft); }
.flow .step.orange { border-color: #ffd9a3; background: var(--orange-soft); }
.flow .step.red { border-color: #ffc0bd; background: var(--red-soft); }
.flow .arrow { flex: 0 0 auto; align-self: center; color: var(--muted); font-size: 20px; }
.layers { display: grid; gap: 8px; }
.layers .layer { padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; }
.layers .layer b { display: block; font-size: 14px; margin-bottom: 8px; }
.layers .row { display: flex; flex-wrap: wrap; gap: 8px; }
.layers .chip { padding: 6px 10px; border-radius: 6px; background: #fff; border: 1px solid var(--line); font-size: 13px; }
.timeline { position: relative; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; padding-top: 22px; }
.timeline::before { content: ""; position: absolute; left: 0; right: 0; top: 8px; height: 2px; background: var(--line); }
.timeline .ms { position: relative; padding-top: 10px; }
.timeline .ms::before { content: ""; position: absolute; top: -20px; left: 0; width: 14px; height: 14px; border-radius: 50%; background: var(--blue); border: 3px solid #fff; box-shadow: 0 0 0 1px var(--line); }
.timeline .ms.done::before { background: var(--green); }
.timeline .ms.next::before { background: var(--orange); }
.timeline .ms strong { display: block; font-size: 14px; }
.timeline .ms small { color: var(--muted); font-size: 12px; }
@media (max-width: 640px) { .timeline { grid-template-columns: 1fr; } .flow .arrow { display: none; } }
```

## 1. Process flow (steps left to right)

Use for a pipeline, a sales or service process, onboarding, "how it works".

```html
<figure class="viz">
  <div class="flow" role="img" aria-label="Lead to delivery process in five steps">
    <div class="step"><strong>1. Lead</strong><small>Web, phone, walk-in</small></div>
    <span class="arrow">&rarr;</span>
    <div class="step"><strong>2. Qualify</strong><small>Budget, timing, trade-in</small></div>
    <span class="arrow">&rarr;</span>
    <div class="step orange"><strong>3. Proposal</strong><small>Quote and demo drive</small></div>
    <span class="arrow">&rarr;</span>
    <div class="step green"><strong>4. Close</strong><small>Deal signed</small></div>
    <span class="arrow">&rarr;</span>
    <div class="step green"><strong>5. Deliver</strong><small>Handover and follow-up</small></div>
  </div>
  <figcaption>Most leads are lost between steps 2 and 3.</figcaption>
</figure>
```

## 2. Flowchart with a decision (SVG)

Use when the process branches. Positions are fixed in a 760-wide box (the viewBox crops to the drawn area); add or move nodes by editing the x and y values.

```html
<figure class="viz">
  <svg viewBox="0 60 760 150" width="100%" role="img" aria-label="Qualified leads continue, others are nurtured">
    <defs>
      <marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0L10 5L0 10z" fill="#647086"/>
      </marker>
    </defs>
    <g font-family="-apple-system, Segoe UI, sans-serif" font-size="13" text-anchor="middle">
      <rect x="10" y="80" width="130" height="50" rx="8" fill="#eaf2ff" stroke="#b8d2ff"/>
      <text x="75" y="110" fill="#263752">New lead</text>
      <path d="M140 105H200" stroke="#647086" stroke-width="1.5" marker-end="url(#ah)"/>
      <path d="M270 70L335 105L270 140L205 105z" fill="#fff2dc" stroke="#ffd9a3"/>
      <text x="270" y="109" fill="#263752">Qualified?</text>
      <path d="M335 105H410" stroke="#647086" stroke-width="1.5" marker-end="url(#ah)"/>
      <text x="372" y="97" fill="#647086" font-size="12">Yes</text>
      <rect x="415" y="80" width="130" height="50" rx="8" fill="#e9f7ef" stroke="#b8e4cb"/>
      <text x="480" y="110" fill="#263752">Book demo</text>
      <path d="M545 105H610" stroke="#647086" stroke-width="1.5" marker-end="url(#ah)"/>
      <rect x="615" y="80" width="130" height="50" rx="8" fill="#e9f7ef" stroke="#b8e4cb"/>
      <text x="680" y="110" fill="#263752">Close</text>
      <path d="M270 140V180H410" stroke="#647086" stroke-width="1.5" fill="none" marker-end="url(#ah)"/>
      <text x="283" y="165" fill="#647086" font-size="12" text-anchor="start">No</text>
      <rect x="415" y="158" width="130" height="44" rx="8" fill="#ffeceb" stroke="#ffc0bd"/>
      <text x="480" y="185" fill="#263752">Nurture later</text>
    </g>
  </svg>
  <figcaption>Only qualified leads get a demo; the rest enter nurture.</figcaption>
</figure>
```

## 3. Layered architecture or capability map

Use for systems, platforms, "what is in the stack".

```html
<figure class="viz">
  <div class="layers">
    <div class="layer" style="background:#eaf2ff;border-color:#b8d2ff"><b>Experience</b>
      <div class="row"><span class="chip">Desktop app</span><span class="chip">Email reports</span></div></div>
    <div class="layer" style="background:#e9f7ef;border-color:#b8e4cb"><b>Agent and skills</b>
      <div class="row"><span class="chip">Reports</span><span class="chip">Diagrams</span><span class="chip">Scheduling</span></div></div>
    <div class="layer" style="background:#f1edff;border-color:#d4c8ff"><b>Models</b>
      <div class="row"><span class="chip">LiteLLM gateway</span><span class="chip">AWS Bedrock</span></div></div>
    <div class="layer" style="background:#fff8d8;border-color:#eadb86"><b>Data</b>
      <div class="row"><span class="chip">DMS</span><span class="chip">CRM</span><span class="chip">Accounting</span></div></div>
  </div>
  <figcaption>Each layer only talks to the one below it.</figcaption>
</figure>
```

## 4. Timeline or roadmap

Use for milestones, phases, history. Mark each `ms` as `done`, `next`, or leave plain for later.

```html
<figure class="viz">
  <div class="timeline">
    <div class="ms done"><strong>Q1</strong><small>Pilot in service</small></div>
    <div class="ms done"><strong>Q2</strong><small>Sales reports</small></div>
    <div class="ms next"><strong>Q3</strong><small>Daily email delivery</small></div>
    <div class="ms"><strong>Q4</strong><small>All departments</small></div>
  </div>
  <figcaption>Green is finished, orange is in progress.</figcaption>
</figure>
```

## 5. Bar chart (SVG)

Use to compare a few categories. For each bar: `height = value / max * 150`, `y = 170 - height`, `x = 40 + index * 90`.
Label the value on top of the bar. The example max is 6,190.

```html
<figure class="viz">
  <svg viewBox="0 0 420 200" width="100%" style="max-width:520px" role="img" aria-label="Net revenue by region">
    <g font-family="-apple-system, Segoe UI, sans-serif" font-size="12" text-anchor="middle" fill="#647086">
      <line x1="30" y1="170" x2="410" y2="170" stroke="#dfe5ee"/>
      <rect x="40"  y="20"  width="60" height="150" rx="4" fill="#1f6feb"/><text x="70"  y="14"  fill="#263752">6,190</text><text x="70"  y="190">South</text>
      <rect x="130" y="55"  width="60" height="115" rx="4" fill="#1f6feb"/><text x="160" y="49"  fill="#263752">4,775</text><text x="160" y="190">North</text>
      <rect x="220" y="96"  width="60" height="74"  rx="4" fill="#1f6feb"/><text x="250" y="90"  fill="#263752">3,053</text><text x="250" y="190">West</text>
      <rect x="310" y="142" width="60" height="28"  rx="4" fill="#e5484d"/><text x="340" y="136" fill="#263752">1,180</text><text x="340" y="190">East</text>
    </g>
  </svg>
  <figcaption>East is the weak region at one fifth of South.</figcaption>
</figure>
```

## 6. Share donut (SVG)

Use for parts of a whole (up to five slices). Circumference is about 314 for radius 50. Each slice's `stroke-dasharray` is
`share * 314` then the rest; `stroke-dashoffset` is minus the running total of earlier slices. Example: 75%, 21%, 4%.

```html
<figure class="viz">
  <svg viewBox="0 0 300 140" width="100%" style="max-width:460px" role="img" aria-label="Revenue share by category">
    <g transform="rotate(-90 70 70)" fill="none" stroke-width="24">
      <circle cx="70" cy="70" r="50" stroke="#1f6feb" stroke-dasharray="235.5 78.5"  stroke-dashoffset="0"/>
      <circle cx="70" cy="70" r="50" stroke="#1b8754" stroke-dasharray="66 248"      stroke-dashoffset="-235.5"/>
      <circle cx="70" cy="70" r="50" stroke="#b86600" stroke-dasharray="12.5 301.5"  stroke-dashoffset="-301.5"/>
    </g>
    <g font-family="-apple-system, Segoe UI, sans-serif" font-size="13" fill="#263752">
      <rect x="150" y="38" width="12" height="12" rx="2" fill="#1f6feb"/><text x="170" y="49">Electronics 75%</text>
      <rect x="150" y="62" width="12" height="12" rx="2" fill="#1b8754"/><text x="170" y="73">Furniture 21%</text>
      <rect x="150" y="86" width="12" height="12" rx="2" fill="#b86600"/><text x="170" y="97">Stationery 4%</text>
    </g>
  </svg>
  <figcaption>Three quarters of revenue comes from one category.</figcaption>
</figure>
```
