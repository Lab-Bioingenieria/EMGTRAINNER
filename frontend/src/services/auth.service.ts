import { API_BASE_URL } from '@/lib/constants'

const TOKEN_KEY = 'emgt_access_token'

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

  isLoggedIn(): boolean {
    return !!localStorage.getItem(TOKEN_KEY)
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
