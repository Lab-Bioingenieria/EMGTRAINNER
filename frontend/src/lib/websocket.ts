import { authService } from '@/services/auth.service'

/** Build a same-origin WebSocket URL and attach the current JWT as query auth. */
export function buildAuthenticatedWebSocketUrl(path: string): string {
  const url = new URL(path, window.location.origin)
  url.protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

  const authorization = authService.authHeaders().Authorization
  if (authorization?.startsWith('Bearer ')) {
    url.searchParams.set('token', authorization.slice('Bearer '.length))
  }

  return url.toString()
}
