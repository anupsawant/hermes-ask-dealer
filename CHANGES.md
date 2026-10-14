# Change log — Ask Dealer desktop customisation

Everything changed while customising Hermes into the Ask Dealer desktop app (Hermes on AWS Bedrock through
LiteLLM), as of 2026-10-08. Status is shown for each item: **committed**, **uncommitted**, or **local only**
(on one machine, not in the repo).

Commits `751e37b612` ("Add Ask Dealer changes") and `26fcd73a7d` ("Update Hermes , skills and external skills", pushed to `origin/ask-dealer-changes` on 2026-10-12) hold the committed items. Upstream base: `dde8800ed9`. Config and SOUL.md changes are local to this machine and are not in either commit.

## 1. Model picker: show only the LiteLLM models

| Item | Where | Status |
|---|---|---|
| Hide providers `openai-api`, `anthropic`, `gemini`, `openrouter` from every model picker | `hermes_cli/config_defaults.py`, `model_catalog.excluded_providers` | committed in 26fcd73a7d |
| Test that the default reaches the picker and that a user list replaces it (`[]` shows all providers again) | `tests/hermes_cli/test_picker_default_exclusions.py` (new) | committed in 26fcd73a7d |
| Same exclusion list written into the user's own config | `<HERMES_HOME>\config.yaml` | local only |

Notes
- This hides providers in the picker only. Keys and sign-ins stay on disk. To block use, restrict the LiteLLM key.
- The messaging gateway's `/model` command reads config without defaults, so it does not use the shipped default.
- Still visible in the picker: a placeholder model `litellm` and an extra `custom` row. Cause: `model.default: litellm` in
  the user's config. Fix: set it to a real model name from the LiteLLM admin panel.
- Check the spelling of the model names. The live backend lists `Pyrack Standard`; older config and logs say `Pyarck Standard`.

## 2. PDF skill: better-looking reports

All under `skills/productivity/pdf/`. **committed**

- `scripts/pdf_create.py`
  - Fixed tables running off the page (cells now wrap, columns fit the page width and never split a word).
  - Added themes (`corporate` default, `modern`, `classic` = the old plain look).
  - Added elements: `title`, `callout`, `metrics` (KPI cards with red/yellow/green status shown as colour and word,
    `sort_by_status` puts red first), `chart` (bar, line, pie), `bullets`, `spacer`; `status_col` on tables.
  - Headings stay on the same page as what follows; short tables stay whole; long tables split and repeat the header.
  - Stray `&` and `<` in text are kept as text (ReportLab used to rewrite `R&D` to `R&D;`).
  - `--preview DIR` renders every page to PNG after building.
- `SKILL.md` rewritten (version 2.0.0): clean lists, short description, element reference, design rules, and a
  **required** step to render and inspect every page before saying a document is done.
- `templates/general_report.json` and `templates/department_daily_report.json` (values are placeholders).
- `tests/test_pdf_skill.py`: 3 tests added (wide table stays on the page, designed report and bullets, classic theme).

Behaviour change: existing specs now render with the `corporate` theme. Add `"theme": "classic"` for the old look.

