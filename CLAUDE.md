# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A fork of Nous Research's [hermes-agent](https://github.com/NousResearch/hermes-agent) (Python agent core + CLI, messaging gateway, Ink TUI, Electron desktop app, dashboard SPA), rebranded as **Gideon, Acme Corp's private AI assistant** ("Ask Dealer" branch). The fork's own changes sit on top of upstream: commit `751e37b612` (parent `dde8800ed9` is clean upstream) rebrands identity strings (`SOUL.md`, `agent/prompt_builder.py` `DEFAULT_AGENT_IDENTITY`, `hermes_cli/default_soul.py`, `apps/desktop/product-identity.cjs`, `en.ts`, window titles) and reworks the PDF skill (`skills/productivity/pdf/`). Python modules, CLI commands, env vars (`HERMES_*`) and the `hermes` binary keep their upstream names. Rebrand only user-facing identity, never internal identifiers.

The commit touches ~27 files, more than the ones named above (tray/quit/notification modules, `index.html`, `src/main.tsx`, `store/onboarding.ts`, `package.json`, ...). `git show --stat 751e37b612` is the list that will conflict on an upstream merge; `git diff 751e37b612~1 -- <file>` shows what the fork changed in any one file.

Rebrand by editing strings on top of the current upstream file; never paste in a whole file from another revision. That commit's `apps/desktop/electron/main.ts` is a different upstream revision (~3,000 changed lines) that PROJECT_MAP.md reports no longer typechecks against its sibling modules, so the working tree restores `751e37b612~1`'s copy plus `APP_NAME` title edits.

Current state of the fork, in-progress work and known traps: @PROJECT_MAP.md

Design spec for the in-progress Google login / dealer edition (build-time `HERMES_DESKTOP_EDITION` switch, allow-listed routes, endpoint setup): `ASK_DEALER_LOGIN.md`. Deliberately not imported; read it when touching login, edition gating or `src/app/login/`. Its Part 2 is a design: only the placeholder UI exists so far (see PROJECT_MAP.md §2).

## Read the area guides first

`AGENTS.md` at the root is the authoritative rule set (prompt-caching invariant, facade + sibling file layout, profile-scope rules, no hardcoded `~/.hermes`, complexity ratchets). Each area has its own `AGENTS.md` that must be read before editing there. Routing table is in the root file. For desktop work: `apps/desktop/AGENTS.md`, `apps/desktop/src/AGENTS.md`, `apps/desktop/DESIGN.md`, `apps/desktop/ENGINEERING.md`. Do not duplicate their content here.

## Commands

### Python (repo root)

```bash
source ./activate              # PowerShell: ./activate.ps1; provisions the PM-managed env. Set an isolated HERMES_HOME first
python scripts/check           # every blocking lint check CI runs (ruff + code-health ratchet + guards)
python scripts/check --only health
scripts/run_tests.sh                       # canonical test runner; on Windows run it through Bash
scripts/run_tests.sh tests/agent/ -v       # a directory
scripts/run_tests.sh tests/hermes_cli/test_desktop_slash_registry.py   # one file
```

Never run bare `pytest`: the runner isolates `HERMES_HOME`, clears credentials and runs each test file in its own subprocess. It needs a test env: `python -m pm.build_env --source . --out .venv --group dev --group test` (or set `HERMES_PYTHON`). Never mutate a Hermes environment with raw pip/uv; after editing `pyproject.toml` run `hermes pm lock` and commit `uv.lock`.

### JavaScript workspaces

Root `package.json` is an npm workspace (`apps/*`, `ui-tui`, `ui-tui/packages/*`, `web`, `tests-js`). Install once from the repo root (`npm ci`); `apps/desktop/scripts/assert-root-install.mjs` fails dev/build if the workspace wasn't installed at the root.

From `apps/desktop`:

