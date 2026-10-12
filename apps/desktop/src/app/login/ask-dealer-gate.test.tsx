// @vitest-environment jsdom
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { CustomEndpointsResponse } from '@/types/hermes'

const getCustomEndpoints = vi.fn<() => Promise<CustomEndpointsResponse>>()
const dismissFirstRunOnboarding = vi.fn()

vi.mock('@/hermes', async importOriginal => ({
  ...(await importOriginal<Record<string, unknown>>()),
  getCustomEndpoints: () => getCustomEndpoints()
}))
vi.mock('@/store/onboarding', () => ({ dismissFirstRunOnboarding: () => dismissFirstRunOnboarding() }))
vi.mock('@/app/settings/custom-endpoints-settings', () => ({
  CustomEndpointsSettings: ({ onConfigSaved }: { onConfigSaved: () => void }) => (
    <button onClick={onConfigSaved} type="button">
      stub-save-endpoint
    </button>
  )
}))

const { AskDealerGate } = await import('./ask-dealer-gate')
const { $signedIn } = await import('@/store/app-login')

const NO_ENDPOINTS: CustomEndpointsResponse = { current: { base_url: '', model: '', provider: '' }, endpoints: [] }

const ONE_ENDPOINT: CustomEndpointsResponse = {
  current: { base_url: 'http://a.test/v1', model: 'm', provider: 'a' },
  endpoints: [
    {
      base_url: 'http://a.test/v1',
      discover_models: true,
      has_api_key: true,
      id: 'a',
      is_current: true,
      model: 'm',
      models: ['m'],
      name: 'A'
    }
  ]
}

function Location() {
  return <output data-testid="location">{useLocation().pathname}</output>
}

function renderGate({ enabled = true, path = '/settings' } = {}) {
  const onConfigSaved = vi.fn()

  render(
    <MemoryRouter initialEntries={[path]}>
      <AskDealerGate enabled={enabled} onConfigSaved={onConfigSaved} onMainModelChanged={vi.fn()} />
      <Location />
    </MemoryRouter>
  )

  return { onConfigSaved }
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  $signedIn.set(false)
})

describe('AskDealerGate', () => {
  it('shows the login screen until sign-in, then lands on the chat route', () => {
    getCustomEndpoints.mockResolvedValue(ONE_ENDPOINT)
    renderGate()

    fireEvent.click(screen.getByRole('button', { name: 'Continue with Google' }))

    expect($signedIn.get()).toBe(true)
    expect(screen.queryByRole('button', { name: 'Continue with Google' })).toBeNull()
    expect(screen.getByTestId('location').textContent).toBe('/')
  })

  it('does not check endpoints before sign-in', () => {
    renderGate()

    expect(getCustomEndpoints).not.toHaveBeenCalled()
  })

  it('opens the endpoint setup popup after sign-in when no endpoint exists', async () => {
    getCustomEndpoints.mockResolvedValue(NO_ENDPOINTS)
    $signedIn.set(true)
    const { onConfigSaved } = renderGate()

    expect(await screen.findByText('Connect your AI endpoint')).toBeTruthy()
    // The popup replaces the generic first-run provider picker.
    expect(dismissFirstRunOnboarding).toHaveBeenCalledTimes(1)

    fireEvent.click(screen.getByRole('button', { name: 'stub-save-endpoint' }))

    expect(onConfigSaved).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(screen.queryByText('Connect your AI endpoint')).toBeNull())
  })

  it('stays closed when an endpoint already exists', async () => {
    getCustomEndpoints.mockResolvedValue(ONE_ENDPOINT)
    $signedIn.set(true)
    renderGate()

    await waitFor(() => expect(getCustomEndpoints).toHaveBeenCalledTimes(1))
    await act(async () => {})

    expect(screen.queryByText('Connect your AI endpoint')).toBeNull()
    expect(dismissFirstRunOnboarding).not.toHaveBeenCalled()
  })

  it('waits for the gateway before checking endpoints', () => {
    $signedIn.set(true)
    renderGate({ enabled: false })

    expect(getCustomEndpoints).not.toHaveBeenCalled()
  })
})