Delivery: the app uses the copy under `<HERMES_HOME>\skills\productivity\pdf\`. It was checked to be identical to
the repo copy (skill sync copies it on desktop start).

## 3. Rename to "Ask Dealer" (in progress)

| Item | Where | Status |
|---|---|---|
| Persona and chat title renamed ("Where Ask Dealer met you", "Welcome to Ask Dealer") | `hermes_cli/setup_profile.py` | committed in 26fcd73a7d |
| Restored 10 constants that the earlier rename edit deleted (`_FRESH_STATE`, `_OWNER`, `SETUP_CHAT_TITLE`, ...) | `hermes_cli/setup_profile.py` | committed in 26fcd73a7d |
| Chat title text updated to match | `apps/desktop/src/i18n/en_app_tour.ts`, `optional-skills/productivity/initiate-setup/SKILL.md` | committed in 26fcd73a7d |
| Earlier "Gideon" rename in other files | `SOUL.md`, `agent/prompt_builder.py`, `hermes_cli/default_soul.py`, `hermes_cli/doctor_state.py`, desktop electron files, `product-identity.cjs`, `intro.tsx`, ... | committed |

Open: about 330 "Gideon" strings remain elsewhere (288 in `apps/desktop/src/i18n/en.ts`), and the strings upstream moved into
`en_boot.ts`, `en_shared_metrics.ts` and similar files still say "Hermes". A single rename pass to "Ask Dealer" is not done.

## 4. Repair: stale files in the last commit

Commit `751e37b612` contained older copies of three files and silently undid about 3,000 lines of upstream work. That caused
11 TypeScript errors in `npm run dev`. Fixed by a three-way merge of current upstream and the earlier edits. **committed in 26fcd73a7d**

- `apps/desktop/electron/main.ts`, `apps/desktop/src/i18n/en.ts`, `apps/desktop/src/components/assistant-ui/thread/status.tsx`
- All 13 conflicts were resolved in favour of upstream's structure. Result: `tsc` passes for the Electron and renderer configs.
- Cost: the rename edits that sat in the conflicting blocks of `main.ts` (update dialogs) and `status.tsx` ("is working") were not carried over.

Before the next commit run `git diff --stat` and check that no unexpected large changes appear.

## 5. File card: Download button for local files

`apps/desktop/src/components/chat/preview-attachment.tsx` and its test. **committed in 26fcd73a7d, tests not run**

- For a file on the user's own computer the card now shows **Open containing folder**, **Download**, **Open preview**.
  Before, Download was hidden for local files on purpose (upstream issue #101683). Directory cards are unchanged.
- Test updated to expect the three buttons. The change has not been seen in the running app.

## 6. Hermes home configuration (local only: `<HERMES_HOME>\config.yaml`, not in the repo)

- `model_catalog.excluded_providers` (see section 1).
- `model.default` and `custom_providers[0].model`: changed from the placeholder `litellm` to `Pyrack Standard` (2026-10-12). Scheduled jobs use the default model, and `litellm` is not in the LiteLLM key's model list, so every run failed with HTTP 403 `key_model_access_denied`. The desktop showed that as "custom rejected your API key", which is misleading: the key itself is valid. Checked directly against LiteLLM: `litellm` returns 403, `Pyrack Standard` returns 200. Not yet re-run as an actual job. Backup: `config.yaml.bak-20261012-modeldefault`.
- **The app undid that fix on 2026-10-13 at 11:07.** It rewrote `config.yaml`: it added a second custom provider `0.0.0.0:4000` (key env `HERMES_CUSTOM_0_0_0_0_4000_API_KEY`, model `litellm`), pointed `model.base_url` and `model.api_key` at it, and set `model.default` back to `litellm`. A scheduled job then showed "model 'litellm' is not available" again. Restored the same day: `model.default: Pyrack Standard`, `base_url: http://localhost:4000`, key `HERMES_CUSTOM_LOCALHOST_4000_API_KEY`, and removed the duplicate provider (`Pyrack Pro Max` stays in the `litellm` provider's model list). Backup of the rewritten file: `config.yaml.bak-20261013-before-restore`. The `.env` entry for the `0.0.0.0` key was left in place. Not yet confirmed against LiteLLM (it was not reachable at the time) or by running the job.
- `display.file_mutation_verifier: false`: hides the warning that the agent appends when a file write failed. It also hides
  warnings about real failed writes.
- `SOUL.md` in the Hermes home: added a short "PDFs and reports" rule (load the `pdf` skill and build with `pdf_create.py`; do not write
  custom PDF code; render and look at the pages). **Applied, not yet verified**: the aim is to stop the Standard model writing its own
  ReportLab script (seen on the "Computer Networks guide" request: plain layout, blank pages, a pip-install approval prompt). Needs a
  rerun of that request to confirm. Backup kept in the scratchpad as `SOUL.md.bak`. The repo's shipped default soul is unchanged.

## 7. Development environment

