# Ask Dealer — Google Login & Dealer Edition

Status: **Design approved (2026-10-09). Login UI built with a placeholder sign-in; Google OAuth not
yet wired.**
Scope: `apps/desktop` (the Electron app branded "Gideon").

### What exists today (placeholder stage)

- `src/app/login/login-screen.tsx` — full-window login screen. "Continue with Google" is **fake**: it
  sets `$signedIn` (`src/store/app-login.ts`, in-memory, so every launch starts at login) and
  navigates to the chat route. The real flow replaces `signIn()` with the IPC call in Part 2 §2.
- `src/app/login/endpoint-setup-dialog.tsx` — after sign-in, once the backend is up, if the active
  profile has **no custom endpoint**, the existing Custom Endpoints form opens in a popup. Saving
  closes it; closing it without saving brings it back next launch. It replaces the generic
  first-run provider picker.
- `src/app/login/ask-dealer-gate.tsx` — composes the two; mounted once in `src/app/contrib/wiring.tsx`.
- No edition switch and no hiding yet: Part 2 §1 and §4 are still to do.

This document has two parts:

- **Part 1 — How to set it up**: creating the Google OAuth client, building the dealer vs. full
  edition, and day-to-day operations.
- **Part 2 — Design spec**: what gets built, where, and how it is tested.

---

## Goal

Ship a simplified, branded desktop app to dealers/customers:

1. The app cannot be used until the person **signs in with Google** (any Google account is accepted;
   there is no server-side allowlist).
2. After sign-in the dealer sees **only chat and endpoint setup**. Every other Hermes area
   (Cron, Messaging, Capabilities, Agents, Profiles, Webhooks, Artifacts, Starmap, Command Center,
   Session import, most Settings) is hidden.
3. Configuring the AI endpoint (name, URL, API key, model) is **one step after login**, not three
   levels deep in Settings → Providers → Custom endpoints.

### Important caveat

The login gate and the hiding are **product experience, not security**. This is an open-source
desktop app: anyone technical can rebuild it with `HERMES_DESKTOP_EDITION=full` or inspect it. Do not
rely on the Google login to protect secrets or paid resources. If that becomes a requirement, the
check must move to a server you control (e.g. your endpoint/proxy verifies the Google ID token).

---

# Part 1 — How to set it up

## 1. Create the Google OAuth client (one time)

1. Open <https://console.cloud.google.com/> and create (or pick) a project, e.g. `ask-dealer`.
2. **APIs & Services → OAuth consent screen**
   - User type: **External** (dealers use their own Google accounts).
   - App name: `Gideon` (or the product name), support email, logo (optional), developer contact.
   - Scopes: add `openid`, `.../auth/userinfo.email`, `.../auth/userinfo.profile`. These are
     non-sensitive scopes, so no Google verification review is needed.
   - Publishing status: while **Testing**, only the listed test users (max 100) can sign in.
     Click **Publish app** before shipping to dealers.
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**.
   - Name: `Gideon Desktop`.
   - Copy the **Client ID** and **Client secret**.

> Why "Desktop app": Google allows desktop clients to use a loopback redirect
> (`http://127.0.0.1:<any port>`) without registering the port, which is what the app uses. Google
> documents that a desktop client's secret is **not confidential** — it ships inside the app; PKCE is
> what protects the flow.

## 2. Build-time configuration

All values are **build-time** (baked into the app); none are read from the dealer's machine.

