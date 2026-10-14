# File changes — Ask Dealer customisation

A file-by-file record of what differs from upstream Hermes (base `dde8800ed9`), as of 2026-10-12. `CHANGES.md` says *what* was
done and why; this file says *which files* it touched. Updated whenever a file is added, changed or removed.

Commits: **A** = `751e37b612` ("Add Ask Dealer changes"), **B** = `26fcd73a7d` ("Update Hermes , skills and external skills", pushed to
`origin/ask-dealer-changes`). Status: committed, uncommitted, or local only (outside the repo).

## In the repo

### Model picker and setup
| File | Change | Commit |
|---|---|---|
| `hermes_cli/config_defaults.py` | `model_catalog.excluded_providers` shipped default (`openai-api`, `anthropic`, `gemini`, `openrouter`) | B |
| `tests/hermes_cli/test_picker_default_exclusions.py` (new) | Default reaches the picker; a user list replaces it | B |
| `hermes_cli/setup_profile.py` | Persona renamed to Ask Dealer; 10 deleted constants restored | A, B |
| `hermes_cli/default_soul.py`, `hermes_cli/doctor_state.py`, `agent/prompt_builder.py`, `SOUL.md` | Product name strings renamed ("Gideon") | A |
| `optional-skills/productivity/initiate-setup/SKILL.md` | "Welcome to Ask Dealer" | B |

### Desktop app (apps/desktop)
| File | Change | Commit |
|---|---|---|
| `electron/main.ts` | Three-way merge of upstream with earlier edits (about 3,000 lines); fixed 11 TypeScript errors | A, B |
| `src/i18n/en.ts` | Same merge repair (11 conflicts resolved to upstream's layout) | A, B |
| `src/components/assistant-ui/thread/status.tsx` | Repaired to upstream; no net change from base now | A, B |
| `src/i18n/en_app_tour.ts` | "Welcome to Ask Dealer" | B |
| `src/components/chat/preview-attachment.tsx` and `.test.tsx` | Local files show Open containing folder, Download and Open preview (test updated, not run) | B |
| `src/components/assistant-ui/embeds/mermaid-embed.tsx` and `.test.tsx` | `htmlLabels: false` so Mermaid diagrams with `<br/>` load as an image; new test fails without the fix | B |
| `electron/minimize-to-tray.ts`, `electron/notification-ipc.ts`, `electron/quit-guard.ts`, `index.html`, `src/main.tsx`, `src/components/chat/intro.tsx`, `src/app/capabilities/scope-selector.tsx`, `src/store/onboarding.ts`, `src/plugins/hermes-bots/labels.ts` | Visible "Hermes" text changed to "Gideon" | A |
| `product-identity.cjs` | App display names changed to Gideon; app id `com.nousresearch.*` to `com.acme.*` | A |
| `package.json`, `package-lock.json` (root) | Added `ws` and `@types/ws`; lockfile regenerated (225 lines). Reason not recorded | A |
| `src/plugins/hermes-bots/group-chat.ts` | 15-line change that includes logic, not only text. **Check:** it removed an upstream comment and fix about the bare `profile` key, so it may be an older copy | A |

### Skills
| File | Change | Commit |
|---|---|---|
| `skills/productivity/pdf/scripts/pdf_create.py` | Rewritten: themes, KPI cards, charts, bullets, callouts, wrapping tables, `--preview` | A |
| `skills/productivity/pdf/SKILL.md` | Version 2.0.0; required render-and-inspect step | A |
| `skills/productivity/pdf/templates/general_report.json`, `department_daily_report.json` (new) | Starter report specs (placeholder values) | A |
| `skills/productivity/pdf/tests/test_pdf_skill.py` | 3 tests added | A |
| `skills/external_skills/mermaid-diagrams/` (new: `SKILL.md`, `references/diagram-types.md`) | Mermaid diagram skill | B |
| `skills/external_skills/onepage/` (new: `SKILL.md`, `LICENSE.txt`, `assets/report-template.html`, `references/design-system.md`, `layout-reference.md`, `advanced-guide.md`) | One-page HTML report skill, MIT, author wjhuang88 | B |
| `skills/external_skills/onepage/SKILL.md` | Diagram Rules now require at least two visuals per report (inline SVG/HTML only); added an Images section; lists the snippets file as always-read | B (Images section), uncommitted (diagram rules) |
| `skills/external_skills/onepage/references/diagram-snippets.md` (new) | Six tested copy-paste visuals: process flow, flowchart, layered architecture, timeline, bar chart, donut chart | uncommitted |

### Other
| File | Change | Commit |
|---|---|---|
| `tests/e2e/core/parity/_drive_cron.py` | One-line rename | A |
| `CHANGES.md` (new) | Feature-level change log | B; later edits uncommitted |
| `FileChanges.md` (new, this file) | File-level change log | uncommitted |
| `workspace_pdf/` (14 files) | Generated PDFs, PNGs, HTML posters and JSON specs from agent test runs. Not code; undecided whether to keep tracked | B |

### Added 2026-10-13 (uncommitted)
| File | Change |
|---|---|
| `ask-dealer-config/config.example.yaml` (new) | Reference copy of the live `<HERMES_HOME>\config.yaml` with a header explaining the app does not read it. Contains no secrets, only `${HERMES_CUSTOM_LOCALHOST_4000_API_KEY}`. It is a snapshot, so it goes stale when the live file changes |

| `hermes_cli/default_soul.py` | `DEFAULT_SOUL_MD` now holds the persona plus all Ask Dealer rules (same text as the live `SOUL.md`); previous one-paragraph default kept as `_PERSONA_ONLY_SOUL` in the legacy-upgrade list | uncommitted |
| `hermes_cli/config_defaults.py` | `DEFAULT_CONFIG["model"]` ships `Anshar Standard` on `192.168.0.114:4000/v1`; `DEFAULT_CONFIG["custom_providers"]` added with one LiteLLM entry | uncommitted |
| `tests/hermes_cli/test_default_soul_rules.py` (new) | Old short default upgrades; edited default untouched; every skill named in the rules exists under `skills/` | uncommitted |

### Untracked, not committed
`nvidia_poster.html`, `nvidia_poster.png` (repo root): generated by the agent.

## Local only (outside the repo, on this machine)

| File | Change | Date |
|---|---|---|
| `<HERMES_HOME>\config.yaml` | Added `model_catalog.excluded_providers`, `display.file_mutation_verifier: false`, `skills.external_dirs`; `model.default` and `custom_providers[0].model` set to `Pyrack Standard` | 2026-10-08 to 10-12 |
| `<HERMES_HOME>\SOUL.md` | Added rules for PDFs, topic PDF images, data PDF charts, report accuracy, one-page reports (now requires at least two diagrams or charts), infographics (Jupyter rule added then removed) | 2026-10-09 to 10-12 |
| `<HERMES_HOME>\config.yaml` (again) | Rewritten by the app on 10-13 (duplicate `0.0.0.0:4000` provider, `model.default: litellm`); restored the same day to `Pyrack Standard` on `localhost:4000` and the duplicate provider removed | 2026-10-13 |
| `<HERMES_HOME>\config.yaml.bak-*` | Backups made before edits (`-modeldefault`, `-before-restore`) | various |

`<HERMES_HOME>` is `C:\Users\SHREE\AppData\Local\hermes`.

## Removed again
`skills/external_skills/jupyter-notebook/`: copied in and deleted on 2026-10-12 before any commit, so it never appears in git history.
