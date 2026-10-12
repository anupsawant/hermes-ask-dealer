import { atom } from 'nanostores'

// Ask Dealer sign-in gate. Placeholder until the Google OAuth flow in
// ASK_DEALER_LOGIN.md lands: "Continue with Google" signs in immediately.
// Session-only on purpose — every launch starts at the login screen.
export const $signedIn = atom(false)

export function signIn() {
  $signedIn.set(true)
}