| Variable | Values | Default | Purpose |
|---|---|---|---|
| `HERMES_DESKTOP_EDITION` | `dealer` \| `full` | `dealer` | `dealer` = login gate + hidden areas. `full` = original Hermes app (for your team's debugging). |
| `ASK_DEALER_GOOGLE_CLIENT_ID` | string | — (required for `dealer`) | Google OAuth Desktop client ID |
| `ASK_DEALER_GOOGLE_CLIENT_SECRET` | string | — (required for `dealer`) | Google OAuth Desktop client secret |

A `dealer` build **fails fast** if the client ID or secret is missing, so a broken login can never
ship.

### Local development

```powershell
# from apps/desktop
$env:ASK_DEALER_GOOGLE_CLIENT_ID = "xxxx.apps.googleusercontent.com"
$env:ASK_DEALER_GOOGLE_CLIENT_SECRET = "GOCSPX-..."
npm run dev                      # dealer edition (default)

$env:HERMES_DESKTOP_EDITION = "full"
npm run dev                      # full Hermes app, no login
```

### Release build

Set the same variables in CI (as secrets) and run the normal `npm run build` /
packaging flow (`apps/desktop/BUILDING.md`).

## 3. What the dealer experiences

1. Launch → **Login screen** → "Continue with Google".
2. The system browser opens Google sign-in. After consenting, the tab says
   "Signed in — you can close this tab" and the app comes forward.
3. First time only (no endpoint configured): **Connect your AI endpoint** screen — Name, URL,
   API key, Model, with **Test** and **Save & continue**. "Advanced" holds the rest.
4. Chat. The sidebar shows **+ New chat**, **⚙ Endpoint** (reopens the endpoint form) and sessions.
5. Next launches: signed in automatically. **Sign out** lives in Settings → Account and the sidebar
   footer.

## 4. Operations & troubleshooting

| Symptom | Cause / fix |
|---|---|
| "Access blocked" / only some users can sign in | Consent screen is still in **Testing** — publish it, or add the user as a test user. |
| Sign-in never returns to the app | A firewall/AV blocked `127.0.0.1`. The flow times out after 5 minutes and shows Retry. |
| "Session expired, sign in again" | Google rejected the refresh token (`invalid_grant`): the user revoked access, changed password, or the token aged out. Expected; they sign in again. |
| Works offline? | Yes, if they signed in successfully before: the cached identity is used and re-checked once online. A first-ever sign-in needs internet. |
| Two dealers share one PC | Chats and endpoints are stored per computer, not per Google account — they see each other's data. Supported setup is one PC per dealer. |

## 5. Showing or hiding an area later

Visibility is decided in **one place**: `apps/desktop/src/lib/edition.ts` (the dealer allow-lists
for routes, sidebar items, settings sections and command palette entries). To expose e.g. Artifacts
to dealers, add its route id to the dealer route allow-list and its sidebar id to the sidebar
allow-list; nothing else changes. The `full` edition ignores the allow-lists.

---

# Part 2 — Design spec

## Decisions (agreed)

| Topic | Decision |
|---|---|
| Audience | Dealers/customers; simplified branded app |
| Identity provider | Google only (OpenID Connect, Authorization Code + PKCE, loopback redirect) |
| Who may enter | Any Google account; no server-side check |
| Mechanism | Build-time **edition** switch (`dealer` default, `full` for dev) |
| Visible after login | Chat/sessions, endpoint setup, slim Settings (Endpoint, Appearance, Account, About) |
| Endpoint UX | Full-screen setup step after first login when none configured + top-level sidebar "Endpoint" entry |
| Endpoint form | Simple fields + collapsed "Advanced" |
| Session lifetime | Stay signed in (encrypted refresh token); offline grace with cached identity |
| Data separation | Per computer, not per Google account |

## Architecture

Follows the desktop seam rules (`apps/desktop/AGENTS.md`): **Electron main owns the OAuth flow and
tokens**; the renderer owns presentation and sees only the signed-in user's public profile.

```
┌──────────────── Electron main ────────────────┐      ┌──────────── Renderer ────────────┐
│ google-auth.ts                                 │      │ store/auth-session.ts ($authSession)
│  · PKCE + state, loopback server 127.0.0.1:0   │ IPC  │ app/login/  LoginScreen          │
│  · shell.openExternal(Google auth URL)         │◄────►│ App root gate (dealer edition)   │
│  · code→token exchange, ID-token verification  │      │ app/endpoint/ setup + page       │
│  · safeStorage-encrypted refresh token on disk │      │ lib/edition.ts allow-lists       │
│ google-auth-ipc.ts  (auth:* handlers)          │      └──────────────────────────────────┘
│ preload.ts → hermesDesktop.auth.{getSession,   │
│              signIn, cancel, signOut,          │
│              onChange}                         │
└────────────────────────────────────────────────┘
```

### 1. Edition switch

- `apps/desktop/product-identity.cjs` gains `edition: 'dealer' | 'full'` derived from
  `HERMES_DESKTOP_EDITION` (validated like `HERMES_DESKTOP_VARIANT`; unknown value → build error).
  `product-identity.d.cts` is updated to match. Default: `dealer`.
- Main process: read via the existing `PRODUCT_IDENTITY` (`electron/product-identity.ts`, baked by
  `scripts/bundle-electron-main.mjs`).
- Renderer: `vite.config.ts` adds `define: { __DESKTOP_EDITION__: JSON.stringify(identity.edition) }`
  reading the same `.cjs` (single derivation).
- `src/lib/edition.ts` is the **only** place the renderer branches on edition:
  `isDealerEdition()`, plus the dealer allow-lists (route ids, sidebar nav ids, settings sections,
  command-palette/slash filter).
- Google client ID/secret are baked into the main bundle only (never the renderer) from
  `ASK_DEALER_GOOGLE_CLIENT_ID/SECRET`; a `dealer` build without them fails.

### 2. Google sign-in — `electron/google-auth.ts`

Endpoints: auth `https://accounts.google.com/o/oauth2/v2/auth`, token
`https://oauth2.googleapis.com/token`, keys `https://www.googleapis.com/oauth2/v3/certs`, revoke
`https://oauth2.googleapis.com/revoke`.

**Sign in**
1. Generate PKCE `code_verifier` (43–128 chars) + `S256` challenge, and a random `state`.
2. Start an HTTP server on `127.0.0.1:0` (random free port); `redirect_uri =
   http://127.0.0.1:<port>/callback`.
3. `shell.openExternal(authUrl)` with `response_type=code`, `scope=openid email profile`,
   `access_type=offline`, `prompt=select_account consent` (guarantees a refresh token), PKCE params,
   `state`.
4. Callback: reject if `state` mismatches or `error` is present; respond with a small "Signed in —
   you can close this tab" (or error) page; close the server; focus the app window.
5. Exchange the code (with `client_secret` + `code_verifier`).
6. Verify the ID token: RS256 signature against Google's JWKS (cached by `kid`), `iss` ∈
   {`accounts.google.com`, `https://accounts.google.com`}, `aud` = client ID, `exp` in the future
   (small clock-skew allowance), `email_verified` true.
7. Persist `{refresh_token, user: {sub, email, name, picture}, verified_at}` to
   `<userData>/ask-dealer-auth.bin`, encrypted with `safeStorage.encryptString`. If
   `safeStorage.isEncryptionAvailable()` is false, keep the session in memory only (user signs in
   each launch) — never write the token in plaintext.
8. Timeout: 5 minutes, or `cancel()` → close server, status `signed_out`.
   Only one sign-in can run at a time; a second `signIn()` returns the in-flight one.

**Launch (`getSession`)**
- No stored file → `signed_out`.
- Stored file → refresh using the refresh token:
  - success → verify the new ID token → `signed_in`.
  - `invalid_grant` → delete the file → `signed_out` with reason `expired`.
  - network failure → `signed_in` with `offline: true` using the cached user (offline grace);
    retry refresh when connectivity returns / on next window focus.
- Access tokens are never persisted and never sent to the renderer; the app only needs identity.

**Sign out**: best-effort POST to the revoke endpoint, delete the file, status `signed_out`.

**IPC** — `electron/google-auth-ipc.ts`, exposed through `electron/preload.ts` as
`hermesDesktop.auth`:

| Call | Returns |
|---|---|
| `getSession()` | `AuthSession` |
| `signIn()` | `AuthSession` (resolves when the flow ends) |
| `cancel()` | `void` |
| `signOut()` | `void` |
| `onChange(cb)` | unsubscribe fn; pushes `AuthSession` on every transition |

```ts
type AuthSession =
  | { status: 'signed_out'; reason?: 'expired' | 'cancelled' | 'timeout' }
  | { status: 'signing_in' }
  | { status: 'signed_in'; user: { email: string; name: string; picture?: string }; offline?: boolean }
  | { status: 'error'; message: string }
```

The handlers are registered only in the `dealer` edition.

### 3. Login gate — renderer

- `src/store/auth-session.ts`: `$authSession` atom (initially `{status: 'checking'}`), seeded by
  `getSession()` and kept current by `onChange`. Actions `signIn`, `cancelSignIn`, `signOut`.
- `src/app/login/login-screen.tsx`: logo + product name, **Continue with Google**; `signing_in`
  shows "Finish signing in in your browser" + Cancel; `error`/`expired`/`timeout` show copy + Retry.
  Follows `apps/desktop/DESIGN.md`.
- App root (`src/app/index.tsx`): in the dealer edition render only `LoginScreen` (or a neutral
  splash while `checking`) until `signed_in`. The backend still boots in parallel, so chat is ready
  right after login. Full edition: no gate.
- Sign out: Settings → Account (shows avatar, name, email, Sign out) and the sidebar footer menu.
  After sign out the app returns to `LoginScreen`; local chats are **not** deleted.

### 4. Hiding — dealer edition only

- **Routes** (`src/app/routes.ts`): the route table is filtered through the dealer allow-list:
  `new` + session routes, `settings`, new `endpoint`. All others are not registered, so deep links,
  the command palette and keyboard shortcuts cannot reach them.
- **Sidebar**: only allow-listed nav entries (`SIDEBAR_NAV_AREA` contributions included); adds
  **⚙ Endpoint**; hides profile/connection switchers and fleet rail.
- **Settings** (`src/app/settings/index.tsx`): sections Endpoint, Appearance, Account, About only;
  the "Applies to" profile scope selector is hidden.
- **Command palette / slash**: filtered to chat-relevant commands
  (`src/lib/desktop-slash-commands.ts` stays the source; the dealer filter layers on top).
- **Onboarding**: the provider-picker overlay (`src/store/onboarding.ts`) is suppressed; the endpoint
  setup step replaces it.
- The full edition is byte-for-byte the current behaviour.

### 5. Endpoint setup

- Refactor `src/app/settings/custom-endpoints-settings.tsx` into:
  - `use-custom-endpoints.ts` — load/save/validate/activate/delete + stale-response guards (the
    existing logic moved, unchanged).
  - `endpoint-form.tsx` — the form, with a `variant: 'full' | 'simple'` prop.
  - `custom-endpoints-settings.tsx` — same page as today (`variant="full"`), so the full edition is
    unchanged.
- **Simple variant fields**: Name, Endpoint URL, API key, Model (combobox populated by **Test**).
  **Advanced** (collapsed): Provider ID, API mode (default Auto-detect), Context length,
  "Use for new chats" (default on), "Discover models" (default on).
- `src/app/endpoint/endpoint-setup-screen.tsx` — full-screen first-run step, shown after login when
  there is no endpoint marked current. **Save & continue** saves (make default) then routes to new
  chat. No skip.
- `src/app/endpoint/endpoint-page.tsx` — `/endpoint` route: saved endpoints list (Use / Delete) +
  the simple form. Also listed as the first Settings section in the dealer edition.
- Backend API unchanged: `/api/providers/custom-endpoints*` (`src/api/config.ts`).

### 6. Strings

New copy goes in `src/i18n/en.ts` (`login.*`, `endpointSetup.*`, `settings.account.*`). Other locales
are `defineLocale` overlays and fall back to English.

### 7. Error handling summary

| Situation | Behaviour |
|---|---|
| Browser closed / user abandons | 5-minute timeout → Login screen with Retry |
| `state` mismatch / `error=access_denied` | Flow aborted, error shown, nothing stored |
| ID token fails verification | Treated as sign-in failure; nothing stored |
| Port bind fails | Error with Retry (new random port each attempt) |
| Refresh `invalid_grant` | Stored session deleted → Login with "session expired" |
| Offline at launch with stored session | Signed in with cached identity (`offline`), re-check later |
| `safeStorage` unavailable | Session kept in memory only; sign in each launch |
| Endpoint Test fails | Existing warning/error toasts; Save still possible |

### 8. Testing

Vitest (run from `apps/desktop`, `npx vitest run <file>`):

- `electron/google-auth.test.ts`: PKCE verifier/challenge pair; `state` mismatch rejected; ID-token
  verification with a locally generated RSA key/JWKS (bad `aud`, bad `iss`, expired, unverified
  email all rejected); refresh `invalid_grant` → `signed_out` + file deleted; network error →
  offline grace; concurrent `signIn` returns the in-flight flow; timeout.
- `src/store/auth-session.test.ts`: transitions driven by `onChange`.
- `src/lib/edition.test.ts`: dealer allow-lists — hidden route ids are unreachable; full edition
  unfiltered.
- `src/app/endpoint/*.test.tsx`: simple variant hides Advanced by default with the agreed defaults;
  setup screen shown only when no current endpoint; Save & continue navigates to chat.
- Existing `custom-endpoints-settings.test.tsx` keeps passing unchanged (full edition parity).

### Files touched (summary)

New: `electron/google-auth.ts`, `electron/google-auth-ipc.ts`, `src/lib/edition.ts`,
`src/store/auth-session.ts`, `src/app/login/*`, `src/app/endpoint/*`,
`src/app/settings/account-settings.tsx`, `src/app/settings/endpoint-form.tsx`,
`src/app/settings/use-custom-endpoints.ts`, tests for each.

Modified: `product-identity.cjs`, `product-identity.d.cts`, `scripts/bundle-electron-main.mjs`,
`vite.config.ts`, `electron/main.ts` (register auth IPC in dealer edition), `electron/preload.ts`,
`src/app/index.tsx`, `src/app/routes.ts`, sidebar (`src/app/chat/sidebar/`), `src/app/settings/index.tsx`,
`src/app/settings/custom-endpoints-settings.tsx`, `src/store/onboarding.ts`, `src/i18n/en.ts`.