```bash
npm run dev                    # Vite on :5174 + Electron against it (dev:fake-boot fakes the boot sequence)
npm run typecheck              # tsc for renderer, electron and e2e projects + electron-builder config
npm run lint / npm run fix     # eslint (+ prettier via `fmt`) over src/ and electron/
npm run check:lint             # typecheck + lint, the quick gate
npm run test:ui                # vitest "ui" project (jsdom, src/**/*.test.{ts,tsx})
npm run test:desktop:platforms # vitest "electron" project (node: electron/, scripts/, e2e/*.unit.test.ts)
npx vitest run src/lib/desktop-slash-commands.test.ts     # a single test file
npx vitest run -t "name fragment"                         # filter by test name
npm run check                  # check:lint + test:ui + test:desktop:platforms + test:desktop:all
npm run test:e2e               # builds, then Playwright specs in e2e/ (visual variants need `cage` on Linux)
npm run build / pack / dist    # compile; package current build; installer. Release bundles: apps/desktop/BUILDING.md
npm run dist:bundled           # bundled variant: stages the Python payload (repo-root scripts/bundles/) then packages
```

CI runs each `check:*` script as its own unit (`.github/scripts/run-workspace-checks.mjs`). `test:desktop:all` (so `npm run check`) first builds the packaged app, which on Windows means a full `dist:win:msix`, unless `HERMES_DESKTOP_SKIP_BUILD=1` and an MSIX already exists. For the local loop run `check:lint`, `test:ui` and `test:desktop:platforms` separately.

`npm run i18n:keys` regenerates the committed, repo-root `locales/_keys.desktop.json` (`--check` verifies; `i18n-keys.test.mjs` pins it to `src/i18n/en.ts`); `hermes plugins validate` uses it to check language packs. Strings: `src/i18n/en.ts` (+ `en_*.ts` split modules) is the source and `types.ts` / `types_*.ts` the type contract. The other locales are `defineLocale` overlays that fall back to English for missing keys, so a new key compiles and renders without them. `apps/desktop/AGENTS.md` still asks for all locales to be updated, and `catalog-completeness.test.ts` only enforces the `updates` copy in fr/de/es.

## Architecture (the parts that span files)

- **One agent core, many surfaces.** `run_agent.py` (`AIAgent` facade, turn loop in `agent/turn_*.py`) is shared by `cli.py`, `gateway/` (messaging platforms), `tui_gateway/` (JSON-RPC backend for the Ink TUI in `ui-tui/` and for Desktop), and `cron/`. Capability is added at the edges (plugins, skills, service-gated tools), not by growing core tool surface.
- **Desktop is three parties.** Electron main (`apps/desktop/electron/`: process lifecycle, backend spawn/pool, updater, IPC through `preload.ts`), the React renderer (`src/`: nanostores + assistant-ui, routes in `src/app`, state in `src/store`, pure helpers in `src/lib`), and a headless `hermes serve` backend per (connection, profile) that the renderer reaches by JSON-RPC (`requestGateway`, transport in `apps/shared`). The renderer never touches Node/Electron directly. State lives with its authority (backend > Electron > renderer).
- **Slash commands:** the desktop disposition of each command is declared once on its `CommandDef` in `hermes_cli/commands.py`; `src/lib/desktop-slash-registry.json` is generated by `scripts/dump_desktop_slash_registry.py` and drift fails both a pytest and a vitest.
- **Packaging identity** comes from one place, `apps/desktop/product-identity.cjs` (variants `''`, `light`, `bundled`, `store`, selected by `HERMES_DESKTOP_VARIANT`), consumed by `electron-builder.config.cjs`. Bundled builds ship a staged Python payload (`scripts/bundles/`); see `BUILDING.md`.
- **Facade + siblings:** big modules (`hermes_state.py`, `gateway/run.py`, `cli.py`, `tools/mcp_tool.py`, ...) are thin facades with `<stem>_<topic>.py` siblings. Find code with `grep -rn "def name" <dir>/<stem>_*.py`. Complexity and file-size ratchets are enforced by `scripts/check`.
- **Profiles:** one process can serve many profiles; code outside a turn must bind profile scope explicitly (`gateway/AGENTS.md` § Profile scope). Use `get_hermes_home()` / `display_hermes_home()`, never a literal `~/.hermes`.

## Conventions worth knowing before a first edit

- Tests assert behavior, not snapshots or source text; fixes ship with 1-2 invariant tests proven red on the base. Tests never write to `~/.hermes/`.
- Non-secret config goes in `config.yaml`, not new `HERMES_*` env vars; `.env` is secrets only.
- Dependencies need upper bounds (`>=floor,<next_major`); Actions and git URLs pin to a SHA.
- `# noqa` does not waive a code-health finding; `# health: allow <RULE> -- <why>` does.
