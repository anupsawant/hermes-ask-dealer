import { useStore } from '@nanostores/react'

import { $signedIn } from '@/store/app-login'

import { EndpointSetupDialog } from './endpoint-setup-dialog'
import { LoginScreen } from './login-screen'

interface AskDealerGateProps {
  /** True once the gateway is open — the endpoint check needs the backend. */
  enabled: boolean
  onConfigSaved: () => void
  onMainModelChanged: (provider: string, model: string) => void
}

// Sign-in first, then the first-run endpoint setup.
export function AskDealerGate({ enabled, onConfigSaved, onMainModelChanged }: AskDealerGateProps) {
  const signedIn = useStore($signedIn)

  if (!signedIn) {
    return <LoginScreen />
  }

  return <EndpointSetupDialog enabled={enabled} onConfigSaved={onConfigSaved} onMainModelChanged={onMainModelChanged} />
}