- Node upgraded to 24.20.0 (npm 11.19.0). The project requires `^22.22.0 || ^24.11.0 || >=26` and npm `<11.10.0 || >=11.17.0`
  (`engine-strict=true` in `.npmrc`).
- `npm ci` from the repo root (the desktop dev run needs a full workspace install).
- Do not run two installs at once: it caused an `EPERM` error.
- The desktop dev run attached to an already-running backend (`hermes dashboard`, port 9119, release 2026.9.24, the installed copy under
  the Hermes home), which is older than the repo code the renderer runs.

## 8. Mermaid diagrams skill (new)

`skills/external_skills/mermaid-diagrams/` (`SKILL.md` and `references/diagram-types.md`). **committed in 26fcd73a7d, verified**

- Writes Mermaid diagrams in fenced `mermaid` blocks. Hermes Desktop already renders them (`mermaid-embed.tsx`, `mermaid` 11.16.1) and
  follows light/dark mode itself.
- Adapted from a pasted third-party skill. Changes: no fixed `theme: neutral` (it would force a light theme in dark mode; the theme is set
  only with `-t` when exporting a PNG), short description, repo section order, pointers to the existing `architecture-diagram`,
  `excalidraw` and `concept-diagrams` skills, a PNG export route for PDFs (`mermaid-cli`, then the `pdf` skill's `image` element), and the
  missing syntax reference written as `references/diagram-types.md`.
- Checks passed: all 11 Mermaid examples parse with the app's own `mermaid` library; `tests/skills/test_authoring_standards.py` passes
  for the whole repo (1492 tests, 7 for this skill). Not yet seen in a running chat.
- Provenance: the source skill had no licence or author. The frontmatter says `author: Ask Dealer` and `license: Unspecified`; confirm
  the origin and set the licence before shipping.

### Mermaid diagrams showed as a broken image (fixed 2026-10-12)

`apps/desktop/src/components/assistant-ui/embeds/mermaid-embed.tsx`. **committed in 26fcd73a7d, verified**

- Symptom: the chat showed a broken image with the alt text "Mermaid diagram". Cause: the diagram embed shows the SVG as a data-URI `<img>`, and Mermaid's default HTML labels put `<br>` and bare `&` inside `<foreignObject>`. That is not valid XML, so the browser refuses the image. Any label with `<br/>` triggered it (the agent writes these often).
- Fix: `htmlLabels: false` (top level and for flowcharts) so labels are plain SVG text.
- Checked in headless Chrome with the real diagram from the chat: broken before, loads after, line breaks and colours intact. New test in `mermaid-embed.test.tsx` fails without the fix and passes with it; the embeds folder and `svg-image` tests pass (47 tests).
- Not seen yet in the running desktop app (needs a renderer reload).

## 9. External skills added

All under `skills/external_skills/`. Picked up automatically via `skills.external_dirs` in `config.yaml`. **committed in 26fcd73a7d, authoring standards verified**

### `onepage` — HTML presentation pages
- Author: wjhuang88, MIT licence (kept in `LICENSE.txt` beside the skill).
- Produces a single self-contained `.html` file: hero + sticky nav + metric cards + architecture diagrams + comparison tables + milestone cards. No images or CDN needed — works offline and is shareable by email.
- Files: `SKILL.md`, `LICENSE.txt`, `assets/report-template.html` (base template with `{{PLACEHOLDERS}}`), `references/design-system.md`, `references/layout-reference.md`, `references/advanced-guide.md`.
- Triggered by: "one-page report", "shareable report", "presentation page", "executive report", "status dashboard" (via SOUL.md rule — see section 10).
- **Diagrams added (2026-10-12).** Reports came out as cards and text with no diagrams. New `references/diagram-snippets.md` holds six copy-paste visuals: process flow, flowchart with a decision, layered architecture, timeline, bar chart, donut chart. The skill now requires at least two visuals per report, built as plain HTML/CSS/inline SVG only (the in-app HTML preview strips scripts, so Mermaid and Chart.js cannot be used), and the SOUL.md one-page rule says the same. Verified: all six snippets rendered in headless Chrome from the shipped file and checked by eye; authoring standards pass (7 tests). Not yet seen from a real agent run in the app, so whether the agent follows the new rule is untested.

### `jupyter-notebook` — dropped (2026-10-12)
- Not used, so it was removed: the skill folder is gone from `external_skills/` and its SOUL.md rule is deleted. Data analysis now goes through the default `execute_code` tool. `optional-skills/data-science/jupyter-notebook/` is untouched if it is wanted later.

## 10. SOUL.md behaviour rules (local only: `<HERMES_HOME>\SOUL.md`)

Rules added to the SOUL.md in `C:\Users\SHREE\AppData\Local\hermes\SOUL.md`. Each takes effect immediately (SOUL.md is loaded fresh on every message — no restart needed).

| Rule | Trigger | Behaviour |
|---|---|---|
| PDF | "make a PDF / report" | Load `pdf` skill, use `pdf_create.py`, render and verify pages |
| Topic PDF images | Topic/informational PDF request | Download images from Wikimedia/Unsplash, embed via `image` element; matplotlib SVG fallback |
| Data PDF charts | Data PDF with visualisations | Generate matplotlib/seaborn charts as PNG first, embed; use Mermaid-CLI for flow diagrams |
| Report accuracy | Any report with numbers/comparisons | Re-verify every narrative claim against source data before finishing; silently fix wrong claims |
| Visual/infographic | "explain findings simply", "show visually" | Load `baoyu-infographic` skill (requires image_generate tool — not yet connected) |
| One-page report | "one-page report", "shareable report", "presentation page" | Load `onepage` skill, build from `assets/report-template.html`, output `.html` file |

Note: `baoyu-infographic` requires an image generation model connected to LiteLLM. Not yet set up — the rule is in place but will fail at the image generation step until an image model (DeepInfra, DALL-E 3, or similar) is added.

### Shipping the rules to other users (2026-10-13)

`hermes_cli/default_soul.py`, `tests/hermes_cli/test_default_soul_rules.py` (new). **uncommitted, verified**

- The rules above only lived in this machine's Hermes home, so a downloaded copy of the app would not have had them. `DEFAULT_SOUL_MD`, the template that is copied into a new user's `SOUL.md` on first run, now contains the same text as the live file: the persona paragraph plus the PDF, topic-PDF images, data-PDF charts, report accuracy, one-page report (with the two-diagrams requirement) and infographic rules.
- Existing installs: a `SOUL.md` still equal to the previous one-paragraph default (`_PERSONA_ONLY_SOUL`, added to the legacy list) is upgraded in place. Any `SOUL.md` a user has edited is left alone, so users who edited theirs do not get the rules.
- New tests: the old short default upgrades to the rules, an edited one is untouched, and every skill named in "load the `x` skill" exists under `skills/` (that last one would have caught the missing `jupyter-notebook`). The two upgrade/skills tests fail on the old template. With the existing SOUL tests: 7 passed.
- Not changed: `agent/prompt_builder.py`'s `DEFAULT_AGENT_IDENTITY` (the fallback when there is no SOUL.md) and the persona wording. The persona still says "Gideon, Acme Corp's" and needs the Ask Dealer rename.
- Caveat: the infographic rule sends the agent to `baoyu-infographic`, which needs an image generation key. Users without one will hit an error on that step.

### Two more SOUL.md rules (2026-10-14, live `SOUL.md` and `default_soul.py`)

**uncommitted. Not yet tried in the app; the test runner could not start here (no bootstrap Python), so only an import check was done.**

- "User choices": when a question has distinct options, use the `clarify` tool (option cards) instead of plain text. Aim: the Standard model asked in plain text (open item 2 below).
- Research cap in the topic-PDF paragraph: at most 3 web searches and 3 page extracts, then write the PDF. Aim: lower token use on PDF requests.
- Windows path rule, added to the "PDFs and reports" paragraph: use forward-slash paths (`C:/Users/...`), never put a Windows path inside `python -c`, and keep the spec, images and output in one scratch folder with relative filenames. Cause (from the chat history of the 2026-10-13 15:06 run): the agent wrote `C:\Users` inside `python -c` (`SyntaxError: truncated \UXXXXXXXX escape`) and ran `pdf_create.py` with a relative spec path from the wrong folder (`FileNotFoundError`). Each failed call re-sent the whole conversation, which is where the extra tokens went. `npx mermaid-cli` itself works (tested: 19s first run, valid PNG).
- Topic-PDF rule rewritten: Mermaid diagrams are now the main visual (at least two, rendered with the `npx mermaid-cli` command, matplotlib fallback after two failures). Web images (Wikimedia/Unsplash) are optional, tried once, never retried. Replaces "each section needs a web image; a topic PDF with no images is not acceptable". Reason: Mermaid export is tested and reliable (19s first run); web image downloads are not, and the retries cost tokens. Trade-off: less photographic richness.
- Per-call size rule, next to the research cap: `web_search` with `limit 4`, `web_extract` with `char_limit` no higher than 6000. The call-count cap alone did not shrink results: in the 2026-10-13 17:23 run the agent used `limit: 8` (20k chars) and `char_limit: 20000` (27k chars), and a `char_limit` passed by the agent overrides `web.extract_char_limit` in config, so the config setting alone would not have applied.
- Checked: `DEFAULT_SOUL_MD` imports, contains the new text, and its ASCII-dash variant is still recognised as a legacy template. The live file and the template are identical. Whether the model now follows the path, diagram and size rules is untested.

## 11. Local config additions (local only)

| Key | File | Value | Purpose |
|---|---|---|---|
| `skills.external_dirs` | `config.yaml` | `D:\hermes-agent\skills\external_skills` | Loads all skills in `external_skills/` without copying them |

## 12. Default model provider for new installs (2026-10-13)

`hermes_cli/config_defaults.py`. **uncommitted**

- `DEFAULT_CONFIG["model"]` now ships `Anshar Standard` on the LiteLLM provider at `192.168.0.114:4000/v1` instead of an empty string. Previously, a fresh install had no model and no provider — the user couldn't chat until they manually configured one.
- `DEFAULT_CONFIG["custom_providers"]` added: one entry (`litellm` at `192.168.0.114:4000/v1`, model `Anshar Standard`). The API key reads from `${HERMES_CUSTOM_192_168_0_114_4000_API_KEY}` (user sets it in `.env` or Settings after install).
- Effect: a new bundled install opens with `Anshar Standard` selected and the LiteLLM endpoint pre-configured. The user only needs to provide their API key.

## 13. Known open items

1. `model.default` is now `Pyrack Standard` (see section 6); confirm the `litellm` placeholder and extra `custom` row are gone from the picker after a restart.
2. The Standard model asks clarifying questions as plain text, not with the `clarify` tool's option cards (Pro does use them).
   Idea: one line in `SOUL.md` telling it to use the `clarify` tool.
3. Decide which backend ships: the repo code, or the installed copy (which lacks the shipped picker default).
4. Complete the "Ask Dealer" rename everywhere (line 1 of SOUL.md still says "Gideon, Acme Corp").
5. Run the project test runner (`scripts/run_tests.sh`) on the touched areas; checks so far used a scratch environment.
6. `26fcd73a7d` also swept in `workspace_pdf/` (14 generated PDFs, PNGs, HTML and JSON specs). Decide whether to keep those in the repo or remove them from tracking.
7. Mermaid skill: licence field says "Unspecified" — confirm origin and update.
8. Connect an image generation model to LiteLLM (DeepInfra recommended) to enable `baoyu-infographic` fully.
9. Not started: dealership data connectors (DMS/CRM), the dealer-reports skill, a scheduled daily report, hiding the JSON and
    narration rows in the chat (frontend), thinking-block styling and verbs (frontend).

## How to undo a local config change

Restore the backups kept in the session scratchpad (`config.yaml.bak`, `.bak2`, `.bak3`), or delete the added blocks from
`<HERMES_HOME>\config.yaml`. Repo changes are undone with `git checkout -- <file>` (uncommitted) or `git revert` (committed).
