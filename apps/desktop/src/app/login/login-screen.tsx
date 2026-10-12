import { useNavigate } from 'react-router'

import { NEW_CHAT_ROUTE } from '@/app/routes'
import { Button } from '@/components/ui/button'
import { useI18n } from '@/i18n'
import { signIn } from '@/store/app-login'

const assetPath = (path: string) => `${import.meta.env.BASE_URL}${path.replace(/^\/+/, '')}`

function GoogleMark() {
  return (
    <svg aria-hidden className="size-4" viewBox="0 0 48 48">
      <path
        d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"
        fill="#FFC107"
      />
      <path
        d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"
        fill="#FF3D00"
      />
      <path
        d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"
        fill="#4CAF50"
      />
      <path
        d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"
        fill="#1976D2"
      />
    </svg>
  )
}

// Full-window sign-in gate. The shell keeps mounting underneath so the backend
// boots while the dealer signs in; this screen only masks it.
export function LoginScreen() {
  const { t } = useI18n()
  const copy = t.askDealer.login
  const navigate = useNavigate()

  function handleSignIn() {
    signIn()
    navigate(NEW_CHAT_ROUTE)
  }

  return (
    <div
      className="fixed inset-0 z-(--z-setup) flex items-center justify-center bg-(--ui-chat-surface-background) p-6"
      // Masks the whole app — must stay filled under window glass. Contract:
      // `[data-glass-opaque]` in styles.css.
      data-glass-opaque=""
    >
      {/* The shell's titlebar is covered, so keep the window draggable. */}
      <div className="absolute inset-x-0 top-0 h-10 [-webkit-app-region:drag]" />
      <div className="grid w-full max-w-sm justify-items-center gap-6 rounded-xl border border-(--stroke-nous) bg-(--ui-chat-bubble-background) px-8 py-10 shadow-nous">
        <img alt="" className="size-14 rounded-xl" src={assetPath('apple-touch-icon.png')} />
        <div className="grid gap-1.5 text-center">
          <h1 className="text-lg font-semibold text-(--ui-text-primary)">{copy.title}</h1>
          <p className="text-sm text-(--ui-text-secondary)">{copy.subtitle}</p>
        </div>
        <Button autoFocus className="w-full" onClick={handleSignIn} size="lg" variant="outline">
          <GoogleMark />
          {copy.continueWithGoogle}
        </Button>
      </div>
    </div>
  )
}
