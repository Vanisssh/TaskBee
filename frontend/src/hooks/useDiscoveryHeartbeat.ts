import { useEffect } from 'react'
import { apiClient } from '../services/api'

export default function useDiscoveryHeartbeat(options?: { id?: string; address?: string; tags?: string[] }) {
  const storageKey = 'taskbee.discovery.frontend.id'
  let id = options?.id || localStorage.getItem(storageKey) || `frontend-${Math.random().toString(36).slice(2, 9)}`
  useEffect(() => {
    if (!localStorage.getItem(storageKey)) localStorage.setItem(storageKey, id)

    // register once (best-effort)
    apiClient.post('/discovery/register', { id, address: options?.address || 'frontend:80', tags: options?.tags || ['frontend'] }).catch(() => {
      // ignore
    })

    const iv = setInterval(() => {
      apiClient.post('/discovery/renew', { id }).catch(() => {
        // ignore
      })
    }, 20000)

    return () => clearInterval(iv)
  }, [])

  return id
}
