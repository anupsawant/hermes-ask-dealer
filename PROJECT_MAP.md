# PROJECT_MAP.md

Working notes for Claude Code: what this checkout is, where it currently stands, and the traps already hit. `CLAUDE.md` has commands and architecture; this file has state and orientation. Update it when the state below changes. Last verified: 2026-10-12 against the working tree on branch `ask-dealer-changes`.

## 1. What this checkout is

- A fork of Nous Research's hermes-agent, rebranded for Acme Corp as **Gideon** ("Ask Dealer"). Everything user-facing says Gideon; internals (`hermes_*` modules, `HERMES_*` env vars, the `hermes` CLI, `hermes serve`) keep upstream names on purpose.
- Fork commit: `751e37b612` "Add Ask Dealer changes" on top of upstream `dde8800ed9`. `HEAD~1` is clean upstream, so `git diff HEAD~1 -- <file>` shows exactly what the fork changed in any file.
- The product being built is the **desktop app** (`apps/desktop`, Electron + React). Almost all current work is there. The Python agent/gateway/TUI are upstream code the desktop spawns as `hermes serve`.
- Branding sources: `apps/desktop/product-identity.cjs` (names, appId `com.acme.*`), `agent/prompt_builder.py` `DEFAULT_AGENT_IDENTITY`, `hermes_cli/default_soul.py`, `SOUL.md`. Not rebranded yet: the Store MSIX identity in `product-identity.cjs` (`NousResearchInc.HermesAgent`, `msixAppIdWithOrg: NousResearch.*`).

## 2. Current work: Google login + dealer edition

Design spec: `ASK_DEALER_LOGIN.md` (root). Goal: dealers must sign in with Google, then see only chat plus a simple custom-endpoint setup; everything else hidden. Spec says login/hiding is product UX, not security.

Built so far (placeholder stage, uncommitted):
- `apps/desktop/src/app/login/` — `login-screen.tsx`, `endpoint-setup-dialog.tsx`, `ask-dealer-gate.tsx` (+ test), mounted once in `src/app/contrib/wiring.tsx`.
- `src/store/app-login.ts` — in-memory `$signedIn`; "Continue with Google" is fake, so every launch starts at login.
- `src/app/settings/custom-endpoints-settings.tsx` — small edit so the existing Custom Endpoints form can open in the post-login popup.

Not built yet (per the spec): real OAuth in Electron main (`electron/google-auth.ts` + IPC + preload), the `edition` switch in `product-identity.cjs`/`vite.config.ts`, `src/lib/edition.ts` allow-lists that hide routes/sidebar/settings, Account section with sign-out.

## 3. State of the working tree (traps already hit)

- **`electron/main.ts` was restored from `HEAD~1`.** The fork commit had replaced it with a different upstream revision (19,231 lines vs 19,786) that no longer matched its sibling modules: 11 `tsc` errors (missing `./chat-onboarding-window`, `describeGitSpawnFailure`, `openLocalPath`, `sshBinary`, ...). Now it is `HEAD~1` plus four `title: 'Hermes'` -> `title: APP_NAME` edits (window titles; `APP_NAME` derives from product identity). `tsc --build tsconfig.electron.json` passes. About 15 user-facing "Hermes" strings in it are not renamed yet (e.g. "Waiting to start Hermes backend"). Rule: rebrand by editing strings on top of the current upstream file; never paste in a whole file from another revision.
- **`ws` and `@types/ws` are declared in `apps/desktop/package.json` and in `package-lock.json` but were not installed** (not in root `node_modules`). `assert-root-install.mjs` refuses `npm run dev`/`build` when any declared dependency is missing. Fix is `npm ci` at the repo root; it needs to be run by the user (`! npm ci` in the prompt) because the auto-mode classifier blocks it as destructive.
- Other sessions: a second Claude session (`desktop-9b`) works in the same tree. It reported restoring `src/i18n/en.ts`, `status.tsx`, `src/plugins/hermes-bots/group-chat.ts` (+ test) to `HEAD~1` with Gideon renames, renaming "Hermes" in the `en_*.ts` modules, and adding an `askDealer` key block to all locales. Check `git status` and ask via SendMessage before editing files it owns.
- `package-lock.json` has uncommitted modifications; do not regenerate it casually.

## 4. Desktop orientation (where to look)

| Need | Look at |
|---|---|
| Electron main process | `apps/desktop/electron/main.ts` (~19.8k lines, monolith) plus many sibling modules, each with a `.test.ts`: `backend-*` (spawn/pool/health), `bootstrap-*`, `external-open.ts`, `terminal-ipc.ts`, `preload.ts` |
| Renderer shell | `src/main.tsx` -> `src/app/index.tsx`; routes in `src/app/routes.ts`; feature areas are folders under `src/app/` |
| Global renderer state | `src/store/*.ts` (nanostores; one concern per file) |
| Extension mount points | `src/app/contrib/wiring.tsx` (where the login gate is mounted), `src/plugins/` (e.g. `hermes-bots`) |
| Strings | `src/i18n/en.ts` (+ `en_*.ts` split modules, one file per other locale, `types.ts`); `locales/_keys.desktop.json` is pinned to `en.ts` |
| Backend RPC | `src/hermes.ts`, `src/api/`, transport in `apps/shared` |
| Settings pages | `src/app/settings/` (custom endpoints form lives here) |
| Build/pack scripts | `apps/desktop/scripts/`, config `electron-builder.config.cjs`, `BUILDING.md` |
| Rules for desktop work | `apps/desktop/AGENTS.md`, `src/AGENTS.md`, `DESIGN.md`, `ENGINEERING.md` |

Dev loop: `npm run dev` (from `apps/desktop`) = Vite renderer on `127.0.0.1:5174` + Electron. `npm run dev:electron` alone type-checks Electron then waits for 5174 forever if the renderer isn't up. Verify changes with `npm run typecheck` and `npx vitest run <file>`.

## 5. Environment notes

- Windows 11, PowerShell primary, Git Bash available. Node 24, npm 11. Run Python tests through Bash (`scripts/run_tests.sh`).
- Python side is not set up in this session (no `.venv` verified). The desktop spawns a `hermes serve` backend; I have not yet checked that a runtime is available here. `npm run dev:fake-boot` (sets `HERMES_DESKTOP_BOOT_FAKE=1`) fakes the boot sequence, but I have not confirmed how far it gets without a backend.
