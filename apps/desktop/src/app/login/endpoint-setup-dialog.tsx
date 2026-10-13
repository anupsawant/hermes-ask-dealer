import { useEffect, useState } from 'react'

import { CustomEndpointsSettings } from '@/app/settings/custom-endpoints-settings'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { getCustomEndpoints } from '@/hermes'
import { useI18n } from '@/i18n'
import { dismissFirstRunOnboarding } from '@/store/onboarding'

interface EndpointSetupDialogProps {
  enabled: boolean
  onConfigSaved: () => void
  onMainModelChanged: (provider: string, model: string) => void
}

type SetupStatus = 'checking' | 'done' | 'open'

// First-run custom endpoint setup, raised after sign-in when the active
// profile has no custom endpoint yet. Closable: it returns on the next launch
// until an endpoint exists.
export function EndpointSetupDialog({ enabled, onConfigSaved, onMainModelChanged }: EndpointSetupDialogProps) {
  const { t } = useI18n()
  const copy = t.askDealer.endpointSetup
  const [status, setStatus] = useState<SetupStatus>('checking')

  useEffect(() => {
    if (!enabled || status !== 'checking') {
      return
    }

    let cancelled = false

    getCustomEndpoints().then(
      data => {
        if (cancelled) {
          return
        }

        if (data.endpoints.length) {
          setStatus('done')

          return
        }

        // This popup replaces the generic provider picker as the first-run
        // setup; the picker still opens if a send later hits a credential wall.
        dismissFirstRunOnboarding()
        setStatus('open')
      },
      // Backend not reachable yet: stay 'checking' and retry when the
      // gateway reconnects (enabled flips back to true).
      () => undefined
    )

    return () => {
      cancelled = true
    }
  }, [enabled, status])

  return (
    <Dialog onOpenChange={open => !open && setStatus('done')} open={status === 'open'}>
      <DialogContent bodyClassName="p-0" className="max-w-3xl">
        <DialogHeader className="px-5 pt-5">
          <DialogTitle>{copy.title}</DialogTitle>
          <DialogDescription>{copy.description}</DialogDescription>
        </DialogHeader>
        <CustomEndpointsSettings
          bare
          onConfigSaved={() => {
            onConfigSaved()
            setStatus('done')
          }}
          onMainModelChanged={onMainModelChanged}
        />
      </DialogContent>
    </Dialog>
  )
}
