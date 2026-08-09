import { API_BASE_URL } from '@/lib/constants'
import { redirectToLogin } from '@/lib/auth-redirect'

const TOKEN_KEY = 'emgt_access_token'

/** Clock skew allowance (seconds) when comparing the JWT `exp` claim. */
const EXPIRY_LEEWAY_SECONDS = 5

type TokenState = 'valid' | 'expired' | 'malformed'

/** Decode a JWT payload without verifying the signature (client-side UX only). */
function decodePayload(token: string): Record<string, unknown> | null {
  const parts = token.split('.')
  if (parts.length !== 3) return null
  try {
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const paddedBase64 = base64.padEnd(
      base64.length + ((4 - (base64.length % 4)) % 4),
      '=',
    )
    const json = decodeURIComponent(
      atob(paddedBase64)
        .split('')
        .map((c) => `%${c.charCodeAt(0).toString(16).padStart(2, '0')}`)
        .join('')
    )
    const payload = JSON.parse(json)
    return payload && typeof payload === 'object' ? payload : null
  } catch {
    return null
  }
}

/**
 * Classify a stored token. A token without an `exp` claim is treated as valid
 * here; the backend remains the authority on acceptance.
 */
function inspectToken(token: string): TokenState {
  const payload = decodePayload(token)
  if (!payload) return 'malformed'
  const exp = payload.exp
  if (exp === undefined || exp === null) return 'valid'
  if (typeof exp !== 'number' || !Number.isFinite(exp)) return 'malformed'
  const nowSeconds = Date.now() / 1000
  return exp + EXPIRY_LEEWAY_SECONDS <= nowSeconds ? 'expired' : 'valid'
}

function getValidStoredToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) return null
  if (inspectToken(token) !== 'valid') {
    authService.clearToken()
    return null
  }
  return token
}

export const authService = {
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },

  clearToken(): void {
    localStorage.removeItem(TOKEN_KEY)
  },

  /**
   * True only when a structurally valid, unexpired token is stored.
   * Expired or malformed tokens are cleared so the app fails closed.
   */
  isLoggedIn(): boolean {
    return getValidStoredToken() !== null
  },

  /**
   * Centralized session-expiry handling: drop the token and send the user to
   * login, keeping the current location as the post-login redirect.
   */
  handleUnauthorized(): void {
    authService.clearToken()
    redirectToLogin()
  },

  /** Authorization header for the stored token, or an empty object when logged out. */
  authHeaders(): Record<string, string> {
    const token = getValidStoredToken()
    return token ? { Authorization: `Bearer ${token}` } : {}
  },

  /** fetch() wrapper that always attaches the Authorization header. */
  async authFetch(input: string, init: RequestInit = {}): Promise<Response> {
    const headers = new Headers(init.headers)
    for (const [key, value] of Object.entries(authService.authHeaders())) {
      headers.set(key, value)
    }

    const response = await fetch(input, {
      ...init,
      headers,
    })

    // Mirror the axios interceptor: a rejected session logs out everywhere.
    if (response.status === 401) {
      authService.handleUnauthorized()
    }

    return response
  },

  async login(email: string, password: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.message || 'Credenciales incorrectas')
    }
    const data = await res.json()
    authService.setToken(data.access_token)
  },

  async register(email: string, password: string, username: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.message || 'Error al registrar usuario')
    }
    // auto-login after register
    await authService.login(email, password)
  },
}
